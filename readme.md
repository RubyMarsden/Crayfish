## Crayfish

This program accompanies the paper "A new approach to SHRIMP II zircon U-Th disequilibrium dating".

### Getting started

#### Standalone executables

Standalone executables are available for Ubuntu and Windows
[here](https://github.com/RubyMarsden/Crayfish/releases). These should be downloadable
and runnable without any further action.

* The executable may take up to 30 seconds to show the window the first time you run the program. Subsequent runs
should be faster.

#### Running the Python code directly

The source code for each release is available
[here](https://github.com/RubyMarsden/Crayfish/releases). Download the source code, unzip
it into a folder. Open a terminal and navigate inside the unzipped folder. Run
```
pip install requirements.txt
```
in order to ensure you have the correct set of Python modules installed. Then to start the program run:
```
python src/Crayfish.py
```