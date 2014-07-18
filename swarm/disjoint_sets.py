#! /usr/bin/env python
#
# Copyright (C) 2014 by R. Lindsay Todd.
# All rights reserved.
#

"""Disjoint sets"""

__all__ = [ 'DisjointSet', 'DisjointSetCollection' ]

class DisjointSet:
    """An equivalence set"""
    def __init__(self, name):
        from weakref import WeakValueDictionary
        self.name = name
        self.parent = WeakValueDictionary()
        self.members = {}

    def set_weight(self, w, parent=None):
        if parent:
            self.parent[w] = parent
        else:
            self.parent[w] = self
        self.members[w] = {self.name}


class DisjointSetCollection:
    """A collection of disjoint sets"""
    
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
                ns = nd[n] = DisjointSet(n)
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

    def find_members(self, w, x):
        """Find all members equivalent to x of the same weight"""
        r = self.find_root(w, x)
        return r.members[w]

    def make_union(self, w, x, y):
        """Join sets"""
        x_root = self.find_root(w, x)
        y_root = self.find_root(w, y)
        if x_root is y_root:
            return
        # Properly, we should maintain height.  Instead, we use size
        # of the sets.  Pathological cases can be constructed, but
        # generally we expect this to behave similarly.
        xr_members = x_root.members[w]
        yr_members = y_root.members[w]
        if len(xr_members) <= len(yr_members):
            x_root.parent[w] = y_root
            yr_members |= xr_members
        else:
            y_root.parent[w] = x_root
            xr_members |= yr_members


def _main():
    import gc
    gc.enable()
    #gc.set_debug(gc.DEBUG_SAVEALL)
    rsg = DisjointSetCollection()
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
    for n in ('a', 'b', 'c', 'd', 'e', 'f', 'g'):
        print(n, 100, rsg.find_members(100, n))
    for n in ('c', 'd', 'e', 'f', 'g', 'h', 'i'):
        print(n, -90, rsg.find_members(-90, n))
    rsg = None
    gc.collect()
    print(gc.garbage)

_main()
