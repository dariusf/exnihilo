
import sys
import argh
from . import dev

def watch():
  dev.main()

parser = argh.ArghParser()
parser.add_commands([watch])

def main():
  parser.dispatch()
