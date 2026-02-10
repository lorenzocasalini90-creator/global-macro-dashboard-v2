import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import plotly.graph_objects as go
import html as _html
from datetime import datetime, timedelta, timezone
from pandas.tseries.offsets import DateOffset

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Global finance | Macro overview",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS (tabs readable; selected RED; expander consistent dark)
# ============================================================
st.markdown(
    """
<style>
  :root{
    --bg:#0b0f19;
    --card:#0f1629;
    --card2:#0c1324;
    --border:rgba(255,255,255,0.10);
    --muted:rgba(255,255,255,0.70);
    --text:rgba(255,255,255,0.94);

    --good:rgba(34,197,94,1);
    --warn:rgba(245,158,11,1);
    --bad:rgba(239,68,68,1);

    --accent:rgba(244,63,94,1);
    --accentSoft:rgba(244,63,94,0.18);
  }

  .stApp {
    background: radial-gradient(1200px 700px at 20% 0%, #121a33 0%, #0b0f19 45%, #0b0f19 100%);
    color: var(--text);
  }
  .block-container { padding-top: 1.0rem; padding-bottom: 2.0rem; }

  h1, h2, h3, h4 { color: var(--text); letter-spacing: -0.02em; }
  .muted { color: var(--muted); }

  /* Tabs: make readable; selected red */
  button[data-baseweb="tab"]{
    color: rgba(255,255,255,0.92) !important;
    font-weight: 700 !important;
    background: rgba(255,255,255,0.04) !important;
    border-radius: 10px !important;
    margin-right: 6px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
  }
  button[data-baseweb="tab"][aria-selected="true"]{
    color: rgba(255,255,255,0.98) !important;
    background: var(--accentSoft) !important;
    border: 1px solid rgba(244,63,94,0.55) !important;
  }

  /* Expander */
  div[data-testid="stExpander"]{
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    background: rgba(255,255,255,0.03) !important;
    overflow: hidden !important;
  }
  div[data-testid="stExpander"] summary{
    background: rgba(255,255,255,0.05) !important;
    color: rgba(255,255,255,0.92) !important;
    padding: 10px 12px !important;
  }
  div[data-testid="stExpander"] summary:hover{
    background: rgba(255,255,255,0.07) !important;
  }

  /* Cards */
  .card{
    background: linear-gradient(180deg, rgba(255,255,255,0.055) 0%, rgba(255,255,255,0.03) 100%);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 16px 16px 14px 16px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.25);
  }
  .cardTitle{ font-size: 0.95rem; color: var(--muted); margin-bottom: 6px; }
  .cardValue{ font-size: 2.1rem; font-weight: 800; line-height: 1.05; color: var(--text); }
  .cardSub{ margin-top: 8px; font-size: 0.98rem; color: var(--muted); }

  .grid3{ display:grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
  .grid2{ display:grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }
  .grid4{ display:grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; }

  /* Pills */
  .pill{
    display:inline-flex;
    align-items:center;
    gap:8px;
    padding: 5px 12px;
    border-radius: 999px;
    border: 1px solid var(--border);
    background: rgba(255,255,255,0.04);
    font-size: 0.88rem;
    color: var(--text);
    white-space: nowrap;
  }
  .dot{ width: 11px; height: 11px; border-radius: 999px; display:inline-block; }
  .pill.good{ border-color: rgba(34,197,94,0.40); background: rgba(34,197,94,0.12); }
  .pill.warn{ border-color: rgba(245,158,11,0.40); background: rgba(245,158,11,0.12); }
  .pill.bad { border-color: rgba(239,68,68,0.40); background: rgba(239,68,68,0.12); }

  /* Section wrapper */
  .section{
    background: rgba(255,255,255,0.025);
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 14px;
    box-shadow: 0 10px 28px rgba(0,0,0,0.20);
    margin-bottom: 14px;
  }
  .sectionHead{ display:flex; align-items:baseline; justify-content:space-between; gap: 12px; margin-bottom: 10px; }
  .sectionTitle{ font-size: 1.15rem; font-weight: 850; color: rgba(255,255,255,0.96); }
  .sectionDesc{ font-size: 0.95rem; color: var(--muted); margin-top: 2px; }

  /* Wallboard tiles */
  .wbGrid{
    display:grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
  }
  @media (max-width: 1200px){
    .wbGrid{ grid-template-columns: repeat(2, minmax(0, 1fr)); }
  }
  @media (max-width: 700px){
    .wbGrid{ grid-template-columns: repeat(1, minmax(0, 1fr)); }
  }

  .wbTile{
    background: rgba(255,255,255,0.028);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 14px 14px 12px 14px;
    box-shadow: 0 10px 26px rgba(0,0,0,0.18);
    min-height: 156px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
  }
  .wbName{ font-size: 0.98rem; font-weight: 850; color: rgba(255,255,255,0.96); margin-bottom: 2px; }
  .wbMeta{ font-size: 0.86rem; color: var(--muted); margin-bottom: 8px; }
  .wbRow{ display:flex; align-items:baseline; justify-content:space-between; gap: 10px; }
  .wbVal{ font-size: 1.65rem; font-weight: 900; letter-spacing:-0.01em; color: rgba(255,255,255,0.96); }
  .wbSmall{ font-size: 0.88rem; color: var(--muted); }
  .wbFoot{ display:flex; align-items:center; justify-content:space-between; gap: 10px; margin-top: 10px; }

  /* Score bar */
  .barWrap{
    height: 10px;
    border-radius: 999px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.08);
    position: relative;
    overflow:hidden;
  }
  .barFill{
    height: 100%;
    border-radius: 999px;
    background: rgba(255,255,255,0.14);
    width: 100%;
    opacity: 0.55;
  }
  .barMark{
    position:absolute;
    top:-4px;
    width: 3px;
    height: 18px;
    border-radius: 2px;
    background: rgba(255,255,255,0.92);
    box-shadow: 0 0 0 2px rgba(0,0,0,0.20);
  }

  /* Alerts */
  .alertBox{
    border: 1px solid rgba(244,63,94,0.40);
    background: rgba(244,63,94,0.10);
    border-radius: 16px;
    padding: 12px 14px;
    margin-bottom: 12px;
  }
  .alertTitle{ font-weight: 850; color: rgba(255,255,255,0.96); margin-bottom: 6px; }
  .alertItem{ color: rgba(255,255,255,0.90); font-size: 0.95rem; margin: 4px 0; }

  code { color: rgba(255,255,255,0.88); }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# INDICATORS & BLOCKS (same as your current set)
# ============================================================

INDICATOR_META = {
    "real_10y": {
        "label": "US 10Y TIPS Real Yield",
        "unit": "%",
        "direction": -1,
        "source": "FRED DFII10",
        "scale": 1.0,
        "ref_line": 0.0,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Real yield (10Y TIPS): the real price of money/time.",
            "reference": "<0% very easy; 0–2% neutral; >2% restrictive (heuristics).",
            "interpretation": "- Higher real yields tighten financial conditions; pressure long-duration assets.\n- Lower real yields typically support risk assets and duration.",
            "bridge": "Higher real yields raise real funding constraints across the system.",
        },
    },
    "nominal_10y": {
        "label": "US 10Y Nominal Yield",
        "unit": "%",
        "direction": -1,
        "source": "FRED DGS10",
        "scale": 1.0,
        "ref_line": None,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Nominal 10Y Treasury yield: benchmark discount rate and broad tightening proxy.",
            "reference": "Fast upside moves often behave like tightening (heuristics).",
            "interpretation": "- Yield up fast = pressure on equities and existing bonds.\n- Yield down can support duration and (sometimes) equities depending on growth/inflation mix.",
            "bridge": "Higher yields mean the market demands more compensation (inflation and/or term premium).",
        },
    },
    "yield_curve_10_2": {
        "label": "US Yield Curve (10Y–2Y)",
        "unit": "pp",
        "direction": +1,
        "source": "FRED DGS10 - DGS2",
        "scale": 1.0,
        "ref_line": 0.0,
        "scoring_mode": "z5y",
        "expander": {
            "what": "10Y–2Y slope: cycle / recession-probability proxy.",
            "reference": "<0 inverted (late-cycle); >0 normal (heuristics).",
            "interpretation": "- Deep/persistent inversion = late-cycle risk.\n- Steepening back above 0 = normalization (often after easing).",
            "bridge": "Inversion = policy tight vs cycle, raising deleveraging risk.",
        },
    },

    "breakeven_10y": {
        "label": "10Y Breakeven Inflation",
        "unit": "%",
        "direction": -1,
        "source": "FRED T10YIE",
        "scale": 1.0,
        "ref_line": 2.5,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Market-implied inflation expectations (10Y).",
            "reference": "~2–3% anchored; materially >3% = sticky risk (heuristics).",
            "interpretation": "- Higher breakevens reduce easing room.\n- Lower/anchoring supports duration and risk budgeting.",
            "bridge": "Higher expected inflation raises the odds of inflation-tolerant policy in stress.",
        },
    },
    "cpi_yoy": {
        "label": "US CPI YoY",
        "unit": "%",
        "direction": -1,
        "source": "FRED CPIAUCSL (computed YoY)",
        "scale": 1.0,
        "ref_line": 3.0,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Headline inflation YoY (proxy).",
            "reference": "2% is target; >3–4% persistent = sticky risk (heuristics).",
            "interpretation": "- Disinflation supports duration and often equities.\n- Re-acceleration pushes 'higher-for-longer' risks.",
            "bridge": "Persistent inflation becomes the binding policy constraint.",
        },
    },
    "unemployment_rate": {
        "label": "US Unemployment Rate",
        "unit": "%",
        "direction": -1,
        "source": "FRED UNRATE",
        "scale": 1.0,
        "ref_line": None,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Labor slack proxy.",
            "reference": "Rapid rises often coincide with growth downshift (heuristics).",
            "interpretation": "- Unemployment rising quickly tends to be risk-off.\n- Stable unemployment is typically benign.",
            "bridge": "Slack + high debt raises pressure for policy support (fiscal/monetary).",
        },
    },

    "usd_index": {
        "label": "USD Index (DXY / Broad Proxy)",
        "unit": "",
        "direction": -1,
        "source": "yfinance DX-Y.NYB (fallback FRED DTWEXBGS)",
        "scale": 1.0,
        "ref_line": None,
        "scoring_mode": "z5y",
        "expander": {
            "what": "USD strength proxy. If DXY is unavailable, uses broad trade-weighted USD index.",
            "reference": "USD up = tighter global conditions (heuristics).",
            "interpretation": "- USD stronger tightens global funding.\n- USD weaker loosens conditions.",
            "bridge": "Stronger USD increases global funding stress where liabilities are USD-linked.",
        },
    },
    "hy_oas": {
        "label": "US High Yield OAS",
        "unit": "pp",
        "direction": -1,
        "source": "FRED BAMLH0A0HYM2",
        "scale": 1.0,
        "ref_line": 4.5,
        "scoring_mode": "z5y",
        "expander": {
            "what": "High-yield credit spread: credit stress / default premium proxy.",
            "reference": "<4% often benign; >6–7% stress (heuristics).",
            "interpretation": "- Spreads widening = risk-off.\n- Tight spreads = risk appetite.",
            "bridge": "Credit stress can accelerate non-linear deleveraging dynamics.",
        },
    },
    "vix": {
        "label": "VIX",
        "unit": "",
        "direction": -1,
        "source": "yfinance ^VIX",
        "scale": 1.0,
        "ref_line": 20.0,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Equity implied volatility (S&P 500).",
            "reference": "<15 low; 15–25 normal; >25 stress (heuristics).",
            "interpretation": "- Higher vol tightens conditions through risk premia.\n- Lower vol often supports risk-taking.",
            "bridge": "Vol spikes tighten conditions even without rate hikes.",
        },
    },
    "spy_trend": {
        "label": "SPY Trend (SPY / 200D MA)",
        "unit": "ratio",
        "direction": +1,
        "source": "yfinance SPY",
        "scale": 1.0,
        "ref_line": 1.0,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Simple trend proxy: SPY vs 200-day moving average.",
            "reference": ">1 = uptrend; <1 = downtrend (heuristics).",
            "interpretation": "- Above 1 supports risk-on behavior.\n- Below 1 signals risk-off trend regime.",
            "bridge": "Trend down + credit stress up is a common deleveraging signature.",
        },
    },
    "hyg_lqd_ratio": {
        "label": "Credit Risk Appetite (HYG / LQD)",
        "unit": "ratio",
        "direction": +1,
        "source": "yfinance HYG, LQD",
        "scale": 1.0,
        "ref_line": None,
        "scoring_mode": "z5y",
        "expander": {
            "what": "High yield vs investment grade ratio: credit risk appetite proxy.",
            "reference": "Ratio up = more HY appetite; down = flight to quality.",
            "interpretation": "- Rising ratio is typically risk-on.\n- Falling ratio indicates quality bid / caution.",
            "bridge": "Flight-to-quality signals tightening funding constraints.",
        },
    },

    "fed_balance_sheet": {
        "label": "Fed Balance Sheet (WALCL)",
        "unit": "bn USD",
        "direction": +1,
        "source": "FRED WALCL (millions -> bn)",
        "scale": 1.0 / 1000.0,
        "ref_line": None,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Total Fed assets: system liquidity proxy.",
            "reference": "Expansion (QE) often supports risk assets; contraction (QT) drains (heuristics).",
            "interpretation": "- Balance sheet up = tailwind.\n- Balance sheet down = headwind.",
            "bridge": "Liquidity plumbing determines whether flows support or drain risk assets.",
        },
    },
    "rrp": {
        "label": "Fed Overnight RRP",
        "unit": "bn USD",
        "direction": -1,
        "source": "FRED RRPONTSYD",
        "scale": 1.0,
        "ref_line": 0.0,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Overnight reverse repo usage: cash parked in risk-free facility.",
            "reference": "High RRP = liquidity 'stuck'; falling RRP can release marginal liquidity (heuristics).",
            "interpretation": "- RRP up = less marginal liquidity for risk.\n- RRP down = potential tailwind.",
            "bridge": "RRP declines can act as a tactical liquidity release valve.",
        },
    },

    "interest_payments": {
        "label": "US Federal Interest Payments (Quarterly)",
        "unit": "bn USD",
        "direction": -1,
        "source": "FRED A091RC1Q027SBEA",
        "scale": 1.0,
        "ref_line": None,
        "scoring_mode": "pct20y",
        "expander": {
            "what": "Government interest expense: debt-service pressure proxy.",
            "reference": "Rising/accelerating debt service reduces policy flexibility (heuristics).",
            "interpretation": "- Persistent rise increases policy constraint.\n- Stabilization reduces constraint.",
            "bridge": "Debt service pressure increases incentives for funding-friendly policy outcomes.",
        },
    },
    "federal_receipts": {
        "label": "US Federal Current Receipts (Quarterly)",
        "unit": "bn USD",
        "direction": +1,
        "source": "FRED FGRECPT",
        "scale": 1.0,
        "ref_line": None,
        "scoring_mode": "pct20y",
        "expander": {
            "what": "Government receipts: supports debt-service capacity.",
            "reference": "Used to compute interest/receipts sustainability proxy.",
            "interpretation": "- Receipts up improves capacity (all else equal).\n- Receipts down tightens constraint.",
            "bridge": "Higher receipts reduce the binding nature of debt service.",
        },
    },
    "interest_to_receipts": {
        "label": "Debt Service Stress (Interest / Receipts)",
        "unit": "ratio",
        "direction": -1,
        "source": "Derived",
        "scale": 1.0,
        "ref_line": None,
        "scoring_mode": "pct20y",
        "expander": {
            "what": "Sustainability proxy: share of receipts consumed by interest expense.",
            "reference": "High and rising = constraint becomes political (heuristics).",
            "interpretation": "- Higher ratio signals tighter fiscal policy constraint.\n- Lower ratio signals more room.",
            "bridge": "Higher debt service increases incentives for inflation-tolerant or funding-friendly policy.",
        },
    },
    "deficit_gdp": {
        "label": "Federal Surplus/Deficit (% of GDP)",
        "unit": "%",
        "direction": -1,
        "source": "FRED FYFSGDA188S",
        "scale": 1.0,
        "ref_line": -3.0,
        "scoring_mode": "pct20y",
        "expander": {
            "what": "Fiscal balance (% of GDP). Negative = deficit.",
            "reference": "Persistent large deficits increase Treasury supply pressure (heuristics).",
            "interpretation": "- More negative implies more supply/funding pressure.\n- Improvement reduces pressure.",
            "bridge": "Supply pressure can show up as higher term premium and weaker duration hedge behavior.",
        },
    },
    "term_premium_10y": {
        "label": "US 10Y Term Premium (ACM)",
        "unit": "%",
        "direction": -1,
        "source": "FRED ACMTP10",
        "scale": 1.0,
        "ref_line": None,
        "scoring_mode": "pct20y",
        "expander": {
            "what": "Term premium: compensation required to hold nominal duration.",
            "reference": "Rising term premium makes long nominal bonds less reliable as a hedge (heuristics).",
            "interpretation": "- Term premium up increases duration risk.\n- Term premium down restores hedge quality.",
            "bridge": "If term premium rises from supply/funding, duration may stop hedging equity drawdowns.",
        },
    },

    "current_account_gdp": {
        "label": "US Current Account Balance (% of GDP)",
        "unit": "%",
        "direction": +1,
        "source": "FRED USAB6BLTT02STSAQ",
        "scale": 1.0,
        "ref_line": 0.0,
        "scoring_mode": "pct20y",
        "expander": {
            "what": "External funding constraint proxy. Negative = reliance on foreign capital.",
            "reference": "More negative implies higher vulnerability during USD tightening (heuristics).",
            "interpretation": "- More negative increases dependence on external funding.\n- Moving toward 0 reduces constraint.",
            "bridge": "External deficits increase vulnerability when global USD funding tightens.",
        },
    },

    "gold": {
        "label": "Gold (GLD)",
        "unit": "",
        "direction": -1,
        "source": "yfinance GLD",
        "scale": 1.0,
        "ref_line": None,
        "scoring_mode": "z5y",
        "expander": {
            "what": "Gold: hedge demand proxy (policy/inflation/tail risk).",
            "reference": "Breakouts often reflect hedge demand rather than growth optimism (heuristics).",
            "interpretation": "- Gold up can signal hedge demand.\n- Gold down in equity bull may reflect clean risk-on.",
            "bridge": "Gold can hedge environments where real returns are compressed or policy turns funding-friendly.",
        },
    },
}

BLOCKS = {
    "price_of_time": {
        "name": "1) Price of Time",
        "weight": 0.20,
        "indicators": ["real_10y", "nominal_10y", "yield_curve_10_2"],
        "desc": "Rates / curve: the price of time and late-cycle signal.",
        "group": "Market Thermometers",
    },
    "macro": {
        "name": "2) Macro Cycle",
        "weight": 0.15,
        "indicators": ["breakeven_10y", "cpi_yoy", "unemployment_rate"],
        "desc": "Inflation and growth constraint on policy reaction.",
        "group": "Market Thermometers",
    },
    "conditions": {
        "name": "3) Conditions & Stress",
        "weight": 0.20,
        "indicators": ["usd_index", "hy_oas", "vix", "spy_trend", "hyg_lqd_ratio"],
        "desc": "Fast regime: USD, credit stress, vol, trend, risk appetite.",
        "group": "Market Thermometers",
    },
    "plumbing": {
        "name": "4) Liquidity / Plumbing",
        "weight": 0.15,
        "indicators": ["fed_balance_sheet", "rrp"],
        "desc": "System liquidity tailwind vs drain for risk assets.",
        "group": "Market Thermometers",
    },
    "policy_link": {
        "name": "5) Fiscal / Policy Constraint",
        "weight": 0.20,
        "indicators": ["interest_to_receipts", "deficit_gdp", "term_premium_10y", "interest_payments", "federal_receipts"],
        "desc": "Debt service, deficit dynamics, and the funding constraint signal.",
        "group": "Structural Constraints",
    },
    "external": {
        "name": "6) External Balance",
        "weight": 0.10,
        "indicators": ["current_account_gdp"],
        "desc": "External funding reliance and vulnerability in USD tightening.",
        "group": "Structural Constraints",
    },
    "gold_block": {
        "name": "7) Gold",
        "weight": 0.00,
        "indicators": ["gold"],
        "desc": "Policy / tail-risk hedge demand confirmation.",
        "group": "Structural Constraints",
    },
}

# ============================================================
# DATA FETCHERS
# ============================================================

def get_fred_api_key():
    try:
        return st.secrets["FRED_API_KEY"]
    except Exception:
        return None

@st.cache_data(ttl=3600)
def fetch_fred_series(series_id: str, start_date: str) -> pd.Series:
    api_key = get_fred_api_key()
    if api_key is None:
        return pd.Series(dtype=float)

    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start_date,
    }
    try:
        r = requests.get(url, params=params, timeout=12)
        r.raise_for_status()
        data = r.json().get("observations", [])
        if not data:
            return pd.Series(dtype=float)
        idx = pd.to_datetime([o["date"] for o in data])
        vals = []
        for o in data:
            try:
                vals.append(float(o["value"]))
            except Exception:
                vals.append(np.nan)
        s = pd.Series(vals, index=idx).replace({".": np.nan}).astype(float).sort_index()
        return s
    except Exception:
        return pd.Series(dtype=float)

@st.cache_data(ttl=3600)
def fetch_yf_one(ticker: str, start_date: str) -> pd.Series:
    try:
        df = yf.Ticker(ticker).history(start=start_date, auto_adjust=True)
        if df is None or df.empty:
            return pd.Series(dtype=float)
        col = "Close"
        if "Adj Close" in df.columns:
            col = "Adj Close"
        s = df[col].dropna()
        s.index = pd.to_datetime(s.index).tz_localize(None) if getattr(s.index, "tz", None) else pd.to_datetime(s.index)
        return s
    except Exception:
        return pd.Series(dtype=float)

@st.cache_data(ttl=3600)
def fetch_yf_many(tickers: list[str], start_date: str) -> dict:
    out = {}
    for t in tickers:
        out[t] = fetch_yf_one(t, start_date)
    return out

# ============================================================
# SCORING
# ============================================================

def rolling_percentile_last(hist: pd.Series, latest: float) -> float:
    h = hist.dropna()
    if len(h) < 10 or pd.isna(latest):
        return np.nan
    return float((h <= latest).mean())

def compute_indicator_score(series: pd.Series, direction: int, scoring_mode: str = "z5y"):
    if series is None or series.empty:
        return np.nan, np.nan, np.nan
    s = series.dropna()
    if len(s) < 20:
        return np.nan, np.nan, (np.nan if s.empty else float(s.iloc[-1]))

    latest = float(s.iloc[-1])
    end = s.index.max()

    if scoring_mode == "pct20y":
        start = end - DateOffset(years=20)
        hist = s[s.index >= start]
        if len(hist) < 20:
            hist = s
        p = rolling_percentile_last(hist, latest)
        sig = (p - 0.5) * 4.0
    else:
        start = end - DateOffset(years=5)
        hist = s[s.index >= start]
        if len(hist) < 10:
            hist = s
        mean = float(hist.mean())
        std = float(hist.std())
        sig = 0.0 if (std == 0 or np.isnan(std)) else (latest - mean) / std

    raw = float(direction) * float(sig)
    raw = float(np.clip(raw, -2.0, 2.0))
    score = (raw + 2.0) / 4.0 * 100.0
    return score, sig, latest

def classify_status(score: float) -> str:
    if np.isnan(score):
        return "n/a"
    if score > 60:
        return "risk_on"
    if score < 40:
        return "risk_off"
    return "neutral"

def status_label(status: str) -> str:
    return {"risk_on":"Risk-on","risk_off":"Risk-off","neutral":"Neutral"}.get(status,"n/a")

def sema(status: str) -> str:
    return {"risk_on":"🟢","neutral":"🟡","risk_off":"🔴"}.get(status,"⚪")

def pill_html(status: str) -> str:
    if status == "risk_on":
        return "<span class='pill good'><span class='dot' style='background:var(--good)'></span>🟢 Risk-on</span>"
    if status == "risk_off":
        return "<span class='pill bad'><span class='dot' style='background:var(--bad)'></span>🔴 Risk-off</span>"
    if status == "neutral":
        return "<span class='pill warn'><span class='dot' style='background:var(--warn)'></span>🟡 Neutral</span>"
    return "<span class='pill'><span class='dot' style='background:rgba(255,255,255,0.5)'></span>n/a</span>"

def fmt_value(val, unit: str, scale: float = 1.0):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "n/a"
    try:
        v = float(val) * float(scale)
    except Exception:
        return "n/a"
    if unit in ("%", "pp"):
        return f"{v:.2f}{unit}"
    if unit == "ratio":
        return f"{v:.3f}"
    if unit == "bn USD":
        return f"{v:.1f} bn"
    if unit == "":
        return f"{v:.2f}"
    return f"{v:.2f} {unit}"

def infer_frequency_days(s: pd.Series) -> float:
    if s is None or s.dropna().shape[0] < 10:
        return 1.0
    idx = pd.to_datetime(s.dropna().index)
    diffs = np.diff(idx.values).astype("timedelta64[D]").astype(int)
    if len(diffs) == 0:
        return 1.0
    return float(np.median(diffs))

def pct_change_over_days(series: pd.Series, days: int) -> float:
    if series is None or series.empty:
        return np.nan
    s = series.dropna()
    if s.empty:
        return np.nan
    last_date = s.index.max()
    target_date = last_date - timedelta(days=days)
    past = s[s.index <= target_date]
    if past.empty:
        return np.nan
    past_val = past.iloc[-1]
    curr_val = s.iloc[-1]
    if pd.isna(past_val) or pd.isna(curr_val) or past_val == 0:
        return np.nan
    return (curr_val / past_val - 1.0) * 100.0

def recent_trend(series: pd.Series) -> dict:
    if series is None or series.dropna().shape[0] < 10:
        return {"window_label": "n/a", "delta_pct": np.nan, "arrow": "→", "days": None}
    freq = infer_frequency_days(series)
    if freq >= 20:
        days = 90
        label = "1Q"
    else:
        days = 30
        label = "30d"
    d = pct_change_over_days(series, days)
    if np.isnan(d):
        return {"window_label": label, "delta_pct": np.nan, "arrow": "→", "days": days}
    arrow = "↑" if d > 0.25 else ("↓" if d < -0.25 else "→")
    return {"window_label": label, "delta_pct": d, "arrow": arrow, "days": days}

def score_bar_html(score: float) -> str:
    pos = 50 if np.isnan(score) else int(np.clip(score, 0, 100))
    return f"""
      <div class="barWrap">
        <div class="barFill"></div>
        <div class="barMark" style="left: calc({pos}% - 2px);"></div>
      </div>
    """

# ============================================================
# PLOTTING
# ============================================================

def plot_premium(series: pd.Series, title: str, ref_line=None, height: int = 320):
    s = series.dropna()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s.index, y=s.values, mode="lines", line=dict(width=2), name=title))
    if ref_line is not None:
        fig.add_hline(y=float(ref_line), line_width=1, line_dash="dot", opacity=0.7)
    fig.add_annotation(
        xref="paper", yref="paper",
        x=0.01, y=0.98,
        text=f"<b>{_html.escape(title)}</b>",
        showarrow=False,
        align="left",
        font=dict(size=14, color="rgba(255,255,255,0.95)"),
        bgcolor="rgba(0,0,0,0.0)"
    )
    fig.update_layout(
        height=height,
        margin=dict(l=10, r=10, t=22, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(255,255,255,0.02)",
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)", zeroline=False),
        showlegend=False,
        font=dict(color="rgba(255,255,255,0.88)"),
    )
    return fig

# ============================================================
# OPERATING LINES
# ============================================================

def operating_lines(block_scores: dict, indicator_scores: dict):
    gs = block_scores.get("GLOBAL", {}).get("score", np.nan)

    def _sg(x):
        if np.isnan(x):
            return 0.0
        return float(x)

    cond = _sg(block_scores.get("conditions", {}).get("score", np.nan))
    macro = _sg(block_scores.get("macro", {}).get("score", np.nan))
    pot = _sg(block_scores.get("price_of_time", {}).get("score", np.nan))
    policy = _sg(block_scores.get("policy_link", {}).get("score", np.nan))

    if not np.isnan(gs):
        if gs >= 60 and cond >= 55:
            equity = "Increase (measured) — risk budget OK, watch credit"
        elif gs <= 40 or cond <= 40:
            equity = "Reduce — defense/quality first"
        else:
            equity = "Neutral — moderate sizing"
    else:
        equity = "n/a"

    termp = _sg(indicator_scores.get("term_premium_10y", {}).get("score", np.nan))
    infl = _sg(indicator_scores.get("cpi_yoy", {}).get("score", np.nan))

    if termp <= 40 and infl <= 45:
        duration = "Short/neutral — avoid long nominals; prefer quality / TIPS tilt"
    elif pot <= 40 and infl <= 45 and termp >= 55:
        duration = "Long (hedge) — disinflation + duration hedge looks cleaner"
    else:
        duration = "Neutral — balance term-premium risk vs cycle"

    hy = _sg(indicator_scores.get("hy_oas", {}).get("score", np.nan))
    hyg = _sg(indicator_scores.get("hyg_lqd_ratio", {}).get("score", np.nan))
    ds = _sg(indicator_scores.get("interest_to_receipts", {}).get("score", np.nan))

    if hy <= 40 or hyg <= 40 or ds <= 40:
        credit = "IG > HY — reduce default / funding risk"
    elif hy >= 60 and hyg >= 60 and policy >= 50:
        credit = "Opportunistic HY — only with sizing discipline"
    else:
        credit = "Neutral — quality + selectivity"

    usd = _sg(indicator_scores.get("usd_index", {}).get("score", np.nan))
    gold = _sg(indicator_scores.get("gold", {}).get("score", np.nan))

    if policy <= 40 and (macro <= 55):
        hedges = "Gold / real-asset tilt — policy constraint risk"
    elif usd <= 40 and cond <= 45:
        hedges = "USD / cash-like — funding stress hedge"
    elif gold <= 40:
        hedges = "Keep a small gold sleeve — hedge demand rising"
    else:
        hedges = "Light mix — cash-like + tactical gold"

    return equity, duration, credit, hedges

# ============================================================
# WALLBOARD TILE (ROBUST RENDER via components.html)
# ============================================================

def _esc(x: str) -> str:
    return _html.escape("" if x is None else str(x))

def render_tile(fragment_html: str, height: int = 210):
    # NOTE: components.html runs inside an iframe -> it does NOT inherit Streamlit CSS.
    # We inject a minimal, self-contained CSS to keep tiles readable & stable.
    tile_css = """
    <style>
      :root{
        --bg:#0b0f19;
        --card:#0f1629;
        --border:rgba(255,255,255,0.10);
        --muted:rgba(255,255,255,0.72);
        --text:rgba(255,255,255,0.94);

        --good:rgba(34,197,94,1);
        --warn:rgba(245,158,11,1);
        --bad:rgba(239,68,68,1);
      }

      html, body{
        margin:0; padding:0;
        background: transparent;
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";
      }

      /* Tile styles (minimal subset) */
      .wbTile{
        background: rgba(255,255,255,0.028);
        border: 1px solid var(--border);
        border-radius: 18px;
        padding: 14px 14px 12px 14px;
        box-shadow: 0 10px 26px rgba(0,0,0,0.18);
        min-height: 156px;
        display:flex;
        flex-direction:column;
        justify-content:space-between;
      }
      .wbName{ font-size: 0.98rem; font-weight: 850; color: rgba(255,255,255,0.96); margin-bottom: 2px; }
      .wbMeta{ font-size: 0.86rem; color: var(--muted); margin-bottom: 8px; }
      .wbRow{ display:flex; align-items:baseline; justify-content:space-between; gap: 10px; }
      .wbVal{ font-size: 1.65rem; font-weight: 900; letter-spacing:-0.01em; color: rgba(255,255,255,0.96); }
      .wbSmall{ font-size: 0.88rem; color: var(--muted); }
      .wbFoot{ display:flex; align-items:center; justify-content:space-between; gap: 10px; margin-top: 10px; }

      /* Pills */
      .pill{
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding: 5px 12px;
        border-radius: 999px;
        border: 1px solid var(--border);
        background: rgba(255,255,255,0.04);
        font-size: 0.88rem;
        color: rgba(255,255,255,0.94);
        white-space: nowrap;
      }
      .dot{ width: 11px; height: 11px; border-radius: 999px; display:inline-block; }
      .pill.good{ border-color: rgba(34,197,94,0.40); background: rgba(34,197,94,0.12); }
      .pill.warn{ border-color: rgba(245,158,11,0.40); background: rgba(245,158,11,0.12); }
      .pill.bad { border-color: rgba(239,68,68,0.40); background: rgba(239,68,68,0.12); }

      /* Score bar */
      .barWrap{
        height: 10px;
        border-radius: 999px;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.08);
        position: relative;
        overflow:hidden;
      }
      .barFill{
        height: 100%;
        border-radius: 999px;
        background: rgba(255,255,255,0.14);
        width: 100%;
        opacity: 0.55;
      }
      .barMark{
        position:absolute;
        top:-4px;
        width: 3px;
        height: 18px;
        border-radius: 2px;
        background: rgba(255,255,255,0.92);
        box-shadow: 0 0 0 2px rgba(0,0,0,0.20);
      }
    </style>
    """

    doc = f"""
    <html>
      <head>
        <meta charset="utf-8">
        {tile_css}
      </head>
      <body>
        {fragment_html}
      </body>
    </html>
    """
    components.html(doc, height=height, scrolling=False)


def wallboard_tile(key: str, series: pd.Series, indicator_scores: dict):
    meta = INDICATOR_META[key]
    sc = indicator_scores.get(key, {})
    score = sc.get("score", np.nan)
    status = sc.get("status", "n/a")
    latest = sc.get("latest", np.nan)

    label = _esc(meta["label"])
    source = _esc(meta["source"])
    latest_txt = _esc(fmt_value(latest, meta["unit"], meta.get("scale", 1.0)))

    tr = recent_trend(series)
    wlab = _esc(tr["window_label"])
    d = tr["delta_pct"]
    arrow = _esc(tr["arrow"])
    d_txt = "n/a" if np.isnan(d) else f"{d:+.1f}%"
    d_txt = _esc(d_txt)

    ref_line = meta.get("ref_line", None)
    ref_txt = "—" if ref_line is None else str(ref_line)
    ref_txt = _esc(ref_txt)

    ref_note = _esc(meta["expander"].get("reference", "—"))

    score_txt = "n/a" if np.isnan(score) else f"{score:.0f}"
    score_txt = _esc(score_txt)

    fragment = f"""
    <div class="wbTile">
      <div>
        <div class="wbName">{label}</div>
        <div class="wbMeta">{source}</div>

        <div class="wbRow">
          <div class="wbVal">{latest_txt}</div>
          <div>{pill_html(status)}</div>
        </div>

        <div style="margin-top:10px;">
          {score_bar_html(score)}
          <div class="wbFoot">
            <div class="wbSmall">Score: <b>{score_txt}</b></div>
            <div class="wbSmall">Trend ({wlab}): <b>{arrow} {d_txt}</b></div>
          </div>
        </div>

        <div class="wbSmall" style="margin-top:8px;">
          Reference: <b>{ref_txt}</b> · {ref_note}
        </div>
      </div>
    </div>
    """
    render_tile(fragment, height=220)

    with st.expander(f"Indicator guide — {meta['label']}", expanded=False):
        exp = meta["expander"]
        st.markdown(f"**What it is:** {exp.get('what','')}")
        st.markdown(f"**Reference levels / thresholds:** {exp.get('reference','')}")
        st.markdown("**How to read it:**")
        st.markdown(exp.get("interpretation", ""))
        st.markdown(f"**Why it matters (policy/funding link):** {exp.get('bridge','')}")

def wallboard_missing_tile(key: str):
    meta = INDICATOR_META[key]
    label = _esc(meta["label"])
    source = _esc(meta["source"])
    fragment = f"""
    <div class="wbTile" style="opacity:0.85;">
      <div>
        <div class="wbName">{label}</div>
        <div class="wbMeta">{source}</div>
        <div class="wbRow">
          <div class="wbVal">Missing</div>
          <div>{pill_html("n/a")}</div>
        </div>
        <div class="wbSmall" style="margin-top:10px;">
          No data available for this series in the selected history window.
        </div>
      </div>
    </div>
    """
    render_tile(fragment, height=190)
    with st.expander(f"Indicator guide — {meta['label']}", expanded=False):
        exp = meta["expander"]
        st.markdown(f"**What it is:** {exp.get('what','')}")
        st.markdown(f"**Reference levels / thresholds:** {exp.get('reference','')}")
        st.markdown("**How to read it:**")
        st.markdown(exp.get("interpretation", ""))
        st.markdown(f"**Why it matters (policy/funding link):** {exp.get('bridge','')}")

# ============================================================
# ALERTS (suggested thresholds)
# ============================================================

ALERT_RULES = {
    # Score boundary proximity:
    "score_near_boundary": {"dist": 5},  # within 5 points of 40 or 60
    # Regime extremes:
    "score_extreme": {"low": 30, "high": 70},
    # Trend magnitude (abs):
    "trend_daily_pct": {"warn": 3.0, "crit": 6.0},   # for daily series 30d
    "trend_slow_pct": {"warn": 5.0, "crit": 10.0},  # for monthly/quarterly 1Q
}

def build_alerts(indicators: dict, indicator_scores: dict):
    alerts = []

    for key, meta in INDICATOR_META.items():
        s = indicators.get(key, pd.Series(dtype=float))
        sc = indicator_scores.get(key, {})
        score = sc.get("score", np.nan)
        status = sc.get("status", "n/a")
        if s is None or s.empty:
            alerts.append(("WARN", meta["label"], "Missing data (series empty in selected window)."))
            continue

        tr = recent_trend(s)
        wlab = tr["window_label"]
        d = tr["delta_pct"]
        days = tr.get("days", None)

        # 1) score near boundary
        if not np.isnan(score):
            dist = ALERT_RULES["score_near_boundary"]["dist"]
            if min(abs(score - 40), abs(score - 60)) <= dist:
                alerts.append(("WARN", meta["label"], f"Score near regime boundary (score={score:.0f})."))

            # 2) extreme regimes
            if score <= ALERT_RULES["score_extreme"]["low"]:
                alerts.append(("CRIT", meta["label"], f"Extreme risk-off reading (score={score:.0f})."))
            if score >= ALERT_RULES["score_extreme"]["high"]:
                alerts.append(("INFO", meta["label"], f"Strong risk-on reading (score={score:.0f})."))

        # 3) large trend moves
        if not np.isnan(d):
            if days == 30:
                warn = ALERT_RULES["trend_daily_pct"]["warn"]
                crit = ALERT_RULES["trend_daily_pct"]["crit"]
            else:
                warn = ALERT_RULES["trend_slow_pct"]["warn"]
                crit = ALERT_RULES["trend_slow_pct"]["crit"]

            if abs(d) >= crit:
                alerts.append(("CRIT", meta["label"], f"Large move over {wlab}: {d:+.1f}%"))
            elif abs(d) >= warn:
                alerts.append(("WARN", meta["label"], f"Notable move over {wlab}: {d:+.1f}%"))

    # de-dup similar lines
    dedup = []
    seen = set()
    for sev, name, msg in alerts:
        k = (sev, name, msg)
        if k not in seen:
            dedup.append((sev, name, msg))
            seen.add(k)

    # sort by severity
    order = {"CRIT": 0, "WARN": 1, "INFO": 2}
    dedup.sort(key=lambda x: (order.get(x[0], 9), x[1]))
    return dedup

# ============================================================
# REPORT PROMPT (your required block, unchanged)
# ============================================================

REPORT_PROMPT = """SYSTEM / ROLE

You are a senior multi-asset macro strategist writing an internal PM / CIO regime report.
You think in terms of market behavior vs structural constraints, not forecasts.
Your job is to diagnose the current macro regime and translate it into portfolio-relevant implications, using a Dalio-enhanced framework.

You are receiving a YAML payload containing updated macro-financial indicators (rates, inflation, credit, liquidity, fiscal, external balance, gold, etc.).

CRITICAL OUTPUT RULES (NON-NEGOTIABLE)

You must reproduce the exact report structure and section order specified below.

No section may be omitted, merged, or reordered, even if indicators are unchanged.

Do not speculate beyond the data provided.

Do not introduce new indicators or concepts not already in the framework.

Writing must be:

concrete,

cautious,

implementation-oriented,

internally consistent across time.

Each analytical block must include:

a short “What it captures” explanation (if specified),

a one-liner,

KPI-level implications.

TASKS

Using the YAML payload:

1. Reconstruct the macro regime

Explicitly separate:

Market Thermometers (fast, reflexive indicators)

Structural Constraints (slow, compounding pressures)

Assign an implicit regime tone (Risk-On / Neutral / Risk-Off) by behavior, not direction.

2. Assess structural regime risk

Evaluate whether conditions point toward:

fiscal dominance,

financial repression,

inflation-tolerant policy,

or continued late-cycle equilibrium.

Do not call crises unless directly implied by constraints.

3. Translate the regime into portfolio logic

Produce an ETF-oriented action note:

Equity exposure

Duration (nominal vs TIPS)

Credit (IG vs HY)

Hedges (USD, gold, cash)

Emphasize asymmetry, risk budgeting, and optionality.

4. Define short-horizon triggers

Provide 3–5 heuristic triggers (2–6 week horizon).

Triggers must be:

observable,

threshold-based,

directly linked to regime change or de-risking.

MANDATORY REPORT STRUCTURE (FOLLOW EXACTLY)

You must generate the report using this exact structure and headings:

# Global Macro Regime Report

## Dalio-Enhanced, Multi-Asset View — Internal PM Edition

[Insert current date]

How to Read This Report: What “Risk-On / Neutral / Risk-Off” Really Means

(Define regimes as behavioral pricing regimes, not forecasts.)

Executive Summary

(Single coherent narrative of the regime, tensions, and positioning.)

Context Overview: How This Framework Works

(Market Thermometers vs Structural Constraints.)

Reconstructing the Regime
Market Thermometers

1. Price of Time

1A) Real & Nominal Rates

1B) Yield Curve

2. Macro Cycle

2A) Inflation, Breakevens & Labor

3. Conditions and Stress

3A) Financial Conditions & Risk Appetite

4. Liquidity Plumbing

4A) Liquidity Plumbing

Structural Constraints
5) Debt & Fiscal

5A) Debt Service & Fiscal Dynamics

6. External Balance
7. Gold
   Structural Regime Shift

(Probability, path, and logic — no speculation.)

ETF-Oriented Action Note

Equity Exposure

Duration

Credit Risk

Hedges

Key Triggers

(3–5 near-term triggers.)

Final Bottom Line

(One paragraph, no bullets.)

Appendix: Portfolio Translation & Regime Playbook (Internal)
A. Regime Scorecard Snapshot
B. What Works in This Regime
C. What Requires Caution
D. Regime Transition Map
E. Trigger Matrix
F. Meta-Rules
G. One-Page CIO Takeaway
TONE GUIDANCE

Write as if the reader:

runs real money,

hates fluff,

cares about downside more than upside.

Prefer:

clear causal language,

short declarative sentences,

disciplined repetition of core ideas.

Avoid:

dramatic language,

forecasts,

narrative speculation.
""".strip()

# ============================================================
# MAIN
# ============================================================

# ============================================================
# OVERLAYS (Regime Quality) — label + action override ONLY
# These do NOT change the global score. They qualify robustness
# and adjust operating lines (ETF playbook) deterministically.
# ============================================================

def _to_daily_ffill(s: pd.Series) -> pd.Series:
    if s is None or s.empty:
        return pd.Series(dtype=float)
    s = s.dropna()
    if s.empty:
        return pd.Series(dtype=float)
    idx = pd.to_datetime(s.index)
    s = pd.Series(s.values, index=idx).sort_index()
    return s.resample("D").ffill()

def _safe_last(s: pd.Series):
    if s is None or s.empty:
        return np.nan
    s = s.dropna()
    return np.nan if s.empty else float(s.iloc[-1])

def compute_overlays(indicators: dict, indicator_scores: dict, block_scores: dict) -> dict:
    cpi = _to_daily_ffill(indicators.get("cpi_yoy", pd.Series(dtype=float)))
    breakeven = _to_daily_ffill(indicators.get("breakeven_10y", pd.Series(dtype=float)))
    real10 = _to_daily_ffill(indicators.get("real_10y", pd.Series(dtype=float)))
    termp = _to_daily_ffill(indicators.get("term_premium_10y", pd.Series(dtype=float)))

    vix = _to_daily_ffill(indicators.get("vix", pd.Series(dtype=float)))
    hy = _to_daily_ffill(indicators.get("hy_oas", pd.Series(dtype=float)))
    spy_tr = _to_daily_ffill(indicators.get("spy_trend", pd.Series(dtype=float)))  # ratio vs 200DMA
    hyg_lqd = _to_daily_ffill(indicators.get("hyg_lqd_ratio", pd.Series(dtype=float)))

    usd = _to_daily_ffill(indicators.get("usd_index", pd.Series(dtype=float)))
    i2r = _to_daily_ffill(indicators.get("interest_to_receipts", pd.Series(dtype=float)))
    deficit = _to_daily_ffill(indicators.get("deficit_gdp", pd.Series(dtype=float)))

    # ---- Overlay A: Inflation (acute pulse vs chronic drift)
    Inflation_Acute = False
    Inflation_Chronic = False
    try:
        cpi_med = cpi.rolling(window=365, min_periods=60).mean()   # ~12m
        cpi_accel = cpi.diff(90)                                  # ~3m pp change
        be_jump = breakeven.diff(30)                              # ~30d pp change
        real_chg_30 = real10.diff(30)

        acute = False
        if len(cpi_accel.dropna()) > 5:
            acute = acute or (_safe_last(cpi_accel) >= 0.5)
        if len(be_jump.dropna()) > 5:
            acute = acute or (_safe_last(be_jump) >= 0.35)
        if len(be_jump.dropna()) > 5 and len(real_chg_30.dropna()) > 5:
            acute = acute or ((_safe_last(be_jump) >= 0.25) and (_safe_last(real_chg_30) >= -0.05))

        chronic = False
        if len(cpi_med.dropna()) > 10:
            chronic = chronic or (_safe_last(cpi_med) >= 3.0)
        real_30 = real10.rolling(window=30, min_periods=10).mean()
        if len(real_30.dropna()) > 10:
            chronic = chronic or (_safe_last(real_30) > 0.5)

        Inflation_Acute = bool(acute)
        Inflation_Chronic = bool(chronic)
    except Exception:
        Inflation_Acute = False
        Inflation_Chronic = False

    Inflation_Severity = 2 if (Inflation_Acute and Inflation_Chronic) else (1 if (Inflation_Acute or Inflation_Chronic) else 0)

    # ---- Overlay B: Concentration / Crowding
    Concentration = False
    try:
        vix_30 = vix.rolling(window=30, min_periods=10).mean()
        hy_30 = hy.rolling(window=30, min_periods=10).mean()
        spy_dist = (spy_tr - 1.0) * 100.0
        hyg_10 = hyg_lqd.rolling(window=10, min_periods=5).mean()

        crowd = False
        if len(vix_30.dropna()) > 5 and len(hy_30.dropna()) > 5 and len(spy_dist.dropna()) > 5:
            crowd = (
                (_safe_last(vix_30) < 12.0) and
                (_safe_last(hy_30) < float(hy_30.median() - 0.5 * hy_30.std())) and
                (_safe_last(spy_dist) >= 8.0)
            )

        hyg_extreme = False
        if len(hyg_10.dropna()) > 30:
            hyg_extreme = _safe_last(hyg_10) >= float(hyg_10.quantile(0.90))

        Concentration = bool(crowd or hyg_extreme)
        Concentration_Severity = 2 if (crowd and hyg_extreme) else (1 if Concentration else 0)
    except Exception:
        Concentration = False
        Concentration_Severity = 0

    # ---- Overlay C: Funding / policy constraint
    FundingConstraint = False
    try:
        i2r_q = i2r.rolling(window=120, min_periods=20).mean()
        usd_30 = usd.rolling(window=30, min_periods=10).mean()

        condition1 = bool(len(i2r_q.dropna()) > 10 and _safe_last(i2r_q) >= 0.12)

        condition2 = False
        if len(deficit.dropna()) > 50:
            condition2 = _safe_last(deficit) <= float(deficit.quantile(0.25))

        tp_chg_60 = termp.diff(60)
        usd_chg_30 = usd_30.pct_change(30)
        condition3 = bool(len(tp_chg_60.dropna()) > 5 and len(usd_chg_30.dropna()) > 5 and (_safe_last(tp_chg_60) >= 0.25) and (_safe_last(usd_chg_30) >= 0.02))

        FundingConstraint = bool(condition1 or condition2 or condition3)
        FundingSeverity = 2 if (condition1 and condition3) else (1 if FundingConstraint else 0)
    except Exception:
        FundingConstraint = False
        FundingSeverity = 0

    tags = []
    if FundingConstraint:
        tags.append("Funding constraint")
    if Inflation_Acute:
        tags.append("Inflation pulse")
    if Inflation_Chronic:
        tags.append("Inflation drift")
    if Concentration:
        tags.append("Crowding risk")

    severity = max(Inflation_Severity, Concentration_Severity, FundingSeverity)

    return {
        "Inflation_Acute": Inflation_Acute,
        "Inflation_Chronic": Inflation_Chronic,
        "Inflation_Severity": Inflation_Severity,
        "Concentration": Concentration,
        "Concentration_Severity": Concentration_Severity,
        "FundingConstraint": FundingConstraint,
        "FundingSeverity": FundingSeverity,
        "RegimeQualityTags": tags,
        "RegimeQualitySeverity": severity,
    }

def overlay_pill(text: str, kind: str = "info") -> str:
    if kind == "bad":
        col, bg, bd = "var(--bad)", "rgba(239,68,68,0.14)", "rgba(239,68,68,0.45)"
    elif kind == "warn":
        col, bg, bd = "var(--warn)", "rgba(245,158,11,0.14)", "rgba(245,158,11,0.45)"
    else:
        col, bg, bd = "rgba(255,255,255,0.88)", "rgba(255,255,255,0.06)", "rgba(255,255,255,0.12)"
    t = _esc(text)
    return f"<span class='pill' style='border:1px solid {bd}; background:{bg}; color:{col};'>{t}</span>"

def overlays_to_html(overlays: dict) -> str:
    tags = overlays.get("RegimeQualityTags", [])
    if not tags:
        return "<span class='pill'>Quality: <b>Clean</b></span>"
    sev = overlays.get("RegimeQualitySeverity", 1)
    kind = "warn" if sev <= 1 else "bad"
    return overlay_pill("Quality: " + ", ".join(tags), kind=kind)

            def apply_overlays_to_operating_lines(eq: str, dur: str, cr: str, hdg: str, overlays: dict, global_status: str):
    if not overlays.get("RegimeQualityTags"):
        return eq, dur, cr, hdg

    if overlays.get("FundingConstraint", False):
        dur = dur + " | <b>Override:</b> avoid relying on long nominal duration; prefer T-bills/cash-like when term premium is supply-driven."
        cr  = cr  + " | <b>Override:</b> tilt IG over HY; reduce leverage sensitivity."
        hdg = hdg + " | <b>Override:</b> emphasize USD/cash-like hedges; gold supportive if credibility questioned."
        if global_status == "Risk-On":
            eq = eq + " | <b>Override:</b> reduce beta; prefer quality/defensive within equity."

    if overlays.get("Inflation_Acute", False):
        dur = dur + " | <b>Override:</b> prefer TIPS/real duration; shorten exposure to rate spikes."
        hdg = hdg + " | <b>Override:</b> real hedges (TIPS/gold) more relevant."

    if overlays.get("Inflation_Chronic", False):
        dur = dur + " | <b>Override:</b> structurally lower long nominal reliance; keep inflation protection."
        cr  = cr  + " | <b>Override:</b> be cautious on tight-spread carry if policy constraint tightens."

    if overlays.get("Concentration", False) and global_status == "Risk-On":
        eq = eq + " | <b>Override:</b> de-concentrate exposures; consider small convex protection if allowed."

    return eq, dur, cr, hdg
def main():
    st.title("Global finance | Macro overview")

    # Sidebar
    st.sidebar.header("Settings")
    if st.sidebar.button("🔄 Refresh data (clear cache)"):
        st.cache_data.clear()
        st.rerun()

    years_back = st.sidebar.slider("History (years)", 5, 30, 15)

    today = datetime.now(timezone.utc).date()
    start_date = (today - DateOffset(years=years_back)).date().isoformat()
    st.sidebar.markdown(f"**Start date:** {start_date}")

    fred_key = get_fred_api_key()
    if fred_key is None:
        st.sidebar.error("⚠️ Missing `FRED_API_KEY` in secrets.")

    # Fetch data
    with st.spinner("Loading data (FRED + yfinance)..."):
        fred = {
            "real_10y": fetch_fred_series("DFII10", start_date),
            "nominal_10y": fetch_fred_series("DGS10", start_date),
            "dgs2": fetch_fred_series("DGS2", start_date),

            "breakeven_10y": fetch_fred_series("T10YIE", start_date),
            "cpi_index": fetch_fred_series("CPIAUCSL", start_date),
            "unemployment_rate": fetch_fred_series("UNRATE", start_date),

            "hy_oas": fetch_fred_series("BAMLH0A0HYM2", start_date),
            "usd_fred": fetch_fred_series("DTWEXBGS", start_date),

            "fed_balance_sheet": fetch_fred_series("WALCL", start_date),
            "rrp": fetch_fred_series("RRPONTSYD", start_date),

            "interest_payments": fetch_fred_series("A091RC1Q027SBEA", start_date),
            "federal_receipts": fetch_fred_series("FGRECPT", start_date),
            "deficit_gdp": fetch_fred_series("FYFSGDA188S", start_date),
            "term_premium_10y": fetch_fred_series("ACMTP10", start_date),

            "current_account_gdp": fetch_fred_series("USAB6BLTT02STSAQ", start_date),
        }

        indicators = {}

        # Derived: yield curve
        if not fred["nominal_10y"].empty and not fred["dgs2"].empty:
            yc = fred["nominal_10y"].to_frame("10y").join(fred["dgs2"].to_frame("2y"), how="inner")
            indicators["yield_curve_10_2"] = (yc["10y"] - yc["2y"]).dropna()
        else:
            indicators["yield_curve_10_2"] = pd.Series(dtype=float)

        # CPI YoY
        if not fred["cpi_index"].empty:
            indicators["cpi_yoy"] = (fred["cpi_index"].pct_change(12) * 100.0).dropna()
        else:
            indicators["cpi_yoy"] = pd.Series(dtype=float)

        # Direct FRED
        indicators["real_10y"] = fred["real_10y"]
        indicators["nominal_10y"] = fred["nominal_10y"]
        indicators["breakeven_10y"] = fred["breakeven_10y"]
        indicators["unemployment_rate"] = fred["unemployment_rate"]

        indicators["hy_oas"] = fred["hy_oas"]
        indicators["fed_balance_sheet"] = fred["fed_balance_sheet"]
        indicators["rrp"] = fred["rrp"]

        indicators["interest_payments"] = fred["interest_payments"]
        indicators["federal_receipts"] = fred["federal_receipts"]
        indicators["deficit_gdp"] = fred["deficit_gdp"]
        indicators["term_premium_10y"] = fred["term_premium_10y"]
        indicators["current_account_gdp"] = fred["current_account_gdp"]

        # Derived: interest / receipts ratio
        ip = indicators.get("interest_payments", pd.Series(dtype=float))
        fr = indicators.get("federal_receipts", pd.Series(dtype=float))
        if (ip is not None and fr is not None) and (not ip.empty) and (not fr.empty):
            join = ip.to_frame("interest").join(fr.to_frame("receipts"), how="inner").dropna()
            join = join[join["receipts"] != 0]
            indicators["interest_to_receipts"] = (join["interest"] / join["receipts"]).dropna()
        else:
            indicators["interest_to_receipts"] = pd.Series(dtype=float)

        # YFinance
        yf_map = fetch_yf_many(["DX-Y.NYB", "^VIX", "SPY", "HYG", "LQD", "GLD"], start_date)

        dxy = yf_map.get("DX-Y.NYB", pd.Series(dtype=float))
        if dxy is None or dxy.empty:
            dxy = fred["usd_fred"]
        indicators["usd_index"] = dxy

        indicators["vix"] = yf_map.get("^VIX", pd.Series(dtype=float))

        spy = yf_map.get("SPY", pd.Series(dtype=float))
        if spy is not None and not spy.empty:
            ma200 = spy.rolling(200).mean()
            indicators["spy_trend"] = (spy / ma200).dropna()
        else:
            indicators["spy_trend"] = pd.Series(dtype=float)

        hyg = yf_map.get("HYG", pd.Series(dtype=float))
        lqd = yf_map.get("LQD", pd.Series(dtype=float))
        if hyg is not None and lqd is not None and (not hyg.empty) and (not lqd.empty):
            joined = hyg.to_frame("HYG").join(lqd.to_frame("LQD"), how="inner").dropna()
            indicators["hyg_lqd_ratio"] = (joined["HYG"] / joined["LQD"]).dropna()
        else:
            indicators["hyg_lqd_ratio"] = pd.Series(dtype=float)

        indicators["gold"] = yf_map.get("GLD", pd.Series(dtype=float))

    # Score indicators
    indicator_scores = {}
    for key, meta in INDICATOR_META.items():
        series = indicators.get(key, pd.Series(dtype=float))
        mode = meta.get("scoring_mode", "z5y")
        score, sig, latest = compute_indicator_score(series, meta["direction"], scoring_mode=mode)
        indicator_scores[key] = {
            "score": score,
            "signal": sig,
            "latest": latest,
            "status": classify_status(score),
            "mode": mode
        }

    # Score blocks + global
    block_scores = {}
    global_score = 0.0
    w_used = 0.0

    for bkey, binfo in BLOCKS.items():
        vals = []
        for ikey in binfo["indicators"]:
            sc = indicator_scores.get(ikey, {}).get("score", np.nan)
            if not np.isnan(sc):
                vals.append(sc)

        bscore = float(np.mean(vals)) if vals else np.nan
        block_scores[bkey] = {"score": bscore, "status": classify_status(bscore)}

        if binfo["weight"] > 0 and not np.isnan(bscore):
            global_score += bscore * binfo["weight"]
            w_used += binfo["weight"]

    global_score = (global_score / w_used) if w_used > 0 else np.nan
    global_status = classify_status(global_score)
    block_scores["GLOBAL"] = {"score": global_score, "status": global_status}

    # Data freshness
    latest_points = [s.index.max() for s in indicators.values() if s is not None and not s.empty]
    data_max_date = max(latest_points) if latest_points else None
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    # Alerts (computed once)
    alerts = build_alerts(indicators, indicator_scores)
    st.session_state["alerts"] = alerts
    overlays = compute_overlays(indicators, indicator_scores, block_scores)

    # Tabs
    tabs = st.tabs(["Overview", "Wallboard", "Framework logic", "Deep dive", "What changed", "Report generation"])

    # ============================================================
    # OVERVIEW
    # ============================================================
    with tabs[0]:
        st.markdown("<div class='muted'>ETF-oriented macro wallboard: separates Market Thermometers (fast) vs Structural Constraints (slow), then maps to operating lines.</div>", unsafe_allow_html=True)


        eq_line, dur_line, cr_line, hdg_line = operating_lines(block_scores, indicator_scores)
            eq_line, dur_line, cr_line, hdg_line = apply_overlays_to_operating_lines(eq_line, dur_line, cr_line, hdg_line, overlays, global_status)

        market_blocks = ["price_of_time", "macro", "conditions", "plumbing"]
        structural_blocks = ["policy_link", "external", "gold_block"]

        def block_line(bkey):
            name = BLOCKS[bkey]["name"]
            sc = block_scores[bkey]["score"]
            stt = block_scores[bkey]["status"]
            sc_txt = "n/a" if np.isnan(sc) else f"{sc:.1f}"
            return f"{sema(stt)} {name}: <b>{status_label(stt)}</b> ({sc_txt})"

        gs_txt = "n/a" if np.isnan(global_score) else f"{global_score:.1f}"

        st.markdown(
            f"""
            <div class="grid3">
              <div class="card">
                <div class="cardTitle">Global Score (0–100) — core blocks</div>
                <div class="cardValue">{gs_txt}</div>
                <div class="cardSub">{pill_html(global_status)}<br/>{overlays_to_html(overlays)}</div>
                <div class="cardSub">
                  <b>Equity:</b> {eq_line}<br/>
                  <b>Duration:</b> {dur_line}<br/>
                  <b>Credit:</b> {cr_line}<br/>
                  <b>Hedges:</b> {hdg_line}
                </div>
              </div>

              <div class="card">
                <div class="cardTitle">Market Thermometers — block scorecard</div>
                <div class="cardSub">
                  {"<br/>".join([block_line(k) for k in market_blocks])}
                </div>
                <div class="cardTitle" style="margin-top:12px;">Structural Constraints — block scorecard</div>
                <div class="cardSub">
                  {"<br/>".join([block_line(k) for k in structural_blocks])}
                </div>
              </div>

              <div class="card">
                <div class="cardTitle">Policy / funding links (one-liners)</div>
                <div class="cardSub">
                  1) <b>Deficit pressure ↑ → supply pressure ↑ → term premium risk ↑</b><br/>
                  2) <b>Debt service pressure ↑ → policy flexibility ↓</b><br/>
                  3) <b>Term premium ↑ + USD ↑ → global tightening impulse</b><br/>
                  4) <b>External deficit → vulnerability in USD tightening</b><br/>
                  5) <b>Gold strength often reflects hedge demand, not growth optimism</b>
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Alerts panel (moved to bottom to keep the 5-second read tight)
        alerts = st.session_state.get("alerts", [])
        if alerts:
            with st.expander("Alerts / attention (data issues, near thresholds, big moves)", expanded=False):
                top = alerts[:12]
                st.markdown("<div class='alertBox'>", unsafe_allow_html=True)
                st.markdown("<div class='alertTitle'>⚠️ Attention (signals worth checking)</div>", unsafe_allow_html=True)
                for sev, name, msg in top:
                    icon = "🟥" if sev == "CRIT" else ("🟧" if sev == "WARN" else "🟦")
                    st.markdown(f"<div class='alertItem'>{icon} <b>{_html.escape(name)}</b>: {_html.escape(msg)}</div>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                left, right = st.columns([2, 1])
                with left:
                    with st.expander("How to read Risk-on / Neutral / Risk-off (behavioral, not forecasts)", expanded=True):
                        st.markdown(
                            """
        **Risk-on:** markets price easier conditions (lower stress premia), credit behaves well, trend and risk appetite are supportive.  
        **Neutral:** mixed signals; sizing discipline matters more than directional conviction.  
        **Risk-off:** stress/tightening dominates; protect downside first (quality, liquidity, hedges).

        **How scores work:**  
        - **Market thermometers** use a ~5Y z-score (`z5y`) → clamped to [-2,+2] → mapped to 0–100.  
        - **Structural constraints** use a ~20Y percentile (`pct20y`) → mapped to [-2,+2] → 0–100.  
        - **Thresholds:** >60 Risk-on, 40–60 Neutral, <40 Risk-off (heuristics).
                            """.strip()
                        )
                with right:
                    st.markdown(
                        f"""
                        <div class="card">
                          <div class="cardTitle">Data & display</div>
                          <div class="cardSub">
                            Now: <b>{now_utc}</b><br/>
                            Latest datapoint: <b>{('n/a' if data_max_date is None else str(pd.to_datetime(data_max_date).date()))}</b><br/>
                            History: <b>{years_back}y</b>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

    # ============================================================
    # WALLBOARD
    # ============================================================
    with tabs[1]:
        st.markdown("## Wallboard")
        st.markdown("<div class='muted'>Order: Overall regime → component scores → operating lines → grouped indicator tiles (no charts).</div>", unsafe_allow_html=True)

        eq_line, dur_line, cr_line, hdg_line = operating_lines(block_scores, indicator_scores)
            eq_line, dur_line, cr_line, hdg_line = apply_overlays_to_operating_lines(eq_line, dur_line, cr_line, hdg_line, overlays, global_status)
        gs_txt = "n/a" if np.isnan(global_score) else f"{global_score:.1f}"

        st.markdown(
            f"""
            <div class="grid2">
              <div class="card">
                <div class="cardTitle">Overall regime</div>
                <div class="cardValue">{gs_txt}</div>
                <div class="cardSub">{pill_html(global_status)}<br/>{overlays_to_html(overlays)}</div>
                <div class="cardSub">{score_bar_html(global_score)}</div>
              </div>
              <div class="card">
                <div class="cardTitle">Operating lines (ETF)</div>
                <div class="cardSub">
                  <b>Equity:</b> {eq_line}<br/>
                  <b>Duration:</b> {dur_line}<br/>
                  <b>Credit:</b> {cr_line}<br/>
                  <b>Hedges:</b> {hdg_line}
                </div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        def comp_row(keys):
            rows = []
            for k in keys:
                sc = block_scores[k]["score"]
                stt = block_scores[k]["status"]
                sc_txt = "n/a" if np.isnan(sc) else f"{sc:.1f}"
                rows.append(f"{sema(stt)} {BLOCKS[k]['name']}: <b>{status_label(stt)}</b> ({sc_txt})")
            return "<br/>".join(rows)

        st.markdown(
            f"""
            <div class="grid2" style="margin-top:14px;">
              <div class="card">
                <div class="cardTitle">Component scores — Market Thermometers</div>
                <div class="cardSub">{comp_row(['price_of_time','macro','conditions','plumbing'])}</div>
              </div>
              <div class="card">
                <div class="cardTitle">Component scores — Structural Constraints</div>
                <div class="cardSub">{comp_row(['policy_link','external','gold_block'])}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- Grouped indicator tiles — responsive grid (no charts) ---
        with st.expander("Market Thermometers", expanded=True):
            render_group(
                "Price of Time",
                "Rates and curve: the price of time and late-cycle signal.",
                ["real_10y", "nominal_10y", "yield_curve_10_2"],
                indicators,
                indicator_scores,
                ncols=3
            )
            render_group(
                "Macro Cycle",
                "Inflation and growth: policy constraint and cycle pressure.",
                ["breakeven_10y", "cpi_yoy", "unemployment_rate"],
                indicators,
                indicator_scores,
                ncols=3
            )
            render_group(
                "Conditions & Stress",
                "Fast regime: USD, credit stress, vol, trend, risk appetite.",
                ["usd_index", "hy_oas", "vix", "spy_trend", "hyg_lqd_ratio"],
                indicators,
                indicator_scores,
                ncols=3
            )
            render_group(
                "Liquidity / Plumbing",
                "System liquidity: tailwind vs drain for risk assets.",
                ["fed_balance_sheet", "rrp"],
                indicators,
                indicator_scores,
                ncols=3
            )

        with st.expander("Structural Constraints", expanded=True):
            render_group(
                "Fiscal / Policy Constraint",
                "Debt service, deficit dynamics, and funding constraint signal.",
                ["interest_to_receipts", "deficit_gdp", "term_premium_10y", "interest_payments", "federal_receipts"],
                indicators,
                indicator_scores,
                ncols=3
            )
            render_group(
                "External Balance",
                "External funding reliance / vulnerability in USD tightening.",
                ["current_account_gdp"],
                indicators,
                indicator_scores,
                ncols=3
            )
            render_group(
                "Gold",
                "Hedge demand / policy credibility signal.",
                ["gold"],
                indicators,
                indicator_scores,
                ncols=3
            )

# Grouped indicator tiles — responsive grid (no charts)
# ORPHAN_CALL_REMOVED def render_group(title: str, desc: str, keys: list, indicators: dict, indicator_scores: dict, ncols: int = 3):
# ORPHAN_CALL_REMOVED     st.markdown(
# ORPHAN_CALL_REMOVED         f"<div class='section'><div class='sectionHead'><div><div class='sectionTitle'>{_html.escape(title)}</div>"
# ORPHAN_CALL_REMOVED         f"<div class='sectionDesc'>{_html.escape(desc)}</div></div></div></div>",
# ORPHAN_CALL_REMOVED         unsafe_allow_html=True
# ORPHAN_CALL_REMOVED     )
    cols = st.columns(ncols)
    for j, k in enumerate(keys):
        with cols[j % ncols]:
            s = indicators.get(k, pd.Series(dtype=float))
            if s is None or s.empty:
                wallboard_missing_tile(k)
            else:
                wallboard_tile(k, s, indicator_scores)

# ORPHAN_EXPANDER_REMOVED with st.expander("Market Thermometers", expanded=True):
    pass

# ORPHAN_EXPANDER_REMOVED with st.expander("Structural Constraints", expanded=True):
    pass
    # ============================================================
    # FRAMEWORK LOGIC (conceptual, no charts)
    # ============================================================
    with tabs[2]:
        st.markdown("## Framework logic")
        st.markdown("<div class='muted'>How the monitoring engine works: Market Thermometers vs Structural Constraints, plus regime-quality overlays.</div>", unsafe_allow_html=True)
        st.markdown("""
### Two layers
- **Market Thermometers (fast):** prices and spreads that move quickly (rates, USD, credit, vol, trend, liquidity).
- **Structural Constraints (slow):** compounding limits that shape policy/funding regimes (inflation persistence, fiscal burden, term premium, external balance).

### Why z-score vs percentile
- **z5y (Thermometers):** compares to a recent regime; useful for fast variables whose 'normal' shifts.
- **pct20y (Constraints):** anchors to longer history for structural extremes.

### How the regime score is built
- Each indicator is mapped to a **0-100 supportiveness score** (direction-adjusted).
- Indicators are aggregated into block scores; blocks into a global score.
- **>60 Risk-On, 40-60 Neutral, <40 Risk-Off** (heuristic thresholds).

### Regime quality overlays (label + action override only)
Overlays do not change the score. They add interpretive tags and adjust the ETF playbook:
- **Inflation pulse (acute):** fast inflation expectations/realization acceleration -> duration hedge quality worsens.
- **Inflation drift (chronic):** persistent inflation constraint -> structurally reduce long nominal reliance.
- **Funding constraint:** debt service/issuance/term premium dynamics -> long duration hedge less reliable; cash/USD hedges gain value.
- **Crowding risk:** low vol + tight spreads + strong trend -> fragility/non-linearity risk; de-concentrate equity exposure.

### Reading conflicts
- Thermometers Risk-On + Constraints Risk-Off -> Risk-On fragile: size down and hedge smarter.
- Thermometers Risk-Off + Constraints benign -> Risk-Off tactical: stress may be positioning/liquidity-driven; wait for confirmation.
""")
        with st.expander("Current regime quality tags (live)", expanded=True):
            st.markdown(overlays_to_html(overlays), unsafe_allow_html=True)
            st.json(overlays)

    # DEEP DIVE
    # ============================================================
    with tabs[3]:
        st.markdown("## Deep dive")
        st.markdown("<div class='muted'>Full charts. Titles embedded inside charts for dark theme readability.</div>", unsafe_allow_html=True)

        group = st.selectbox(
            "Select section",
            ["Price of Time", "Macro Cycle", "Conditions & Stress", "Liquidity / Plumbing", "Fiscal / Policy Constraint", "External Balance & Gold"],
            index=0
        )

        group_map = {
            "Price of Time": ["real_10y", "nominal_10y", "yield_curve_10_2"],
            "Macro Cycle": ["breakeven_10y", "cpi_yoy", "unemployment_rate"],
            "Conditions & Stress": ["usd_index", "hy_oas", "vix", "spy_trend", "hyg_lqd_ratio"],
            "Liquidity / Plumbing": ["fed_balance_sheet", "rrp"],
            "Fiscal / Policy Constraint": ["interest_to_receipts", "deficit_gdp", "term_premium_10y", "interest_payments", "federal_receipts"],
            "External Balance & Gold": ["current_account_gdp", "gold"],
        }

        for k in group_map[group]:
            meta = INDICATOR_META[k]
            s = indicators.get(k, pd.Series(dtype=float))

            st.markdown("<div class='section'>", unsafe_allow_html=True)
            sc = indicator_scores.get(k, {})
            score = sc.get("score", np.nan)
            status = sc.get("status", "n/a")
            latest = sc.get("latest", np.nan)
            latest_txt = fmt_value(latest, meta["unit"], meta.get("scale", 1.0))

            tr = recent_trend(s)
            wlab = tr["window_label"]
            d = tr["delta_pct"]
            arrow = tr["arrow"]
            d_txt = "n/a" if np.isnan(d) else f"{d:+.1f}%"

            st.markdown(
                f"""
                <div class="sectionHead">
                  <div>
                    <div class="sectionTitle">{_html.escape(meta["label"])}</div>
                    <div class="sectionDesc">{_html.escape(meta["source"])}</div>
                  </div>
                  <div style="text-align:right;">
                    <div style="display:flex; gap:10px; justify-content:flex-end; flex-wrap:wrap;">
                      <span class="pill">Latest: <b>{_html.escape(latest_txt)}</b></span>
                      {pill_html(status)}
                      <span class="pill">Score: <b>{("n/a" if np.isnan(score) else f"{score:.0f}")}</b></span>
                      <span class="pill">Trend ({_html.escape(wlab)}): <b>{_html.escape(arrow)} {_html.escape(d_txt)}</b></span>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if s is None or s.empty:
                st.warning("Missing data for this indicator in the selected history window.")
            else:
                fig = plot_premium(s, meta["label"], ref_line=meta.get("ref_line", None), height=340)
                st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False}, key=f"deep_{k}")

            with st.expander("Indicator guide (definition, thresholds, why it matters)", expanded=False):
                exp = meta["expander"]
                st.markdown(f"**What it is:** {exp.get('what','')}")
                st.markdown(f"**Reference levels / thresholds:** {exp.get('reference','')}")
                st.markdown("**How to read it:**")
                st.markdown(exp.get("interpretation", ""))
                st.markdown(f"**Why it matters (policy/funding link):** {exp.get('bridge','')}")

            st.markdown("</div>", unsafe_allow_html=True)

    # ============================================================
    # WHAT CHANGED (table + hot list “singled out”)
    # ============================================================
    with tabs[4]:
        st.markdown("## What changed")
        st.markdown(
            "<div class='muted'>Watch what is moving (trend) and what is close to regime thresholds (score). "
            "Hotlist highlights the most relevant items.</div>",
            unsafe_allow_html=True
        )

        rows = []
        for key, meta in INDICATOR_META.items():
            s = indicators.get(key, pd.Series(dtype=float))
            if s is None or s.empty:
                continue

            tr = recent_trend(s)
            window = tr["window_label"]
            dwin = tr["delta_pct"]

            d7 = pct_change_over_days(s, 7)
            d30 = pct_change_over_days(s, 30)
            d90 = pct_change_over_days(s, 90)
            d1y = pct_change_over_days(s, 365)

            sc = indicator_scores.get(key, {})
            score = sc.get("score", np.nan)
            status = sc.get("status", "n/a")
            mode = meta.get("scoring_mode", "z5y")

            # attention: (a) close to 40/60, (b) magnitude of main trend
            if np.isnan(score):
                prox = 0.0
            else:
                prox = max(0.0, 20.0 - min(abs(score - 40), abs(score - 60))) / 20.0

            if np.isnan(dwin):
                move = 0.0
            else:
                # Normalize move vs thresholds (daily 30d vs slow 1Q)
                if window == "30d":
                    move = min(1.0, abs(dwin) / ALERT_RULES["trend_daily_pct"]["warn"])
                else:
                    move = min(1.0, abs(dwin) / ALERT_RULES["trend_slow_pct"]["warn"])

            attention = 0.55 * prox + 0.45 * move
            hot = "HOT" if attention >= 0.65 else ("WATCH" if attention >= 0.50 else "")

            rows.append({
                "Indicator": meta["label"],
                "Scoring": mode,
                "Regime": status_label(status),
                "Score": (np.nan if np.isnan(score) else round(score, 1)),
                f"Trend ({window}) %": (np.nan if np.isnan(dwin) else round(dwin, 2)),
                "Δ 7d %": (np.nan if np.isnan(d7) else round(d7, 2)),
                "Δ 30d %": (np.nan if np.isnan(d30) else round(d30, 2)),
                "Δ 1Q %": (np.nan if np.isnan(d90) else round(d90, 2)),
                "Δ 1Y %": (np.nan if np.isnan(d1y) else round(d1y, 2)),
                "Hotlist": hot,
                "Attention": round(attention, 2),
            })

        if not rows:
            st.info("No sufficient data to compute changes.")
        else:
            df = pd.DataFrame(rows)

            # Hotlist first
            hot_df = df[df["Hotlist"].isin(["HOT", "WATCH"])].sort_values(["Hotlist", "Attention"], ascending=[True, False]).head(12)
            if not hot_df.empty:
                st.markdown("### Singled out (HOT / WATCH)")
                for _, r in hot_df.iterrows():
                    badge = "🔥 HOT" if r["Hotlist"] == "HOT" else "👀 WATCH"
                    st.markdown(
                        f"""
                        <div class="card" style="margin-bottom:10px;">
                          <div class="cardTitle">{_html.escape(badge)} — {_html.escape(r["Indicator"])}</div>
                          <div class="cardSub">
                            Regime: <b>{_html.escape(r["Regime"])}</b> · Score: <b>{r["Score"]}</b> ·
                            Trend: <b>{r[[c for c in df.columns if c.startswith("Trend")][0]]:+.2f}%</b> ·
                            Attention: <b>{r["Attention"]:.2f}</b>
                          </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.markdown("### Full table")
            st.dataframe(
                df.sort_values(["Hotlist", "Attention"], ascending=[True, False]).reset_index(drop=True),
                use_container_width=True,
                column_config={
                    "Indicator": st.column_config.TextColumn("Indicator", width="large"),
                    "Scoring": st.column_config.TextColumn("Scoring", help="z5y (fast) vs pct20y (slow)."),
                    "Regime": st.column_config.TextColumn("Regime", help="Derived from 0–100 score: >60 Risk-on, 40–60 Neutral, <40 Risk-off."),
                    "Score": st.column_config.NumberColumn("Score"),
                    "Hotlist": st.column_config.TextColumn("Hotlist", help="HOT / WATCH based on threshold proximity + move."),
                    "Attention": st.column_config.NumberColumn("Attention", help="0–1 heuristic relevance score."),
                }
            )

            st.caption(
                "Note: % changes use closest available past observation (series frequencies differ). "
                "Use Wallboard for reference levels and Deep dive for chart context."
            )

    # ============================================================
    # REPORT GENERATION
    # ============================================================
    with tabs[5]:
        st.markdown("## Report generation")
        st.markdown("<div class='muted'>Single copy/paste output: prompt first, then YAML payload.</div>", unsafe_allow_html=True)

        if st.button("Generate one-shot prompt + payload"):
            payload_lines = []
            payload_lines.append("macro_regime_payload:")
            payload_lines.append(f"  generated_at_utc: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
            payload_lines.append(f"  global_score: {0.0 if np.isnan(global_score) else round(global_score, 1)}")
            payload_lines.append(f"  global_status: {global_status}")
            payload_lines.append("  scoring_notes: \"Market thermometers use z5y; structural constraints use pct20y\"")

            payload_lines.append("  blocks:")
            for bkey, binfo in BLOCKS.items():
                bscore = block_scores[bkey]["score"]
                bstatus = block_scores[bkey]["status"]
                payload_lines.append(f"    - key: \"{bkey}\"")
                payload_lines.append(f"      name: \"{binfo['name']}\"")
                payload_lines.append(f"      group: \"{binfo['group']}\"")
                payload_lines.append(f"      weight: {binfo['weight']}")
                payload_lines.append(f"      score: {0.0 if np.isnan(bscore) else round(bscore, 1)}")
                payload_lines.append(f"      status: {bstatus}")

            eq_line, dur_line, cr_line, hdg_line = operating_lines(block_scores, indicator_scores)
            eq_line, dur_line, cr_line, hdg_line = apply_overlays_to_operating_lines(eq_line, dur_line, cr_line, hdg_line, overlays, global_status)
            payload_lines.append("  operating_lines:")
            payload_lines.append(f"    equity_exposure: \"{eq_line}\"")
            payload_lines.append(f"    duration: \"{dur_line}\"")
            payload_lines.append(f"    credit: \"{cr_line}\"")
            payload_lines.append(f"    hedges: \"{hdg_line}\"")

            payload_lines.append("  alerts:")
            for sev, name, msg in alerts[:20]:
                payload_lines.append(f"    - severity: \"{sev}\"")
                payload_lines.append(f"      indicator: \"{name}\"")
                payload_lines.append(f"      message: \"{msg}\"")

            payload_lines.append("  indicators:")
            for key, meta in INDICATOR_META.items():
                s_info = indicator_scores.get(key, {})
                score = s_info.get("score", np.nan)
                status = s_info.get("status", "n/a")
                latest = s_info.get("latest", np.nan)
                series = indicators.get(key, pd.Series(dtype=float))

                tr = recent_trend(series)
                window = tr["window_label"]
                dwin = tr["delta_pct"]

                payload_lines.append(f"    - key: \"{key}\"")
                payload_lines.append(f"      name: \"{meta['label']}\"")
                payload_lines.append(f"      source: \"{meta['source']}\"")
                payload_lines.append(f"      scoring_mode: \"{meta.get('scoring_mode','z5y')}\"")
                payload_lines.append(f"      latest_value: \"{fmt_value(latest, meta['unit'], meta.get('scale', 1.0))}\"")
                payload_lines.append(f"      score: {0.0 if np.isnan(score) else round(score, 1)}")
                payload_lines.append(f"      status: {status}")
                payload_lines.append(f"      trend_window: \"{window}\"")
                payload_lines.append(f"      trend_change_pct: {0.0 if np.isnan(dwin) else round(dwin, 2)}")
                payload_lines.append(f"      reference_line: {('null' if meta.get('ref_line', None) is None else meta.get('ref_line'))}")
                payload_lines.append(f"      reference_notes: \"{meta['expander'].get('reference','')}\"")

            payload_text = "\n".join(payload_lines)

            one_shot = (
                "### COPY/PASTE BELOW (PROMPT + PAYLOAD)\n\n"
                + REPORT_PROMPT
                + "\n\n---\n\n"
                + "YAML PAYLOAD:\n\n```yaml\n"
                + payload_text
                + "\n```\n"
            )

            st.code(one_shot, language="markdown")
            st.caption("Tip: paste the entire block into a new chat. The model should follow the prompt, then read the YAML payload.")

if __name__ == "__main__":
    main()
