import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load dataset
df = pd.read_csv("C:/Users/priya/OneDrive/Desktop/farmersIP copy/farmersIP copy/crop_recommendation/crop_recommendation.csv")

# Features and labels
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = df['label']

# Train model
model = RandomForestClassifier()
model.fit(X, y)

# Save model
joblib.dump(model, "crop_model.pkl")
