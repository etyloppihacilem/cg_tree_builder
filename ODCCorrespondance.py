# ###################################646f75627420796f7572206f776e206578697374656e6365###################################
#
#              """          ODCCorrespondance.py
#       -\-    _|__
#        |\___/  . \        Created on 04 Jun. 2026 at 17:07
#        \     /(((/        by hmelica
#         \___/)))/         hmelica@student.42.fr
#
# ######################################################################################################################

import json
from re import match


class ODCCorrespondance:
    def __init__(self, filename, sim):
        print(f"Loading '{filename}'", end=" ", flush=True)
        with open(filename) as f:
            data = json.load(f)
        self.data = {}
        print("... organizing ...", end=" ", flush=True)
        for d in data:
            try:
                self.data[d["net"]].append(d)
            except KeyError:
                self.data[d["net"]] = [d]
        print("... loaded.")
        self.sim = sim

    def get_signal_name(self, net) -> str:
        # Si il y a plusieurs matchs pour un même net, il faut trier avec le depth (non implémenté...)
        # rg "A1" new.json | grep
        #   "root/testbench/uut/pico/_13434_/A1": {
        #   "root/testbench/uut/pico/_13432_/A1": {
        #   "root/testbench/uut/pico/_13430_/A1": {
        #   "root/testbench/uut/pico/_13343_/A1": {
        #   "root/testbench/uut/pico/_07343_/A1": {
        #   "root/testbench/uut/RAM/POLY/_18343_/A1": {
        #   "root/testbench/uut/RAM/POLY/_09343_/A1": {
        #   "root/testbench/uut/RAM/POLY/IP_ODC/u_mul_x3/_343_/A1": {
        #   "root/testbench/uut/RAM/POLY/IP_ODC/u_mul_x2/_343_/A1": {
        #   "root/testbench/uut/RAM/POLY/IP_ODC/u_mul_t3/_343_/A1": {
        #   "root/testbench/uut/RAM/POLY/IP_ODC/u_mul_t2/_343_/A1": {
        #   "root/testbench/uut/RAM/POLY/IP_ODC/u_mul_t1/_343_/A1": {
        try:
            net_plugs = self.data[net]
        except KeyError:
            print(f"[ERROR] Net {net} not found in correspondance data.")
            return None
        for c in net_plugs:
            m = match(r"^subckt_(\d*_)", c["name"])
            if not m:
                print(f"[ERROR] Could not extract subckt number of '{c["name"]}'")
                return None
            nb = m.group(1)
            # _7343_ -> _07343_
            res = self.sim.find_data([fr"_0*{nb}", "/"+c["io"]])
            if res is not None:
                return res["name"]
        for c in net_plugs:
            print(c)
        return None
