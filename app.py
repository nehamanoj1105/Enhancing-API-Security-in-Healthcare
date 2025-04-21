from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder


db = SQLAlchemy()


model = joblib.load("isolation_forest_model.pkl")
scaler = joblib.load("scaler.pkl")

def create_app():
    app = Flask(__name__)
    
    
    app.config['SECRET_KEY'] = 'your_very_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    
    Swagger(app)
    db.init_app(app)

   
    @app.route('/')
    def home():
        return "Welcome to the Anomaly Detection API!"

    
    @app.route('/predict', methods=['POST'])
    def predict_anomaly():
        data = request.get_json()
        
        
        login_time = data['login_time']
        failed_attempts = data['failed_attempts']
        login_location = data['login_location']
        
       
        input_data = pd.DataFrame([[login_time, failed_attempts, login_location]], columns=['login_time', 'failed_attempts', 'login_location'])
        
        # Handle categorical data (if 'login_location' is a string)
        if isinstance(input_data['login_location'][0], str):
            encoder = LabelEncoder()
            input_data['login_location'] = encoder.fit_transform(input_data['login_location'])

        
        input_scaled = scaler.transform(input_data)

       
        prediction = model.predict(input_scaled)
        
       
        if prediction == -1:
            return jsonify({"message": "Anomaly detected"}), 200
        else:
            return jsonify({"message": "Normal login"}), 200
    
    from routes import register_routes
    register_routes(app)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
