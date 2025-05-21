
# 滾倉模擬器：手機最佳化 + PWA 主畫面功能 + AI 策略模擬平台 + 成長曲線圖解

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
這是一個策略模擬與分享平台，你可以試算槓桿與價格區間，加倉邏輯、自動推演資金成長，並儲存／載入你的專屬策略。
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
    selected_labels = st.multiselect("選擇模擬槓桿（含風險提示）", leverage_labels, default=["10x ✅穩健", "20x 🟡中風險"])
    leverage_options = [leverage_map[label] for label in selected_labels]

    add_trigger_pct = st.slider("每浮盈多少%加倉", 5, 100, 20, step=5)
    add_ratio = st.slider("每次加倉比例（對目前倉位）", 10, 100, 50, step=10)
    average_gain_pct = st.slider("每輪平均獲利 (%)", min_value=5, max_value=100, value=30, step=5)
    growth_target = st.number_input("目標金額 (USDT)", value=100000)

# --- 成長曲線模擬區塊 ---
st.subheader("📈 滾倉資金成長模擬")

if st.button("模擬資金成長曲線"):
    capital = total_margin
    target = growth_target
    growth_rate = average_gain_pct / 100
    history = []
    lot_history = []
    round_count = 0
    position_size = 1.0  # 初始倉位假設為 1（單位數量）

    while capital < target and round_count < 100:
        round_count += 1
        profit = capital * growth_rate
        capital += profit

        # 倉位推進模擬
        lot_added = position_size * (add_ratio / 100)
        position_size += lot_added
        push_ratio = round(lot_added / position_size * 100, 2)

        history.append({"輪數": round_count, "累積資金": round(capital, 2), "本輪獲利": round(profit, 2)})
        lot_history.append({"輪數": round_count, "本輪新增倉位": round(lot_added, 4), "累積倉位": round(position_size, 4), "推進比率(%)": push_ratio})

    df = pd.DataFrame(history)
    lot_df = pd.DataFrame(lot_history)

    st.line_chart(df.set_index("輪數")["累積資金"])
    st.dataframe(df)
    st.markdown("---")
    st.subheader("📦 倉位推進明細")
    st.dataframe(lot_df)

    st.success(f"預估約需 {round_count} 輪操作可達成 {target:,} USDT 目標資金。")
