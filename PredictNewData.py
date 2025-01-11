import pandas as pd
import joblib  

# Load the trained model
model = joblib.load('crash_prediction_best_model.joblib')

# Read the last entry from the data.csv file
data = pd.read_csv('data.csv', sep=',', header=None, names=['Round', 'Time', 'NumberOfPlayers', 'TotalBet', 'TotalWinning', 'OnCash'])
last_entry = data.iloc[-1]  # Get the last row

# Preprocess the last entry
last_entry['Time'] = last_entry['Time'].split(': ')[1]  # Extract time without the prefix
last_entry['NumberOfPlayers'] = float(last_entry['NumberOfPlayers'].split(': ')[1])
last_entry['TotalBet'] = float(last_entry['TotalBet'].split(': ')[1])
last_entry['TotalWinning'] = float(last_entry['TotalWinning'].split(': ')[1])
last_entry['OnCash'] = float(last_entry['OnCash'].split(': ')[1])  # Include 'OnCash' value

# Extract Hour, Minute, and Second from the 'Time' column
time_components = last_entry['Time'].split(':')
last_entry['Hour'] = int(time_components[0])
last_entry['Minute'] = int(time_components[1])
last_entry['Second'] = int(time_components[2])

# Extract relevant features, including 'OnCash'
X_new = last_entry[['NumberOfPlayers', 'TotalBet', 'TotalWinning', 'OnCash', 'Hour', 'Minute', 'Second']].values.reshape(1, -1)

# Predict the 'OnCash' value for the new round
prediction = model.predict(X_new)

# Print the previous and predicted 'OnCash' values
previous_oncash = last_entry['OnCash']
print(f"Previous OnCash value: {previous_oncash}")
print(f"Predicted OnCash value for the last round: {prediction[0]}")
