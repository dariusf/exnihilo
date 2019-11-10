#!/bin/bash

python -i <(cat <(echo "import sys; sys.path.insert(0, '')") tests/*.py)