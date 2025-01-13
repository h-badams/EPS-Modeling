# HS2 Battery Modeling - v0
# no degradation variables yet
# just one lithium ion battery
# goal here is to experiment with multiple models, 
# and try to fashion a roughly representative battery + simulation / experiment

import pybamm
import numpy as np

run_solve = True

# until we get into more detail with simulation stuff, simulation variables are listed here
hours = 12

# this is how we set specifics of the battery
# using battery params given by a paper
params = pybamm.ParameterValues('OKane2022')

# currently some issues as to what can be written as a function - pybamm is picky
def custom_current(t):
    # return pybamm.maximum(0, 1 * pybamm.sin(t / 300))
    # return 0.2 + 0.4 * pybamm.sin(t / 3600)
    return 0.5

# check - is this making a bigger pack - or breaking a battery into smaller parts?
# params['Number of cells connected in series to make a battery'] = 5.0
# params['Number of electrodes connected in parallel to make a cell'] = 2.0

# can change current applied
params['Current function [A]'] = custom_current

# can also change params this way
# note - don't pass a chemistry into Parameter values - this is deprecated
params.update({"Ambient temperature [K]": 268.15})
params.update({"Upper voltage cut-off [V]": 4.21})
# params_values.update({"Lithium plating kinetic rate constant [m.s-1]": 1E-9})
params.update({"Lithium plating transfer coefficient": 0.5})
params.update({"Dead lithium decay constant [s-1]": 1e-4})

# using several different battery models, of which DFN is the most complex
models = [
    # pybamm.lithium_ion.SPM(),
    # pybamm.lithium_ion.SPMe(),
    pybamm.lithium_ion.DFN(),
    pybamm.lithium_ion.DFN(options={"thermal": "lumped", "lithium plating": "reversible"}, name="realisticDFN")
]

sols = []

# solve the simulation for each model
# still not sure how to customize simulations / experiments
if run_solve:
    for model in models:
        sim = pybamm.Simulation(model, parameter_values=params)
        sol = sim.solve([0, hours * 3600])
        sols.append(sol)
        
    pybamm.dynamic_plot(sols)