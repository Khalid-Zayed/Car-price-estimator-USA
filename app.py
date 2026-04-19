import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import json

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

# --- 2. FULL CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;900&display=swap');

    /* ── Global ── */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    #MainMenu, footer, header, .stDeployButton,
    div[data-testid="stToolbar"] { visibility: hidden; display: none; }

    /* ── Typography ── */
    .main-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 3.8rem;
        color: #000000 !important;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -1px;
    }
    .sub-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.85rem;
        color: #32cd32 !important;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 4px;
        margin-bottom: 40px;
    }
    label, p, span, div, .stMarkdown { color: #000000 !important; font-weight: 600; }

    /* ── Input Fields ── */
    .stTextInput input, .stNumberInput input {
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #e8e8e8 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #32cd32 !important;
        box-shadow: 0 0 0 1px #32cd32 !important;
    }

    /* ── PRIMARY BUTTON — green on ALL states ── */
    div.stButton > button:first-child {
        background-color: #32cd32 !important;
        color: #000000 !important;
        font-weight: 900 !important;
        width: 100% !important;
        border-radius: 12px !important;
        height: 4.5rem !important;
        border: none !important;
        font-family: 'Montserrat', sans-serif !important;
        letter-spacing: 1px !important;
        transition: background-color 0.15s ease, transform 0.1s ease !important;
    }
    div.stButton > button:first-child:hover {
        background-color: #28b828 !important;
        color: #000000 !important;
        transform: translateY(-1px) !important;
        border: none !important;
    }
    div.stButton > button:first-child:active {
        background-color: #22a022 !important;
        color: #000000 !important;
        transform: translateY(0px) !important;
        border: none !important;
    }
    div.stButton > button:first-child:focus,
    div.stButton > button:first-child:focus:not(:active) {
        background-color: #32cd32 !important;
        color: #000000 !important;
        border: none !important;
        box-shadow: 0 0 0 3px rgba(50,205,50,0.35) !important;
    }

    /* ── POPOVER: force white regardless of browser dark mode ── */
    div[data-testid="stPopover"] > div,
    div[data-testid="stPopoverBody"],
    section[data-testid="stPopoverBody"] {
        background-color: #ffffff !important;
        border: 2px solid #32cd32 !important;
        color: #000000 !important;
    }
    div[data-testid="stPopoverBody"] *,
    section[data-testid="stPopoverBody"] * {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    [data-baseweb="popover"] > div,
    [data-baseweb="popover"] ul,
    [data-baseweb="popover"] li {
        background-color: #ffffff !important;
        color: #000000 !important;
    }
    div[data-testid="stPopoverBody"] input,
    section[data-testid="stPopoverBody"] input {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #e8e8e8 !important;
        border-radius: 8px !important;
    }

    /* ── Result Cards ── */
    .stat-card {
        background: #ffffff;
        padding: 22px 18px;
        border-radius: 14px;
        border: 1px solid #eeeeee;
        border-bottom: 4px solid #32cd32;
        text-align: center;
        margin-bottom: 16px;
    }
    .stat-card small {
        font-size: 0.68rem !important;
        color: #999999 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
    }
    .stat-card h1 {
        color: #000000 !important;
        font-weight: 900;
        font-size: 2.4rem;
        margin: 6px 0 0 0;
        font-family: 'Montserrat', sans-serif;
    }
    .stat-card h3 {
        color: #000000 !important;
        font-weight: 700;
        font-size: 1.05rem;
        margin: 6px 0 0 0;
    }
    .green-text { color: #32cd32 !important; }

    .insight-box {
        background: #f8f9f8;
        padding: 22px 24px;
        border-radius: 12px;
        border-left: 5px solid #32cd32;
        color: #000 !important;
        line-height: 1.7;
        font-size: 0.95rem;
        margin-top: 8px;
    }

    .car-header {
        text-align: center;
        margin: 36px 0 24px 0;
    }
    .car-header h2 {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.8rem;
        font-weight: 900;
        color: #000000 !important;
        margin: 0 0 4px 0;
    }
    .car-header small {
        color: #999 !important;
        font-size: 0.78rem;
        letter-spacing: 1.5px;
        font-weight: 700;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)


# --- 3. SEARCH LOGIC ---
def deep_market_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=7)
            return "\n".join([f"{r['title']}: {r['body']}" for r in results]) if results else "No data found."
    except Exception:
        return "Search unavailable."


# --- 4. TREND ICON HELPER ---
def trend_icon(trend_str):
    t = trend_str.lower()
    if any(w in t for w in ["up", "rising", "increas", "appreciat", "strong", "bull"]):
        return "▲"
    if any(w in t for w in ["down", "fall", "declin", "depreciat", "weak", "bear"]):
        return "▼"
    return "─"


# --- 5. THE INTERFACE ---
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
        st.markdown(
            "<h3 style='color:#32cd32; font-family:Montserrat,sans-serif;'>Vehicle Support Request</h3>",
            unsafe_allow_html=True,
        )
        r_brand = st.text_input("Brand", key="req_b")
        r_model = st.text_input("Model", key="req_m")
        r_year = st.number_input("Year", 1900, 2026, 2024, key="req_y")

        if st.button("SUBMIT REQUEST", key="req_submit"):
            if r_brand and r_model:
                try:
                    supabase.table("car_requests").insert(
                        {"brand": r_brand, "model": r_model, "year": int(r_year)}
                    ).execute()
                    st.toast("Request received!", icon="✅")
                except Exception:
                    st.error("Database connection issue. Please try again.")
            else:
                st.warning("Please fill in both Brand and Model.")


# --- 6. AI EXECUTION & RESULTS ---
if submit and brand and model:
    full_name = f"{year} {brand} {model} {trim}".strip()
    miles_display = f"{int(miles):,}"

    with st.spinner(f"Scanning live market data for {full_name}..."):
        search_results = deep_market_search(f"{full_name} market price valuation specifications")

    with st.spinner("Running AI valuation analysis..."):
        try:
            system_msg = (
                "You are an expert automotive market analyst. "
                "Always respond with valid JSON only. No markdown, no explanation, no extra text."
            )
            prompt = (
                f"Analyze the market value of a {full_name} with {miles} miles on the odometer.\n"
                f"Use this real-time market context:\n{search_results}\n\n"
                f"Return a single JSON object with these exact keys:\n"
                f"- exists (boolean): true if this is a real vehicle model, false if not\n"
                f"- price (string): estimated market value range, e.g. '$85,000 – $95,000'\n"
                f"- trend (string): one short phrase describing the market trend, e.g. 'Rising steadily'\n"
                f"- specs: an object with keys engine, hp, zero_sixty, top (all strings)\n"
                f"- why (string): 2-3 sentence explanation of the valuation and key factors\n"
                f"If exists is false, set why to explain why the vehicle is unknown or invalid."
            )

            raw = client_groq.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
            ).choices[0].message.content

            cleaned = raw.replace("```json", "").replace("```", "").strip()
            data = json.loads(cleaned)

        except json.JSONDecodeError:
            st.error("The AI returned an unexpected format. Please try again.")
            st.stop()
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    if not data.get("exists", True):
        st.error(f"Vehicle not recognised: {data.get('why', 'Unknown vehicle model.')}")
    else:
        # Log to Supabase (silent fail)
        try:
            supabase.table("car_logs").insert({
                "brand": brand,
                "model": model,
                "year": int(year),
                "price": data["price"],
                "miles": int(miles),
                "logic": data["why"],
            }).execute()
        except Exception:
            pass

        # Results Dashboard
        icon = trend_icon(data["trend"])

        st.markdown(
            f'<div class="car-header">'
            f'<h2>{full_name}</h2>'
            f'<small>{miles_display} miles on odometer</small>'
            f'</div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2)
        c1.markdown(
            f'<div class="stat-card">'
            f'<small>Estimated Value</small>'
            f'<h1 class="green-text">{data["price"]}</h1>'
            f'</div>',
            unsafe_allow_html=True,
        )
        c2.markdown(
            f'<div class="stat-card">'
            f'<small>Market Trend</small>'
            f'<h1>{icon} {data["trend"]}</h1>'
            f'</div>',
            unsafe_allow_html=True,
        )

        p1, p2, p3, p4 = st.columns(4)
        p1.markdown(
            f'<div class="stat-card"><small>Engine</small>'
            f'<h3>{data["specs"]["engine"]}</h3></div>',
            unsafe_allow_html=True,
        )
        p2.markdown(
            f'<div class="stat-card"><small>Power</small>'
            f'<h3>{data["specs"]["hp"]}</h3></div>',
            unsafe_allow_html=True,
        )
        p3.markdown(
            f'<div class="stat-card"><small>0 – 60 mph</small>'
            f'<h3>{data["specs"]["zero_sixty"]}s</h3></div>',
            unsafe_allow_html=True,
        )
        p4.markdown(
            f'<div class="stat-card"><small>Top Speed</small>'
            f'<h3>{data["specs"]["top"]}</h3></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="insight-box">'
            f'<b>AI Valuation Logic:</b><br>{data["why"]}'
            f'</div>',
            unsafe_allow_html=True,
        )
