from SALib.analyze.sobol import analyze
from SALib.sample.sobol import sample
from SALib.test_functions import Ishigami
import numpy as np

# Define the model inputs
problem = {
    'num_vars': 3,
    'names': ['x1', 'x2', 'x3'],
    'bounds': [[-3.14159265359, 3.14159265359],
               [-3.14159265359, 3.14159265359],
               [-3.14159265359, 3.14159265359]],
    

}

# Generate samples
param_values = sample(problem, 1024)
print([problem[k] for k in problem.keys()])
print(param_values)
# Run model (example)
Y = Ishigami.evaluate(param_values)
print(Y)
# Perform analysis
Si = analyze(problem, Y, print_to_console=True)

# Print the first-order sensitivity indices
print(Si['S1'])
print(Si['S2'])
print(Si['ST'])