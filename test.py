import numpy as np
def foo(x, base=0.05):
    return np.around(base*np.around(x/base), 2)

print(foo(0.15))