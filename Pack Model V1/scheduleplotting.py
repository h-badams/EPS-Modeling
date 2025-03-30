import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('Pack Model V1/power_schedule.csv')

ig, axes = plt.subplots(2, 1, figsize=(8, 10), sharex=True)

# Plot y1 vs x
axes[0].plot(df['Time (min)'], df['Total Power (W)'], marker='o', linestyle='-', color='b')
axes[1].set_xlabel('Time (min)')
axes[0].set_ylabel('Total Power (W)')
axes[0].set_title('Plot of Power vs. Time')
axes[0].grid(True)

# Plot y2 vs x
axes[1].plot(df['Time (min)'], df['Net Discharge Current (A)'], marker='s', linestyle='-', color='r')
axes[1].set_xlabel('Time (min)')
axes[1].set_ylabel('Current (A)')
axes[1].set_title('Plot of Discharge Current vs. Time')
axes[1].grid(True)

# Adjust layout for better spacing
plt.tight_layout()
plt.show()