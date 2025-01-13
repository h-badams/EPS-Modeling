import pybamm
import numpy as np
import matplotlib.pyplot as plt

pybamm.set_logging_level("NOTICE")

models = []
models.append(pybamm.lithium_ion.SPMe())
models.append(pybamm.lithium_ion.DFN())

parameter_values = pybamm.ParameterValues('Chen2020')

# CCCV experiment

experiment = pybamm.Experiment([
    ("Discharge at 0.5C until 3.3V",
     "Rest for 1 hour"),
    ("Charge at 0.5C until 4.2V",
     "Hold at 4.2V until 65mA"),
    ("Rest for 1 hour")
])

sols = []

for model in models:
    sim = pybamm.Simulation(model, experiment=experiment, parameter_values=parameter_values)
    sols.append(sim.solve())
    sim.solution.cycles[1].plot(["Terminal voltage [V]", "Current [A]", "Throughput capacity [A.h]"])

    
# pybamm.dynamic_plot(sols)
