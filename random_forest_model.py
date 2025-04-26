import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score, cross_val_predict
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Load dataset
df = pd.read_csv('simulated_data.csv')

# Handle missing values and encode categorical features
label_encoder = LabelEncoder()
df['login_location'] = df['login_location'].fillna('Unknown')  # Handle missing values
known_locations = df['login_location'].unique()
df['login_location'] = df['login_location'].apply(lambda x: x if x in known_locations else 'Unknown')

df['login_locations'] = label_encoder.fit_transform(df['login_location'])


X = df[['login_time', 'failed_attempts', 'login_locations']]
y = df['label']


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')

# Stratified K-Fold Cross-Validation
kf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)


cross_val_results = cross_val_score(model, X_scaled, y, cv=kf, scoring='accuracy')


print("Cross-Validation Accuracy: ", cross_val_results.mean())


model.fit(X_scaled, y)


y_pred = cross_val_predict(model, X_scaled, y, cv=kf)

# Evaluate the Model Performance
print("\n--- Random Forest Model Evaluation ---")
print("Accuracy:", accuracy_score(y, y_pred))
print("Precision (anomaly detection):", precision_score(y, y_pred, pos_label=-1))
print("Recall (anomaly detection):", recall_score(y, y_pred, pos_label=-1))
print("F1 Score (anomaly detection):", f1_score(y, y_pred, pos_label=-1))
print("Confusion Matrix:\n", confusion_matrix(y, y_pred))

# Hyperparameter tuning (optional)
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [50, 100, 200],
    'max_depth': [None, 10, 20, 30],
    'min_samples_split': [2, 5, 10],
}

grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=kf, scoring='accuracy')
grid_search.fit(X_scaled, y)

# Best parameters from grid search
print("\nBest parameters found: ", grid_search.best_params_)


#new_data = pd.read_csv('new_data.csv')

# Handle missing values and encode categorical features in new data
#new_data['login_location'] = new_data['login_location'].fillna('Unknown')
#new_data['login_location'] = new_data['login_location'].apply(lambda x: x if x in known_locations else 'Unknown')
#new_data['login_locations'] = label_encoder.transform(new_data['login_location'])

# Scale the new data
#new_data_scaled = scaler.transform(new_data[['login_time', 'failed_attempts', 'login_locations']])

# Make predictions on new data
#predictions = model.predict(new_data_scaled)'''
# Save the Random Forest model
#save_directory = r" path to save the file "
#joblib.dump(model, save_directory + 'random_forest_model.pkl');
#joblib.dump(scaler, save_directory + 'scaler.pkl');
#joblib.dump(label_encoder, save_directory + 'label_encoder.pkl');
