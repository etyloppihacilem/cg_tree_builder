# ###################################646f75627420796f7572206f776e206578697374656e6365###################################
#
#              """          main.py
#       -\-    _|__
#        |\___/  . \        Created on 03 Jun. 2026 at 13:54
#        \     /(((/        by hmelica
#         \___/)))/         hmelica@student.42.fr
#
# ######################################################################################################################

from Simulation import Simulation
from ODCCorrespondance import ODCCorrespondance
from ODCResults import ODCResults


sim = Simulation("./post_synth.vcd")
cor = ODCCorrespondance("./top_bien_correspondance.json", sim)
res = ODCResults("./top_bien_odc.json", sim, cor)

i = 0
for t in sim:
    print(f"tick at {t}")
    i+=1
    if i > 20:
        break
