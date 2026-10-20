import streamlit as st
from SmartApi import SmartConnect
import pyotp  # जर तुम्ही 2FA/TOTP वापरत असाल तर

st.set_page_config(page_title="Angel One Price Action Analyzer", layout="centered")

st.title("📈 Angel One Live Data - Price Action & Candle Strength")
st.write("अँजेल वन स्मार्टएपीआय (SmartAPI) द्वारे निफ्टी आणि बँक निफ्टीचा लाईव्ह डेटा फेच करा.")

# Sidebar for Credentials
with st.sidebar:
    st.header("🔑 Angel One Credentials")
    api_key = st.text_input("API Key", type="password")
    client_id = st.text_input("Client ID (User ID)")
    password = st.text_input("Password / MPIN", type="password")
    totp_secret = st.text_input("TOTP Secret (optional)", type="password")

# Main Connection and Data Fetch
if st.button("अँजेल वनशी कनेक्ट करा व डेटा आणा"):
    if not api_key or not client_id or not password:
        st.warning("कृपया तुमचे सर्व क्रेडेन्शियल्स (API Key, Client ID, Password) भरा.")
    else:
        try:
            smartApi = SmartConnect(api_key=api_key)
            
            # TOTP जनरेट करणे (अँजेल वन लॉगिनसाठी आवश्यक असल्यास)
            token = ""
            if totp_secret:
                try:
                    token = pyotp.TOTP(totp_secret).now()
                except Exception as e:
                    st.error(f"TOTP जनरेट करताना एरर आला: {e}")
            
            # लॉगिन प्रक्रिया
            data = smartApi.generateSession(client_id, password, token)
            
            if data and data.get('status'):
                st.success("अँजेल वन API शी यशस्वीपणे कनेक्ट झाले!")
                
                # लाईव्ह एलटीपी (LTP) डेटा मिळवण्यासाठी (उदा. निफ्टी आणि बँक निफ्टी)
                # टीप: अँजेल वनमध्ये टोकन नंबर्स वापरावे लागतात (उदा. निफ्टी ५० साठी '99926000', बँक निफ्टीसाठी '99926009')
                exchange = "NSE"
                tradingsymbol = "Nifty 50"
                symboltoken = "99926000"
                
                ltp_data = smartApi.ltpData(exchange, tradingsymbol, symboltoken)
                st.write("### लाईव्ह मार्केट अपडेट (LTP):")
                st.json(ltp_data)
                
            else:
                st.error(f"लॉगिन फेल झाले: {data.get('message', 'Unknown error')}")
                
        except Exception as e:
            st.error(f"तांत्रिक अडचण आली: {e}")
