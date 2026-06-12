# ###################################646f75627420796f7572206f776e206578697374656e6365###################################
#
#              """          Leaf.py
#       -\-    _|__
#        |\___/  . \        Created on 12 Jun. 2026 at 10:36
#        \     /(((/        by hmelica
#         \___/)))/         hmelica@student.42.fr
#
# ######################################################################################################################

from ODCResults import ODCRes


class Leaf:
    def __init__(self):
        self.name = None
        self.pattern = None
        self._left = None
        self._right = None
        # self.function = None

    def initFromODCRes(self, result: ODCRes):
        self.name = result.name
        self.pattern = result.pattern
        # self.function = result.function

    def __getitem__(self, index):
        if index == 0:
            return self._left
        if index == 1:
            return self._right
        raise IndexError

    def __iter__(self):
        yield self._left
        yield self._right

    def __xor__(self, other):
        xor = self.pattern ^ other.pattern
        return xor.count(1)  # return distance between patterns

    def __or__(self, other):
        return self.pattern | other.pattern

    @property
    def left(self):
        return self._left

    @left.setter
    def left(self, child):
        self._left = child
        if self._right is not None:
            self.pattern = self._left | self._right

    @property
    def right(self):
        return self._right

    @right.setter
    def right(self, child):
        self._right = child
        if self._left is not None:
            self.pattern = self._left | self._right

    def addChild(self, child):
        if self.left is None:
            self.left = child
        elif self.right is None:
            self.right = child
        else:
            raise IndexError

    def __len__(self):
        return (0 if self.left is None else 1) + (0 if self.right is None else 1)

    def isLeaf(self):
        return len(self) == 0

    def toDict(self):
        return {
            "name": self.name,
            "pattern": str(self.pattern),
            "distance": -1
            if self.right is None or self.left is None
            else self.left ^ self.right,
            "norme": -1
            if self.right is None or self.left is None
            else (self.left ^ self.right) / len(self.right.pattern),
            "left": self.left.toDict() if self.left is not None else None,
            "right": self.right.toDict() if self.right is not None else None,
            # "function": str(self.function),
        }
