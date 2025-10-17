import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import RandomizedSearchCV
import pickle
import os

# Load and preprocess data
print("Loading data...")
data_path = os.path.join(os.path.dirname(__file__), 'model', 'data.csv')
flight_data = pd.read_csv(data_path)

# Extract features
print("Processing features...")
X = pd.get_dummies(flight_data[['Total_Stops', 'Journey_day', 'Journey_month', 
                               'Dep_hour', 'Dep_min', 'Arrival_hour', 'Arrival_min',
                               'Duration_hours', 'Duration_mins', 'Airline', 
                               'Source', 'Destination']], drop_first=True)
y = flight_data['Price']

# Split the data
print("Splitting data...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define parameter grid for RandomForestRegressor
params = {
    'n_estimators': [100, 200, 300, 400],
    'max_features': ['auto', 'sqrt'],
    'max_depth': [10, 20, 30, 40, 50, None],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

# Create and train the model
print("Training model...")
rf = RandomForestRegressor()
model = RandomizedSearchCV(estimator=rf, param_distributions=params, 
                          n_iter=10, cv=3, verbose=2, n_jobs=-1)
model.fit(X_train, y_train)

# Save the model
print("Saving model...")
model_path = os.path.join(os.path.dirname(__file__), 'model', 'flight_prediction.pkl')
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

print("Model training completed and saved successfully!")

# Print model performance
print("\nModel Performance:")
print(f"Training Score: {model.score(X_train, y_train):.4f}")
print(f"Testing Score: {model.score(X_test, y_test):.4f}")
