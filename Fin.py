import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# 1. 頁面配置與字體設定
st.set_page_config(page_title="價值鏈戰略監控塔", layout="wide")
st.title("🛡️ 財務工程：價值鏈運籌與生存閉環監控系統")

# 修復中文字體顯示 (Windows 環境)
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei'] 
plt.rcParams['axes.unicode_minus'] = False 

# 2. 側邊欄：財務架構與資本設定
st.sidebar.header("🏦 財務架構與資本設定")
equity = st.sidebar.number_input("股東權益 (Equity)", value=5000000, step=100000)
initial_cash = st.sidebar.number_input("初始現金 (Initial Cash)", value=2000000, step=100000)
debt_rate = st.sidebar.slider("短期貸款年利率 (%)", 1, 20, 8) / 100
tax_rate = st.sidebar.slider("所得稅率 (%)", 0, 30, 20) / 100

st.sidebar.header("💱 信用與周轉政策")
dso = st.sidebar.slider("應收天數 (DSO - 收款時間)", 15, 120, 60)
dpo = st.sidebar.slider("應付天數 (DPO - 付款時間)", 15, 120, 45)

st.sidebar.header("🏭 營運固定資產")
fixed_assets = st.sidebar.number_input("固定資產 (PP&E)", value=3000000, step=1000000)

# 3. 主畫面：營運現況
st.subheader("📦 營運現況與產品價值鏈設定")
c1, c2 = st.columns(2)
annual_sales = c1.number_input("年度營收 (Revenue)", value=15000000, step=1000000)
avg_gross_margin = c2.slider("加權平均毛利率 (%)", 5, 60, 30) / 100
dio = st.slider("平均庫存周轉天數 (DIO)", 20, 180, 90)

# --- 4. 核心財務工程運算邏輯 (校準分母，防止數值爆炸) ---
def calculate_system_metrics(sales, gm, dio_val, dso_val, dpo_val, eq, cash, d_rate, tax, fa):
    # 分子：營收與利潤
    daily_sales = sales / 365
    daily_cogs = daily_sales * (1 - gm)
    ebit = sales * (gm - 0.15) # 假設 15% 營業費用率
    nopat = ebit * (1 - tax)
    
    # 分母：營運資產餘額 (時點數值，這是防止 ROA/ROIC 爆炸的關鍵)
    inv_balance = daily_cogs * dio_val
    ar_balance = daily_sales * dso_val
    ap_balance = daily_cogs * dpo_val
    
    # 現金流與融資
    wc_needed = inv_balance + ar_balance - ap_balance
    loan_amount = max(0, wc_needed - cash)
    interest_expense = loan_amount * d_rate
    net_income = (ebit - interest_expense) * (1 - tax)
    
    # 指標計算
    total_assets = inv_balance + ar_balance + fa + cash
    invested_capital = inv_balance + fa
    
    roe = (net_income / eq) * 100
    roa = (net_income / total_assets) * 100
    roic = (nopat / invested_capital) * 100
    ccc = dio_val + dso_val - dpo_val 
    
    return roe, roa, roic, ccc, wc_needed, loan_amount, interest_expense

# 執行計算
roe, roa, roic, ccc, wc, loan, interest = calculate_system_metrics(
    annual_sales, avg_gross_margin, dio, dso, dpo, equity, initial_cash, debt_rate, tax_rate, fixed_assets
)

# --- 5. 核心指標儀表板 ---
st.divider()
st.subheader("📈 資產回報與投資效率")
m1, m2, m3, m4 = st.columns(4)
m1.metric("ROE (股東權益報酬)", f"{roe:.2f}%")
m2.metric("ROA (資產報酬率)", f"{roa:.2f}%")
m3.metric("ROIC (投下資本回報率)", f"{roic:.2f}%")
m4.metric("現金循環週期 (CCC)", f"{ccc:.1f} 天")

# --- 6. 營運細節指標 ---
st.divider()
st.subheader("💰 營運資金與生存監控")
k1, k2, k3 = st.columns(3)
k1.metric("營運資金佔用 (WC)", f"${wc:,.0f}")
k2.metric("自動融資金額", f"${loan:,.0f}")
k3.metric("年度融資利息", f"${interest:,.0f}")

# --- 7. 戰略熱圖：ROE 敏感度分析 ---
st.divider()
st.subheader("🔥 價值鏈決策熱圖：DIO 與 DSO 對 ROE 的影響")

dio_range = np.linspace(30, 180, 10)
dso_range = np.linspace(30, 120, 10)
roe_matrix = []

for s_dso in dso_range:
    row = []
    for s_dio in dio_range:
        m_roe, _, _, _, _, _, _ = calculate_system_metrics(
            annual_sales, avg_gross_margin, s_dio, s_dso, dpo, equity, initial_cash, debt_rate, tax_rate, fixed_assets
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

st.info("💡 **戰略解讀**：ROIC 反映經營本質。如果 ROE 遠高於 ROIC，代表正利用財務槓桿放大回報；若 ROA 過低，需注意庫存或應收帳款是否太臃腫。")
