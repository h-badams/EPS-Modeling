import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Read the CSV file, skipping initial metadata rows
df = pd.read_csv("Comparison with Physical Battery/Data/Trace 2025-03-27 3.csv", skiprows=8)

# Rename columns for clarity
df.columns = ["Time", "Voltage", "Power"]

# Convert Time column to datetime objects
df["Time"] = pd.to_datetime(df["Time"])

# Calculate time in seconds from the first timestamp
df["Time (s)"] = (df["Time"] - df["Time"].iloc[0]).dt.total_seconds()

# Define the trimming duration
n = 0  # Change this value as needed

# Filter the DataFrame to remove first and last n seconds
df = df[(df["Time (s)"] >= n) & (df["Time (s)"] <= df["Time (s)"].iloc[-1] - n)]

# Plot data
plt.figure(figsize=(8, 5))
plt.plot(df["Time (s)"], df["Voltage"], marker='o', linestyle='-')
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Voltage vs Time (Trimmed)")
plt.grid()
plt.show()
