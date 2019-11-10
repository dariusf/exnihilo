
import subprocess
import re
from lark import Lark, Transformer
import itertools
from collections import namedtuple
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from functools import total_ordering
from terminaltables import SingleTable
import randomcolor
from colors import color
from multiprocessing.pool import ThreadPool
from threading import RLock
import random
import glob


# TODO abstract over it and move to solve?
POOL = ThreadPool(processes=1)
PROCESS = None
LOCK = RLock()

clingo_parser = Lark(r'''
  start: fact+
  fact: atom ("(" [fact ("," fact)*] ")")?
  atom: WORD
  WORD: ("a".."z" | "0".."9" | "_")+
  WHITESPACE: (" " | "\n")+
  %ignore WHITESPACE
''')

COLOURS = {}
RAND_COLOR = randomcolor.RandomColor()
COLOURS['_int'] = RAND_COLOR.generate(luminosity='light')[0]

def colourize(name):
  global COLOURS, RAND_COLOR
  # only primitives allowed

  # only facts are allowed because of our nasty choice of representation of atom names
  # name = term.name
  if isinstance(name, int):
    # return term._replace(name=)
    return color(str(name), fg=COLOURS['_int'])

  if name not in COLOURS:
    COLOURS[name] = RAND_COLOR.generate(luminosity='light')[0]
  # return term._replace(name=color(name, fg=COLOURS[name]))
  # return term._replace(name=)
  return color(name, fg=COLOURS[name])


# hacks to get rid of the box-drawing chars
# https://github.com/Robpol86/terminaltables/blob/master/terminaltables/other_tables.py
[setattr(SingleTable, p, '') for p in dir(SingleTable) if p.startswith('CHAR_')]

@total_ordering
class Fact(namedtuple('Fact', 'name,args')):
  def __str__(self):
    return repr(self)

  def __repr__(self):
    if self.args:
      return '{}({})'.format(colourize(self.name), ','.join(str(a) for a in self.args))
    else:
      return colourize(self.name)

  # https://docs.python.org/3/library/functools.html#functools.total_ordering
  def __lt__(self, other):
    o = self.name
    fo = other.name
    if isinstance(o, int):
      p = 0
    else:
      p = 1
    if isinstance(fo, int):
      op = 0
    else:
      op = 1
    a = [p, self.name, len(self.args), *self.args]
    b = [op, other.name, len(other.args), *other.args]
    return a < b


class Postprocess(Transformer):
    def start(self, items):
      return items # strip one layer

    def fact(self, items):
      if len(items) == 1:
        return items[0] # really an atom
      else:
        # the name can be a python value
        return Fact(name=items[0].name, args=items[1:])

    def atom(self, items):
      v = items[0].value
      try:
        v = int(v)
      except:
        pass
      # we use this representation instead of the raw int/string so heterogenous lists of facts can be sorted
      return Fact(name=v, args=[])

def call_clingo(args):
  global PROCESS, LOCK
  with LOCK:
    r = random.randint(1,1000000)
    # TODO needs tweaking
    # 1
    randomness = ['--sign-def=rnd', '--rand-freq=1', '--seed=' + str(r)]
    # randomness = []
    PROCESS = subprocess.Popen(['clingo', *randomness, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    clingo_output, _ = PROCESS.communicate()
  return clingo_output.decode('utf-8')


def parse_clingo(output):
  return Postprocess().transform(clingo_parser.parse(output))


def term_dimensions():
  r, c = os.popen('stty size', 'r').read().split()
  return int(r), int(c)


def split_columns(lst, n):
  r = [[] for i in range(n)]
  for i, e in enumerate(lst):
    r[i % n].append(e)
  return r


def clear():
  # clears and moves cursor
  print(chr(27) + "[H" + chr(27) + "[J")


def reevaluate():
  files = glob.glob('*.lp')
  if not files:
    print('No .lp files found')
    return

  print('Solving...', end=' ', flush=True)

  raw = call_clingo(files)

  if 'UNSATISFIABLE' in raw:
    print(raw)
    return

  r, c = term_dimensions()

  # TODO this regex
  for m in re.finditer(r'Answer:[^\n]+\n([^\n]+)\n(?:SATISFIABLE|Optimization:)', raw):
    facts = parse_clingo(m.group(1))

    print(facts)
    facts = sorted(facts)

    facts = split_columns(facts, r-3)

    table = SingleTable(facts)
    table.inner_heading_row_border = False
    clear()
    print(table.table)


def act(path):
  global PROCESS, LOCK
  if path.endswith('.lp'):
    with LOCK:
      if PROCESS:
        PROCESS.kill()
        PROCESS = None
    POOL.apply_async(reevaluate)

class Handler(FileSystemEventHandler):

  def on_created(self, e):
    act(e.src_path)

  def on_modified(self, e):
    act(e.src_path)


def main():
  reevaluate()
  event_handler = Handler()
  observer = Observer()
  observer.schedule(event_handler, '.', recursive=False)
  observer.start()
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()

# TODO specialization of main to expose result as dataframe
