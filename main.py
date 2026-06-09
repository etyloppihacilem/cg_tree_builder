# ###################################646f75627420796f7572206f776e206578697374656e6365###################################
#
#              """          main.py
#       -\-    _|__
#        |\___/  . \        Created on 03 Jun. 2026 at 13:54
#        \     /(((/        by hmelica
#         \___/)))/         hmelica@student.42.fr
#
# ######################################################################################################################

from datetime import datetime

from rich.traceback import install

from ODCResults import ODCResults
from Simulation import Simulation

install(show_locals=True)

sim = Simulation("./t_nouveau.vcd")
# cor = ODCCorrespondance("./top_nouveau_correspondance.json", sim)
res = ODCResults("./top_nouveau_odc.json", sim)

start = datetime.now()

for index, t in enumerate(sim):
    print(f"tick {index}/{len(sim)} ({index * 100 / len(sim):.2f}%)")
    res.stepAtTime(t)
    print("\033[F\033[K", end="", flush=True)

end = datetime.now()
print(f"Elapsed time: {str(end - start).split('.')[0]} seconds")

res.saveToFile("pattern_nouveau.json")
