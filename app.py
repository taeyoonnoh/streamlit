import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# 페이지 기본 설정
st.set_page_config(page_title="Stock Dashboard", layout="wide")

# 제목
st.title("📈 Stock Market Dashboard")

# 화폐 단위 선택
currency = st.selectbox("💵 화폐 단위를 선택하세요", ["USD", "KRW"])

# 주식 종목 입력
ticker = st.text_input("🔍 종목 코드를 입력하세요 (예: AAPL, TSLA, GOOG)", "AAPL")

# 기간 선택 (드롭다운, 한글로 변경)
period = st.selectbox("📅 기간을 선택하세요", ["1개월", "3개월", "6개월", "12개월"], index=0)

# 기간에 해당하는 Yahoo Finance 코드 매핑
period_mapping = {
    "1개월": "1mo",
    "3개월": "3mo",
    "6개월": "6mo",
    "12개월": "1y"
}

# 차트 유형 선택 (Line 차트 / Candlestick 차트)
chart_type = st.radio("📊 차트 유형을 선택하세요", ["Line 차트", "Candlestick 차트"], index=0)

# 환율 정보 가져오기 (달러/원)
if currency == "KRW":
    exchange_rate = yf.Ticker("USDKRW=X")
    exchange_rate_data = exchange_rate.history(period="1d")
    usd_to_krw = exchange_rate_data["Close"].iloc[-1]
    st.metric(label="📉 현재 환율 (USD → KRW)", value=f"₩{usd_to_krw:,.2f}")
else:
    usd_to_krw = 1  # USD이면 변환 없이 그대로 USD로 표시

# 데이터 가져오기
if ticker:
    stock_data = yf.Ticker(ticker)
    hist = stock_data.history(period=period_mapping[period])  # 선택된 기간의 데이터

    # 실시간 가격 및 날짜 표시
    current_price = stock_data.history(period="1d")["Close"].iloc[-1]
    current_date = stock_data.history(period="1d").index[-1]

    # 가격 변환 (USD → KRW)
    if currency == "KRW":
        current_price_krw = current_price * usd_to_krw
        st.metric(label="📌 현재 주가", value=f"₩{current_price_krw:,.2f}", delta=f"📅 {current_date.strftime('%Y-%m-%d')}")
    else:
        st.metric(label="📌 현재 주가", value=f"${current_price:,.2f}", delta=f"📅 {current_date.strftime('%Y-%m-%d')}")

    # 주가 차트 및 최고/최저점 표시
    st.subheader("📊 주가 차트")

    # 캔들 차트 (주가)
    fig = make_subplots(
        rows=2, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.1,
        subplot_titles=(f"{ticker} 주식 차트", "거래량"),
        shared_yaxes=True
    )

    # Line 차트 (주가)
    if chart_type == "Line 차트":
        if currency == "KRW":
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'] * usd_to_krw,
                mode='lines',
                name="Line",
                line=dict(color='blue'),
            ), row=1, col=1)
        else:
            fig.add_trace(go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name="Line",
                line=dict(color='blue'),
            ), row=1, col=1)
    elif chart_type == "Candlestick 차트":
        # Candlestick 차트 (주가)
        if currency == "KRW":
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'] * usd_to_krw,
                high=hist['High'] * usd_to_krw,
                low=hist['Low'] * usd_to_krw,
                close=hist['Close'] * usd_to_krw,
                name="Candlesticks"
            ), row=1, col=1)
        else:
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name="Candlesticks"
            ), row=1, col=1)

    # 거래량 차트 (Volume)
    fig.add_trace(go.Bar(
        x=hist.index,
        y=hist['Volume'],
        name="Volume",
        marker=dict(color='rgba(255, 99, 71, 0.6)'),
        hovertemplate='%{x}<br>Volume: %{y}',  # 마우스 오버 시 데이터 표시
    ), row=2, col=1)

    # 최저점, 최고점, 현재 주가 계산
    min_idx = hist['Close'].idxmin()  # 최저 종가 인덱스
    max_idx = hist['Close'].idxmax()  # 최고 종가 인덱스

    min_price = hist['Close'].min()
    max_price = hist['Close'].max()
    min_volume = hist.loc[min_idx, 'Volume']
    max_volume = hist.loc[max_idx, 'Volume']

    # 상승/하락 퍼센트 계산
    price_change_min = ((current_price - min_price) / min_price) * 100
    price_change_max = ((current_price - max_price) / max_price) * 100
    
    # 날짜를 datetime으로 변환하여 strftime 사용
    min_date = min_idx if isinstance(min_idx, pd.Timestamp) else pd.Timestamp(min_idx)
    max_date = max_idx if isinstance(max_idx, pd.Timestamp) else pd.Timestamp(max_idx)
    
    # 날짜를 'YYYY-MM-DD' 형식으로 표시
    min_date_str = min_date.strftime('%Y-%m-%d')
    max_date_str = max_date.strftime('%Y-%m-%d')

    # 3개의 박스를 표시
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; padding: 10px;">
            <div style="border: 2px solid red; border-radius: 5px; padding: 10px; width: 30%; background-color: rgba(255, 0, 0, 0.1);">
                <strong>최저:</strong> {min_price:.2f} {currency}<br>
                <strong>날짜:</strong> {min_date_str}<br>
                <strong>거래량:</strong> {min_volume}
            </div>
            <div style="border: 2px solid green; border-radius: 5px; padding: 10px; width: 30%; background-color: rgba(0, 255, 0, 0.1);">
                <strong>최고:</strong> {max_price:.2f} {currency}<br>
                <strong>날짜:</strong> {max_date_str}<br>
                <strong>거래량:</strong> {max_volume}
            </div>
            <div style="border: 2px solid blue; border-radius: 5px; padding: 10px; width: 30%; background-color: rgba(0, 0, 255, 0.1);">
                <strong>현재:</strong> {current_price:.2f} {currency}<br>
                <strong>상승:</strong> {price_change_min:.2f}%<br>
                <strong>하락:</strong> {price_change_max:.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 최저점, 최고점 y축 표시 (점선으로 표시)
    fig.add_shape(
        type="line",
        x0=hist.index[0],
        x1=hist.index[-1],
        y0=min_price,
        y1=min_price,
        line=dict(color="red", width=2, dash="dash"),
        name="최저점"
    )

    fig.add_shape(
        type="line",
        x0=hist.index[0],
        x1=hist.index[-1],
        y0=max_price,
        y1=max_price,
        line=dict(color="green", width=2, dash="dash"),
        name="최고점"
    )

    # 레이아웃 설정
    fig.update_layout(
        title=f"{ticker} 주식 차트",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=True,
        template="plotly_dark",
    )

    # Streamlit에서 차트 표시
    st.plotly_chart(fig)
