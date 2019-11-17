
import sys
import argh
import os
from . import dev

def watch(directory='.', recursive=False):
  dev.main(directory=os.path.abspath(directory), recursive=recursive)

parser = argh.ArghParser()
parser.add_commands([watch])

def main():
  parser.dispatch()
