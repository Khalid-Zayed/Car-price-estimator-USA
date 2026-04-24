import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS
from supabase import create_client, Client
from datetime import datetime
import json

# ============================================================
# 1. CONFIG & CLIENTS
# ============================================================
groq_key = st.secrets.get("GROQ_API_KEY")
sb_url   = st.secrets.get("SUPABASE_URL")
sb_key   = st.secrets.get("SUPABASE_KEY")

if not all([groq_key, sb_url, sb_key]):
    st.error("Missing Secrets! Check GROQ_API_KEY, SUPABASE_URL, and SUPABASE_KEY.")
    st.stop()

client_groq = Groq(api_key=groq_key)
supabase: Client = create_client(sb_url, sb_key)

st.set_page_config(page_title="Run&Drive AI | Market Pro", layout="centered")

# ============================================================
# 2. CSS  (gatekeeper page + main dashboard)
# ============================================================
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;900&display=swap');

    /* ── Global ── */
    .stApp { background-color: #ffffff !important; color: #000000 !important; }
    #MainMenu, footer, header, .stDeployButton,
    div[data-testid="stToolbar"] { visibility: hidden; display: none; }

    /* ── Body font ── */
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

    /* ── Page titles ── */
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

    /* ── Gatekeeper page ── */
    .gate-wrapper {
        max-width: 460px;
        margin: 80px auto 0 auto;
        text-align: center;
    }
    .gate-logo {
        font-family: 'Montserrat', sans-serif;
        font-size: 3.6rem;
        font-weight: 900;
        color: #000000 !important;
        letter-spacing: -2px;
        margin-bottom: 4px;
    }
    .gate-sub {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.78rem;
        font-weight: 700;
        color: #32cd32 !important;
        text-transform: uppercase;
        letter-spacing: 5px;
        margin-bottom: 52px;
    }
    .gate-label {
        font-family: 'Montserrat', sans-serif;
        font-size: 0.82rem;
        font-weight: 700;
        color: #888888 !important;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-bottom: 10px;
        text-align: left;
    }
    .gate-divider {
        width: 48px;
        height: 3px;
        background: #32cd32;
        border-radius: 2px;
        margin: 0 auto 36px auto;
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
        caret-color: #000000 !important;
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

    /* ── Number stepper +/- ── */
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

    /* ── Global button base ── */
    button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border-color: #cccccc !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    /* ── PRIMARY CTA — green, all states ── */
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

    /* ── REQUEST TOGGLE BUTTON ── */
    .request-toggle > div.stButton > button:first-child {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1.5px solid #32cd32 !important;
        border-radius: 10px !important;
        font-size: 0.88rem !important;
        font-weight: 700 !important;
        height: auto !important;
        width: auto !important;
        min-width: 0 !important;
        padding: 0.5rem 1.2rem !important;
        letter-spacing: 0.3px !important;
        margin-top: 0 !important;
    }
    .request-toggle > div.stButton > button:first-child:hover {
        background-color: #f2fdf2 !important;
        color: #000000 !important;
        border-color: #28b828 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    .request-toggle > div.stButton > button:first-child:focus {
        background-color: #ffffff !important;
        color: #111111 !important;
        border: 1.5px solid #32cd32 !important;
        box-shadow: none !important;
    }

    /* ── REQUEST PANEL ── */
    .request-panel {
        background: #ffffff;
        border: 2px solid #32cd32;
        border-radius: 14px;
        padding: 24px 28px;
        margin-top: 12px;
    }
    .request-panel h3 {
        font-family: 'Montserrat', sans-serif !important;
        font-size: 1.05rem !important;
        font-weight: 900 !important;
        color: #32cd32 !important;
        margin: 0 0 18px 0 !important;
        letter-spacing: 0.5px;
    }

    /* ── SUBMIT REQUEST button — compact ── */
    .submit-request-btn > div.stButton > button:first-child {
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
        padding: 0 1.4rem !important;
        margin-top: 10px !important;
        transform: none !important;
    }
    .submit-request-btn > div.stButton > button:first-child:hover {
        background-color: #28b828 !important;
        color: #000000 !important;
        transform: none !important;
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

    /* ── Welcome banner shown after login ── */
    .welcome-bar {
        background: #f4fdf4;
        border: 1px solid #d0f0d0;
        border-radius: 10px;
        padding: 10px 18px;
        margin-bottom: 28px;
        font-size: 0.88rem;
        font-weight: 700;
        color: #228822 !important;
        text-align: center;
        font-family: 'Montserrat', sans-serif !important;
    }
    </style>
""", unsafe_allow_html=True)


# ============================================================
# 3. HELPER FUNCTIONS
# ============================================================
def is_valid_name(name: str) -> bool:
    """Ask Groq to verify the input is a real human name."""
    try:
        resp = client_groq.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a name validator. "
                        "Reply with valid JSON only: {\"valid\": true} or {\"valid\": false}. "
                        "Return true if the input looks like a real human name (first, last, or both). "
                        "Return false for numbers, gibberish, single letters, symbols, or non-name words."
                    ),
                },
                {"role": "user", "content": f"Is this a valid human name? Input: \"{name}\""},
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            max_tokens=20,
        ).choices[0].message.content
        result = json.loads(resp.replace("```json", "").replace("```", "").strip())
        return result.get("valid", False)
    except Exception:
        # Fallback: basic check — at least 2 chars, only letters/spaces/hyphens
        return len(name.strip()) >= 2 and all(c.isalpha() or c in " -'" for c in name.strip())


def log_user_access(name: str):
    """Log authenticated user to user_access_logs table."""
    try:
        supabase.table("user_access_logs").insert({
            "name": name.strip(),
            "accessed_at": datetime.utcnow().isoformat(),
        }).execute()
    except Exception:
        pass  # Silent fail — don't block access over a logging error


def deep_market_search(query: str) -> str:
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=7)
            return "\n".join([f"{r['title']}: {r['body']}" for r in results]) if results else "No data found."
    except Exception:
        return "Search unavailable."


def trend_icon(trend_str: str) -> str:
    t = trend_str.lower()
    if any(w in t for w in ["up", "rising", "increas", "appreciat", "strong", "bull"]):
        return "▲"
    if any(w in t for w in ["down", "fall", "declin", "depreciat", "weak", "bear"]):
        return "▼"
    return "─"


# ============================================================
# 4. SESSION STATE INIT
# ============================================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_name" not in st.session_state:
    st.session_state.user_name = ""
if "show_request" not in st.session_state:
    st.session_state.show_request = False
if "request_sent" not in st.session_state:
    st.session_state.request_sent = False


# ============================================================
# 5. GATEKEEPER — blocks everything until name is validated
# ============================================================
if not st.session_state.authenticated:

    # Centre the gate content
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown('<div class="gate-wrapper">', unsafe_allow_html=True)

        st.markdown('<p class="gate-logo">Run&Drive</p>', unsafe_allow_html=True)
        st.markdown('<p class="gate-sub">Expert Market Intelligence</p>', unsafe_allow_html=True)
        st.markdown('<div class="gate-divider"></div>', unsafe_allow_html=True)
        st.markdown('<p class="gate-label">Enter your name to continue</p>', unsafe_allow_html=True)

        entered_name = st.text_input(
            label="",
            placeholder="e.g. Khalid Zayed",
            key="gate_name_input",
            label_visibility="collapsed",
        )

        if st.button("ENTER", key="gate_submit"):
            name_clean = entered_name.strip()
            if not name_clean:
                st.warning("Please enter your name.")
            else:
                with st.spinner("Verifying..."):
                    if is_valid_name(name_clean):
                        log_user_access(name_clean)
                        st.session_state.authenticated = True
                        st.session_state.user_name = name_clean
                        st.rerun()
                    else:
                        st.error("That doesn't look like a valid name. Please enter your real name.")

        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()  # Hard stop — nothing below renders until authenticated


# ============================================================
# 6. MAIN DASHBOARD  (only reached after authentication)
# ============================================================
st.markdown('<h1 class="main-title">Run&Drive</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Expert Market Intelligence</p>', unsafe_allow_html=True)

# Welcome bar showing the logged-in user's name
st.markdown(
    f'<div class="welcome-bar">Welcome, {st.session_state.user_name} &nbsp;—&nbsp; '
    f'your session is active</div>',
    unsafe_allow_html=True,
)

with st.container():
    brand = st.text_input("Car Brand", placeholder="e.g. Mercedes-Benz")
    model = st.text_input("Car Model", placeholder="e.g. G63 AMG")
    trim  = st.text_input("Trim / Version (Optional)", placeholder="e.g. Magno Edition")
    year  = st.number_input("Year of Manufacture", min_value=1900, max_value=2026, value=2024)
    miles = st.number_input("Current Odometer (Miles)", min_value=0, value=0)

    submit = st.button("RUN DEEP MARKET ANALYSIS")

    # ── Request toggle ──
    toggle_label = "▲  Hide Request Form" if st.session_state.show_request else "Can't find your car? Request adding it now"
    st.markdown('<div class="request-toggle">', unsafe_allow_html=True)
    if st.button(toggle_label, key="toggle_request"):
        st.session_state.show_request = not st.session_state.show_request
        st.session_state.request_sent = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Request panel ──
    if st.session_state.show_request:
        st.markdown('<div class="request-panel">', unsafe_allow_html=True)
        st.markdown('<h3>Vehicle Support Request</h3>', unsafe_allow_html=True)

        r_brand = st.text_input("Car Brand", key="req_brand", placeholder="e.g. Ferrari")
        r_model = st.text_input("Car Model", key="req_model", placeholder="e.g. SF90 Stradale")
        r_trim  = st.text_input("Trim / Version (Optional)", key="req_trim", placeholder="e.g. Assetto Fiorano")
        r_year  = st.number_input("Year of Manufacture", min_value=1900, max_value=2026, value=2024, key="req_year")

        st.markdown('<div class="submit-request-btn">', unsafe_allow_html=True)
        if st.button("SUBMIT REQUEST", key="req_submit"):
            if r_brand and r_model:
                try:
                    payload = {
                        "brand": r_brand,
                        "model": r_model,
                        "year":  int(r_year),
                    }
                    if r_trim:
                        payload["trim"] = r_trim
                    supabase.table("car_requests").insert(payload).execute()
                    st.session_state.request_sent = True
                    st.rerun()
                except Exception:
                    st.error("Database connection issue. Please try again.")
            else:
                st.warning("Please fill in at least Brand and Model.")
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.request_sent:
            st.success("✅ Request received! We'll add this vehicle soon.")

        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# 7. AI ANALYSIS & RESULTS
# ============================================================
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
        # Log to car_logs — includes the user's name
        try:
            supabase.table("car_logs").insert({
                "brand":     brand,
                "model":     model,
                "year":      int(year),
                "price":     data["price"],
                "miles":     int(miles),
                "logic":     data["why"],
                "user_name": st.session_state.user_name,
            }).execute()
        except Exception:
            pass

        icon = trend_icon(data["trend"])

        # Car image via Wikipedia free API (no key needed, always works)
        def get_wiki_image(query):
            import urllib.request, urllib.parse
            try:
                search_term = urllib.parse.quote(query)
                api_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{search_term}"
                req = urllib.request.Request(api_url, headers={"User-Agent": "RunDriveApp/1.0"})
                with urllib.request.urlopen(req, timeout=4) as resp:
                    info = __import__("json").loads(resp.read())
                    thumb = info.get("thumbnail", {}).get("source", "")
                    # Get full size version
                    if thumb:
                        return thumb.replace("/320px-", "/1200px-")
            except Exception:
                pass
            return ""

        wiki_query = f"{brand} {model}"
        car_image_url = get_wiki_image(wiki_query)
        # Fallback: try just brand if model page not found
        if not car_image_url:
            car_image_url = get_wiki_image(brand)

        st.markdown(
            f'<div class="car-header">'
            f'<h2>{full_name}</h2>'
            f'<small>{miles_display} miles on odometer</small>'
            f'</div>',
            unsafe_allow_html=True,
        )

        if car_image_url:
            st.markdown(
                f'<div style="border-radius:16px; overflow:hidden; margin-bottom:24px; '
                f'border: 1px solid #eeeeee; box-shadow: 0 4px 24px rgba(0,0,0,0.07);">'
                f'<img src="{car_image_url}" style="width:100%; height:320px; '
                f'object-fit:cover; object-position:center; display:block;">'
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
