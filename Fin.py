import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 頁面配置
st.set_page_config(page_title="價值鏈終極戰略塔", layout="wide")
st.title("🛡️ 財務工程：價值鏈全數據閉環與自動診斷系統")

# 修復中文字體
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False 

# 2. 側邊欄設定
st.sidebar.header("📦 期初營運數據")
beg_inv = st.sidebar.number_input("上期期末存貨", value=1200000)
beg_ar = st.sidebar.number_input("上期應收帳款", value=1800000)
beg_ap = st.sidebar.number_input("上期應付帳款", value=1000000)

st.sidebar.header("⚠️ 風險與非現金設定")
obs_rate = st.sidebar.slider("存貨年跌價率 (%)", 0, 30, 5) / 100
bad_debt_rate = st.sidebar.slider("應收壞帳率 (%)", 0, 15, 2) / 100
depreciation = st.sidebar.number_input("本期折舊費用", value=400000)

st.sidebar.header("🏦 財務架構")
equity = st.sidebar.number_input("股東權益 (Equity)", value=5000000)
initial_cash = st.sidebar.number_input("期初現金餘額", value=1500000)
debt_rate = st.sidebar.slider("短期貸款利率 (%)", 1, 15, 7) / 100

# 3. 主畫面營運設定
c1, c2, c3 = st.columns(3)
annual_sales = c1.number_input("年度營收目標", value=18000000)
gross_margin = c2.slider("產品毛利率 (%)", 10, 60, 35) / 100
fixed_assets = c3.number_input("固定資產淨值", value=3500000)

st.divider()
g1, g2, g3 = st.columns(3)
dio = g1.slider("目標庫存天數 (DIO)", 20, 180, 75)
dso = g2.slider("應收天數 (DSO)", 15, 120, 50)
dpo = g3.slider("應付天數 (DPO)", 15, 120, 45)

# --- 4. 核心運算函數 (支持參數輸入以供熱圖調用) ---
def core_engine(s_dio, s_dso):
    daily_sales = annual_sales / 365
    daily_cogs = (annual_sales * (1 - gross_margin)) / 365
    end_inv = daily_cogs * s_dio
    end_ar = daily_sales * s_dso
    end_ap = daily_cogs * dpo
    
    wc_change = (end_inv - beg_inv) + (end_ar - beg_ar) - (end_ap - beg_ap)
    inventory_loss = end_inv * obs_rate
    bad_debt_loss = end_ar * bad_debt_rate
    
    ebitda = annual_sales * (gross_margin - 0.12)
    ebit = ebitda - depreciation - inventory_loss - bad_debt_loss
    
    wc_needed = end_inv + end_ar - end_ap
    loan = max(0, wc_needed - initial_cash)
    interest = loan * debt_rate
    
    icr = ebit / interest if interest > 0 else 999.0
    ni = max(0, (ebit - interest) * (1 - 0.2))
    
    roe = (ni / equity) * 100
    roic = (ebit * (1 - 0.2) / (end_inv + fixed_assets)) * 100
    ocf = ni + depreciation - wc_change
    f_cash = initial_cash + ocf
    
    return roe, roic, ocf, f_cash, loan, interest, icr, inventory_loss, ni

# --- 5. 執行主面板運算 ---
roe_val, roic_val, ocf_val, cash_val, loan_val, int_val, icr_val, inv_l, ni_val = core_engine(dio, dso)

# --- 6. 指標面板顯示 ---
st.divider()
st.subheader("📈 價值鏈核心指標")
m1, m2, m3, m4 = st.columns(4)
m1.metric("ROE (股東報酬)", f"{roe_val:.2f}%")
m2.metric("ROIC (經營效率)", f"{roic_val:.2f}%")
m3.metric("營業現金流 (OCF)", f"${ocf_val:,.0f}")
m4.metric("利息保障倍數 (ICR)", f"{icr_val:.2f}")

st.divider()
st.subheader("💰 生存監控數據")
k1, k2, k3 = st.columns(3)
k1.metric("預估期末現金", f"${cash_val:,.0f}")
k2.metric("自動融資需求", f"${loan_val:,.0f}")
k3.metric("年度利息支出", f"-${int_val:,.0f}")

# --- 7. 自動戰略診斷報告 ---
st.divider()
st.subheader("🤖 數位孿生：自動戰略診斷報告")
has_alert = False

if ocf_val < 0:
    st.error(f"🚨 **流動性危機**：本期營運現金流為負 (${ocf_val:,.0f})。")
    has_alert = True
if icr_val < 1.5:
    st.error(f"🚨 **財務安全預警**：利息保障倍數僅 {icr_val:.2f}。")
    has_alert = True
if inv_l > (ni_val * 0.2):
    st.warning(f"⚠️ **資產減損風險**：存貨跌價損失 (${inv_l:,.0f}) 已侵蝕超過 20% 淨利。")
    has_alert = True
if not has_alert:
    st.success("🌟 **診斷結果**：目前價值鏈運作健康，指標皆在安全範圍。")

# --- 8. 戰略熱圖 (修正循環調用) ---
st.divider()
st.subheader("🔥 戰略壓力測試：DIO 與 DSO 對 ROE 的影響")

dio_range = np.linspace(30, 180, 10)
dso_range = np.linspace(30, 120, 10)
roe_matrix = []

for s_dso in dso_range:
    row = []
    for s_dio in dio_range:
        # 調用核心引擎計算矩陣點
        m_roe, _, _, _, _, _, _, _, _ = core_engine(s_dio, s_dso)
        row.append(m_roe)
    roe_matrix.append(row)

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(roe_matrix, annot=True, fmt=".1f", cmap="RdYlGn",
            xticklabels=[int(x) for x in dio_range],
            yticklabels=[int(y) for y in dso_range], ax=ax)
ax.set_xlabel("庫存天數 (DIO)")
ax.set_ylabel("應收天數 (DSO)")
st.pyplot(fig)
