from flask import Flask, request, jsonify, render_template
from utils import get_crop_recommendation
import traceback
import os

app = Flask(__name__)

# --------------------------------
# Home Route – Form Interface
# --------------------------------
@app.route('/')
def home():
    return render_template('index.html')  # Simple HTML form

# --------------------------------
# Prediction API Endpoint
# --------------------------------
@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json() if request.is_json else request.form

        # Extract parameters
        N = float(data.get('N'))
        P = float(data.get('P'))
        K = float(data.get('K'))
        ph = float(data.get('ph'))

        # Weather parameters (optional)
        temperature = data.get('temperature')
        humidity = data.get('humidity')
        rainfall = data.get('rainfall')
        lat = data.get('lat')
        lon = data.get('lon')

        # Convert types if available
        temperature = float(temperature) if temperature else None
        humidity = float(humidity) if humidity else None
        rainfall = float(rainfall) if rainfall else None
        lat = float(lat) if lat else None
        lon = float(lon) if lon else None

        # Get predictions
        recommendations = get_crop_recommendation(
            N=N, P=P, K=K, ph=ph,
            lat=lat, lon=lon,
            temperature=temperature, humidity=humidity, rainfall=rainfall
        )

        # Return JSON response
        return jsonify({
            "status": "success",
            "recommendations": recommendations
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


# --------------------------------
# Run the app
# --------------------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


#comment to check1