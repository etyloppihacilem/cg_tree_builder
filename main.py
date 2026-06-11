# ###################################646f75627420796f7572206f776e206578697374656e6365###################################
#
#              """          main.py
#       -\-    _|__
#        |\___/  . \        Created on 03 Jun. 2026 at 13:54
#        \     /(((/        by hmelica
#         \___/)))/         hmelica@student.42.fr
#
# ######################################################################################################################

import argparse
from datetime import datetime
from multiprocessing import Process, Queue
from threading import Thread

from rich.traceback import install

from ODCResults import ODCResults
from Simulation import Simulation

install(show_locals=True)

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


def runPatternExtraction(res, vcd_file, vcd_to_json, clk_name, rst_name, nb_jobs):

    sim = Simulation(
        vcd_file,
        clk=clk_name,
        reset=rst_name,
        json_filename=f"{vcd_file}.json" if vcd_to_json else None,
    )
    res.linkToSimulation(sim)
    sim.freeUnused()

    todo = Queue(len(res.data) + nb_jobs)
    todo_result = Queue()

    start = datetime.now()

    processes = []
    for _ in range(nb_jobs):
        processes.append(
            Process(target=PatternCalculator, args=(todo, todo_result, res))
        )

    result_thread = Thread(target=ResultThread, args=(todo_result, res))
    result_thread.start()

    for p in processes:
        p.start()

    try:
        print("\n")
        last_print = datetime.now() - start
        for bindex, t in enumerate(sim):
            elapsed = datetime.now() - start
            if (elapsed - last_print).total_seconds() >= 1.0:
                last_print = elapsed
                eta = str(((len(sim) - (bindex + 1)) * elapsed) / (bindex + 1)).split(
                    "."
                )[0]
                print("\033[F\033[K" * 2, end="", flush=True)
                print(f"tick {bindex}/{len(sim)} ({bindex * 100 / len(sim):.2f}%)")
                print(f"Elapsed time {str(elapsed).split('.')[0]} ; ETA {eta}")

            for i in range(len(res.data)):
                todo.put((i, bindex, t))

        elapsed = datetime.now() - start
        print(f"Elapsed time {str(elapsed).split('.')[0]}")
        print("Waiting for processes to end. Could take a while as well.")

        for _ in range(nb_jobs):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extrait et organise les motifs d'activité",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "odc_file",
        type=str,
        help="Le fichier JSON qui contient les information d'observabilité",
    )
    parser.add_argument(
        "simulation",
        nargs="+",
        help="Les fichiers .vcd de sortie de simulation à analyser",
    )
    parser.add_argument(
        "-s",
        "--sim_output",
        action="store_true",
        help="Crée un fichier JSON qui contient le contenu parsé des vcd",
    )
    parser.add_argument(
        "--clk_signal",
        type=str,
        default="clk",
        help="Le nom du signal d'horloge dans les simulations",
    )
    parser.add_argument(
        "--reset_signal",
        type=str,
        default="resetn",
        help="Le nom du signal de reset dans les simulations",
    )
    parser.add_argument(
        "-n",
        "--nb_jobs",
        type=int,
        default=4,
        help="Le nombre de process à lancer pour le traitement des simulations",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="pattern.json",
        help="Le fichier JSON de sortie où les motifs seront écrits",
    )
    args = parser.parse_args()

    res = ODCResults(args.odc_file)
    for vcd in args.simulation:
        print(f"Extracting patterns from '{vcd}'")
        runPatternExtraction(
            res, vcd, args.sim_output, args.clk_signal, args.reset_signal, args.nb_jobs
        )
        print(f"Patterns extracted from '{vcd}'")
    res.saveToFile(args.output)
