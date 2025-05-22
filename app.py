# 滾倉模擬器互動版（多幣種 + 幣/U 本位選擇 + 降槓桿風控 + JSON 儲存 + 圖表模擬 + 強平價格計算 + 每輪加倉明細表 + 滾倉 vs 浮盈加倉對比）

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

st.set_page_config(
    page_title="浮盈加倉降槓桿模擬器",
    page_icon="⚖️",
    layout="wide"
)

st.title("📉 多幣種滾倉模擬平台 + 降槓桿風控 + 強平價格預估 + 策略對比")

with st.sidebar:
    st.header("參數設定")
    coin = st.selectbox("幣種", ["BTC", "ETH", "SOL", "TON", "PROMP"])
    margin_mode = st.radio("保證金模式", ["U 本位", "幣本位"])
    strategy_name = st.text_input("策略名稱", value="風控降槓桿策略")
    note = st.text_area("備註", value="比較浮盈加倉 vs 每段平倉滾倉模式")

    start_price = st.number_input("起始價格", value=106000.0)
    target_price = st.number_input("目標價格", value=150000.0)
    initial_margin = st.number_input("初始保證金", value=100.0, min_value=0.00001, format="%.5f")
    leverage = st.slider("初始槓桿", 1, 100, 10)
    gain_trigger_pct = st.slider("浮盈加倉觸發 %", 5, 100, 15) / 100
    add_ratio = st.slider("每次加倉比例 %", 10, 100, 80) / 100
    reserve_ratio = st.slider("保留利潤比例 %", 0, 100, 20) / 100
    step_price_pct = st.slider("價格每步漲幅 %", 1, 10, 2) / 100
    stoploss_drawdown = st.slider("最高價回撤停損 %", 1, 50, 10) / 100

# 降槓桿條件
leverage_drop_points = {
    3: 5,
    5: 3,
    10: 1
}

def simulate(strategy_type):
    capital = initial_margin
    price = start_price
    max_price = start_price
    reserve_profit = 0
    current_leverage = leverage
    position = (capital * current_leverage / price) if margin_mode == "幣本位" else (capital * current_leverage)
    add_count = 0

    price_track, capital_track, position_track = [price], [capital], [position]
    reserve_track, leverage_track, liquidation_track = [0], [current_leverage], [price - price / leverage]
    add_table = []

    while price < target_price:
        price *= (1 + step_price_pct)
        max_price = max(price, max_price)
        if price < max_price * (1 - stoploss_drawdown): break

        for threshold, new_lev in sorted(leverage_drop_points.items()):
            if capital >= initial_margin * threshold and current_leverage > new_lev:
                current_leverage = new_lev
                position = (capital * current_leverage / price) if margin_mode == "幣本位" else (capital * current_leverage)

        entry_price = price
        profit_per_unit = step_price_pct * (price if margin_mode == "幣本位" else 1)
        unrealized_profit = position * profit_per_unit

        if unrealized_profit / capital >= gain_trigger_pct:
            new_profit = capital * gain_trigger_pct
            add_amount = new_profit * add_ratio
            reserve_amount = new_profit * reserve_ratio

            capital += add_amount
            reserve_profit += reserve_amount

            if strategy_type == "滾倉":
                capital = initial_margin + reserve_profit

            position = (capital * current_leverage / price) if margin_mode == "幣本位" else (capital * current_leverage)
            add_count += 1
            add_table.append({"價格": round(entry_price, 2), "資金總額": round(capital, 2), "槓桿倉位": round(position, 2)})

        price_track.append(price)
        capital_track.append(capital)
        position_track.append(position)
        reserve_track.append(reserve_profit)
        leverage_track.append(current_leverage)
        liquidation_track.append(price - price / current_leverage)

    change_pct = (price - start_price) / start_price
    floating_profit = position * change_pct * (price if margin_mode == "幣本位" else 1)
    final_profit = round(floating_profit + reserve_profit, 2)

    return {
        "加倉次數": add_count,
        "最終槓桿": current_leverage,
        "保留收益": reserve_profit,
        "總投入": capital,
        "倉位": position,
        "總獲利": final_profit,
        "強平價": liquidation_track[-1],
        "圖表": pd.DataFrame({
            f"價格_{strategy_type}": price_track,
            f"資金_{strategy_type}": capital_track,
            f"倉位_{strategy_type}": position_track
        }),
        "明細": pd.DataFrame(add_table)
    }

# 執行模擬
result_浮盈 = simulate("浮盈")
result_滾倉 = simulate("滾倉")

st.subheader("📊 策略獲利比較")
st.metric("浮盈加倉總獲利", f"{result_浮盈['總獲利']:.2f} USDT")
st.metric("滾倉策略總獲利", f"{result_滾倉['總獲利']:.2f} USDT")

st.subheader("📈 資金變化對比圖")
chart_df = pd.concat([result_浮盈["圖表"], result_滾倉["圖表"]], axis=1)
st.line_chart(chart_df)

st.subheader("📋 浮盈加倉推演明細")
st.dataframe(result_浮盈["明細"])

st.subheader("📋 滾倉策略推演明細")
st.dataframe(result_滾倉["明細"])
