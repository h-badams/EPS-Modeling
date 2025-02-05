'''
Author: Henry Adams (2025)

HS2 Battery Pack Modeling - Version 1

Minimum Viable Product:

    -Battery Pack of LG M50 Batteries w/ Parameters from Chen2020 Dataset
    (Use liionpack to describe circuit configuration)
    Easily modifiable pack configuration

    -A way to represent both charge/discharge data (solar panel power production & system loads),
    and run experiments with that data

    -A way to plot relevant **pack** variables against each other

Features to add after that:

    -Validation against a test datasheet for our specific battery (LG MJ 1)
    
    -Battery degradation, either through a physics-based mechanism, or through some other
    rule (need to further consult PyBaMM Docs for more info on this)
'''

import numpy as np
import matplotlib.pyplot as plt

import pybamm
import liionpack as lp

# TODO: Be able to import "charging" and "load" numpy arrays, where charging_data[i]
# is the amount of energy/voltage/amperage being provided by the solar panels (not sure on details yet),
# from (10*i) seconds to (10*(i+1)) seconds, and like wise load_data[i] is the discharge current (I think)
# from time = 10*i to time = 10(i+1)

# Currently doing everything in the span of one orbit, will change this

orbit_duration = 90 # minutes
sampling_rate = 6 # updates / min (update every 10 seconds)

times = np.linspace(0, orbit_duration, orbit_duration * sampling_rate)

# Replace the arrays below with actual estimates on our charge/discharge

charging_data = 2 * np.cos(np.pi * times / 200) # These are just stand-ins for real data
load_data = 2 + 0.5 * np.cos(np.pi * times / 50)

plt.plot(times, load_data)
plt.plot(times, charging_data)
plt.show()

# Pick a set of Parameters (Until something better comes along, we will use Chen 2020)

params = pybamm.ParameterValues('Chen2020')

start_voltage = params['Open-circuit voltage at 100% SOC [V]']

# Initialize pack configuration

series = 11
parallel = 1
num_cells = series * parallel

oc_voltage_init = series * start_voltage

i_mag = 5.0 
# TODO: I know this is the value of a current source in the circuit diagram, but IDK what it does
# It's possible this should also be 10A since our new battery is closer to 10A

wire_resistance = 1e-3 # internal resistance of connections between batteries

netlist = lp.setup_circuit(Np=parallel, Ns=series, 
                           Rb=wire_resistance, Rc=wire_resistance, Ri=wire_resistance,
                           V=oc_voltage_init, I=i_mag)

# Setup an experiment that accurately represents subsystem loads and power we're getting

