import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import pandas as pd
import json
from datetime import datetime

# --- 1. SETUP ---
groq_key = st.secrets.get("GROQ_API_KEY")
sb_url = st.secrets.get("SUPABASE_URL")
sb_key = st.secrets.get("SUPABASE_KEY")

if not all([groq_key, sb_url, sb_key]):
    st.error("Secrets Missing: Check GROQ_API_KEY, SUPABASE_URL, and SUPABASE_KEY.")
    st.stop()

client_groq = Groq(api_key=groq_key)
supabase: Client = create_client(sb_url, sb_key)

st.set_page_config(page_title="Run&Drive AI | Market Pro", layout="centered")

# --- 2. THE AGGRESSIVE CSS FIX ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&display=swap');
    
    /* Force Light Mode Aesthetics */
    .stApp { background-color: #ffffff; color: #000000; }
    #MainMenu, footer, header, .stDeployButton, div[data-testid="stToolbar"] {visibility: hidden; display: none;}
    
    .main-title { font-family: 'Montserrat', sans-serif; font-size: 4rem; color: #000000 !important; text-align: center; margin-bottom: 0px; }
    .sub-title { font-family: 'Montserrat', sans-serif; font-size: 1rem; color: #32cd32 !important; text-align: center; text-transform: uppercase; letter-spacing: 2px; margin-bottom: 40px; }
    
    /* Universal Label Visibility */
    label, p, span, div, .stMarkdown { color: #000000 !important; font-weight: 700; }
    
    /* Main Inputs */
    .stTextInput input, .stNumberInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #eeeeee !important; 
        border-radius: 8px !important;
        caret-color: #000000 !important; 
    }

    /* --- THE FIX FOR THE BLACK BOX (POPOVER) --- */
    /* This forces the popover container to be WHITE */
    div[data-testid="stPopoverBody"] {
        background-color: #ffffff !important;
        border: 2px solid #32cd32 !important;
        padding: 20px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
    }
    
    /* This forces all text inside the popover to be BLACK */
    div[data-testid="stPopoverBody"] * {
        color: #000000 !important;
    }

    /* Style the trigger button at the bottom */
    div[data-testid="stPopover"] > button {
        background-color: #f8f9fa !important;
        color: #32cd32 !important;
        border: 1px solid #32cd32 !important;
        font-weight: 700 !important;
        width: 100% !important;
        border-radius: 10px !important;
    }

    /* Primary Analysis Button */
    div.stButton > button:first-child { 
        background-color: #32cd32 !important; 
        color: #000000 !important;           
        font-weight: 900 !important; 
        width: 100% !important; 
        border-radius: 12px !important; 
        height: 4.5rem !important; 
        border: none !important; 
    }

    .stat-card { background: #ffffff; padding: 25px; border-radius: 15px; border: 1px solid #eee; border-bottom: 5px solid #32cd32; text-align: center; margin-bottom: 20px; }
    .stat-card h1 { color: #000000 !important; margin: 5px 0; font-weight: 900; font-size: 2.8rem; }
    .green-text { color: #32cd32 !important; }
    .insight-box { background: #f9f9f9; padding: 20px; border-radius: 10px; border-left: 5px solid #32cd32; margin-top: 20px; color: #000 !important; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. LOGIC ---
def deep_market_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=6)
            return "\n".join([f"{r['title']}: {r['body']}" for r in results]) if results else "No data."
    except:
        return "Search error."

# --- 4. THE UI ---
st.markdown('<h1 class="main-title">Run&Drive</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Expert Market Intelligence</p>', unsafe_allow_html=True)

with st.container():
    brand = st.text_input("Car Brand", placeholder="Enter brand...")
    model = st.text_input("Car Model", placeholder="Enter model...")
    trim = st.text_input("Trim / Version (Optional)", placeholder="e.g. Sport")
    year = st.number_input("Year of Manufacture", min_value=1900, max_value=2026, value=2024)
    miles = st.number_input("Current Odometer Reading (Miles)", min_value=0, value=0)
    
    submit = st.button("RUN DEEP MARKET ANALYSIS")

    # --- THE REQUEST POPOVER ---
    with st.popover("Can't find your car? Request it here"):
        st.markdown("### Vehicle Support Request")
        st.write("Enter details below and we will add this car to our database.")
        
        r_brand = st.text_input("Request Brand", key="req_b")
        r_model = st.text_input("Request Model", key="req_m")
        r_year = st.number_input("Year", 1900, 2026, 2024, key="req_y")
        r_trim = st.text_input("Trim", key="req_t")
        
        if st.button("SUBMIT REQUEST", key="btn_req"):
            if r_brand and r_model:
                try:
                    supabase.table("car_requests").insert({
                        "brand": r_brand, "model": r_model, "year": r_year, "trim": r_trim
                    }).execute()
                    st.toast("🚀 Request received! Your car will be added shortly.", icon="✅")
                except Exception as e:
                    st.error(f"Sync error: {e}")
            else:
                st.warning("Brand and Model are required.")

# --- 5. EXECUTION ---
if submit and brand and model:
    with st.spinner("Analyzing Market Data..."):
        clean_trim = trim.strip() if trim else ""
        full_name = f"{year} {brand} {model} {clean_trim}".strip().replace("  ", " ")
        search_results = deep_market_search(f"{full_name} specs and market price")
        
        try:
            prompt = f"Verify and value {full_name} at {miles} miles. Use context: {search_results}. Return JSON: {{'exists': bool, 'price': 'str', 'trend': 'str', 'specs': {{'engine': 'str', 'hp': 'str', 'zero_sixty': 'str', 'top': 'str'}}, 'why': 'str'}}"
            response = client_groq.chat.completions.create(
                messages=[{"role":"user","content":prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1
            ).choices[0].message.content

            data = json.loads(response.replace('```json', '').replace('```', '').strip())

            if not data.get("exists", True):
                st.error(f"Analysis Rejected: {data['why']}")
            else:
                try:
                    supabase.table("car_logs").insert({
                        "brand": brand, "model": model, "year": year, 
                        "price": data["price"], "miles": miles, "logic": data["why"]
                    }).execute()
                    st.toast("📊 Data Logged")
                except: pass

                st.markdown(f"<h2 style='text-align:center; color:black; margin-top:40px;'>{full_name}</h2>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                c1.markdown(f'<div class="stat-card"><small>ESTIMATED VALUE</small><h1 class="green-text">{data["price"]}</h1></div>', unsafe_allow_html=True)
                c2.markdown(f'<div class="stat-card"><small>MARKET TREND</small><h1>{data["trend"]}</h1></div>', unsafe_allow_html=True)

                p1, p2, p3, p4 = st.columns(4)
                p1.markdown(f'<div class="stat-card"><small>ENGINE</small><h3>{data["specs"]["engine"]}</h3></div>', unsafe_allow_html=True)
                p2.markdown(f'<div class="stat-card"><small>POWER</small><h3>{data["specs"]["hp"]} HP</h3></div>', unsafe_allow_html=True)
                p3.markdown(f'<div class="stat-card"><small>0-60</small><h3>{data["specs"]["zero_sixty"]}s</h3></div>', unsafe_allow_html=True)
                p4.markdown(f'<div class="stat-card"><small>TOP SPEED</small><h3>{data["specs"]["top"]}</h3></div>', unsafe_allow_html=True)
                st.markdown(f'<div class="insight-box"><b>Logic:</b> {data["why"]}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error: {e}")
