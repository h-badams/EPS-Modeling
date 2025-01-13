import pybamm
import matplotlib.pyplot as plt
import os

os.chdir(pybamm.__path__[0] + "/..")

model = pybamm.lithium_ion.SPM({"SEI": "ec reaction limited"})
parameter_values = pybamm.ParameterValues("Mohtat2020")
parameter_values.update({"SEI kinetic rate constant [m.s-1]": 1e-14})

N = 10
cccv_experiment = pybamm.Experiment(
    [
        (
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/50",
            "Discharge at 1C until 3V",
            "Rest for 1 hour",
        )
    ]
    * N
)

charge_experiment = pybamm.Experiment(
    [
        (
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/50",
        )
    ]
)
rpt_experiment = pybamm.Experiment([("Discharge at C/3 until 3V",)])

sim = pybamm.Simulation(
    model, experiment=cccv_experiment, parameter_values=parameter_values
)
cccv_sol = sim.solve()
sim = pybamm.Simulation(
    model, experiment=charge_experiment, parameter_values=parameter_values
)
charge_sol = sim.solve(starting_solution=cccv_sol)
sim = pybamm.Simulation(
    model, experiment=rpt_experiment, parameter_values=parameter_values
)
rpt_sol = sim.solve(starting_solution=charge_sol)

# pybamm.dynamic_plot(rpt_sol.cycles[-1], ["Current [A]", "Voltage [V]"])

cccv_sols = []
charge_sols = []
rpt_sols = []
M = 5
for i in range(M):
    if i != 0:  # skip the first set of ageing cycles because it's already been done
        sim = pybamm.Simulation(
            model, experiment=cccv_experiment, parameter_values=parameter_values
        )
        cccv_sol = sim.solve(starting_solution=rpt_sol)
        sim = pybamm.Simulation(
            model, experiment=charge_experiment, parameter_values=parameter_values
        )
        charge_sol = sim.solve(starting_solution=cccv_sol)
        sim = pybamm.Simulation(
            model, experiment=rpt_experiment, parameter_values=parameter_values
        )
        rpt_sol = sim.solve(starting_solution=charge_sol)
    cccv_sols.append(cccv_sol)
    charge_sols.append(charge_sol)
    rpt_sols.append(rpt_sol)
    
# pybamm.dynamic_plot(rpt_sols[-1].cycles[-1], ["Current [A]", "Voltage [V]"])

cccv_cycles = []
cccv_capacities = []
rpt_cycles = []
rpt_capacities = []
for i in range(M):
    for j in range(N):
        cccv_cycles.append(i * (N + 2) + j + 1)
        start_capacity = (
            rpt_sol.cycles[i * (N + 2) + j]
            .steps[2]["Discharge capacity [A.h]"]
            .entries[0]
        )
        end_capacity = (
            rpt_sol.cycles[i * (N + 2) + j]
            .steps[2]["Discharge capacity [A.h]"]
            .entries[-1]
        )
        cccv_capacities.append(end_capacity - start_capacity)
    rpt_cycles.append((i + 1) * (N + 2))
    start_capacity = rpt_sol.cycles[(i + 1) * (N + 2) - 1][
        "Discharge capacity [A.h]"
    ].entries[0]
    end_capacity = rpt_sol.cycles[(i + 1) * (N + 2) - 1][
        "Discharge capacity [A.h]"
    ].entries[-1]
    rpt_capacities.append(end_capacity - start_capacity)
plt.scatter(cccv_cycles, cccv_capacities, label="Ageing cycles")
plt.scatter(rpt_cycles, rpt_capacities, label="RPT cycles")
plt.xlabel("Cycle number")
plt.ylabel("Discharge capacity [A.h]")
plt.legend()

plt.show()
