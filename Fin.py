import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing


# 1. 頁面配置
st.set_page_config(page_title="價值鏈終極戰略塔", layout="wide")
st.title("🛡️ 財務-運籌數位孿生：全維度戰略監控塔")

# 字體設定 (針對不同系統做相容)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'Arial'] 
plt.rcParams['axes.unicode_minus'] = False 

# --- 側邊欄：全域財務與期初數據 ---
st.sidebar.header("🏦 全域財務設定")
equity = st.sidebar.number_input("股東權益 (Equity)", value=5000000)
initial_cash = st.sidebar.number_input("期初現金餘額", value=1500000)
debt_rate = st.sidebar.slider("貸款利率 (%)", 1, 20, 8) / 100
depreciation = st.sidebar.number_input("本期折舊費用", value=400000)
tax_rate = 0.2

st.sidebar.header("📦 期初營運數據 (上期結轉)")
beg_inv = st.sidebar.number_input("上期期末存貨 (Beg Inv)", value=1200000)
beg_ar = st.sidebar.number_input("上期應收帳款 (Beg AR)", value=1800000)
beg_ap = st.sidebar.number_input("上期應付帳款 (Beg AP)", value=1000000)

st.sidebar.header("⚠️ 風險損耗設定")
obs_rate = st.sidebar.slider("存貨年跌價率 (%)", 0, 30, 5) / 100
bad_debt_rate = st.sidebar.slider("應收壞帳率 (%)", 0, 15, 2) / 100

# --- 核心運算引擎 ---
def run_engine(s_sales, s_gm, s_dio, s_dso, s_dpo):
    daily_sales = s_sales / 365
    daily_cogs = (s_sales * (1 - s_gm)) / 365
    e_inv, e_ar, e_ap = daily_cogs * s_dio, daily_sales * s_dso, daily_cogs * s_dpo
    
    # 損益計算
    ebit = (s_sales * (s_gm - 0.12)) - depreciation - (e_inv * obs_rate) - (e_ar * bad_debt_rate)
    loan = max(0.0, (e_inv + e_ar - e_ap) - initial_cash)
    interest = loan * debt_rate
    ni = max(0.0, (ebit - interest) * (1 - tax_rate))
    
    # 指標
    roe = (ni / equity) * 100 if equity > 0 else 0
    roic = (ebit * (1 - tax_rate) / max((e_inv + 3000000), 1)) * 100
    icr = ebit / max(interest, 0.0001)
    
    # 現金流
    wc_change = (e_inv - beg_inv) + (e_ar - beg_ar) - (e_ap - beg_ap)
    ocf = ni + depreciation - wc_change
    f_cash = initial_cash + ocf
    return roe, roic, ocf, icr, f_cash, loan, interest, wc_change

# --- 分頁系統 ---
tab1, tab2 = st.tabs(["🔮 AI 銷售預測中心", "📊 財務工程控制塔"])

# --- Tab 1: AI 預測 ---
with tab1:
    st.header("🔮 多品項 AI 銷售預測")
    default_data = {
        "品項": ["高階產品 A", "大眾產品 B", "基礎零件 C"],
        "歷史月營收(萬/月)": [
            "100,110,105,120,130,140,150,160,155,170,185,200",
            "50,55,52,60,65,70,68,75,80,85,90,95",
            "30,31,30,32,33,35,34,36,37,38,39,40"
        ],
        "是否為季節性": [True, False, False],
        "預計毛利率(%)": [40, 25, 15],
        "預計庫存天數(DIO)": [90, 60, 45]
    }
    edited_df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

    total_annual_sales = 0
    wavg_gm, wavg_dio = 0, 0
    item_results = []

    for _, row in edited_df.iterrows():
        try:
            h_data = [float(x.strip()) * 10000 for x in str(row["歷史月營收(萬/月)"]).split(",")]
            if row["是否為季節性"]:
                model = ExponentialSmoothing(h_data, trend='add', seasonal='add', seasonal_periods=4).fit()
            else:
                model = ExponentialSmoothing(h_data, trend='add', seasonal=None).fit()
            ann_pred = float(model.forecast(1).iloc[0]) * 12
            total_annual_sales += ann_pred
            item_results.append({
                "品項": row["品項"], 
                "預測年營收": ann_pred, 
                "GM": row["預計毛利率(%)"]/100, 
                "DIO": row["預計庫存天數(DIO)"]
            })
        except: continue

    if total_annual_sales > 0:
        for item in item_results:
            weight = item["預測年營收"] / total_annual_sales
            wavg_gm += item["GM"] * weight
            wavg_dio += item["DIO"] * weight
        st.bar_chart(pd.DataFrame(item_results).set_index("品項")["預測年營收"])
        st.success(f"✅ AI 預估年度營收目標為 **${total_annual_sales:,.0f}**")
    else:
        total_annual_sales, wavg_gm, wavg_dio = 15000000, 0.30, 60

# --- Tab 2: 財務控制塔 ---
with tab2:
    st.header("📊 價值鏈聯動與壓力測試")
    
    achieve_rate = st.slider("🎯 銷售達成率壓力測試 (%)", 50, 150, 100) / 100
    
    c1, c2, c3 = st.columns(3)
    base_sales = c1.number_input("AI 預測基礎營收", value=int(total_annual_sales))
    actual_sales = base_sales * achieve_rate
    st.caption(f"📢 當前壓力測試下的實際營收: ${actual_sales:,.0f}")
    
    final_gm = c2.slider("綜合毛利率 (%)", 5, 60, int(wavg_gm*100)) / 100
    final_dio = c3.slider("庫存天數 (DIO)", 10, 200, int(wavg_dio))
    
    st.divider()
    g1, g2 = st.columns(2)
    dso = g1.slider("應收天數 (DSO)", 15, 150, 60)
    dpo = g2.slider("應付天數 (DPO)", 15, 150, 45)

    # 執行主運算
    roe_v, roic_v, ocf_v, icr_v, f_cash_v, loan_v, int_v, wc_c_v = run_engine(actual_sales, final_gm, final_dio, dso, dpo)

    # --- 顯示 KPI ---
    st.subheader("📈 關鍵績效指標 (KPI)")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ROE (股東回報)", f"{roe_v:.2f}%")
    m2.metric("ROIC (經營效率)", f"{roic_v:.2f}%")
    m3.metric("OCF (營運現金流)", f"${ocf_v:,.0f}")
    m4.metric("利息保障倍數 (ICR)", f"{icr_v:.2f}")

    # --- 生存監控數據 ---
    st.divider()
    st.subheader("💰 生存監控與營運資金")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("期末預估現金", f"${f_cash_v:,.0f}")
    k2.metric("自動融資需求", f"${loan_v:,.0f}")
    k3.metric("年度利息支出", f"-${int_v:,.0f}")
    k4.metric("營運資金淨變動", f"-${wc_c_v:,.0f}")

    # --- 敏感度分析區塊 (優化單位) ---
    st.divider()
    st.subheader("🎯 多維度敏感度分析")
    
    param_map = {
        "銷售達成率": "achieve",
        "綜合毛利率": "gm",
        "庫存天數 (DIO)": "dio",
        "應收天數 (DSO)": "dso"
    }
    
    sc1, sc2, sc3 = st.columns(3)
    x_label = sc1.selectbox("選擇橫軸 (X-axis)", list(param_map.keys()), index=2)
    y_label = sc2.selectbox("選擇縱軸 (Y-axis)", list(param_map.keys()), index=1)
    z_label = sc3.selectbox("監控目標 (Z-axis)", ["ROE (%)", "營運現金流 (OCF)"])

    # 單位轉換係數 (ROE保持不變, OCF轉為萬元)
    scale_factor = 1.0 if z_label == "ROE (%)" else 10000.0
    unit_label = "%" if z_label == "ROE (%)" else "萬元"

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
    ax.set_title(f"戰略交叉影響：{z_label} (單位：{unit_label})")
    ax.set_xlabel(f"{x_label} 變動幅度")
    ax.set_ylabel(f"{y_label} 變動幅度")
    st.pyplot(fig)

    # --- 龍捲風圖 (同步目標與單位) ---
    st.subheader(f"🌪️ 戰略槓桿影響力排序 (目標：{z_label})")
    st.caption(f"分析各因子變動 ±10% 對 {z_label} 的絕對影響量")
    
    base_val = roe_v if z_label == "ROE (%)" else ocf_v
    
    t_scenarios = {
        "毛利率提升 10%": run_engine(actual_sales, min(final_gm*1.1, 1.0), final_dio, dso, dpo),
        "營收提升 10%": run_engine(actual_sales*1.1, final_gm, final_dio, dso, dpo),
        "DIO 下降 10%": run_engine(actual_sales, final_gm, final_dio*0.9, dso, dpo),
        "DSO 下降 10%": run_engine(actual_sales, final_gm, final_dio, dso*0.9, dpo),
    }
    
    idx = 0 if z_label == "ROE (%)" else 2
    tornado_df = pd.DataFrame({
        "因子": t_scenarios.keys(),
        "變化量": [(v[idx] - base_val) / scale_factor for v in t_scenarios.values()]
    }).sort_values(by="變化量")
    
    st.bar_chart(tornado_df.set_index("因子"))

    # 戰略診斷
    st.divider()
    st.subheader("🤖 自動戰略診斷報告")
    if achieve_rate < 0.8:
        st.warning(f"⚠️ **銷售低迷警報**：達成率僅 {achieve_rate*100:.0f}%，注意資產減損風險。")
    if ocf_v < 0: 
        st.error(f"🚨 **流動性危機**：營運現金流入不敷出。建議優先縮短 DSO 或延展 DPO。")
    elif roe_v > 15:
        st.success(f"🌟 **績效卓越**：目前的配置下股東回報相當理想。")

