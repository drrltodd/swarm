#! /usr/bin/env python
#
# Copyright (C) 2014 by R. Lindsay Todd.
# All rights reserved.
#

"""Resource agents"""

__all__ = [ 'ResourceSetGroup' ]


class ResourceSet:
    """An equivalence set of resources, by name"""
    def __init__(self, name):
        from weakref import WeakValueDictionary
        self.name = name
        self.parent = WeakValueDictionary()
        self.rank = {}

    def set_weight(self, w, parent=None):
        if parent:
            self.parent[w] = parent
        else:
            self.parent[w] = self
        self.rank[w] = 0


class ResourceSetGroup:
    """A group of resource sets, by name"""
    
    def __init__(self):
        self._names = {}

    def make_set(self, w, name_list):
        """Make a set with the specified names in it."""
        zn = name_list[0]
        nd = self._names
        for n in name_list:
            try:
                ns = nd[n]
            except KeyError:
                ns = nd[n] = ResourceSet(n)
            ns.set_weight(w, nd[zn])

    def make_sets(self, w, *name_set):
        """Make sets"""
        for n in name_set:
            self.make_set(w, n)

    def find_root(self, w, x):
        """Find the root of the set"""
        n = self._names[x]
        try:
            np = n.parent[w]
        except KeyError:
            return None
        while np.parent[w] != np:
            np = np.parent[w]
        n.parent[w] = np
        return np

    def make_union(self, w, x, y):
        """Join sets"""
        x_root = self.find_root(w, x)
        y_root = self.find_root(w, y)
        if x_root is y_root:
            return
        if x_root.rank[w] < y_root.rank[w]:
            x_root.parent[w] = y_root
        elif x_root.rank[w] > y_root.rank[w]:
            y_root.parent[w] = x_root
        else:
            y_root.parent[w] = x_root
            x_root.rank[w] += 1



def _main():
    rsg = ResourceSetGroup()
    rsg.make_sets(100, ['a'], ['b'], ['c'], ['d'], ['e'], ['f'], ['g'])
    rsg.make_sets(-90, 'c', 'd', 'e', 'f', 'g', 'h', 'i')
    rsg.make_union(100, 'a', 'b')
    rsg.make_union(100, 'c', 'b')
    rsg.make_union(100, 'd', 'e')
    rsg.make_union(100, 'f', 'g')
    rsg.make_union(100, 'e', 'g')
    rsg.make_union(-90, 'f', 'c')
    for n in ('a', 'b', 'c', 'd', 'e', 'f', 'g'):
        print(n, 100, rsg.find_root(100, n).name)
    for n in ('c', 'd', 'e', 'f', 'g', 'h', 'i'):
        print(n, -90, rsg.find_root(-90, n).name)

_main()
