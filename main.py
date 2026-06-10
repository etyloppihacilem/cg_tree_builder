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
from multiprocessing import Process, Queue
from threading import Thread

from rich.traceback import install

from ODCResults import ODCResults
from Simulation import Simulation

install(show_locals=True)

NB_JOBS = 24

STOP = -2


def PatternCalculator(queue: Queue, resultQueue: Queue, res: ODCResults):
    while True:
        index, bindex, time = queue.get()
        if index == STOP:
            break
        result = res.data[index].calculate(time)
        resultQueue.put((index, bindex, result))


def ResultThread(resultQueue: Queue, res: ODCResults):
    while True:
        index, bindex, val = resultQueue.get()
        if index == STOP:
            break
        res.data[index].addResult(val, bindex)


sim = Simulation("./t.vcd")
res = ODCResults("./picorv32_complete_odc.json", sim)
sim.freeUnused()

todo = Queue(len(res.data) + NB_JOBS)
todo_result = Queue()

start = datetime.now()

processes = []
for _ in range(NB_JOBS):
    processes.append(
        Process(target=PatternCalculator, args=(todo, todo_result, res))
    )

result_thread = Thread(target=ResultThread, args=(todo_result, res))
result_thread.start()

for p in processes:
    p.start()

try:
    for bindex, t in enumerate(sim):
        elapsed = datetime.now() - start
        print(f"tick {bindex}/{len(sim)} ({bindex * 100 / len(sim):.2f}%)")
        print(f"Elapsed time {str(elapsed).split('.')[0]} ; ETA {str(((len(sim) - (bindex + 1)) * elapsed) / (bindex + 1)).split('.')[0]}")

        for i in range(len(res.data)):
            todo.put((i, bindex, t))

        print("\033[F\033[K" * 2, end="", flush=True)

    print(f"Elapsed time {str(elapsed).split('.')[0]}")
    print("Waiting for processes to end. Could take a while as well.")

    for _ in range(NB_JOBS):
        todo.put((STOP, 0, 0))
except BaseException as e:
    for p in processes:
        p.kill()
        p.join()
    raise e

for p in processes:
    p.join()

todo_result.put((STOP, -1, -1))

result_thread.join()

end = datetime.now()
print(f"Elapsed time: {str(end - start).split('.')[0]} seconds")

res.saveToFile("picorv32_complete_pattern.json")
