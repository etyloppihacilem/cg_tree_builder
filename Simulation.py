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
                address = "/".join(pile)
                address = address.replace("\\\\", "\\")
                plug = {
                    key: val
                    for key, val in d.items()
                    if key not in {"name", "children", "data"}
                }
                plug.update({"name": address})
                plug["data"] = [(i[0], i[1]) for i in d["data"]]
                plug["data_time"] = [int(i[0]) for i in d["data"]]
                flat[address] = plug
        if "children" in d:
            todo.put(None)
            for child in d["children"]:
                todo.put(child)
        else:
            pile.pop(-1)
    return flat


class Simulation:
    def __init__(self, filename, clk="clk", reset="resetn"):
        self.used = set()
        print(f"Loading '{filename}'", end=" ", flush=True)
        with open(filename) as vcd_file:
            vcd = VcdParser()
            vcd.parse(vcd_file)
            data = vcd.scope.toJson()
            self.data = flatten_vcd(data)
        # with open(f"{filename}.json", "w") as f:
        #     import json
        #     json.dump(self.data, f, indent=2)
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
        self.rst_data = rst_data
        self.clk = []
        reset = True
        for i in self.clk_data:
            if reset:
                val = self.dataAtTime(i[0], self.rst_data)
                if val[1] == "1":
                    reset = False
            elif i[1] == "1":  # raising edge
                self.clk.append(i[0])

    def find_data(self, filters):
        if type(filters) is not list:
            filters = [filters]
        ret = None
        for f in filters:
            # try:
            #     prog = self.rcache[f]
            # except KeyError:
            #     prog = re.compile(f)
            #     self.rcache[f] = prog
            # print(f"filter: {f}")
            if ret is None:
                # ret = [i for i in self.data.values() if prog.search(i["name"]) is not None]
                # ret = [i for i in self.data.values() if re.search(f, i["name"]) is not None]
                ret = [i for i in self.data.values() if f in i["name"]]
            else:
                # ret = [i for i in ret if prog.search(i["name"]) is not None]
                # ret = [i for i in ret if re.search(f, i["name"]) is not None]
                ret = [i for i in ret if f in i["name"]]
            # for i in self.data.values():
            #     if "result_buffer" in i["name"]:
            #         print({key: val if key != "data" else len(val) for key, val in i.items()})
            if len(ret) == 0:
                return None
        if ret is None:
            return ret
        if len(ret) > 1:
            print(
                f"[WARNING] More than one match for signal {filters}: {len(ret)} sig."
            )
            # for r in ret:
            #     print(" ", {key: val if key != "data" else len(val) for key, val in r.items()})
        self.used.add(ret[0]["name"])
        return ret[0]

    def getSigAtTime(self, time, sig_name):
        return self.dataAtTime(time, self.data[sig_name])

    def dataAtTime(self, time, data):
        idx = bisect_right(data["data_time"], time) - 1
        if idx >= 0:
            return data["data"][idx]
        print(f"[WARNING] No data at {time}")
        return None

    def get_data(self, time, filters):
        data = self.find_data(filters)
        if data is None:
            print(f"[ERROR] No match for {filters}")
            return None
        ret = self.dataAtTime(time, data)
        if ret is None:
            print(f"[ERROR] No data found at {time} for {filters}")
        return ret

    def freeUnused(self):
        selected = []
        for key in self.data.keys():
            if key not in self.used:
                selected.append(key)
        for key in selected:
            del self.data[key]

    def __iter__(self):
        return iter(self.clk)

    def __len__(self):
        return len(self.clk)
