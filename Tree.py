# ###################################646f75627420796f7572206f776e206578697374656e6365###################################
#
#              """          Tree.py
#       -\-    _|__
#        |\___/  . \        Created on 12 Jun. 2026 at 10:36
#        \     /(((/        by hmelica
#         \___/)))/         hmelica@student.42.fr
#
# ######################################################################################################################

import json
import numpy as np

from Leaf import Leaf

INF = float("inf")


class Tree:
    def __init__(self):
        self.leafs = []

    def addLeaf(self, leaf):
        self.leafs.append(leaf)

    def MakePairs(self):
        matrice = np.array(
            [
                [
                    self.leafs[i] ^ self.leafs[j] if j != i else INF
                    for j in range(len(self.leafs))
                ]
                for i in range(len(self.leafs))
            ]
        )
        level = []
        removed = 0
        while len(self.leafs) - removed > 1:
            print(f"Matching {len(self.leafs) - removed}")
            idx_lineaire = np.argmin(matrice)
            i, j = np.unravel_index(idx_lineaire, matrice.shape)
            new_leaf = Leaf()
            new_leaf.addChild(self.leafs[i])
            new_leaf.addChild(self.leafs[j])
            self.leafs[i] = None
            self.leafs[j] = None
            removed += 2
            matrice[i, :] = INF
            matrice[:, i] = INF
            matrice[j, :] = INF
            matrice[:, j] = INF
            level.append(new_leaf)
            print("\033[F\033[K", end="")
        if len(self.leafs) - removed > 0:
            self.leafs = [i for i in self.leafs if i is not None]
        else:
            self.leafs.clear()
        self.leafs += level  # addition car si feuilles impaires

    def buildTree(self):
        print("Building tree...")
        while len(self.leafs) > 1:
            print(f"Reducing {len(self.leafs)}")
            self.MakePairs()
            print("\033[F\033[K", end="")
        print("done.")

    def saveToFile(self, filename):
        print(f"Writing tree to '{filename}'")
        with open(filename, "w") as f:
            json.dump(self.leafs[0].toDict(), f, indent=2)
