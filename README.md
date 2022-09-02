# abs2rel

A python script that traverses a whole package turning local absolute imports into relative ones.

## Installation

```bash
pip install abs2rel
```

## Usage

After installing, just go to your package top-level directory and execute the `abs2rel` command.

## License

abs2rel is dedicated to the public domain with [The Unlicense][].

## Efficiency

This command does not identify 100% of the possible local absolute imports. However, at its current state, it manages to identify all but a single import statement in a real package containing more than 200 python files (some with several local imports).

Future improvements should increase its efficiency even more. At its current state though, it can already reduce substantialy the time needed to convert local absolute imports from a Python package into local relative imports. Additionally, because the conversion happens programmatically, it is less error-prone than making the changes by hand.


[The Unlicense]: https://unlicense.org/
