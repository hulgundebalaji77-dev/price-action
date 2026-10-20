import streamlit as st
from SmartApi import SmartConnect
import pyotp
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Angel One Price Action Analyzer", layout="centered")

st.title("📈 Angel One Live Price Action & Candle Strength")
st.write("अँजेल वन लाईव्ह डेटावरून निफ्टी/बँक निफ्टीची कँडल स्ट्रेंथ तपासा.")

# Sidebar for Credentials
with st.sidebar:
    st.header("🔑 Angel One Credentials")
    api_key = st.text_input("API Key", type="password")
    client_id = st.text_input("Client ID (User ID)")
    password = st.text_input("Password / MPIN", type="password")
    totp_secret = st.text_input("TOTP Secret (optional)", type="password")

# Index Selection
index_choice = st.selectbox("इंडेक्स निवडा", ["Nifty 50", "Bank Nifty"])
timeframe_choice = st.selectbox("टाईमफ्रेम", ["ONE_MINUTE", "FIVE_MINUTE", "FIFTEEN_MINUTE"])

# Token Mapping for Angel One
symbol_token = "99926000" if index_choice == "Nifty 50" else "99926009"
tradingsymbol_str = "NIFTY" if index_choice == "Nifty 50" else "BANKNIFTY"

if st.button("लाईव्ह डेटा आणा व ॲनालिसिस करा"):
    if not api_key or not client_id or not password:
        st.warning("कृपया तुमचे सर्व क्रेडेन्शियल्स भरा.")
    else:
        try:
            smartApi = SmartConnect(api_key=api_key)
            
            token = ""
            if totp_secret:
                token = pyotp.TOTP(totp_secret).now()
            
            data = smartApi.generateSession(client_id, password, token)
            
            if data and data.get('status'):
                st.success("अँजेल वनशी यशस्वीपणे कनेक्ट झाले!")
                
                # Fetching Historical/Candle Data with correct date range for today
                to_date = datetime.now()
                from_date = to_date - timedelta(days=5) # 5 days to ensure historical candles are found
                
                historicParam = {
                    "exchange": "NSE",
                    "symboltoken": symbol_token,
                    "interval": timeframe_choice,
                    "fromdate": from_date.strftime("%Y-%m-%d %H:%M"),
                    "todate": to_date.strftime("%Y-%m-%d %H:%M")
                }
                
                candle_response = smartApi.getCandleData(historicParam)
                
                if candle_response and candle_response.get('status') and candle_response.get('data'):
                    raw_data = candle_response['data']
                    df = pd.DataFrame(raw_data, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
                    
                    # Ensure correct numerical values and take the second last or latest completed candle if market is running
                    latest = df.iloc[-1]
                    open_p, high_p, low_p, close_p = float(latest['Open']), float(latest['High']), float(latest['Low']), float(latest['Close'])
                    
                    # Fallback check if OHLC is identical (live tick simulation fix)
                    if open_p == high_p == low_p == close_p and len(df) > 1:
                        latest = df.iloc[-2] # take previous completed candle
                        open_p, high_p, low_p, close_p = float(latest['Open']), float(latest['High']), float(latest['Low']), float(latest['Close'])

                    st.write("### लेटेस्ट कँडल डेटा (OHLC):")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Open", round(open_p, 2))
                    col2.metric("High", round(high_p, 2))
                    col3.metric("Low", round(low_p, 2))
                    col4.metric("Close", round(close_p, 2))

                    # Market Analysis Class (Including Bullish & Bearish / Put-Call support)
                    class MarketAnalysis:
                        def
