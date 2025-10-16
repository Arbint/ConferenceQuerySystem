# Poetry Setup

The project is configured with ```poetry```

To install poetry:
```sh
curl -sSL https://install.python-poetry.org | python3 -
```

To user poetry to define and run the project, first initialized the project:

```sh
poerty init
```

It will ask a few questions, but all these settings can be changed later on in the generated pyproject.toml file. to see how toml file works: [toml File quick doc](tomlFileConfig.md)

Go to the generated ```pyproject.toml``` file, and configure your project to your liking:

* under the ```project``` table:
    * define the python version:
        ```toml
        [project]
        requires-python = "=3.12.10"
        ```
    * define the python packages (dependences):
        ```toml
        [project]
        dependencies = [
            "streamlit==1.38.0",
            "qrcode==8.0",
            "pillow==10.4.0",
        ]
        ```
        ```NOTE:```for dependencies, you can also do:
        ```sh
        poetry add packagename
        ```
        to add it to the ```dependencies``` list.

    * under the ```tool.poetry``` table, define your own packages(where are you source code & modules):
        ```toml
        [tool.poetry]
        packages = [
            {include = "conferencequerysystem", from="src"}
        ]
        ```

    * under ```tool.poetry.scripts```, define your runable scripts:
        ```toml
        [tool.poetry.scripts]
        qrcodegen = "conferencequerysystem.qrCodeGen:main"
        ```
        this is saying: there is a command called ```qrcodegen```, when executed, call, the ```main``` function defined in the ```qrCodeGen.py``` file under the ```conferencequerysystem``` module.

        and we call run the command by doing:

        ```sh
        poetry run qrcodegen
        ```

To create a virtual environment, we will need to be sure the current active python version is the same as the python version defined in he ```pyproject.toml``` file:

```toml
[project]
requires-python = "=3.12.10"
```

Easiest way to do that, is to make the path to the python executable be the first in the path environment variable.

now do:
```sh
poetry install
```

this will:

* Create the python virtual environment if it does not exist
* Install all packages defined in the ```dependencies``` list under the ```project``` table defined inthe pyproject.toml file.
```toml
[project]
dependencies = [
    "streamlit==1.38.0",
    "qrcode==8.0",
    "pillow==10.4.0",
]
```
* Install your own package (your src code) to the python virtual environment, in editable mode.
    * editable mode means that your project is added as a package to the virtual environment similar to adding packages like PySide6, but instead of building and copying your project source files to the virtual environment, it links to your current project src files, which means you can edit your project src file and run the program without a re-install.

Optionally, you can do a build, which will make a distributable package for your project:

```sh
poetry build
```

this will create a dist folder under the project, and with in, zipped up files that can be used as packages by other projects.