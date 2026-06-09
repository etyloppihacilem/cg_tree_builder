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
            # sig_name = cor.get_signal_name(str(s))
            # if sig_name is None:
            #     print(f"[ERROR] Signal {str(s)} has no correspondance.")
            #     raise ValueError
            sym = str(s)
            match = ODCRes.re_offset.match(str(s))
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
            self.signals[sym] = sig["name"]
            self.sim = sim

    def getBitValue(self, data):
        if len(data[1]) <= self.offset:
            return "0"
        return data[1][self.offset]

    def calculate(self, time):
        correspondance = {}
        for sym, sig_name in self.signals.items():
            data = self.sim.getSigAtTime(time, sig_name)
            value = self.getBitValue(data)
            if value == "X":
                print("Undefined behavior !!")
                print("")
                correspondance[sym] = S.false
                # could be NaN but X does not go into Mutibs...
            elif value == "0":
                correspondance[sym] = S.false
            elif value == "1":
                correspondance[sym] = S.true
        result = self.function.subs(correspondance)
        # self.pattern.append(1 if result == S.true else 0)
        return 1 if result == S.true else 0
        # .subs etc

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

        # print("")
        for index, d in enumerate(data["odc_results"]):
            # if index % 10 == 0:
            #     print("\033[F\033[K", end="", flush=True)
            #     print(f"Nets {index}/{len(data["odc_results"])} ({index*100/len(data["odc_results"]):.2f}%)")
            self.data.append(ODCRes(d, sim))
        # print("\033[F\033[K", end="", flush=True)

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
