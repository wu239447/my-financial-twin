import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# --- 1. Global Config & Font Setting ---
# Use standard fonts to avoid rendering issues on GitHub/Streamlit Cloud
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False 

st.set_page_config(page_title="Value Chain Strategic Tower", layout="wide")
st.title("🛡️ Finance-Logistics Digital Twin: Strategic Monitor")

# --- Sidebar: Global Finance Settings ---
st.sidebar.header("🏦 Global Finance Setup")
equity = st.sidebar.number_input("Equity", value=5000000)
initial_cash = st.sidebar.number_input("Initial Cash Balance", value=1500000)
debt_rate = st.sidebar.slider("Interest Rate (%)", 1, 20, 8) / 100
depreciation = st.sidebar.number_input("Depreciation Expense", value=400000)
tax_rate = 0.2

st.sidebar.header("📦 Opening Balances")
beg_inv = st.sidebar.number_input("Beg Inventory", value=1200000)
beg_ar = st.sidebar.number_input("Beg Accounts Receivable (AR)", value=1800000)
beg_ap = st.sidebar.number_input("Beg Accounts Payable (AP)", value=1000000)

st.sidebar.header("⚠️ Risk & Obsolescence")
obs_rate = st.sidebar.slider("Inv. Obsolescence Rate (%)", 0, 30, 5) / 100
bad_debt_rate = st.sidebar.slider("Bad Debt Rate (%)", 0, 15, 2) / 100

# --- Core Calculation Engine ---
def run_engine(s_sales, s_gm, s_dio, s_dso, s_dpo):
    daily_sales = s_sales / 365
    daily_cogs = (s_sales * (1 - s_gm)) / 365
    e_inv, e_ar, e_ap = daily_cogs * s_dio, daily_sales * s_dso, daily_cogs * s_dpo
    
    # P&L Calculation
    ebit = (s_sales * (s_gm - 0.12)) - depreciation - (e_inv * obs_rate) - (e_ar * bad_debt_rate)
    loan = max(0.0, (e_inv + e_ar - e_ap) - initial_cash)
    interest = loan * debt_rate
    ni = max(0.0, (ebit - interest) * (1 - tax_rate))
    
    # Metrics
    roe = (ni / equity) * 100 if equity > 0 else 0
    roic = (ebit * (1 - tax_rate) / max((e_inv + 3000000), 1)) * 100
    icr = ebit / max(interest, 0.0001)
    
    # Cash Flow
    wc_change = (e_inv - beg_inv) + (e_ar - beg_ar) - (e_ap - beg_ap)
    ocf = ni + depreciation - wc_change
    f_cash = initial_cash + ocf
    return roe, roic, ocf, icr, f_cash, loan, interest, wc_change

# --- Tabs ---
tab1, tab2 = st.tabs(["🔮 AI Sales Forecast", "📊 Strategy Control Tower"])

# --- Tab 1: AI Forecast ---
with tab1:
    st.header("🔮 Multi-Product AI Sales Forecast")
    default_data = {
        "Product": ["Premium A", "Mass B", "Component C"],
        "Hist_Monthly_Rev(10k)": [
            "100,110,105,120,130,140,150,160,155,170,185,200",
            "50,55,52,60,65,70,68,75,80,85,90,95",
            "30,31,30,32,33,35,34,36,37,38,39,40"
        ],
        "Seasonal": [True, False, False],
        "Target_GM(%)": [40, 25, 15],
        "Target_DIO": [90, 45, 30]
    }
    edited_df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

    total_annual_sales = 0
    wavg_gm, wavg_dio = 0, 0
    item_results = []

    for _, row in edited_df.iterrows():
        try:
            h_data = [float(x.strip()) * 10000 for x in str(row["Hist_Monthly_Rev(10k)"]).split(",")]
            if row["Seasonal"]:
                model = ExponentialSmoothing(h_data, trend='add', seasonal='add', seasonal_periods=4).fit()
            else:
                model = ExponentialSmoothing(h_data, trend='add', seasonal=None).fit()
            ann_pred = float(model.forecast(1).iloc[0]) * 12
            total_annual_sales += ann_pred
            item_results.append({
                "Product": row["Product"], 
                "Forecast_Rev": ann_pred, 
                "GM": row["Target_GM(%)"]/100, 
                "DIO": row["Target_DIO"]
            })
        except: continue

    if total_annual_sales > 0:
        for item in item_results:
            weight = item["Forecast_Rev"] / total_annual_sales
            wavg_gm += item["GM"] * weight
            wavg_dio += item["DIO"] * weight
        st.bar_chart(pd.DataFrame(item_results).set_index("Product")["Forecast_Rev"])
        st.success(f"✅ AI Estimated Annual Revenue Target: **${total_annual_sales:,.0f}**")
    else:
        total_annual_sales, wavg_gm, wavg_dio = 15000000, 0.30, 60

# --- Tab 2: Control Tower ---
with tab2:
    st.header("📊 Value Chain Linkage & Stress Test")
    
    achieve_rate = st.slider("🎯 Sales Achievement Stress Test (%)", 50, 150, 100) / 100
    
    c1, c2, c3 = st.columns(3)
    base_sales = c1.number_input("Base AI Revenue", value=int(total_annual_sales))
    actual_sales = base_sales * achieve_rate
    st.caption(f"📢 Actual Revenue under Stress: ${actual_sales:,.0f}")
    
    final_gm = c2.slider("Blended Gross Margin (%)", 5, 60, int(wavg_gm*100)) / 100
    final_dio = c3.slider("Inventory Days (DIO)", 10, 200, int(wavg_dio))
    
    st.divider()
    g1, g2 = st.columns(2)
    dso = g1.slider("AR Days (DSO)", 15, 150, 60)
    dpo = g2.slider("AP Days (DPO)", 15, 150, 45)

    # Core Execution
    roe_v, roic_v, ocf_v, icr_v, f_cash_v, loan_v, int_v, wc_c_v = run_engine(actual_sales, final_gm, final_dio, dso, dpo)

    # --- KPI Dashboard ---
    st.subheader("📈 Key Performance Indicators (KPI)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ROE", f"{roe_v:.2f}%")
    m2.metric("ROIC", f"{roic_v:.2f}%")
    m3.metric("OCF (Operating Cash Flow)", f"${ocf_v:,.0f}")
    m4.metric("ICR (Interest Coverage)", f"{icr_v:.2f}")

    # --- Liquidity Monitor ---
    st.divider()
    st.subheader("💰 Liquidity & Working Capital")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Ending Cash", f"${f_cash_v:,.0f}")
    k2.metric("Financing Need", f"${loan_v:,.0f}")
    k3.metric("Annual Interest", f"-${int_v:,.0f}")
    k4.metric("Net WC Change", f"-${wc_c_v:,.0f}")

    # --- Sensitivity Analysis (English Optimized) ---
    st.divider()
    st.subheader("🎯 Sensitivity Analysis")
    
    param_map = {
        "Sales Achievement": "achieve",
        "Gross Margin": "gm",
        "Inventory Days (DIO)": "dio",
        "AR Days (DSO)": "dso"
    }
    
    sc1, sc2, sc3 = st.columns(3)
    x_label = sc1.selectbox("X-axis", list(param_map.keys()), index=2)
    y_label = sc2.selectbox("Y-axis", list(param_map.keys()), index=1)
    z_label = sc3.selectbox("Z-axis (Target)", ["ROE (%)", "Cash Flow (OCF)"])

    scale_factor = 1.0 if z_label == "ROE (%)" else 10000.0
    unit_label = "%" if z_label == "ROE (%)" else "10k"

    steps = np.linspace(0.7, 1.3, 10) 
    sens_data = []

    for y_m in steps:
        row = []
        for x_m in steps:
            p = {"s": actual_sales, "g": final_gm, "di": final_dio, "ds": dso}
            for label, mult in [(x_label, x_m), (y_label, y_m)]:
                if param_map[label] == "achieve": p["s"] *= mult
                elif param_map[label] == "gm": p["g"] *= mult
                elif param_map[label] == "dio": p["di"] *= mult
                elif param_map[label] == "dso": p["ds"] *= mult
            
            r, _, o, _, _, _, _, _ = run_engine(p["s"], p["g"], p["di"], p["ds"], dpo)
            val = r if z_label == "ROE (%)" else o
            row.append(val / scale_factor)
        sens_data.append(row)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(sens_data, annot=True, fmt=".1f", cmap="RdYlGn",
                xticklabels=[f"{int(s*100)}%" for s in steps],
                yticklabels=[f"{int(s*100)}%" for s in steps], ax=ax)
    ax.set_title(f"Strategic Impact: {z_label} (Unit: {unit_label})")
    ax.set_xlabel(f"{x_label} Variance")
    ax.set_ylabel(f"{y_label} Variance")
    st.pyplot(fig)

    # --- Tornado Chart (English Optimized) ---
    st.subheader(f"🌪️ Strategic Leverage Ranking (Target: {z_label})")
    st.caption(f"Absolute impact on {z_label} per ±10% change")
    
    base_val = roe_v if z_label == "ROE (%)" else ocf_v
    
    t_scenarios = {
        "GM +10%": run_engine(actual_sales, min(final_gm*1.1, 1.0), final_dio, dso, dpo),
        "Sales +10%": run_engine(actual_sales*1.1, final_gm, final_dio, dso, dpo),
        "DIO -10%": run_engine(actual_sales, final_gm, final_dio*0.9, dso, dpo),
        "DSO -10%": run_engine(actual_sales, final_gm, final_dio, dso*0.9, dpo),
    }
    
    idx = 0 if z_label == "ROE (%)" else 2
    tornado_df = pd.DataFrame({
        "Factor": t_scenarios.keys(),
        "Impact": [(v[idx] - base_val) / scale_factor for v in t_scenarios.values()]
    }).sort_values(by="Impact")
    
    st.bar_chart(tornado_df.set_index("Factor"))

    # Strategic Diagnosis
    st.divider()
    st.subheader("🤖 Strategic Diagnosis Report")
    if achieve_rate < 0.8:
        st.warning(f"⚠️ **Sales Warning**: Achievement at {achieve_rate*100:.0f}%. Watch out for inventory write-downs.")
    if ocf_v < 0: 
        st.error(f"🚨 **Liquidity Crisis**: Negative OCF. Optimize DSO or extend DPO immediately.")
    elif roe_v > 15:
        st.success(f"🌟 **Strong Performance**: Optimal configuration for shareholder returns.")
