import pandas as pd
import numpy as np
import random

known_locations = ['Kollam', 'Coimbatore', 'Kochi', 'Chennai']
unusual_locations = ['Delhi', 'Mumbai', 'Hyderabad', 'Noida']

normal_hours = list(range(6, 22))  # 6 AM to 10 PM
unusual_hours = list(range(0, 6)) + list(range(22, 24))  # Night

# Helper function to create an anomaly row
def create_anomaly():
    login_time = random.choice(normal_hours + unusual_hours)
    login_location = random.choice(known_locations + unusual_locations)
    failed_attempts = random.randint(0, 9)
    
    # Count suspicious traits
    suspicious_traits = 0
    if login_time in unusual_hours: suspicious_traits += 1
    if login_location in unusual_locations: suspicious_traits += 1
    if failed_attempts > 3: suspicious_traits += 1

    label = -1 if suspicious_traits >= 1 else 1
    return {
        'login_time': login_time,
        'failed_attempts': failed_attempts,
        'login_location': login_location,
        'label': label
    }

# Generate data
normal_data = []
for _ in range(700):
    normal_data.append({
        'login_time': random.choice(normal_hours),
        'failed_attempts': random.choice([0, 1, 2]),
        'login_location': random.choice(known_locations),
        'label': 1
    })

suspicious_data = [create_anomaly() for _ in range(300)]

# Combine & Shuffle
df = pd.DataFrame(normal_data + suspicious_data)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# Save
df.to_csv('simulated_data.csv', index=False)
print("hospital login data saved!")
