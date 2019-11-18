#!/usr/bin/env python

from exnihilo import *
from graphviz import Digraph

world = solve(file='map.lp')
g = Digraph()

for w in world:
  [g.node(str(v.id), str(v.id)) for v in w['vertex'].itertuples()]
  [g.edge(str(e.a), str(e.b)) for e in w['edge'].itertuples()]
  g.render(view=True, directory='/tmp')
