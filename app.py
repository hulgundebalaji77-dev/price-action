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
                
                # Fetching Historical/Candle Data
                to_date = datetime.now()
                from_date = to_date - timedelta(days=5) 
                
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
                    
                    # Convert to numeric to avoid string issues
                    for col in ['Open', 'High', 'Low', 'Close']:
                        df[col] = pd.to_numeric(df[col])

                    # Get the latest completed/forming candle
                    latest = df.iloc[-1]
                    open_p, high_p, low_p, close_p = float(latest['Open']), float(latest['High']), float(latest['Low']), float(latest['Close'])
                    
                    st.write("### लेटेस्ट कँडल डेटा (OHLC):")
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Open", round(open_p, 2))
                    col2.metric("High", round(high_p, 2))
                    col3.metric("Low", round(low_p, 2))
                    col4.metric("Close", round(close_p, 2))

                    # Market Analysis Class
                    class MarketAnalysis:
                        def __init__(self, open_price, high_price, low_price, close_price):
                            self.open = open_price
                            self.high = high_price
                            self.low = low_price
                            self.close = close_price

                        def is_green(self):
                            return self.close > self.open

                        def calculate_body_range(self):
                            return abs(self.close - self.open)

                        def calculate_total_range(self):
                            return self.high - self.low

                        def evaluate_strength(self):
                            total_range = self.calculate_total_range()
                            if total_range == 0:
                                return "Doji / No Range"
                            
                            body = self.calculate_body_range()
                            upper_wick = self.high - max(self.open, self.close)
                            body_percentage = (body / total_range) * 100

                            if self.is_green():
                                if body_percentage >= 70 and upper_wick <= (total_range * 0.15):
                                    return "Strong Bullish Momentum (Option C equivalent)"
                                elif body_percentage >= 40:
                                    return "Moderate Bullish (Option B equivalent)"
                                else:
                                    return "Weak Bullish / High Rejection (Option A equivalent)"
                            else:
                                return "Bearish Candle"

                    analyzer = MarketAnalysis(open_p, high_p, low_p, close_p)
                    strength = analyzer.evaluate_strength()
                    
                    st.markdown("---")
                    st.info(f"**कँडल स्ट्रेंथ निकाल:** {strength}")
                    
                    if "Strong Bullish" in strength:
                        st.success("🚨 **सिग्नल: BUY CALL (CE)** - मजबूत बायर मोमेंटम आढळला!")
                    elif "Moderate Bullish" in strength:
                        st.warning("⚠️ **सिग्नल: WAIT/WATCH** - मध्यम मोमेंटम, कन्फर्मेशनची वाट पाहा.")
                    else:
                        st.error("❌ **सिग्नल: AVOID/BEARISH** - कमजोर कँडल किंवा सेलिंग प्रेशर.")
                else:
                    st.error("कँडल डेटा मिळवण्यात अपयश आले. कृपया नंतर प्रयत्न करा.")
            else:
                st.error(f"लॉगिन फेल झाले: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"तांत्रिक अडचण आली: {e}")
