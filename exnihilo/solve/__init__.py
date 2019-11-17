
import clyngor
import itertools
# import pandas as pd
from .interruptible import *

program = '''
a.
{ b(1) }.
b(2).
c(X) :- b(X).
'''

# [frozenset({('c', (2,)), ('b', (1,)), ('a', ())})]

def fst(x):
  return x[0]

def solve(program):
  # TODO handle unsat
  # TODO random
  # TODO number of answers
  # TODO file vs str input
  # TODO return a dataframe

  # TODO indexing relations, or maybe querying dataframe is sufficient

  # TODO translation into records with names taken from annotations
  # TODO automatically define the records
  # TODO examples and tests

  answers = clyngor.ASP(program).careful_parsing
  # assumes that there's no overloading by arity

  for answer in answers: # nondeterminism
    yield {k: list(list(name_and_args[1]) for name_and_args in v) for k, v in itertools.groupby(sorted(answer, key=fst), key=fst)}

for a in solve(program):
  print(a)
