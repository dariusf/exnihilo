#!/usr/bin/env python

from exnihilo import *
from graphviz import Digraph
import subprocess

world = solve(file='map.lp')
g = Digraph()

for wo in world:
  [g.node(str(v.id), str(v.id)) for v in wo['vertex'].itertuples()]
  [g.edge(str(e.a), str(e.b)) for e in wo['edge'].itertuples()]

  with open('/tmp/lol.dot', 'w') as f:
    f.write(g.source)

  subprocess.check_call(['dot', '-o', '/tmp/lol.png', '-Tpng', '/tmp/lol.dot'])
  subprocess.check_call(['open', '/tmp/lol.png'])
