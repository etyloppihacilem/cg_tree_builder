# ###################################646f75627420796f7572206f776e206578697374656e6365###################################
#
#              """          main.py
#       -\-    _|__
#        |\___/  . \        Created on 03 Jun. 2026 at 13:54
#        \     /(((/        by hmelica
#         \___/)))/         hmelica@student.42.fr
#
# ######################################################################################################################

from simulation import Simulation

# import json, sys
# from pyDigitalWaveTools.vcd.parser import VcdParser
# if len(sys.argv) > 1:
#     fname = sys.argv[1]
# else:
#     print('Give me a vcd file to parse')
#     sys.exit(-1)
#
# with open(fname) as vcd_file:
#     vcd = VcdParser()
#     vcd.parse(vcd_file)
#     data = vcd.scope.toJson()
#     print(json.dumps(data, indent=2, sort_keys=True))
#
# exit(0)

# a = Simulation("./tb_adder.vcd")
a = Simulation("./post_synth.vcd")
