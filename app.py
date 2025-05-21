# 滾倉模擬器互動版（多幣種 + 幣/U 本位選擇 + 降槓桿風控 + JSON 儲存 + 圖表模擬 + 強平價格計算）

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json

st.set_page_config(
    page_title="浮盈加倉降槓桿模擬器",
    page_icon="⚖️",
    layout="wide"
)

st.title("📉 多幣種滾倉模擬平台 + 降槓桿風控 + 強平價格預估")

with st.sidebar:
    st.header("參數設定")
    coin = st.selectbox("幣種", ["BTC", "ETH", "SOL", "TON", "PROMP"])
    margin_mode = st.radio("保證金模式", ["U 本位", "幣本位"])
    strategy_name = st.text_input("策略名稱", value="風控降槓桿策略")
    note = st.text_area("備註", value="模擬從起始價格到目標價格，加倉並隨浮盈降槓桿")

    start_price = st.number_input("起始價格", value=106000.0)
    target_price = st.number_input("目標價格", value=150000.0)
    initial_margin = st.number_input("初始保證金", value=100.0)
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

# 幣本位與U本位倉位換算
if margin_mode == "幣本位":
    position = (initial_margin * leverage) / start_price
else:
    position = initial_margin * leverage

capital = initial_margin
price = start_price
max_price = start_price
add_count = 0
reserve_profit = 0
current_leverage = leverage

price_track = [price]
capital_track = [capital]
position_track = [position]
reserve_track = [reserve_profit]
leverage_track = [current_leverage]
liquidation_track = [start_price - (start_price / leverage)]

while price < target_price:
    price *= (1 + step_price_pct)
    max_price = max(price, max_price)

    if price < max_price * (1 - stoploss_drawdown):
        break

    for threshold, new_lev in sorted(leverage_drop_points.items()):
        if capital >= initial_margin * threshold and current_leverage > new_lev:
            current_leverage = new_lev
            if margin_mode == "幣本位":
                position = (capital * current_leverage) / price
            else:
                position = capital * current_leverage

    unrealized_profit = position * step_price_pct * (price if margin_mode == "幣本位" else 1)

    if unrealized_profit / capital >= gain_trigger_pct:
        new_profit = capital * gain_trigger_pct
        add_amount = new_profit * add_ratio
        reserve_amount = new_profit * reserve_ratio

        capital += add_amount
        reserve_profit += reserve_amount
        if margin_mode == "幣本位":
            position = (capital * current_leverage) / price
        else:
            position = capital * current_leverage
        add_count += 1

    price_track.append(price)
    capital_track.append(capital)
    position_track.append(position)
    reserve_track.append(reserve_profit)
    leverage_track.append(current_leverage)
    liquidation_price = price - (price / current_leverage)
    liquidation_track.append(liquidation_price)

final_price = price
price_change_pct = (final_price - start_price) / start_price
floating_profit = position * price_change_pct * (final_price if margin_mode == "幣本位" else 1)
final_profit = round(floating_profit + reserve_profit, 2)

st.subheader("📈 模擬結果")
st.metric("加倉次數", add_count)
st.metric("最終槓桿", current_leverage)
st.metric("保留收益", f"{reserve_profit:.2f} USDT")
st.metric("總投入", f"{capital:.2f} USDT")
st.metric("倉位控制", f"{position:.6f} {'幣' if margin_mode == '幣本位' else 'USDT'}")
st.metric("含保留最終獲利", f"{final_profit:.2f} USDT")
st.metric("當前強平價格", f"{liquidation_track[-1]:.2f} USDT")

st.line_chart(pd.DataFrame({
    "價格": price_track,
    "資金": capital_track,
    "倉位": position_track,
    "保留": reserve_track,
    "槓桿": leverage_track,
    "強平價": liquidation_track
}))

st.download_button(
    label="💾 儲存策略 JSON",
    file_name=f"{strategy_name}_{coin}.json",
    mime="application/json",
    data=json.dumps({
        "策略名稱": strategy_name,
        "幣種": coin,
        "保證金模式": margin_mode,
        "起始價格": start_price,
        "目標價格": target_price,
        "初始保證金": initial_margin,
        "加倉觸發%": gain_trigger_pct,
        "加倉比例%": add_ratio,
        "保留比例%": reserve_ratio,
        "模擬漲幅步伐": step_price_pct,
        "槓桿變化": leverage_drop_points,
        "最終槓桿": current_leverage,
        "保留獲利": reserve_profit,
        "總投入": capital,
        "倉位": position,
        "總獲利": final_profit,
        "最終強平價": liquidation_track[-1],
        "說明": note
    }, ensure_ascii=False)
)
