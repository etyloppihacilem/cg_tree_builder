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


def runPatternExtraction(res, vcd_file, vcd_to_json, clk_name, rst_name):
    sim = Simulation(
        vcd_file,
        clk=clk_name,
        reset=rst_name,
        json_filename=f"{vcd_file}.json" if vcd_to_json else None,
    )
    res.linkToSimulation(sim)
    sim.freeUnused()

    start = datetime.now()

    len_res_data = len(res.data)
    for i, r in enumerate(res.data):
        print(f"{i}/{len_res_data} ({i * 100 / len_res_data:.2f}%)")
        r.run()
        print("\033[F\033[K", end="")

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
            res, vcd, args.sim_output, args.clk_signal, args.reset_signal
        )
        print(f"Patterns extracted from '{vcd}'")
    res.saveToFile(args.output)
