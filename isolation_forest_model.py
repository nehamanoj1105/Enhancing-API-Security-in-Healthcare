import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder
import joblib

def isolation_forest_model():
    # loading simulated data
    df = pd.read_csv('simulated_data.csv')

    label_encoder = LabelEncoder()
    df['login_locations'] = label_encoder.fit_transform(df['login_location'])

    X = df[['login_time', 'failed_attempts', 'login_locations']]

    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X)

    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(X_train_scaled)

    df['anomaly'] = model.predict(X_test_scaled)
    df['anomaly'] = df['anomaly'].map({1: 'Normal', -1: 'Suspicious'})

    suspicious = df[df['anomaly'] == 'Suspicious']
    print("Flagged Suspicious Logins:")
    print(suspicious)

    # Save the model and scaler
    joblib.dump(model, 'isolation_forest_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl') 


if __name__ == "__main__":
    isolation_forest_model()
