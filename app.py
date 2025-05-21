# 滾倉模擬器：策略分享型互動平台

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import io

st.set_page_config(page_title="策略分享滾倉模擬器", layout="wide")

st.title("📊 策略分享型：多幣種滾倉模擬平台")

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

    leverage_options = st.multiselect("選擇模擬槓桿", [3, 5, 10, 15, 20, 25], default=[10, 20])
    add_trigger_pct = st.slider("每浮盈多少%加倉", 5, 100, 20, step=5)
    add_ratio = st.slider("每次加倉比例（對目前倉位）", 10, 100, 50, step=10)
    average_gain_pct = st.slider("每輪平均獲利 (%)", min_value=5, max_value=100, value=30, step=5)
    growth_target = st.number_input("目標金額 (USDT)", value=100000)

# 儲存策略
if st.button("📥 儲存策略 JSON"):
    strategy = {
        "strategy_name": strategy_name,
        "note": note,
        "coin": coin,
        "original_margin": original_margin,
        "profit": profit,
        "min_price": min_price,
        "max_price": max_price,
        "price_step": price_step,
        "leverage_options": leverage_options,
        "add_trigger_pct": add_trigger_pct,
        "add_ratio": add_ratio,
        "average_gain_pct": average_gain_pct,
        "growth_target": growth_target
    }
    st.download_button("下載 JSON 檔案", json.dumps(strategy), file_name=f"{strategy_name}.json")

# 載入策略
uploaded_file = st.file_uploader("📤 載入策略 JSON 檔案")
if uploaded_file is not None:
    strategy_data = json.load(uploaded_file)
    st.session_state.update(strategy_data)
    st.success("✅ 策略已載入，可重新整理頁面以套用參數")

# --- 模擬運算（略，保留原本模擬邏輯） ---
# 建議將原本「計算」、「圖表」、「成長模擬」、「浮盈加倉模擬」區塊保留

st.markdown("""
📘 你可以將策略下載並分享給朋友，或載入舊策略進行編輯與回測。
""")
