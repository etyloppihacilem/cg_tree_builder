# ###################################646f75627420796f7572206f776e206578697374656e6365###################################
#
#              """          simulation.py
#       -\-    _|__
#        |\___/  . \        Created on 03 Jun. 2026 at 13:54
#        \     /(((/        by hmelica
#         \___/)))/         hmelica@student.42.fr
#
# ######################################################################################################################

from queue import LifoQueue
from bisect import bisect_right
from pyDigitalWaveTools.vcd.parser import VcdParser


def flatten_vcd(data):
    flat = {}
    todo = LifoQueue()
    pile = []
    todo.put(data)

    while not todo.empty():
        d = todo.get()
        if d is None:
            pile.pop(-1)
            continue
        pile.append(d["name"])
        if "data" in d:
            if len(d["data"]) > 0:
                flat["/".join(pile)] = {
                    key: val for key, val in d.items() if key != "children"
                }
        if "children" in d:
            todo.put(None)
            for child in d["children"]:
                todo.put(child)
        else:
            pile.pop(-1)
    return flat


class Simulation:
    def __init__(self, file_name, clk="clk", reset="resetn"):
        print(f"Loading '{file_name}'", end=" ", flush=True)
        with open(file_name) as vcd_file:
            vcd = VcdParser()
            vcd.parse(vcd_file)
            data = vcd.scope.toJson()
            self.data = flatten_vcd(data)
        print("... loaded.")
        clk_data = self.find_data([clk])
        if clk_data is None:
            print(f"[ERROR] Signal {clk} not found.")
            raise ValueError
        self.clk_data = clk_data["data"]
        rst_data = self.find_data([reset])
        if rst_data is None:
            print(f"[ERROR] Signal {reset} not found.")
            raise ValueError
        self.rst_data = rst_data["data"]

    def find_data(self, filters):
        ret = None
        first = True
        for f in filters:
            if first:
                ret = [i for i in self.data.values() if f in i["name"]]
                first = False
            else:
                ret = [i for i in ret if f in i["name"]]
        if len(ret) == 0:
            return None
        if len(ret) > 1:
            print(f"[WARNING] More than one match for signal {filters}")
        return ret[0]

    def data_at_time(self, time, data):
        idx = bisect_right([i[0] for i in data], time) - 1
        if idx >= 0:
            return data[idx]
        print(f"[WARNING] No data at {time}")
        return None

    def get_data(self, time, filters):
        data = self.find_data(filters)
        if data is None:
            print(f"[ERROR] No match for {filters}")
            return None
        data = data["data"]
        ret = self.data_at_time(time, data)
        if ret is None:
            print(f"[ERROR] No data found at {time} for {filters}")
        return ret

    def __iter__(self):
        reset = True
        for i in self.clk_data:
            if reset:
                val = self.data_at_time(i[0], self.rst_data)
                if val[1] == "1":
                    reset = False
            elif i[1] == "1":  # raising edge
                yield i[0]
