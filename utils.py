import os
import joblib
import numpy as np
import requests
from dotenv import load_dotenv

# -------------------------------
# Load environment variables
# -------------------------------
load_dotenv()
OWM_API_KEY = os.getenv("OWM_API_KEY", None)

# -------------------------------
# Load trained models
# -------------------------------
MODELS_DIR = "models"
rf_model = joblib.load(os.path.join(MODELS_DIR, "rf_model.joblib"))
scaler = joblib.load(os.path.join(MODELS_DIR, "scaler.joblib"))
label_encoder = joblib.load(os.path.join(MODELS_DIR, "label_encoder.joblib"))

# -------------------------------
# Fetch live weather from OpenWeatherMap API
# -------------------------------
def get_weather(lat: float, lon: float):
    """
    Fetches temperature, humidity, rainfall from OpenWeatherMap.
    Returns None if API key is missing or invalid.
    """
    if not OWM_API_KEY:
        print("⚠️ No API key provided, skipping weather API.")
        return None

    url = (
        f"https://api.openweathermap.org/data/2.5/weather?"
        f"lat={lat}&lon={lon}&appid={OWM_API_KEY}&units=metric"
    )
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if res.status_code != 200:
            print(f"⚠️ Weather API error: {data.get('message', 'Unknown error')}")
            return None

        temperature = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        rainfall = data.get("rain", {}).get("1h", 0.0)
        return {"temperature": temperature, "humidity": humidity, "rainfall": rainfall}

    except Exception as e:
        print(f"⚠️ Weather API request failed: {e}")
        return None

# -------------------------------
# Predict crop recommendation
# -------------------------------
def predict_crop(features: dict):
    required_keys = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    for key in required_keys:
        if key not in features:
            raise ValueError(f"Missing key: {key}")

    input_data = np.array([[features['N'], features['P'], features['K'],
                            features['temperature'], features['humidity'],
                            features['ph'], features['rainfall']]])
    input_scaled = scaler.transform(input_data)
    probabilities = rf_model.predict_proba(input_scaled)[0]
    sorted_indices = np.argsort(probabilities)[::-1]
    top3 = [
        {
            "crop": label_encoder.inverse_transform([sorted_indices[i]])[0],
            "confidence": float(probabilities[sorted_indices[i]] * 100)
        }
        for i in range(3)
    ]
    return top3

# -------------------------------
# Utility function for combined workflow
# -------------------------------
def get_crop_recommendation(N, P, K, ph, lat=None, lon=None,
                            temperature=None, humidity=None, rainfall=None):
    """
    Use weather API if lat/lon and valid API key exist; otherwise fallback to manual input.
    """
    if lat is not None and lon is not None:
        weather = get_weather(lat, lon)
        if weather:
            temperature = weather['temperature']
            humidity = weather['humidity']
            rainfall = weather['rainfall']
        else:
            print("⚠️ Using manual weather input instead of API.")

    # Require manual weather if still None
    if temperature is None or humidity is None or rainfall is None:
        raise ValueError("Temperature, humidity, and rainfall are required if no API weather available.")

    features = {
        "N": N,
        "P": P,
        "K": K,
        "temperature": temperature,
        "humidity": humidity,
        "ph": ph,
        "rainfall": rainfall
    }
    return predict_crop(features)
