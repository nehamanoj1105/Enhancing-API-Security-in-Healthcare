import joblib
model = joblib.load('SS-Model/xgb_model.pkl')

print(model)
print("Is fitted?", hasattr(model, 'feature_importances_'))  # XGBoost specific

