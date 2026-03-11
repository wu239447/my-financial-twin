import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# 1. 頁面配置
st.set_page_config(page_title="價值鏈終極戰略塔", layout="wide")
st.title("🛡️ 財務-運籌數位孿生：全數據閉環監控系統")

# 中文字體設定
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'SimHei', 'DejaVu Sans', 'Arial'] 
plt.rcParams['axes.unicode_minus'] = False 

# --- 側邊欄：全域財務與期初營運數據 (生命線設定) ---
st.sidebar.header("🏦 全域財務設定")
equity = st.sidebar.number_input("股東權益 (Equity)", value=5000000)
initial_cash = st.sidebar.number_input("期初現金餘額", value=1500000)
debt_rate = st.sidebar.slider("短期貸款利率 (%)", 1, 20, 8) / 100
depreciation = st.sidebar.number_input("本期折舊費用", value=400000)
tax_rate = 0.2

st.sidebar.header("📦 期初營運數據 (上期結轉)")
beg_inv = st.sidebar.number_input("上期期末存貨 (Beg Inv)", value=1200000)
beg_ar = st.sidebar.number_input("上期應收帳款 (Beg AR)", value=1800000)
beg_ap = st.sidebar.number_input("上期應付帳款 (Beg AP)", value=1000000)

st.sidebar.header("⚠️ 風險損耗設定")
obs_rate = st.sidebar.slider("存貨年跌價率 (%)", 0, 30, 5) / 100
bad_debt_rate = st.sidebar.slider("應收壞帳率 (%)", 0, 15, 2) / 100

# --- 建立分頁 ---
tab1, tab2 = st.tabs(["🔮 AI 銷售預測中心", "📊 財務工程控制塔"])

# --- 分頁一：AI 銷售預測中心 ---
with tab1:
    st.header("🔮 多品項 AI 銷售預測 (含季節性偵測)")
    
    default_data = {
        "品項": ["高階產品 A", "大眾產品 B", "基礎零件 C"],
        "歷史月營收(萬/月)": [
            "100,110,105,120,130,140,150,160,155,175,190,200",
            "50,55,52,60,65,70,68,75,80,85,90,95",
            "30,31,30,32,33,35,34,36,37,38,39,40"
        ],
        "是否為季節性": [True, False, False],
        "預計毛利率(%)": [45, 30, 20],
        "預計庫存天數(DIO)": [90, 60, 45]
    }
    edited_df = st.data_editor(pd.DataFrame(default_data), num_rows="dynamic")

    total_annual_sales = 0
    wavg_gm = 0
    wavg_dio = 0
    item_results = []

    for _, row in edited_df.iterrows():
        try:
            h_data = [float(x.strip()) * 10000 for x in str(row["歷史月營收(萬/月)"]).split(",")]
            if row["是否為季節性"]:
                model = ExponentialSmoothing(h_data, trend='add', seasonal='add', seasonal_periods=4).fit()
            else:
                model = ExponentialSmoothing(h_data, trend='add', seasonal=None).fit()
            
            ann_pred = float(model.forecast(1)) * 12
            total_annual_sales += ann_pred
            item_results.append({"品項": row["品項"], "預測年營收": ann_pred, "GM": row["預計毛利率(%)"]/100, "DIO": row["預計庫存天數(DIO)"]})
        except: continue

    if total_annual_sales > 0:
        for item in item_results:
            weight = item["預測年營收"] / total_annual_sales
            wavg_gm += item["GM"] * weight
            wavg_dio += item["DIO"] * weight
        st.bar_chart(pd.DataFrame(item_results).set_index("品項")["預測年營收"])
        st.success(f"✅ AI 預測完成：綜合年度營收目標為 **${total_annual_sales:,.0f}**")
    else:
        total_annual_sales, wavg_gm, wavg_dio = 15000000, 0.30, 60

# --- 分頁二：財務工程控制塔 ---
with tab2:
    st.header("📊 財務-運籌價值鏈聯動與生存監控")
    
    c1, c2, c3 = st.columns(3)
    final_sales = c1.number_input("年度營收目標", value=int(total_annual_sales))
    final_gm = c2.slider("綜合毛利率 (%)", 5, 60, int(wavg_gm*100)) / 100
    final_dio = c3.slider("綜合庫存天數 (DIO)", 10, 200, int(wavg_dio))
    
    st.divider()
    g1, g2 = st.columns(2)
    dso = g1.slider("應收天數 (DSO)", 15, 150, 60)
    dpo = g2.slider("應付天數 (DPO)", 15, 150, 45)

    def run_engine(s_sales, s_gm, s_dio, s_dso):
        daily_sales = s_sales / 365
        daily_cogs = (s_sales * (1 - s_gm)) / 365
        e_inv, e_ar, e_ap = daily_cogs * s_dio, daily_sales * s_dso, daily_cogs * dpo
        
        # 損益與隱形成本
        inv_loss = e_inv * obs_rate
        ar_loss = e_ar * bad_debt_rate
        ebit = (s_sales * (s_gm - 0.12)) - depreciation - inv_loss - ar_loss
        
        # 融資需求與現金流閉環
        wc_end = e_inv + e_ar - e_ap
        loan = max(0, wc_end - initial_cash)
        interest = loan * debt_rate
        ni = max(0, (ebit - interest) * (1 - tax_rate))
        
        # 核心指標
        roe = (ni / equity) * 100
        roic = (ebit * (1 - tax_rate) / (e_inv + 3000000)) * 100
        icr = ebit / interest if interest > 0 else 999
        
        # 營運現金流 (含期初結轉)
        wc_change = (e_inv - beg_inv) + (e_ar - beg_ar) - (e_ap - beg_ap)
        ocf = ni + depreciation - wc_change
        f_cash = initial_cash + ocf
        
        return roe, roic, ocf, icr, f_cash, loan, interest, wc_change

    # 執行運算
    roe_v, roic_v, ocf_v, icr_v, f_cash_v, loan_v, int_v, wc_c_v = run_engine(final_sales, final_gm, final_dio, dso)

    # --- 關鍵績效指標 ---
    st.subheader("📈 價值鏈核心 KPI")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("ROE (股東回報)", f"{roe_v:.2f}%")
    m2.metric("ROIC (經營效率)", f"{roic_v:.2f}%")
    m3.metric("OCF (營運現金流)", f"${ocf_v:,.0f}")
    m4.metric("利息保障倍數 (ICR)", f"{icr_v:.2f}")

    # --- 補回：生存監控數據區塊 ---
    st.divider()
    st.subheader("💰 生存監控與營運資金數據")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("期末預估現金", f"${f_cash_v:,.0f}")
    k2.metric("自動融資需求", f"${loan_v:,.0f}")
    k3.metric("年度利息支出", f"-${int_v:,.0f}")
    k4.metric("營運資金淨變動", f"-${wc_c_v:,.0f}", help="負值代表現金被資產增長吸走")

    # 戰略診斷
    st.divider()
    st.subheader("🤖 自動戰略診斷報告")
    if ocf_v < 0: st.error(f"🚨 **流動性危機**：現金正在流失 (${ocf_v:,.0f})")
    if icr_v < 1.5: st.error(f"🚨 **財務安全預警**：利息負擔過重")
    if not (ocf_v < 0 or icr_v < 1.5): st.success("🌟 目前價值鏈狀態良好。")

    # 熱圖
    st.divider()
    st.subheader("🔥 戰略熱圖：DIO 與 DSO 對 ROE 的影響")
    dio_r = np.linspace(30, 180, 10)
    dso_r = np.linspace(30, 120, 10)
    matrix = [[run_engine(final_sales, final_gm, d, s)[0] for d in dio_r] for s in dso_r]
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(matrix, annot=True, fmt=".1f", cmap="RdYlGn", xticklabels=[int(x) for x in dio_r], yticklabels=[int(y) for y in dso_r], ax=ax)
    ax.set_xlabel("庫存天數 (DIO)")
    ax.set_ylabel("應收天數 (DSO)")
    st.pyplot(fig)
