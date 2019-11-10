
from collections import namedtuple, OrderedDict
import builtins

from .. import solve

# TODO get rid of this import
import clyngor

default_builtins = set(vars(builtins).keys())

Cardinality = namedtuple('Cardinality', 'low, high')

class World(object):
  def __init__(self):
    self.constraints_cardinality = {}
    self.defined_names = {}

  def __enter__(self):
    global current_world
    current_world = self

  def __exit__(self, exc_type, exc_value, traceback):
    global current_world
    current_world = None

global_world = World()

current_world = None

def span(low, high):
  return range(low, high+1)


def alt(*possibilities):
  return possibilities

def world():
  if current_world:
    return current_world
  else:
    return global_world

# TODO https://docs.python.org/3/whatsnew/3.6.html#whatsnew36-pep468
def thing(_name, **fields):
  # A container for ASP output which users would interact with
  container = namedtuple(_name, fields.keys())

  # TODO this doesn't have to be the named tuple
  setattr(builtins, _name, container)
  container._fields = fields

  # Adding a method
  # https://stackoverflow.com/a/2982
  # _name = lambda self: self.__name__
  # container._name = _name.__get__(container)
  container._name = _name

  world().defined_names[_name] = container


def up_to(n, thing):
  world().constraints_cardinality[thing._name] = Cardinality(low=0, high=n)


def exactly(n, thing):
  world().constraints_cardinality[thing._name] = Cardinality(low=n, high=n)


def raw(s):
  return ''


def python_ident_to_atom(name):
  return name.lower() # TODO


def var_names_list(thing):
    return [f'{fname[0].upper()}{i}' for i, (fname, _) in enumerate(thing._fields.items())]


def domains_program():
  r = []
  for thing in world().defined_names.values():
    thing_name = python_ident_to_atom(thing._name)

    # field domains
    for fname, fdomain in thing._fields.items():
      field_name = python_ident_to_atom(fname)
      r.append(f'{thing_name}_{field_name}({";".join(str(v) for v in fdomain)})')

    # the thing itself
    var_names = var_names_list(thing)
    head = f'{thing_name}({",".join(var_names)})'

    body = ', '.join(f'{thing_name}_{fname}({var_names[i]})' for i, (fname, _) in enumerate(thing._fields.items()))

    if thing._name in world().constraints_cardinality:
      ut = world().constraints_cardinality[thing._name]
      head = f'{ut.low} {{ {head} : {body} }} {ut.high}'
      r.append(head)
    else:
      r.append(f'{head} :- {body}')
  return '.\n'.join(r) + '.\n'


def debug_state():
  print('==debug==')
  print('current', current_world, id(current_world))
  print('global', global_world, id(global_world))


def generate(debug=False):
  program = domains_program()

  if debug:
    print(program)

  # TODO use solve api
  answers = clyngor.ASP(program).careful_parsing

  # manual decoding because of API deficiencies
  things = {python_ident_to_atom(p._name): p for p in world().defined_names.values()}

  results = []
  for answer in answers:
    for name, args in answer:
      if name in things:
        results.append(things[name](*args))
    break

  return results



def test():
  with World() as xfile:
    pass

  # globals()['a'] = 'test'
  # TODO caution if aliasing an existing global
  builtins.a = 'test'