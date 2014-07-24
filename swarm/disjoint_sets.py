#! /usr/bin/env python
#
# Copyright (C) 2014 by R. Lindsay Todd.
# All rights reserved.
#

"""Disjoint sets"""

__all__ = [ 'DisjointSet', 'DisjointSetCollection' ]

class DisjointSet:
    """A member of an equivalence set, and possibly leader"""
    def __init__(self, name):
        from weakref import WeakValueDictionary
        self.name = name
        self.parent = WeakValueDictionary()
        self.members = {}


    def set_parent(self, parent=None, w=None):
        """Set the parent set of this member, which may be itself."""
        if parent:
            self.parent[w] = parent
        else:
            self.parent[w] = self
        self.members[w] = {self.name}


class DisjointSetCollection:
    """A collection of disjoint sets"""
    
    def __init__(self, factory=DisjointSet):
        self._names = {}
        self._factory = factory
        self._roots = {}

    def make_singleton(self, name, w=None):
        """Make a set with the single 'name' in it.

        Parameters:
            name = Name handle for this set member
            w    = "Weight" of equivalence classes

        Returns:
            The singleton set object

        It is possible that a singleton is requested that already
        appears in the collection, in which case the member object is
        returned, perhaps already belonging to equivalence classes.

        The "weight" allows different equivalence classes to be created.
        """

        nd = self._names
        try:
            ns = nd[name]
        except KeyError:
            # We know it is fresh.
            ns = nd[name] = self._factory(name)
        else:
            # Make sure we have entry to [w]
            if w in ns.parent:
                # Already set up.
                return ns
        # We haven't set up for [w] yet.
        ns.parent[w] = ns
        ns.members[w] = {name}
        self._roots[w] = self._roots.get(w, set()) | {name}
        return ns


    def make_set(self, w, name_list):
        """Make a set of a list of names."""

        first, *rest = [ self.make_singleton(n,w) for n in name_list ]
        for r in rest:
            #first.set_parent(first, w, r)
            self.make_union(w, first, r)
        return self.find_root(w, first.name)


    def make_sets(self, w, *name_set):
        """Make sets"""
        for n in name_set:
            self.make_set(w, n)


    def find_root(self, w, x):
        """Find the root of the set"""
        n = self._names[x]
        try:
            np = n.parent[w]
            npp = np.parent[w]
        except KeyError:
            return None
        while npp != np:
            onp,np,npp = np,npp,npp.parent[w]
            onp.parent[w] = npp
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
            self._roots[w] -= {x_root.name}
        else:
            y_root.parent[w] = x_root
            xr_members |= yr_members
            self._roots[w] -= {y_root.name}

    def get_roots(self, w=None):
        """Return a set of "roots", one for each equivalence class."""
        return self._roots[w]


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
    print(100, rsg.get_roots(100))
    print(-90, rsg.get_roots(-90))
    rsg = None
    gc.collect()
    print(gc.garbage)

_main()
