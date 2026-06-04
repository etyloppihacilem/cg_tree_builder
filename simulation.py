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
            flat["/".join(pile)] = {key: val for key, val in d.items() if key not in {"name", "children"}}
        if "children" in d:
            todo.put(None)
            for child in d["children"]:
                todo.put(child)
        else:
            pile.pop(-1)
    return flat


class Simulation:
    def __init__(self, file_name, clk="clk", reset="resetn", tb="testbench"):
        with open(file_name) as vcd_file:
            vcd = VcdParser()
            vcd.parse(vcd_file)
            data = vcd.scope.toJson()
            # print(self.data.keys())
            # print(self.data["name"])
            # [print(i["name"]) for i in self.data["children"]]
            # a = self.data["children"][0]
            # [print(i["name"]) for i in a["children"]]
            self.data = flatten_vcd(data)
            import json
            print(json.dumps(self.data, indent=2))
