
# This code is for comparing our real world test data to our pybamm predictions

#%%
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import pybamm
import liionpack as lp


#%%
params = pybamm.ParameterValues('Chen2020')


# These params don't really seem to do anything?
params.update({'Nominal cell capacity [A.h]': 3.5})
params.update({'Open-circuit voltage at 0% SOC [V]': 2.5})
params.update({'Open-circuit voltage at 100% SOC [V]': 4.2})
params.update({'Upper voltage cut-off [V]': 4.2})
params.update({'Lower voltage cut-off [V]': 2.5})
params.update({'Current function [A]': 8.0})

# trying physical params
badness_factor = 0.85

init_electrolyte = params['Initial concentration in electrolyte [mol.m-3]']
init_neg_elec = params['Initial concentration in negative electrode [mol.m-3]']
init_pos_elec = params['Initial concentration in positive electrode [mol.m-3]']

params.update({'Initial concentration in electrolyte [mol.m-3]' : init_electrolyte * badness_factor})
params.update({'Initial concentration in negative electrode [mol.m-3]' : init_neg_elec * badness_factor})
params.update({'Initial concentration in positive electrode [mol.m-3]' : init_pos_elec * badness_factor})

### Physical Test Values ###

starting_voltage = 3.54 # voltage where we started the physical test
discharge_current = 2.5

minutes = 20

#%%
experiment = pybamm.Experiment(
    [10 * (f"Discharge at 0.5A until {starting_voltage}V",
     "Rest for 1 hour"),
     (f"Discharge at {discharge_current}A for {minutes} minutes",
    "Rest for 30 seconds")
    ], period="10 seconds"
)

models = [pybamm.lithium_ion.SPM({"SEI": "ec reaction limited"}), pybamm.lithium_ion.SPMe(), pybamm.lithium_ion.DFN()]

sims = [pybamm.Simulation(model=model, parameter_values=params, experiment=experiment) for model in models]
sols = [sim.solve() for sim in sims]

def run_experiment(test_conditions, params):
    starting_voltage, discharge_current, minutes = test_conditions
    experiment = pybamm.Experiment(
        [10 * (f"Discharge at 0.5A until {starting_voltage}V",
        "Rest for 1 hour"),
        (f"Discharge at {discharge_current}A for {minutes} minutes",
        "Rest for 30 seconds")
        ], period="10 seconds"
    )
    model = pybamm.lithium_ion.DFN()
    sim = pybamm.Simulation(model=model, parameter_values=params, experiment=experiment)
    sol = sim.solve()
    
    return sol['Time [s]'].entries, sol['Terminal voltage [V]'].entries


#%%
pybamm.dynamic_plot(sols, ["Voltage [V]"])

times = [sol["Time [s]"].entries for sol in sols]
voltages = [sol['Terminal voltage [V]'].entries for sol in sols]

plt.plot(times[0], voltages[0])

#%%
### Chose model to compare real world data data to
time_vals = times[2]
voltage_vals = voltages[2]

cutoff_time = time_vals[-1] - ((minutes+0.5)*60.0)

indices = np.where(time_vals >= cutoff_time)[0]

time_vals = time_vals[indices]
pybamm_time_vals = time_vals - time_vals[0]
pybamm_voltage_vals = voltage_vals[indices]

#%%
### Get Real Data

df = pd.read_csv("Comparison with Physical Battery/Data/Trace 2025-03-27 4.csv", skiprows=8)

# Rename columns for clarity
df.columns = ["Time", "Voltage", "Power"]

# Convert Time column to datetime objects
df["Time"] = pd.to_datetime(df["Time"])

# Calculate time in seconds from the first timestamp
df["Time (s)"] = (df["Time"] - df["Time"].iloc[0]).dt.total_seconds()

# Identify sharp drop and rise
voltage_diff = df["Voltage"].diff()
sharp_drop_idx = voltage_diff.idxmin()
sharp_rise_idx = voltage_diff.idxmax()

sharp_drop_time = df.loc[sharp_drop_idx, "Time (s)"]
sharp_rise_time = df.loc[sharp_rise_idx, "Time (s)"]
sharp_drop_magnitude = abs(voltage_diff.min())
sharp_rise_magnitude = abs(voltage_diff.max())

# Adjust the voltage in the interval between drop and rise
df.loc[(df["Time (s)"] >= sharp_drop_time) & (df["Time (s)"] < sharp_rise_time), "Voltage"] += sharp_drop_magnitude

# %%
real_time_vals = df['Time (s)'].values
real_voltage_vals = df['Voltage'].values

print(real_voltage_vals)
# %%
# Create plot
plt.figure(figsize=(10, 5))
plt.plot(real_time_vals, real_voltage_vals, label="Real Test Data", color="blue", linestyle="-")  # Solid line
plt.plot(pybamm_time_vals, pybamm_voltage_vals, label="DFN  Model", color="red", linestyle="--")  # Dashed line

# Labels & legend
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Real Test Data vs PyBaMM Predictions (20 min, CC 2A discharge)")
plt.legend()
plt.grid(True)

# Show plot
plt.show()

if __name__ == '__main__':
    
    # load all test params (discharge curve and starting info)
    
    initial_conditions = [(), (), ()] # tuples are (starting voltage, minutes of test)
    
    # test_curves = get_discharge_curves(file paths)
    
    # below we run a lot of pybamm experiments
    param_sets = ['Chen2020']
    params_to_change = []
    
    floats_to_change_by = [0.8 + 0.05 * i for i in range(5)]
    increment = 0.05
    min_float = 0.8
    max_float = 1.0
    
    for x in param_sets:
        params = pybamm.ParameterValues[x]
        
        pointer = 0
        place_values = [min_float for p in params_to_change]
        
        while pointer < len(params_to_change):
            pointer = 0
            
            for i, param in enumerate(params_to_change):
                params.update({param : params[param] * place_values[i]})

            # run pybamm experiments (one for each piece of test data)
            
            for test in test_set:
                initial_condition, discharge_curve = test
                
                prediction_curve = run_experiment(test_conditions=())
                
                # measure mse
                # record if best
            
            while pointer < len(params_to_change) and abs(place_values[pointer] - max_float) < 1e-9:
                place_values[pointer] = min_float
                pointer += 1
            if pointer < len(params_to_change):
                place_values[pointer] += increment
            

    # plot best, print mse