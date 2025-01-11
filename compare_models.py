import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import numpy as np

# Load the test dataset
test_data = pd.read_csv('data.csv', sep=',', header=None, names=['Round', 'Time', 'NumberOfPlayers', 'TotalBet', 'TotalWinning', 'OnCash'])

# Define the preprocessing function
def preprocess_data(data):
    data['NumberOfPlayers'] = data['NumberOfPlayers'].str.replace('NumberOfPlayers: ', '').astype(float)
    data['TotalBet'] = data['TotalBet'].str.replace('TotalBet: ', '').astype(float)
    data['TotalWinning'] = data['TotalWinning'].str.replace('TotalWinning: ', '').astype(float)
    data['OnCash'] = data['OnCash'].str.replace('OnCash: ', '').astype(float)
    data['Time'] = data['Time'].str.replace('Time: ', '')
    data['Time'] = pd.to_datetime(data['Time'], errors='coerce')
    data = data.dropna(subset=['Time'])
    data['Hour'] = data['Time'].dt.hour
    data['Minute'] = data['Time'].dt.minute
    data['Second'] = data['Time'].dt.second
    data.replace(0, np.nan, inplace=True)
    return data

# Preprocess the test data
test_data = preprocess_data(test_data)

# Extract features and target variable from the test data
X_test = test_data[['NumberOfPlayers', 'TotalBet', 'TotalWinning', 'Hour', 'Minute', 'Second', 'OnCash']]
y_test = test_data['OnCash']

# Load the models
model_without_tuning = joblib.load('crash_prediction_model.joblib')
model_with_tuning = joblib.load('crash_prediction_model_with_tuning.joblib')

# Predictions for the model without tuning
y_pred_without_tuning = model_without_tuning.predict(X_test)
rmse_without_tuning = mean_squared_error(y_test, y_pred_without_tuning, squared=False)
r2_without_tuning = r2_score(y_test, y_pred_without_tuning)

# Predictions for the model with tuning
y_pred_with_tuning = model_with_tuning.predict(X_test)
rmse_with_tuning = mean_squared_error(y_test, y_pred_with_tuning, squared=False)
r2_with_tuning = r2_score(y_test, y_pred_with_tuning)

# Print metrics
print("Model without tuning - RMSE:", rmse_without_tuning, "R^2 Score:", r2_without_tuning)
print("Model with tuning - RMSE:", rmse_with_tuning, "R^2 Score:", r2_with_tuning)
