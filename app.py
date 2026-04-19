import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
import json

# --- 1. CONFIG & SECRETS ---
groq_key = st.secrets.get("GROQ_API_KEY")
sb_url   = st.secrets.get("SUPABASE_URL")
sb_key   = st.secrets.get("SUPABASE_KEY")

if not all([groq_key, sb_url, sb_key]):
    st.error("Missing Secrets! Check GROQ_API_KEY, SUPABASE_URL, and SUPABASE_KEY.")
    st.stop()

client_groq = Groq(api_key=groq_key)
supabase: Client = create_client(sb_url, sb_key)

st.set_page_config(page_title="Run&Drive AI | Market Pro", layout="centered")

# --- 2. CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&display=swap');

    /* ── Global ── */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    #MainMenu, footer, header, .stDeployButton,
    div[data-testid="stToolbar"] { visibility: hidden; display: none; }

    /* ── Body font — bigger and more professional ── */
    html, body, [class*="css"] {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 16px !important;
    }

    /* ── Labels ── */
    label {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 700 !important;
        color: #111111 !important;
        letter-spacing: 0.3px !important;
    }

    /* ── General text ── */
    p, span, div, .stMarkdown {
        color: #000000 !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    /* ── Page title ── */
    .main-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 4.2rem;
        font-weight: 900;
        color: #000000 !important;
        text-align: center;
        margin-bottom: 0px;
        letter-spacing: -2px;
    }
    .sub-title {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.82rem;
        font-weight: 700;
        color: #32cd32 !important;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 5px;
        margin-bottom: 44px;
    }

    /* ── Text inputs ── */
    .stTextInput input, .stNumberInput input {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #000000 !important;
        background-color: #ffffff !important;
        border: 2px solid #e0e0e0 !important;
        border-radius: 10px !important;
        padding: 0.6rem 0.9rem !important;
        caret-color: #000000 !important;   /* FIX: blinking cursor now visible */
    }
    .stTextInput input::placeholder, .stNumberInput input::placeholder {
        color: #aaaaaa !important;
        font-weight: 500 !important;
    }
    .stTextInput input:focus, .stNumberInput input:focus {
        border-color: #32cd32 !important;
        box-shadow: 0 0 0 2px rgba(50,205,50,0.20) !important;
        outline: none !important;
        caret-color: #000000 !important;
    }

    /* ── Number stepper +/- buttons ── */
    button[data-testid="stNumberInputStepDown"],
    button[data-testid="stNumberInputStepUp"] {
        background-color: #f4f4f4 !important;
        color: #000000 !important;
        border: 1px solid #e0e0e0 !important;
        font-weight: 700 !important;
    }
    button[data-testid="stNumberInputStepDown"]:hover,
    button[data-testid="stNumberInputStepUp"]:hover {
        background-color: #32cd32 !important;
        color: #000000 !important;
        border-color: #32cd32 !important;
    }

    /* ── Global button base (prevents dark-mode black override) ── */
    button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #cccccc !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    /* ── PRIMARY CTA button — green, all states ── */
    div.stButton > button:first-child {
        background-color: #32cd32 !important;
        color: #000000 !important;
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1rem !important;
        font-weight: 900 !important;
        letter-spacing: 1.5px !important;
        width: 100% !important;
        border-radius: 12px !important;
        height: 4rem !important;
        border: none !important;
        margin-top: 6px !important;
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
        box-shadow: 0 0 0 3px rgba(50,205,50,0.30) !important;
    }

    /* ── POPOVER trigger button — slim white pill with green border ── */
    div[data-testid="stPopover"] > button,
    button[data-testid="stPopoverButton"],
    div[data-testid="stPopover"] button {
        background-color: #ffffff !important;
        color: #222222 !important;
        border: 1.5px solid #32cd32 !important;
        border-radius: 10px !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important;
        padding: 0.45rem 1rem !important;
        height: auto !important;
        width: auto !important;
    }
    div[data-testid="stPopover"] > button:hover,
    div[data-testid="stPopover"] button:hover {
        background-color: #f2fdf2 !important;
        color: #000000 !important;
        border-color: #28b828 !important;
    }

    /* ── POPOVER BODY ── */
    div[data-testid="stPopoverBody"],
    section[data-testid="stPopoverBody"],
    div[data-testid="stPopover"] > div {
        background-color: #ffffff !important;
        border: 2px solid #32cd32 !important;
        border-radius: 14px !important;
        padding: 20px !important;
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
        border: 2px solid #e0e0e0 !important;
        border-radius: 8px !important;
        caret-color: #000000 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }

    /* ── SUBMIT REQUEST button inside popover — compact, not fat ── */
    div[data-testid="stPopoverBody"] div.stButton > button,
    section[data-testid="stPopoverBody"] div.stButton > button {
        background-color: #32cd32 !important;
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 0.85rem !important;
        letter-spacing: 1px !important;
        width: auto !important;
        min-width: 160px !important;
        height: 2.6rem !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0 1.2rem !important;
        margin-top: 8px !important;
    }
    div[data-testid="stPopoverBody"] div.stButton > button:hover,
    section[data-testid="stPopoverBody"] div.stButton > button:hover {
        background-color: #28b828 !important;
        color: #000000 !important;
        border: none !important;
    }

    /* ── Result cards ── */
    .stat-card {
        background: #ffffff;
        padding: 24px 16px;
        border-radius: 14px;
        border: 1px solid #eeeeee;
        border-bottom: 4px solid #32cd32;
        text-align: center;
        margin-bottom: 16px;
    }
    .stat-card small {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 0.65rem !important;
        color: #999999 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-weight: 700;
    }
    .stat-card h1 {
        font-family: 'Montserrat', sans-serif !important;
        color: #000000 !important;
        font-weight: 900;
        font-size: 2.2rem;
        margin: 8px 0 0 0;
    }
    .stat-card h3 {
        font-family: 'Montserrat', sans-serif !important;
        color: #000000 !important;
        font-weight: 700;
        font-size: 1rem;
        margin: 8px 0 0 0;
    }
    .green-text { color: #32cd32 !important; }

    .insight-box {
        background: #f8faf8;
        padding: 22px 26px;
        border-radius: 12px;
        border-left: 5px solid #32cd32;
        color: #111 !important;
        line-height: 1.75;
        font-size: 0.97rem;
        font-family: 'Montserrat', sans-serif !important;
        margin-top: 10px;
    }

    .car-header {
        text-align: center;
        margin: 40px 0 28px 0;
    }
    .car-header h2 {
        font-family: 'Montserrat', sans-serif;
        font-size: 1.9rem;
        font-weight: 900;
        color: #000000 !important;
        letter-spacing: -0.5px;
        margin: 0 0 6px 0;
    }
    .car-header small {
        color: #999 !important;
        font-size: 0.75rem;
        letter-spacing: 2px;
        font-weight: 700;
        text-transform: uppercase;
        font-family: 'Montserrat', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)


# --- 3. SEARCH ---
def deep_market_search(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=7)
            return "\n".join([f"{r['title']}: {r['body']}" for r in results]) if results else "No data found."
    except Exception:
        return "Search unavailable."


# --- 4. TREND ICON ---
def trend_icon(trend_str):
    t = trend_str.lower()
    if any(w in t for w in ["up", "rising", "increas", "appreciat", "strong", "bull"]):
        return "▲"
    if any(w in t for w in ["down", "fall", "declin", "depreciat", "weak", "bear"]):
        return "▼"
    return "─"


# --- 5. INTERFACE ---
st.markdown('<h1 class="main-title">Run&Drive</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Expert Market Intelligence</p>', unsafe_allow_html=True)

with st.container():
    brand = st.text_input("Car Brand", placeholder="e.g. Mercedes-Benz")
    model = st.text_input("Car Model", placeholder="e.g. G63 AMG")
    trim  = st.text_input("Trim / Version (Optional)", placeholder="e.g. Magno Edition")
    year  = st.number_input("Year of Manufacture", min_value=1900, max_value=2026, value=2024)
    miles = st.number_input("Current Odometer (Miles)", min_value=0, value=0)

    submit = st.button("RUN DEEP MARKET ANALYSIS")

    # ── Popover: all 5 fields matching the main form ──
    with st.popover("Can't find your car? Request adding it now"):
        st.markdown(
            "<h3 style='color:#32cd32; font-family:Montserrat,sans-serif; "
            "font-size:1.1rem; font-weight:900; margin-bottom:16px;'>"
            "Vehicle Support Request</h3>",
            unsafe_allow_html=True,
        )
        r_brand = st.text_input("Car Brand", key="req_brand", placeholder="e.g. Ferrari")
        r_model = st.text_input("Car Model", key="req_model", placeholder="e.g. SF90 Stradale")
        r_trim  = st.text_input("Trim / Version (Optional)", key="req_trim",  placeholder="e.g. Assetto Fiorano")
        r_year  = st.number_input("Year of Manufacture", min_value=1900, max_value=2026, value=2024, key="req_year")
        r_miles = st.number_input("Current Odometer (Miles)", min_value=0, value=0, key="req_miles")

        if st.button("SUBMIT REQUEST", key="req_submit"):
            if r_brand and r_model:
                try:
                    supabase.table("car_requests").insert({
                        "brand": r_brand,
                        "model": r_model,
                        "trim":  r_trim,
                        "year":  int(r_year),
                        "miles": int(r_miles),
                    }).execute()
                    st.toast("Request received!", icon="✅")
                except Exception:
                    st.error("Database connection issue. Please try again.")
            else:
                st.warning("Please fill in at least Brand and Model.")


# --- 6. AI & RESULTS ---
if submit and brand and model:
    full_name     = f"{year} {brand} {model} {trim}".strip()
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
                f"- price (string): estimated market value range, e.g. '$85,000 - $95,000'\n"
                f"- trend (string): one short phrase describing the market trend, e.g. 'Rising steadily'\n"
                f"- specs: an object with keys engine, hp, zero_sixty, top (all strings)\n"
                f"- why (string): 2-3 sentence explanation of the valuation and key factors\n"
                f"If exists is false, set why to explain why the vehicle is unknown or invalid."
            )

            raw = client_groq.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user",   "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1,
            ).choices[0].message.content

            cleaned = raw.replace("```json", "").replace("```", "").strip()
            data    = json.loads(cleaned)

        except json.JSONDecodeError:
            st.error("The AI returned an unexpected format. Please try again.")
            st.stop()
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    if not data.get("exists", True):
        st.error(f"Vehicle not recognised: {data.get('why', 'Unknown vehicle model.')}")
    else:
        try:
            supabase.table("car_logs").insert({
                "brand": brand,
                "model": model,
                "year":  int(year),
                "price": data["price"],
                "miles": int(miles),
                "logic": data["why"],
            }).execute()
        except Exception:
            pass

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
            f'<div class="stat-card"><small>Estimated Value</small>'
            f'<h1 class="green-text">{data["price"]}</h1></div>',
            unsafe_allow_html=True,
        )
        c2.markdown(
            f'<div class="stat-card"><small>Market Trend</small>'
            f'<h1>{icon} {data["trend"]}</h1></div>',
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
