import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 頁面配置與環境設定
st.set_page_config(page_title="價值鏈終極戰略塔", layout="wide")
st.title("🛡️ 財務工程：價值鏈全數據閉環與利息安全監控系統")

# 修復中文字體 (Windows 環境)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False 

# 2. 側邊欄：完整期初數據 (資產負債表結轉)
st.sidebar.header("📦 期初營運數據 (上期結轉)")
beg_inv = st.sidebar.number_input("上期期末存貨 (Beg Inv)", value=1200000)
beg_ar = st.sidebar.number_input("上期應收帳款 (Beg AR)", value=1800000)
beg_ap = st.sidebar.number_input("上期應付帳款 (Beg AP)", value=1000000)

st.sidebar.header("⚠️ 風險與非現金設定")
obs_rate = st.sidebar.slider("存貨年跌價/損耗率 (%)", 0, 30, 5) / 100
bad_debt_rate = st.sidebar.slider("應收帳款壞帳率 (%)", 0, 15, 2) / 100
depreciation = st.sidebar.number_input("本期折舊費用 (Non-cash)", value=400000)

st.sidebar.header("🏦 財務架構與利息")
equity = st.sidebar.number_input("股東權益 (Equity)", value=5000000)
initial_cash = st.sidebar.number_input("期初現金餘額", value=1500000)
debt_rate = st.sidebar.slider("短期貸款利率 (%)", 1, 15, 7) / 100
tax_rate = 0.2

# 3. 主畫面：價值鏈核心營運設定
st.subheader("🏭 價值鏈營運與管制節點設定")
c1, c2, c3 = st.columns(3)
annual_sales = c1.number_input("年度營收目標 (Revenue)", value=18000000)
gross_margin = c2.slider("產品加權毛利率 (%)", 10, 60, 35) / 100
fixed_assets = c3.number_input("固定資產 (PP&E) 淨值", value=3500000)

# 營運管制節點
st.divider()
g1, g2, g3 = st.columns(3)
dio = g1.slider("目標庫存天數 (DIO)", 20, 180, 75)
dso = g2.slider("應收帳款天數 (DSO)", 15, 120, 50)
dpo = g3.slider("應付帳款天數 (DPO)", 15, 120, 45)

# --- 4. 核心財務工程：全數據閉環運算邏輯 ---
def calculate_master_metrics(sales, gm, d_io, d_so, d_po, eq, cash, d_rate, tax, fa, b_inv, b_ar, b_ap, depr, o_rate, bd_rate):
    # A. 營運基礎數據
    daily_sales = sales / 365
    daily_cogs = (sales * (1 - gm)) / 365
    
    # B. 期末營運資產與負債餘額
    end_inv = daily_cogs * d_io
    end_ar = daily_sales * d_so
    end_ap = daily_cogs * d_po
    
    # C. 營運資金變動 (WC Change)
    wc_change = (end_inv - b_inv) + (end_ar - b_ar) - (end_ap - b_ap)
    
    # D. 隱形成本與利潤 (EBIT)
    inventory_loss = end_inv * o_rate
    bad_debt_loss = end_ar * bd_rate
    ebitda = sales * (gm - 0.12) # 假設 12% 營運費用
    ebit = ebitda - depr - inventory_loss - bad_debt_loss
    
    # E. 融資與利息
    total_wc_needed = end_inv + end_ar - end_ap
    loan_needed = max(0, total_wc_needed - cash)
    interest_exp = loan_needed * d_rate
    
    # F. 利息保障倍數 (ICR) = EBIT / 利息
    icr = ebit / interest_exp if interest_exp > 0 else 999.0
    
    # G. 最終獲利與指標
    net_income = max(0, (ebit - interest_exp) * (1 - tax))
    nopat = ebit * (1 - tax)
    ocf = net_income + depr - wc_change # 營業現金流
    final_cash = cash + ocf
    
    roe = (net_income / eq) * 100
    total_assets = end_inv + end_ar + (fa - depr) + final_cash
    roa = (net_income / total_assets) * 100
    roic = (nopat / (end_inv + fa)) * 100
    
    return roe, roa, roic, ocf, final_cash, loan_needed, interest_exp, icr, wc_change

# 執行計算
roe, roa, roic, ocf, f_cash, loan, interest, icr, wc_c = calculate_master_metrics(
    annual_sales, gross_margin, dio, dso, dpo, equity, initial_cash, debt_rate, tax_rate, fixed_assets, beg_inv, beg_ar, beg_ap, depreciation, obs_rate, bad_debt_rate
)

# --- 5. 指標儀表板 ---
st.divider()
st.subheader("📈 價值鏈核心指標 (含利息安全監控)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("ROE (股東回報)", f"{roe:.2f}%")
m2.metric("ROIC (經營獲利)", f"{roic:.2f}%")
m3.metric("營業現金流 (OCF)", f"${ocf:,.0f}")

# 利息保障倍數 (ICR) 顏色預警
if icr > 3.0:
    m4.metric("利息保障倍數 (ICR)", f"{icr:.2f}", delta="安全", delta_color="normal")
elif icr > 1.5:
    m4.metric("利息保障倍數 (ICR)", f"{icr:.2f}", delta="警告", delta_color="off")
else:
    m4.metric("利息保障倍數 (ICR)", f"{icr:.2f}", delta="危險", delta_color="inverse")

# --- 6. 營運與生存監控 ---
st.divider()
st.subheader("💰 現金流與生存監控詳細數據")
k1, k2, k3, k4 = st.columns(4)
k1.metric("期末預估現金", f"${f_cash:,.0f}")
k2.metric("營運資金變動", f"-${wc_c:,.0f}", help="負值代表現金流失至資產中")
k3.metric("自動融資需求", f"${loan:,.0f}")
k4.metric("年度利息支出", f"-${interest:,.0f}")

# --- 7. 戰略洞察 ---
st.info(f"💡 **戰略導讀**：當前模式產生了 **${interest:,.0f}** 的利息，佔營業利潤 (EBIT) 的 **{100/icr if icr>0 else 0:.1f}%**。您的利息保障倍數為 **{icr:.2f}**，這代表您的經營獲利覆蓋債務利息的能力。")

# --- 8. 戰略熱圖：DIO 與 DSO 對 ROE 的影響 ---
st.subheader("🔥 戰略壓力測試：周轉效率對 ROE 的真實衝擊")
dio_range = np.linspace(30, 180, 10)
dso_range = np.linspace(30, 120, 10)
roe_matrix = []

for s_dso in dso_range:
    row = []
    for s_dio in dio_range:
        m_roe, _, _, _, _, _, _, _, _ = calculate_master_metrics(
            annual_sales, gross_margin, s_dio, s_dso, dpo, equity, initial_cash, debt_rate, tax_rate, fixed_assets, beg_inv, beg_ar, beg_ap, depreciation, obs_rate, bad_debt_rate
        )
        row.append(m_roe)
    roe_matrix.append(row)

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(roe_matrix, annot=True, fmt=".1f", cmap="RdYlGn",
            xticklabels=[int(x) for x in dio_range],
            yticklabels=[int(y) for y in dso_range], ax=ax)
ax.set_xlabel("庫存天數 (DIO)")
ax.set_ylabel("應收天數 (DSO)")
st.pyplot(fig)
