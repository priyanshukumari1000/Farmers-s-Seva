from flask import Flask, render_template, request
import joblib
import numpy as np

from flask import Flask, render_template, request
import joblib

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('data_dashboard.html')

@app.route('/crop_recommendation', methods=['GET', 'POST'])
def crop_recommendation():
    if request.method == 'POST':
        # Dummy prediction (replace with real model logic)
        N = request.form['N']
        return render_template('crop_recommendation.html', crop="Wheat")
    return render_template('crop_recommendation.html')

if __name__ == '__main__':
    app.run(debug=True)


# Load the trained model
model = joblib.load('crop_model.pkl')

@app.route('/crop_recommendation', methods=['GET', 'POST'])
def crop_recommendation():
    if request.method == 'POST':
        try:
            N = float(request.form['N'])
            P = float(request.form['P'])
            K = float(request.form['K'])
            temperature = float(request.form['temperature'])
            humidity = float(request.form['humidity'])
            ph = float(request.form['ph'])
            rainfall = float(request.form['rainfall'])

            prediction = model.predict([[N, P, K, temperature, humidity, ph, rainfall]])
            crop = prediction[0]

            return render_template('crop_recommendation.html', crop=crop)

        except Exception as e:
            return f"Error: {e}"
    return render_template('crop_recommendation.html')
