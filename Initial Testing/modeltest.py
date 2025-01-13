import pybamm
import numpy as np
import matplotlib.pylab as plt

# basic example with a differential equation model

model = pybamm.BaseModel("test")
y = pybamm.Variable("y")
a = pybamm.InputParameter("a")

# set up differential equation
model.rhs = {y: a * y}
model.initial_conditions = {y : 1}

# print(model.rhs[y])

# choose a better solver for more complicated DEs
solver = pybamm.CasadiSolver(
    mode="fast", rtol=1e-8, atol=1e-8
)

timesteps = 100
t_eval = np.linspace(0, 1, timesteps)
sols = []

'''for a_value in [1,2,3,4]:
    solution = solver.solve(model, t_eval, inputs={'a': a_value})
    plt.plot(solution.t, solution.y.T, label='a={}'.format(a_value))

plt.xlabel('t')
plt.ylabel('y')
plt.legend()
plt.show()'''

# example with a DFN battery model

model = pybamm.lithium_ion.DFN()
geometry = model.default_geometry
params = pybamm.ParameterValues('Chen2020')
params.update({'Current function [A]': '[input]'})
params.process_geometry(geometry)
params.process_model(model)

var = pybamm.standard_spatial_vars
var_pts = {var.x_n: 30, var.x_s: 30, var.x_p: 30, var.r_n: 10, var.r_p: 10}
mesh = pybamm.Mesh(geometry, model.default_submesh_types, var_pts)

disc = pybamm.Discretisation(mesh, model.default_spatial_methods)
disc.process_model(model)

timesteps = 1000
t_eval = np.linspace(0, 3 * 3600, timesteps)
solver = pybamm.CasadiSolver(mode='safe', atol = 1e-6, rtol = 1e-3)

# testing different current draws, plotting voltage
for x in [0.4, 0.8, 1.2, 1.6, 2.0]:
    solution = solver.solve(model, t_eval, inputs = {'Current function [A]': x})
    plt.plot(t_eval, solution['Terminal voltage [V]'](t_eval), label='Current function [A] = {}'.format(x))
    
plt.xlabel('t')
plt.ylabel('V')
plt.legend()
plt.show()