
from exnihilo import *

def test_cardinality():
  with World():
    thing('Person',
      name=alt('x', 'y'),
      age=span(1, 3)
    )
    exactly(1, Person)
    result = solve()

  assert len(result) == 1
  assert result[0].name in ['x', 'y']
  assert result[0].age in [1, 2, 3]
