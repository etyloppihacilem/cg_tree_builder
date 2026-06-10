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
import re
from datetime import datetime

from sympy import sympify, S
from tibs import Mutibs


class ODCRes:
    re_offset = re.compile(r"(.*)\[(\d*)\]")

    def __init__(self, result: dict, sim):
        self.name = result["name"]
        self.function = sympify(result["function_sympy"])
        self.pattern = Mutibs()
        self.offset = 0

        self.signals = {}
        for s in self.function.atoms():
            sym = str(s)
            match = ODCRes.re_offset.match(sym)
            if match is not None:
                self.offset = int(match.group(2))
                sym = match.group(1)
            try:
                sig = sim.find_data([sym])
            except re.PatternError as e:
                print(f"problem with: {sym}")
                raise e
            if sig is None:
                print(f"[ERROR] Signal {sym} was not found.")
                raise ValueError
            self.signals[str(s)] = sig["name"]
            self.sim = sim
            self.correspondance = {}

    def getBitValue(self, data):
        if len(data[1]) <= self.offset:
            return "0"
        return data[1][self.offset]

    def calculate(self, time):
        for symbol in self.function.atoms():
            data = self.sim.getSigAtTime(time, str(self.signals[str(symbol)]))
            value = self.getBitValue(data)
            if value == "X":
                print("Undefined behavior !!")
                print("")
                self.correspondance[symbol] = False
                # could be NaN but X does not go into Mutibs...
            elif value == "0":
                self.correspondance[symbol] = False
            elif value == "1":
                self.correspondance[symbol] = True
        result = self.function.subs(self.correspondance)
        return 1 if result == S.true else 0

    def addResult(self, val, bindex):
        if bindex >= len(self.pattern):
            self.pattern.extend([0] * (bindex - len(self.pattern) + 1))
        self.pattern[bindex] = val

    def to_dict(self):
        return {"name": self.name, "pattern": str(self.pattern)}


class ODCResults:
    def __init__(self, filename, sim):
        print(f"Loading '{filename}', looking for nets into vcd, could take a while.")
        with open(filename) as f:
            data = json.load(f)
        self.data = []

        start = datetime.now()

        for index, d in enumerate(data["odc_results"]):
            self.data.append(ODCRes(d, sim))

        end = datetime.now()
        print(f"Elapsed time: {str(end - start).split('.')[0]} seconds")

        self.sim = sim
        print("... loaded.")

    def stepAtTime(self, time):
        for sig in self.data:
            sig.calculate(time)

    def saveToFile(self, filename):
        print(f"Writing patterns to {filename}")
        with open(filename, "w") as f:
            json.dump([s.to_dict() for s in self.data], f, indent=2)
