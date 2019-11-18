
# Ex Nihilo

## Installation

```sh
pip install git+https://github.com/dariusf/exnihilo.git
brew install graphviz clingo
```

## Getting started

The `exnihilo` executable is now available. It currently has one subcommand, `watch`, a [ghcid](https://github.com/ndmitchell/ghcid)-style tool that runs clingo when .lp files change and formats the output.

This is also a library for mapping clingo's output to pandas DataFrames. Check out the [examples](examples).

```sh
cd examples/map
./map.py
```

## Tests

```sh
pytest -s
```
