import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

#@st.cache_data(ttl=86400)  # refresh once per day
def load_sea_level_data():
    return pd.read_csv("sea_level_daily.csv")

sea_level_df = load_sea_level_data()

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
        "location": "Guwahati,IN",
        "lat": 26.523652454077087, 
        "lon": 88.7287456762074 
        
    },
    
    "Kochi": {
        "type": "coastal",
        "location": "Kochi,IN",
        "lat": 9.930327510572434, 
        "lon": 76.26445391748359
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

sea_level_anomaly = 0.0

if city_info["type"] == "coastal":
    city_sea = sea_level_df[sea_level_df["city"] == city]
    if not city_sea.empty:
        sea_level_anomaly = float(city_sea.iloc[-1]["sea_level_anomaly"])

# Training the model
def train_model():
    if city_info["location"] == "Delhi,IN":
        df = pd.read_csv("delnew_csv.csv") 
        X = df[['precip', 'River_Level', 'temp', 'humidity', 'windspeed']]
        y = df['Flood']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100) #random_state=42 after 100?
        model.fit(X_train, y_train)
    elif city_info["location"] == "Jalpaiguri,IN":
        df = pd.read_csv("jalpaiguri.csv") 
        A = df[['precip', 'River_Level', 'temp', 'humidity', 'windspeed']]
        b = df['Flood']
        A_train, A_test, b_train, b_test = train_test_split(A, b, test_size=0.2, random_state=42)
        model = RandomForestClassifier(n_estimators=100) #random_state=42 after 100?
        model.fit(A_train, b_train)

    csv1 = pd.read_csv("delnew_csv.csv")
    csv2 = pd.read_csv("jalpaiguri.csv")

# Combine datasets
    combined = pd.concat([csv1, csv2], ignore_index=True)

# Features and target
    C = combined[['precip','River_Level','temp','humidity','windspeed']]
    D = combined['Flood']  # 0,1,2
    C_train, C_test, D_train, D_test = train_test_split(C, D, test_size=0.2, random_state=42)
    D_pred = model.predict(C_test)
    accuracy = model.score(C_test, D_test)
    return model, accuracy

# Train model/test accuracy
model, accuracy = train_model()

# Input for river level
river_level = st.number_input("🌊 Enter current river level (in meters):", min_value=0.0, step=0.1) 
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


# Make prediction if both inputs are ready
if weather and river_level:
    st.subheader("📊 Today's Weather Data:") #st.subheader("📊 Live Environmental Data")
    st.json(weather)

    if city_info["type"] == "coastal":
        st.write(f"🌊 Sea Surface Height Anomaly (Copernicus): "f"**{round(sea_level_anomaly, 2)} m**")

    # Format data for prediction
    input_data = pd.DataFrame([{
        'precip': weather['precip'],
        'River_Level': river_level,
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
            if river_level > 50:
                st.error("🔴 ALERT: River flooding WILL LIKELY occur.")
            elif river_level > 48.9:
                st.warning("🟠 WARNING: River flooding is POSSIBLE.")
            else:
                st.success("🟢 River flooding is NOT EXPECTED.")
            
    elif city_info["type"] == "coastal":
        if sea_level_anomaly > 0.4  and river_level>3.75 :
            st.error("🔴 Coastal flooding VERY LIKELY.")
        elif sea_level_anomaly > 0.2 and river_level>2.75:
            st.warning("🟠 Elevated sea level detected.")
        else:
            st.success("🟢 Coastal conditions stable.")


     # Also run the model prediction
    prediction = model.predict(input_data)[0]
    st.subheader("📊 Model-Based Prediction:")
    if prediction == 2:
        st.error("🚩 Model says: FLOOD HIGHLY LIKELY – Stay safe!")
    elif prediction == 1:
        st.warning("⚠️ Model says: FLOOD LIKELY – Stay safe!")
    else:
        st.success("✅ Model says: NO FLOOD expected today.")

st.write("✅ Model accuracy:", round(accuracy * 100, 2), "%")



#st.write("✅ Model accuracy on test data:", accuracy)





