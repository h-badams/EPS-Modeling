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

# Identify sharp drop and rise
voltage_diff = df["Voltage"].diff()
sharp_drop_idx = voltage_diff.idxmin()
sharp_rise_idx = voltage_diff.idxmax()

sharp_drop_time = df.loc[sharp_drop_idx, "Time (s)"]
sharp_rise_time = df.loc[sharp_rise_idx, "Time (s)"]
sharp_drop_magnitude = abs(voltage_diff.min())
sharp_rise_magnitude = abs(voltage_diff.max())

print(f"Sharp drop at {sharp_drop_time:.3f} s with magnitude {sharp_drop_magnitude:.6f} V")
print(f"Sharp rise at {sharp_rise_time:.3f} s with magnitude {sharp_rise_magnitude:.6f} V")

# Adjust the voltage in the interval between drop and rise
df.loc[(df["Time (s)"] >= sharp_drop_time) & (df["Time (s)"] < sharp_rise_time), "Voltage"] += sharp_drop_magnitude

# Plot data
plt.figure(figsize=(8, 5))
plt.plot(df["Time (s)"], df["Voltage"], marker='o', linestyle='-')
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Voltage vs Time")
plt.grid()
plt.show()
