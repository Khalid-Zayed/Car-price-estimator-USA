import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import pandas as pd
import json
from datetime import datetime

# --- 1. CONFIG & SECRETS ---
groq_key = st.secrets.get("GROQ_API_KEY")
sb_url = st.secrets.get("SUPABASE_URL")
sb_key = st.secrets.get("SUPABASE_KEY")

if not all([groq_key, sb_url, sb_key]):
    st.error("Missing Secrets! Check GROQ_API_KEY, SUPABASE_URL, and SUPABASE_KEY.")
    st.stop()

client_groq = Groq(api_key=groq_key)
supabase: Client = create_client(sb_url, sb_key)

st.set_page_config(page_title="Run&Drive AI | Market Pro", layout="centered")

# --- 2. CSS (POPOVER DARK-MODE FIX + FULL THEME) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;900&display=swap');

    /* ── Global ── */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    #MainMenu, footer, header, .stDeployButton,
    div[data-testid="stToolbar"] { visibility: hidden; display: none; }

    /* ── Typography ── */
    .main-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 4rem; color: #000000 !important;
        text-align: center; margin-bottom: 0px;
    }
    .sub-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 1rem; color: #32cd32 !important;
        text-align: center; text-transform: uppercase;
        letter-spacing: 2px; margin-bottom: 40px;
    }
    label, p, span, div, .stMarkdown { color: #000000 !important; font-weight: 700; }

    /* ── Input Fields ── */
    .stTextInput input, .stNumberInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #eeeeee !important;
        border-radius: 8px !important;
    }

    /* ── POPOVER FIX: force white + black in ALL dark-mode scenarios ── */

    /* The outer popover container */
    div[data-testid="stPopover"] > div,
    div[data-testid="stPopoverBody"],
    section[data-testid="stPopoverBody"] {
        background-color: #ffffff !important;
        border: 2px solid #32cd32 !important;
        color: #000000 !important;
    }

    /* Every element INSIDE the popover */
    div[data-testid="stPopoverBody"] *,
    section[data-testid="stPopoverBody"] * {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Override the Streamlit popover arrow / backdrop */
    [data-baseweb="popover"] > div,
    [data-baseweb="popover"] ul,
    [data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }

    /* Input fields specifically inside the popover */
    div[data-testid="stPopoverBody"] input,
    section[data-testid="stPopoverBody"] input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #eeeeee !important;
        border-radius: 8px !important;
    }

    /* ── Primary Button ── */
    div.stButton > button:first-child {
        background-color: #32cd32 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        width: 100% !important;
        border-radius: 12px !important;
        height: 4.5rem !important;
        border: none !important;
    }

    /* ── Result Cards ── */
    .stat-card {
        background: #ffffff;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #eee;
        border-bottom: 5px solid #32cd32;
        text-align: center;
        margin-bottom: 20px;
    }
    .stat-card h1 { color: #000000 !important; font-weight: 900; font-size: 2.8rem; margin: 5px 0; }
    .green-text { color: #32cd32 !important; }
    .insight-box {
        background: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #32cd32;
        color: #000 !important;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)


# --- 3. SEARCH LOGIC ---
def deep_market_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=6)
            return "\n".join([f"{r['title']}: {r['body']}" for r in results]) if results else "No data."
    except Exception:
        return "Search error."


# --- 4. THE INTERFACE ---
st.markdown('<h1 class="main-title">Run&Drive</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Expert Market Intelligence</p>', unsafe_allow_html=True)

with st.container():
    brand = st.text_input("Car Brand", placeholder="e.g. Mercedes-Benz")
    model = st.text_input("Car Model", placeholder="e.g. G63 AMG")
    trim = st.text_input("Trim / Version (Optional)", placeholder="e.g. Magno Edition")
    year = st.number_input("Year of Manufacture", 1900, 2026, 2024)
    miles = st.number_input("Current Odometer (Miles)", 0, value=0)

    submit = st.button("RUN DEEP MARKET ANALYSIS")

    with st.popover("Can't find your car? Request adding it now"):
        st.markdown("<h3 style='color:#32cd32;'>Vehicle Support Request</h3>", unsafe_allow_html=True)
        r_brand = st.text_input("Brand", key="req_b")
        r_model = st.text_input("Model", key="req_m")
        r_year = st.number_input("Year", 1900, 2026, 2024, key="req_y")

        if st.button("SUBMIT REQUEST", key="req_submit"):
            if r_brand and r_model:
                try:
                    supabase.table("car_requests").insert(
                        {"brand": r_brand, "model": r_model, "year": r_year}
                    ).execute()
                    st.toast("🚀 Request received!", icon="✅")
                except Exception:
                    st.error("Database connection issue.")


# --- 5. AI EXECUTION & RESULTS DASHBOARD ---
if submit and brand and model:
    with st.spinner("Analyzing Market Data..."):
        full_name = f"{year} {brand} {model} {trim}".strip()
        search_results = deep_market_search(f"{full_name} market price and specifications")

        try:
            prompt = (
                f"Analyze {full_name} with {miles} miles. "
                f"Use context: {search_results}. "
                f"Return JSON only: {{'exists': bool, 'price': 'str', 'trend': 'str', "
                f"'specs': {{'engine': 'str', 'hp': 'str', 'zero_sixty': 'str', 'top': 'str'}}, 'why': 'str'}}"
            )
            response = client_groq.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
            ).choices[0].message.content

            data = json.loads(response.replace("```json", "").replace("```", "").strip())

            if not data.get("exists", True):
                st.error(f"Analysis Rejected: {data['why']}")
            else:
                # Log to Supabase
                try:
                    supabase.table("car_logs").insert({
                        "brand": brand,
                        "model": model,
                        "year": year,
                        "price": data["price"],
                        "miles": miles,
                        "logic": data["why"],
                    }).execute()
                except Exception:
                    pass

                # Results Dashboard
                st.markdown(
                    f"<h2 style='text-align:center; color:black; margin-top:40px;'>{full_name}</h2>",
                    unsafe_allow_html=True,
                )

                c1, c2 = st.columns(2)
                c1.markdown(
                    f'<div class="stat-card"><small>ESTIMATED VALUE</small>'
                    f'<h1 class="green-text">{data["price"]}</h1></div>',
                    unsafe_allow_html=True,
                )
                c2.markdown(
                    f'<div class="stat-card"><small>MARKET TREND</small>'
                    f'<h1>{data["trend"]}</h1></div>',
                    unsafe_allow_html=True,
                )

                p1, p2, p3, p4 = st.columns(4)
                p1.markdown(
                    f'<div class="stat-card"><small>ENGINE</small>'
                    f'<h3>{data["specs"]["engine"]}</h3></div>',
                    unsafe_allow_html=True,
                )
                p2.markdown(
                    f'<div class="stat-card"><small>POWER</small>'
                    f'<h3>{data["specs"]["hp"]}</h3></div>',
                    unsafe_allow_html=True,
                )
                p3.markdown(
                    f'<div class="stat-card"><small>0-60</small>'
                    f'<h3>{data["specs"]["zero_sixty"]}s</h3></div>',
                    unsafe_allow_html=True,
                )
                p4.markdown(
                    f'<div class="stat-card"><small>TOP SPEED</small>'
                    f'<h3>{data["specs"]["top"]}</h3></div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<div class="insight-box"><b>AI Valuation Logic:</b> {data["why"]}</div>',
                    unsafe_allow_html=True,
                )

        except Exception as e:
            st.error(f"Market analysis timeout. Error: {e}")
