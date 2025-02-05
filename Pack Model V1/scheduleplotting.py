import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV file into a pandas DataFrame
df = pd.read_csv('power_schedule.csv')

plt.figure(figsize=(8, 6))
plt.plot(df['Time (min)'], df['Total Power (W)'], marker='o', linestyle='-', color='b')
plt.xlabel('Time (min)')
plt.ylabel('Total Power (W)')
plt.title('Plot of Power vs Time')
plt.grid(True)
plt.show()