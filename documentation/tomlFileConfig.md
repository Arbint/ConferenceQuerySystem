# Toml File Structure

TOML is a configuration file format, similar to JSON, that can be used to store almost any kind of structured data.

In Python projects, the pyproject.toml file is commonly used to define configuration settings for the project.

It can include things like the name of the project, the modules it contains, the authors, and what tools are used to build or run the project.



### The ```.toml``` file organizes configurations into tables, like these:

```
[project]
...
[build-system]
...
[tool.poetry]
...
```
so in this case, ```project```,  ```build-system```, ```tool.poetry``` are tables.

```poetry``` is a nested table under ```tool``` table.

### Inside each table, are ```key = value``` lines:

```
name = "programscheduler"
version = "0.1.0"
requires-python = ">=3.9,<3.14"
```

* Strings use quotes "...".

* Numbers, booleans (true, false), and arrays (lists) are written plainly.

* Example array:
```
dependencies = ["pyside6>=6.9.1,<7.0.0"]
```

* Array of tables:

when you need an array of dictionaries as a value, like multiple authors, use the following syntax:

```
[project]
authors = [
    {name = "Arbint",email = "cg.jingtianli@gmail.com"},
    {name = "Anoter Author",email = "cg.jingtianli@gmail.com", cell = 1234555}
]
```
some data here are recognized like name and email, but cell is an arbitaray data that the build tools do not understand, so they will just simple be ignored.

# Build Tools:

Defined in ```pyproject.toml```:
```toml
[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```
in here: 

* requires = what tools to install before building, but rarely need more than one.

* build-backend = after installing everyting in the requires, what module to used for the building (has to exist in one of the required tools that's installed)

Build tools like poetry are used to help with:

### 1, Project setup

* Generate a clean project layout

* Create a pyproject.toml file with basic metadata (name, version, author, etc.)

* Set up a src/ layout to separate code from config

* Like a scaffold or project initializer


### 2, Dependency Management

* Add, update, or remove packages (like requests, pyside6, etc.)

```bash
poetry add flask
poetry remove numpy
```

* Automatically resolve and lock exact versions

* Store dependency versions in a poetry.lock file

* Like a package manager + version control (think npm, pip, composer)

### 3, Environment Management

* Automatically create and manage a virtual environment per project

```bash
poetry run python
```
To define which python to use, we can do:
```bash
poetry env use /directory/path/to/python
```
Or We can make sure that the python version we want to use to be the first in the path.

* Keeps dependencies isolated from the global Python installation

Similar to venv, but automated and project-aware

### 4, building Packages

Create distributable .whl and .tar.gz files

```bash
poetry build
```
The Two Package Formats
### 1 .whl — Wheel
A built distribution (a pre-packaged, installable format), think of it as a zip file of your libaray src files + addtional meta data + c binaries built if required.  

Contains the original .py files. 

Fast to install, no extra work needed.


### 2. .tar.gz — Source distribution (also called sdist)
A source distribution — the raw source code of your package, compressed

Needs to be built by pip when installed

Acts as a fallback when a wheel is unavailable or unsupported on the user’s platform

* Handles the structure, metadata, and format needed for pip install

Equivalent to python -m build

they are essentially a zipped folder, the files within are different:

| Item                        | `.sdist`      | `.whl`          |
| --------------------------- | ------------- | --------------- |
| `pyproject.toml`            | ✅ Yes         | ❌ No            |
| `setup.py` / `setup.cfg`    | ✅ Often       | ❌ No            |
| Raw source (`.py`, `.c`)    | ✅ Yes         | ✅ Yes/No¹       |
| Compiled extensions (`.so`) | ❌ No          | ✅ Yes (if used) |
| `*.dist-info/` metadata     | ❌ No          | ✅ Yes           |
| `README.md`, `tests/`       | ✅ Often       | ❌ No            |
| Ready to install?           | ❌ Needs build | ✅ Yes           |


### What is setup.py?
ususally looks like this, predecessor of the pyproject.toml
```py
from setuptools import setup, find_packages

setup(
    name="myproject",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mycli = myproject.cli:main",
        ]
    },
)
```
### What is setup.cfg?
ussuall looks like this, a config file that contains the same info a setup.py usually has:

```toml
[metadata]
name = myproject
version = 0.1.0
description = A cool project
author = Arbint
author_email = arbint@example.com

[options]
packages = find:
install_requires =
    requests>=2.0.0
    numpy

[options.entry_points]
console_scripts =
    mycli = myproject.cli:main

```
with a setup.cfg file, you can make your setup.py simpler:

```py
from setuptools import setup
setup()
```
this will let setuptools pull config from setup.cfg if it can find any.


### 5. Publishing to PyPI
Upload your project to PyPI or TestPyPI

```bash
poetry publish --build
```
Handles authentication, versioning, and upload protocols

### 6. Configuration and metadata management
All in one pyproject.toml:

* Project name, version, author

* License

* Dependencies

* Scripts/entry points

* Tool configs (e.g. for Black, MyPy)

### 7. Running scripts and tools
Run your app or scripts in the project environment:

```bash
poetry run python main.py
```
Or register CLI commands:

```toml
[tool.poetry.scripts]
mytool = "my_package.main:main"
```

### 8. Lock file management

* poetry.lock ensures repeatable installs for all developers on the project

* poetry install always installs exact versions

Like package-lock.json for Python
