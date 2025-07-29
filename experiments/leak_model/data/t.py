from wntr.epanet import toolkit as tk
lib = tk._lib                    # the ctypes.CDLL handle
print("loaded dylib:", lib._name)