
from lark import Lark, Transformer
from collections import namedtuple


Fact = namedtuple('Fact', ['name', 'args'])

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

clingo_parser = Lark(r'''
  start: fact+
  fact: atom ("(" [fact ("," fact)*] ")")?
  atom: WORD
  WORD: ("a".."z" | "0".."9" | "_")+
  WHITESPACE: (" " | "\n")+
  %ignore WHITESPACE
''')


def parse_clingo(output):
  return Postprocess().transform(clingo_parser.parse(output))


import random
from threading import RLock
import subprocess

PROCESS = None
LOCK = RLock()


def call_clingo(args):
  global PROCESS, LOCK
  with LOCK:
    r = random.randint(1,1000000)
    # TODO seed needs tweaking
    randomness = ['--sign-def=rnd', '--rand-freq=1', '--seed=' + str(r)]
    # randomness = []
    PROCESS = subprocess.Popen(['clingo', *randomness, *args], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    clingo_output, _ = PROCESS.communicate()
  return clingo_output.decode('utf-8')


import re

# lol no sum types
Result = namedtuple('Result', ['raw', 'facts'])


def solve_interruptible(files):
  global PROCESS, LOCK
  # TODO may not even need to lock since it's called on one thread
  with LOCK:
    if PROCESS:
      PROCESS.kill()
      PROCESS = None

  raw = call_clingo(files)
  if 'UNSATISFIABLE' in raw:
    return Result(raw=raw, facts=[])

  # TODO this regex
  for m in re.finditer(r'Answer:[^\n]+\n([^\n]+)\n(?:SATISFIABLE|Optimization:)', raw):
    facts = parse_clingo(m.group(1))

    # we only expect one answer
    return Result(raw=None, facts=facts)
