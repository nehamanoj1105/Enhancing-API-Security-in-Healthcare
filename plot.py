import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import seaborn as sns

# Set a clean style
sns.set(style="whitegrid")

# 1. Login Success vs Failure
success = 93  # % Success
failure = 7   # % Failure

plt.figure(figsize=(6,4))
sns.barplot(x=["Success", "Failure"], y=[success, failure], palette="viridis")
plt.title("Login Success vs Failure Rate")
plt.ylabel("Percentage (%)")
plt.ylim(0, 100)
plt.show()

# 2. Unauthorized Access Blocked over Time
# Simulating 7 days of data
days = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
unauthorized_attempts = [0, 1, 0, 2, 0, 1, 0]  # Low, spikes when attack simulated

plt.figure(figsize=(8,5))
sns.lineplot(x=days, y=unauthorized_attempts, marker="o", color="red")
plt.title("Unauthorized Access Attempts Blocked Over Time")
plt.xlabel("Day")
plt.ylabel("Blocked Attempts")
plt.show()

# 3. API Response Time vs Number of Users
users = [1, 5, 10, 20, 50, 100, 150]
response_times = [100, 120, 140, 180, 250, 400, 550]  # ms

plt.figure(figsize=(8,5))
sns.lineplot(x=users, y=response_times, marker="o", color="blue")
plt.title("API Response Time vs Number of Concurrent Users")
plt.xlabel("Number of Users")
plt.ylabel("Response Time (ms)")
plt.show()

