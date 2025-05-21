# 滾倉模擬器：手機最佳化 + PWA 主畫面功能 + AI 策略模擬平台 + 成長曲線圖解 + 倉位推進 + JSON 輸出儲存功能 + 多槓桿對比模擬

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import io
import random

st.set_page_config(
    page_title="策略滾倉模擬器 App",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="apple-touch-icon" sizes="512x512" href="https://raw.githubusercontent.com/pbo88/rolling-strategy-simulator/main/icon512.png">
    <link rel="manifest" href="https://raw.githubusercontent.com/pbo88/rolling-strategy-simulator/main/manifest.json">
""", unsafe_allow_html=True)

st.title("📊 策略分享型：多幣種滾倉模擬平台（手機版最佳化）")

st.markdown("""
這是一個策略模擬與分享平台，你可以：
- 試算槓桿與價格區間
- 加倉邏輯調整
- 自動推演資金成長
- 查看資金與倉位推進圖
- 多組槓桿資金成長對比
- AI 分析風險與提供建議
- 匯出/載入你的專屬策略 JSON
""")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("策略參數輸入")
    strategy_name = st.text_input("策略名稱", value="我的浮盈加倉策略")
    note = st.text_area("策略說明 / 備註", value="這是一套浮盈 20% 就加倉 50% 的螺旋成長策略")

    coin = st.selectbox("選擇幣種", ["BTC", "ETH", "SOL", "TON", "PROMP"])
    original_margin = st.number_input("原始保證金 (USDT)", value=100, step=10)
    profit = st.number_input("浮盈 (USDT)", value=0, step=10)
    total_margin = original_margin + profit

    min_price = st.number_input("最低模擬價格 (該幣種)", value=100, step=10)
    max_price = st.number_input("最高模擬價格 (該幣種)", value=1000, step=50)
    price_step = st.number_input("價格間隔", value=100, step=10)

    leverage_full_range = list(range(1, 101))
    leverage_labels = [
        f"{x}x ⚠️高風險" if x > 50 else (f"{x}x 🟡中風險" if x > 20 else f"{x}x ✅穩健")
        for x in leverage_full_range
    ]
    leverage_map = dict(zip(leverage_labels, leverage_full_range))
    default_labels = [leverage_labels[9], leverage_labels[19]]
    selected_labels = st.multiselect("選擇模擬槓桿（含風險提示）", leverage_labels, default=default_labels)
    leverage_options = [leverage_map[label] for label in selected_labels]

    add_trigger_pct = st.slider("每浮盈多少%加倉", 5, 100, 20, step=5)
    add_ratio = st.slider("每次加倉比例（對目前倉位）", 10, 100, 50, step=10)
    average_gain_pct = st.slider("每輪平均獲利 (%)", min_value=5, max_value=100, value=30, step=5)
    growth_target = st.number_input("目標金額 (USDT)", value=100000)

    st.markdown("---")
    st.download_button(
        label="💾 儲存策略 JSON",
        file_name=f"{strategy_name}.json",
        mime="application/json",
        data=json.dumps({
            "策略名稱": strategy_name,
            "幣種": coin,
            "原始保證金": original_margin,
            "浮盈": profit,
            "價格區間": [min_price, max_price, price_step],
            "槓桿選項": leverage_options,
            "浮盈加倉觸發%": add_trigger_pct,
            "加倉比例%": add_ratio,
            "平均獲利%": average_gain_pct,
            "目標資金": growth_target,
            "備註": note
        }, ensure_ascii=False)
    )

# --- 多組槓桿對比模擬 ---
st.subheader("📊 多組槓桿資金成長對比圖")
compare_df = pd.DataFrame()
for lev in leverage_options:
    capital = total_margin
    growth_rate = average_gain_pct / 100
    round_count = 0
    capital_track = []
    while capital < growth_target and round_count < 100:
        round_count += 1
        capital += capital * growth_rate
        capital_track.append(capital)
    compare_df[f"{lev}x"] = pd.Series(capital_track)

if not compare_df.empty:
    st.line_chart(compare_df)

# --- AI 風險評估區塊 ---
st.subheader("🤖 AI 策略風險分析與建議")
risk_score = average_gain_pct + add_ratio + (100 if max(leverage_options) > 50 else 0)
if risk_score < 100:
    st.markdown("### 🔵 風險等級：低")
    st.info("此策略偏向穩健，適合長期滾倉與複利增長。")
elif risk_score < 180:
    st.markdown("### 🟡 風險等級：中")
    st.warning("此策略風險與報酬平衡，建議搭配風控規劃與回測。")
else:
    st.markdown("### 🔴 風險等級：高")
    st.error("此策略風險偏高，槓桿與加倉頻率可能導致爆倉，請務必審慎使用。")
