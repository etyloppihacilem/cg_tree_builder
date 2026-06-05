# ###################################646f75627420796f7572206f776e206578697374656e6365###################################
#
#              """          ODCResults.py
#       -\-    _|__
#        |\___/  . \        Created on 04 Jun. 2026 at 17:06
#        \     /(((/        by hmelica
#         \___/)))/         hmelica@student.42.fr
#
# ######################################################################################################################

import json

from sympy import sympify
from tibs import Mutibs


class ODCRes:
    def __init__(self, result: dict, sim, cor):
        self.name = result["name"]
        self.function = sympify(result["function_sympy"])
        self.pattern = Mutibs()

        self.signals = {}
        for s in self.function.atoms():
            sig_name = cor.get_signal_name(str(s))
            if sig_name is None:
                print(f"[ERROR] Signal {str(s)} has no correspondance.")
                raise ValueError
            self.signals[str(s)] = sig_name


class ODCResults:
    def __init__(self, filename, sim, cor):
        print(f"Loading '{filename}'", end=" ", flush=True)
        print("")
        with open(filename) as f:
            data = json.load(f)
        self.data = []
        for d in data["odc_results"]:
            self.data.append(ODCRes(d, sim, cor))
        print("... loaded.")
