# 滾倉模擬器：策略分享型互動平台 + AI 策略分析建議 + AI 優化建議生成 + AI 自動生成策略

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import io
import random

st.set_page_config(page_title="策略分享滾倉模擬器", layout="wide")

st.title("📊 策略分享型：多幣種滾倉模擬平台")

st.markdown("""
這是一個策略模擬與分享平台，你可以試算槓桿與價格區間，加倉邏輯、自動推演資金成長，並儲存／載入你的專屬策略。
""")

# --- AI 自動生成策略 ---
st.subheader("✨ AI 自動生成策略")

if st.button("🧠 產生新策略建議"):
    gen_strategy = {
        "strategy_name": f"AI 策略 {random.randint(1000, 9999)}",
        "note": "由 AI 根據穩健收益與低風險自動生成的策略",
        "coin": random.choice(["BTC", "ETH", "SOL", "TON", "PROMP"]),
        "original_margin": random.choice([50, 100, 200]),
        "profit": 0,
        "min_price": 100,
        "max_price": 1000,
        "price_step": 100,
        "leverage_options": [random.choice([5, 10])],
        "add_trigger_pct": random.choice([15, 20, 25]),
        "add_ratio": random.choice([20, 30, 40]),
        "average_gain_pct": random.choice([15, 20, 25]),
        "growth_target": random.choice([10000, 20000, 50000])
    }
    st.json(gen_strategy)
    st.download_button("📥 下載此策略 JSON", data=json.dumps(gen_strategy), file_name=f"AI_strategy_{gen_strategy['coin']}.json")

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

# --- AI 評估建議區塊 ---
st.subheader("🤖 AI 策略風險分析與建議")

risk = "低"
score = 80
recommend = "✔️ 策略設定偏保守，具備良好風險控管。可考慮在加倉比例與初始槓桿上進一步優化收益潛力。"

if add_ratio > 70 or average_gain_pct > 50:
    risk = "高"
    score = 40
    recommend = "⚠️ 策略可能過於激進，風險偏高，建議降低加倉比例或平均收益預期。"
elif add_ratio > 50 or average_gain_pct > 40:
    risk = "中"
    score = 65
    recommend = "🟡 策略具成長潛力，但風險與回撤需密切監控。建議使用較低槓桿起步。"

st.metric("📊 AI 風險等級", risk)
st.metric("📈 AI 評分 (越高代表越穩健)", score)
st.info(recommend)

# --- AI 優化建議區塊 ---
st.subheader("🧠 AI 策略優化建議 (模擬演算)")

optimized_ratio = max(10, min(40, 100 - average_gain_pct))
optimized_gain = max(5, min(25, 60 - add_ratio // 2))
optimized_leverage = [l for l in leverage_options if l <= 10]

suggestion = f"建議將加倉比例調整至 {optimized_ratio}%，預期每輪收益調整為 {optimized_gain}%。使用較穩健槓桿組合如 {optimized_leverage} 可提升整體穩健性。"

st.success(suggestion)

st.markdown("""
📘 你可以將策略下載並分享給朋友，或載入舊策略進行編輯與回測。
""")
