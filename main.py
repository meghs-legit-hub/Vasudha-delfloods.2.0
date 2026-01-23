import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

#@st.cache_data(ttl=86400)  # refresh once per day
#def load_sea_level_data():
#    return pd.read_csv("sea_level_daily.csv")

#sea_level_df = load_sea_level_data()

# Page setup
st.set_page_config(page_title="Flood Prediction System", layout="centered")
st.title("🌊 Flood Prediction & Early Warning System")

# City configuration
CITY_CONFIG = {
    "Delhi": {
        "type": "inland",
        "location": "Delhi,IN",
        "lat": 28.6139,
        "lon": 77.2090
    },
    "Jalpaiguri": {
        "type": "inland",
        "location": "Jalpaiguri,IN",
        "lat": 26.523652454077087, 
        "lon": 88.7287456762074 
        
    },
        
    "Mumbai": {
        "type": "coastal",
        "location": "Mumbai,IN",
        "lat": 18.9640,
        "lon": 72.8205
    },
    "Chennai": {
        "type": "coastal",
        "location": "Chennai,IN",
        "lat": 13.0827,
        "lon": 80.2707
    }
}

city = st.selectbox("📍 Select City / District", list(CITY_CONFIG.keys()))
city_info = CITY_CONFIG[city]

#sea_level_anomaly = 0.0

#if city_info["type"] == "coastal":
#    city_sea = sea_level_df[sea_level_df["city"] == city]
#    if not city_sea.empty:
#        sea_level_anomaly = float(city_sea.iloc[-1]["sea_level_anomaly"])

# Training the model
def train_model1():
    if city_info["location"] == "Delhi,IN":
        df = pd.read_csv("delnew_csv.csv") 
        X = df[['precip', 'River_Level', 'temp', 'humidity', 'windspeed']]
        y = df['Flood']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model1 = RandomForestClassifier(n_estimators=100) #random_state=42 after 100?
        model1.fit(X_train, y_train)
        accuracy1 = model1.score(X_test, y_test)
        return model1, accuracy1

def train_model2():
    if city_info["location"] == "Jalpaiguri,IN":
        dJ = pd.read_csv("jalpaiguri.csv") 
        A = dJ[['precip', 'River_Level', 'temp', 'humidity', 'windspeed']]
        b = dJ['Flood']
        A_train, A_test, b_train, b_test = train_test_split(A, b, test_size=0.2, random_state=42)
        model2 = RandomForestClassifier(n_estimators=100) #random_state=42 after 100?
        model2.fit(A_train, b_train)
        accuracy2 = model2.score(A_test, b_test)
        return model2, accuracy2

def train_model3():
    if city_info["location"] == "Mumbai,IN":
        dM = pd.read_csv("mumbai.csv") 
        C = dM[['precip', 'Sea_Level_Anomaly', 'temp', 'humidity', 'windspeed']]
        d = dM['Flood']
        C_train, C_test, d_train, d_test = train_test_split(C, d, test_size=0.2, random_state=42)
        model3 = RandomForestClassifier(n_estimators=100) #random_state=42 after 100?
        model3.fit(C_train, d_train)
        accuracy3 = model3.score(C_test, d_test)
        return model3, accuracy3
        
def train_model4():
    if city_info["location"] == "Chennai,IN":
        dC = pd.read_csv("chennai.csv") 
        P = dC[['precip', 'Sea_Level_Anomaly', 'temp', 'humidity', 'windspeed']]
        q = dC['Flood']
        P_train, P_test, q_train, q_test = train_test_split(P, q, test_size=0.2, random_state=42)
        model4 = RandomForestClassifier(n_estimators=100) #random_state=42 after 100?
        model4.fit(P_train, q_train)
        accuracy4 = model4.score(P_test, q_test)
        return model4, accuracy4

# Train model/test accuracy
if city_info["location"] == "Delhi,IN":
    model1, accuracy1 = train_model1()
elif city_info["location"] == "Jalpaiguri,IN":
    model2, accuracy2 = train_model2()
elif city_info["location"] == "Mumbai,IN":
    model3, accuracy3 = train_model3()
elif city_info["location"] == "Chennai,IN":
    model4, accuracy4 = train_model4()
    
# Input for river level
if city_info['type'] == 'inland':
    river_level = st.number_input("🌊 Enter current River Level (in meters):", min_value=0.0, step=0.1)
elif city_info['type'] == 'coastal':
    sea_level_anomaly = st.number_input("🌊 Enter current Sea Level Anomaly (in meters):", min_value=0.0, step=0.1)
#river_level = st.number_input(f"🌊 Enter river level for {city} (meters)",min_value=0.0,step=0.1)


# ✅ Function to safely fetch weather data
def fetch_weather_data(location):
    today = datetime.now().strftime("%Y-%m-%d")
    api_key = "HC8QD5Y25CNY89PCZB3643W4X"

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{location}/{today}/{today}"
    params = {
        "unitGroup": "metric",
        "include": "days",
        "key": api_key,
        "contentType": "json"
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if "days" in data and len(data["days"]) > 0:
            today_data = data["days"][0]
            return {
                "precip": today_data.get("precip") or 0.0,
                "temp": today_data.get("temp") or 0.0,
                "humidity": today_data.get("humidity") or 0.0,
                "windspeed": today_data.get("windspeed") or 0.0
            }
    return None


# Get weather
weather = fetch_weather_data(city_info["location"])

ready = False

if city_info["type"] == "inland":
    ready = weather is not None and river_level > 0

elif city_info["type"] == "coastal":
    ready = weather is not None and sea_level_anomaly > 0


# Make prediction if both inputs are ready
if ready:
    st.subheader("📊 Today's Weather Data:") #st.subheader("📊 Live Environmental Data")
    st.json(weather)
    #    if city_info["type"] == "coastal":
    #        st.write(f"🌊 Sea Surface Height Anomaly (Copernicus): "f"**{round(sea_level_anomaly, 2)} m**")
    # Format data for prediction
    if city_info["type"] == "inland":
        input_data1 = pd.DataFrame([{
            'precip': weather['precip'],
            'River_Level': river_level,
            'temp': weather['temp'],
            'humidity': weather['humidity'],
            'windspeed': weather['windspeed']
        }])
        
    elif city_info["type"] == "coastal":    
        input_data2 = pd.DataFrame([{
            'precip': weather['precip'],
            'Sea_Level_Anomaly': sea_level_anomaly,
            'temp': weather['temp'],
            'humidity': weather['humidity'],
            'windspeed': weather['windspeed']
        }])
        
          # Show river level rule-based prediction
    st.subheader("📢 Flood Risk Assessment")
    if city_info["type"] == "inland":
        if city_info["location"] == "Delhi,IN":
            if river_level > 205.55:
                st.error("🔴 ALERT: River flooding WILL LIKELY occur.")
            elif river_level > 202:
                st.warning("🟠 WARNING: River flooding is POSSIBLE.")
            else:
                st.success("🟢 River flooding is NOT EXPECTED.")
                
                
            
        elif city_info["location"] == "Jalpaiguri,IN":
            if river_level > 87:
                st.error("🔴 ALERT: River flooding WILL LIKELY occur.")
            elif river_level > 85.1:
                st.warning("🟠 WARNING: River flooding is POSSIBLE.")
            else:
                st.success("🟢 River flooding is NOT EXPECTED.")
                
    elif city_info["type"] == "coastal":
        if city_info["location"] == "Mumbai,IN":
            if sea_level_anomaly > 0.4:
                st.error("🔴 Coastal flooding VERY LIKELY.")
            elif sea_level_anomaly > 0.3:
                st.warning("🟠 Elevated sea level detected.")
            else:
                st.success("🟢 Coastal conditions stable.")
            
        elif city_info["location"] == "Chennai,IN":
            if sea_level_anomaly > 1.2:
                st.error("🔴 Coastal flooding VERY LIKELY.")
            elif sea_level_anomaly > 1.0:
                st.warning("🟠 Elevated sea level detected.")
            else:
                st.success("🟢 Coastal conditions stable.")
    
    
         # Also run the model prediction
    if city_info["type"] == "inland":
        if city_info["location"] == "Delhi,IN":
            prediction1 = model1.predict(input_data1)[0]
            st.subheader("📊 Model-Based Prediction:")
            if prediction1 == 2:
                st.error("🚩 Model says: FLOOD HIGHLY LIKELY – Stay safe!")
            elif prediction1 == 1:
                st.warning("⚠️ Model says: FLOOD LIKELY – Stay safe!")
            else:
                st.success("✅ Model says: NO FLOOD expected today.")
       
        elif city_info["location"] == "Jalpaiguri,IN":
            prediction2 = model2.predict(input_data1)[0]
            st.subheader("📊 Model-Based Prediction:")
            if prediction2 == 2:
                st.error("🚩 Model says: FLOOD HIGHLY LIKELY – Stay safe!")
            elif prediction2 == 1:
                st.warning("⚠️ Model says: FLOOD LIKELY – Stay safe!")
            else:
                st.success("✅ Model says: NO FLOOD expected today.")
    elif city_info["type"] == "coastal":
        if city_info["location"] == "Mumbai,IN":
            prediction3 = model3.predict(input_data2)[0]
            st.subheader("📊 Model-Based Prediction:")
            if prediction3 == 2:
                st.error("🚩 Model says: FLOOD HIGHLY LIKELY – Stay safe!")
            elif prediction3 == 1:
                st.warning("⚠️ Model says: FLOOD LIKELY – Stay safe!")
            else:
                st.success("✅ Model says: NO FLOOD expected today.")
            
        elif city_info["location"] == "Chennai,IN":
            prediction4 = model4.predict(input_data2)[0]
            st.subheader("📊 Model-Based Prediction:")
            if prediction4 == 2:
                st.error("🚩 Model says: FLOOD HIGHLY LIKELY – Stay safe!")
            elif prediction4 == 1:
                st.warning("⚠️ Model says: FLOOD LIKELY – Stay safe!")
            else:
                st.success("✅ Model says: NO FLOOD expected today.")
            

#st.write("✅ Model accuracy:", round(accuracy * 100, 2), "%")



#st.write("✅ Model accuracy on test data:", accuracy)











































