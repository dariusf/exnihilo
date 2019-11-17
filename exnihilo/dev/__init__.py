
import itertools
from collections import namedtuple
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from terminaltables import SingleTable
import glob
from functools import total_ordering
from ..solve import solve_interruptible, Fact
import randomcolor
from colors import color
from multiprocessing.pool import ThreadPool


POOL = ThreadPool(processes=1)

COLOURS = {}
RAND_COLOR = randomcolor.RandomColor()
COLOURS['_int'] = RAND_COLOR.generate(luminosity='light')[0]

DIRECTORY = None

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


@total_ordering
class RenderFact:

  def __init__(self, f):
    self.f = f

  def __str__(self):
    return repr(self)

  def __repr__(self):
    if self.f.args:
      return '{}({})'.format(colourize(self.f.name), ','.join(str(a) for a in self.f.args))
    else:
      return colourize(self.f.name)

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


def wrap(f):
  '''
  Recursively replace every Fact constructor
  '''
  return RenderFact(f._replace(args=[wrap(a) for a in f.args]))


# hacks to get rid of the box-drawing chars
# https://github.com/Robpol86/terminaltables/blob/master/terminaltables/other_tables.py
[setattr(SingleTable, p, '') for p in dir(SingleTable) if p.startswith('CHAR_')]


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
  path = '*.lp'
  if DIRECTORY:
    path = os.path.join(DIRECTORY, path)
  files = glob.glob(path)
  if not files:
    print('No .lp files found')
    return

  # in case solving takes a while
  print('Solving...', end=' ', flush=True)

  res = solve_interruptible(files=files)

  if res.raw and 'UNSATISFIABLE' in res.raw:
    print(res.raw)
    return

  r, c = term_dimensions()

  facts = res.facts

  facts = sorted(facts)

  # before we destroy the structure for rendering
  facts = [wrap(f) for f in facts]

  facts = split_columns(facts, r-3)

  table = SingleTable(facts)
  table.inner_heading_row_border = False
  clear()
  print(table.table)


def act(path):
  # global PROCESS, LOCK
  global POOL
  if path.endswith('.lp'):
    # with LOCK:
    #   if PROCESS:
    #     PROCESS.kill()
    #     PROCESS = None
    POOL.apply_async(reevaluate)

class Handler(FileSystemEventHandler):

  def on_created(self, e):
    act(e.src_path)

  def on_modified(self, e):
    act(e.src_path)


def main(directory, recursive):
  global DIRECTORY
  DIRECTORY = directory
  reevaluate()
  event_handler = Handler()
  observer = Observer()
  observer.schedule(event_handler, directory, recursive=recursive)
  observer.start()
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()

# TODO specialization of main to expose result as dataframe
