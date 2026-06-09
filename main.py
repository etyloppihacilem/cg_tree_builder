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
from multiprocessing import Process, Queue, Barrier
from threading import Thread

from rich.traceback import install

from ODCResults import ODCResults
from Simulation import Simulation

install(show_locals=True)

NB_JOBS = 24
WAIT = -1
STOP = -2

barrier = Barrier(NB_JOBS)


def PatternCalculator(queue: Queue, resultQueue: Queue, b: Barrier, res: ODCResults):
    while True:
        index, time = queue.get()
        if index == WAIT:
            b.wait()
            continue
        elif index == STOP:
            break
        result = res.data[index].calculate(time)
        resultQueue.put((index, result))


def ResultThread(resultQueue: Queue, res: ODCResults):
    while True:
        index, val = resultQueue.get()
        if index == STOP:
            break
        res.data[index].addResult(val)


sim = Simulation("./t_nouveau.vcd")
# cor = ODCCorrespondance("./top_nouveau_correspondance.json", sim)
res = ODCResults("./top_nouveau_odc.json", sim)
sim.freeUnused()

todo = Queue(len(res.data) + NB_JOBS)
todo_result = Queue()

start = datetime.now()

processes = []
for _ in range(NB_JOBS):
    processes.append(
        Process(target=PatternCalculator, args=(todo, todo_result, barrier, res))
    )

result_thread = Thread(target=ResultThread, args=(todo_result, res))
result_thread.start()

for p in processes:
    p.start()

for index, t in enumerate(sim):
    elapsed = datetime.now() - start
    print(f"tick {index}/{len(sim)} ({index * 100 / len(sim):.2f}%)")
    print(f"Elapsed time {str(elapsed).split('.')[0]} ; ETA {str(((len(sim) - (index + 1)) * elapsed) / (index + 1)).split('.')[0]}")
    # res.stepAtTime(t)
    for i in range(len(res.data)):
        todo.put((i, t))
    for _ in range(NB_JOBS):
        todo.put((WAIT, 0))
    print("\033[F\033[K" * 2, end="", flush=True)
    if index == 20:
        break

print(f"Elapsed time {str(elapsed).split('.')[0]}")
print("Waiting for processes to end.")

for _ in range(NB_JOBS):
    todo.put((STOP, 0))

for p in processes:
    p.join()

todo_result.put((STOP, -1))

result_thread.join()

end = datetime.now()
print(f"Elapsed time: {str(end - start).split('.')[0]} seconds")

res.saveToFile("pattern_nouveau.json")
