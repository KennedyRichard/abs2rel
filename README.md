# abs2rel

A python script that traverses a whole package turning local absolute imports into relative ones.

It can reduce substantialy the time needed to convert local absolute imports from a Python package into local relative imports. Additionally, because the conversion is automated, it is less error-prone than having someone make the changes manually.

This command only recognizes local absolute imports which are in the `from ... import ...` format, where the `from` and `import` keywords are on the same line.

This script was originally tested on the [nodezator app](https://github.com/IndiePython/nodezator) at commit [be4c17f](https://github.com/IndiePython/nodezator/commit/be4c17f4c9d09951b48345836fb24de70f5ee90f), managing to convert all 1685 existing absolute local imports across 270 python files into relative imports successfully, without needing any additional manual work.

If you want to try this yourself, just clone nodezator, checkout the mentioned commit and, inside the nodezator/nodezator folder, execute the `abs2rel` command. Then, go up one folder level and launch the app with `python -m nodezator` and you'll see that the local relative imports work properly, launching the app without problems.


## Installation

```bash
pip install abs2rel
```

## Usage

After installing, just go to your package top-level directory and execute the `abs2rel` command. Before actually changing the files, the script presents the number of imports and files that are about to be changed and asks the user to confirm in order to proceed. Remember to make a backup of your package before executing this script, just in case.

## License

abs2rel is dedicated to the public domain with [The Unlicense](https://unlicense.org/).
