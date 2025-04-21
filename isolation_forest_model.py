!pip install pandas scikit-learn
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import joblib

def isolation_forest_model():
    #loaidng simulated data
    df=pd.read_csv('simulated_data.csv')

    label_encoder=LabelEncoder()
    # Handle unknown login_location values by assigning them to a default category ("Unknown")
    df['login_location'] = df['login_location'].fillna('Unknown')  # Handle missing values
    known_locations = df['login_location'].unique()
    df['login_location'] = df['login_location'].apply(lambda x: x if x in known_locations else 'Unknown')

    df['login_locations'] = label_encoder.fit_transform(df['login_location'])
    # features
    X = df[['login_time', 'failed_attempts', 'login_locations']]

    #split for training
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

    #scale data
    scaler=StandardScaler()
    X_train_scaled=scaler.fit_transform(X_train)
    X_test_scaled=scaler.transform(X_test)

    # Train the model
    model = IsolationForest(contamination=0.1, random_state=42)  # 30% assumed anomalies
    model.fit(X_train_scaled)

    X_test = X_test.copy() 
    X_test['anomaly'] = model.predict(X_test_scaled)
    X_test['anomaly'] = X_test['anomaly'].map({1: 'Normal', -1: 'Suspicious'})

    suspicious = df.loc[X_test[X_test['anomaly'] == 'Suspicious'].index]
    print("Flagged Suspicious Logins:")
    print(suspicious)
    # Save the model and scaler
    joblib.dump(model,'isolation_forest_model.pkl')
    joblib.dump(scaler,'scaler.pkl')
    joblib.dump(label_encoder,'label_encoder.pkl')
if __name__ == "__main__":
    isolation_forest_model()
