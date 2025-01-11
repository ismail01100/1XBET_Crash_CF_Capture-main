import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score 
from sklearn.ensemble import HistGradientBoostingRegressor
import joblib

def preprocess_data(data):
    # Convert numerical columns to appropriate data types
    data['NumberOfPlayers'] = data['NumberOfPlayers'].str.replace('NumberOfPlayers: ', '').astype(float)
    data['TotalBet'] = data['TotalBet'].str.replace('TotalBet: ', '').astype(float)
    data['TotalWinning'] = data['TotalWinning'].str.replace('TotalWinning: ', '').astype(float)
    data['OnCash'] = data['OnCash'].str.replace('OnCash: ', '').astype(float)
    
    # Convert 'Time' column to datetime type
    data['Time'] = data['Time'].str.replace('Time: ', '')  # Remove 'Time:' prefix
    data['Time'] = pd.to_datetime(data['Time'], errors='coerce')
    
    # Handle rows with NaT (Not a Time) values
    data = data.dropna(subset=['Time'])
    
    # Extract hour, minute, and second as separate columns
    data['Hour'] = data['Time'].dt.hour
    data['Minute'] = data['Time'].dt.minute
    data['Second'] = data['Time'].dt.second
    
    # Replace 0 values with NaN in NumberOfPlayers and TotalWinning
    data['NumberOfPlayers'] = data['NumberOfPlayers'].replace(0, np.nan)
    data['TotalWinning'] = data['TotalWinning'].replace(0, np.nan)
    
    # Fill NaN values with 0
    data['NumberOfPlayers'] = data['NumberOfPlayers'].fillna(0)
    data['TotalWinning'] = data['TotalWinning'].fillna(0)
    
    return data


def train_best_model(X, y):
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Best model parameters obtained from tuning
    best_params = {'learning_rate': 0.2, 'max_iter': 300, 'max_leaf_nodes': 15}
    
    # Initialize the model with the best parameters
    model = HistGradientBoostingRegressor(**best_params)
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Evaluate the model
    train_rmse = mean_squared_error(y_train, model.predict(X_train), squared=False)
    test_rmse = mean_squared_error(y_test, model.predict(X_test), squared=False)
    
    # Calculate R^2 score (accuracy)
    train_r2 = r2_score(y_train, model.predict(X_train))
    test_r2 = r2_score(y_test, model.predict(X_test))
    
    print("Best Model Parameters:", best_params)
    print("Train RMSE:", train_rmse)
    print("Test RMSE:", test_rmse)
    print("Train R^2 Score (Accuracy): {:.2f}%".format(train_r2 * 100))
    print("Test R^2 Score (Accuracy): {:.2f}%".format(test_r2 * 100))
    
    return model


def calculate_accuracy(y_true, y_pred, threshold_percentage):
    # Calculate the threshold value
    threshold = threshold_percentage / 100 * y_true.mean()
    
    # Count the number of correct predictions
    correct_predictions = np.sum(np.abs(y_true - y_pred) <= threshold)
    
    # Calculate accuracy
    accuracy = correct_predictions / len(y_true)
    
    return accuracy


def main():
    # Load the data from data.csv into a DataFrame
    data = pd.read_csv('data.csv', sep=',', header=None, names=['Round', 'Time', 'NumberOfPlayers', 'TotalBet', 'TotalWinning', 'OnCash'])

    # Convert columns to appropriate data types and preprocess data
    data = preprocess_data(data)

    # Select features (X) and target variable (y)
    X = data[['NumberOfPlayers', 'TotalBet', 'TotalWinning', 'Hour', 'Minute', 'Second', 'OnCash']]
    y = data['OnCash']

    # Train the best model
    model = train_best_model(X, y)
    
    # Make predictions on the test set
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    y_test_pred = model.predict(X_test)

    # Calculate accuracy based on correct predictions
    threshold_percentage = 5  # ±5% threshold
    accuracy = calculate_accuracy(y_test, y_test_pred, threshold_percentage)
    
    print("Accuracy based on correct predictions (±{}% threshold): {:.2f}%".format(threshold_percentage, accuracy * 100))

    # Save the trained model
    joblib.dump(model, 'crash_prediction_best_model.joblib')

if __name__ == "__main__":
    main()
