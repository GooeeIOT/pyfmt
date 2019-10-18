# pyfmt

Python auto-formatting using [isort](https://isort.readthedocs.io/en/latest/) and
[black](https://black.readthedocs.io/en/latest/).

## Installation

### Using pip

```console
pip3 install git+https://github.com/GooeeIOT/pyfmt.git
```

### From source

```console
git clone https://github.com/GooeeIOT/pyfmt
cd pyfmt
python setup.py install
```

### Install the git hook

Prevent a `git push` from completing if the formatter runs and there is a code difference from what
is about to be `push`ed.

```console
ln -sf path/to/pyfmt/git_hooks/pre-push .git/hooks
```

This is a check only and does not alter your code. Run `pyfmt` to fix.

### Use in a Jenkinsfile

You can add [contrib/jenkins/pyfmt.groovy](contrib/jenkins/pyfmt.groovy) to your Jenkins pipeline
library to use `pyfmt("paths/to your/code")` in a `Jenkinsfile`.

## Usage

Be advised with projects in a virtual env: `isort` works best when your virtual env is active.
Then, imports will sort in the correct way (system packages, 3rd parts packages, local packages).
If you are not in your virtual env, the global Python environment will be used which might place
your local package imports in with the 3rd party package imports.

```console
usage: pyfmt [-h] [--check] [--line-length LINE_LENGTH]
             [--extra-isort-args EXTRA_ISORT_ARGS]
             [--extra-black-args EXTRA_BLACK_ARGS]
             [PATH]

positional arguments:
  PATH                  path to base directory where pyfmt will be run;
                        defaults to $BASE_CODE_DIR or the current directory

optional arguments:
  -h, --help            show this help message and exit
  --check               don't write changes, just print the files that would
                        be formatted
  --line-length LINE_LENGTH
                        max characters per line; defaults to $MAX_LINE_LENGTH
                        or 100
  --extra-isort-args EXTRA_ISORT_ARGS
                        additional args to pass to isort
  --extra-black-args EXTRA_BLACK_ARGS
                        additional args to pass to black
```

* `--check` returns non-zero exist status if files need formatting, but doesn't modify files. This
  is appropriate for CI systems where you might want to fail a build if the code is not formatted
  correctly.
* If no specific path is specified, all files in the current directory and all sub directories where
  you run the code will be formatted.
* As a matter of convenience, you may set `$BASE_CODE_DIR` in your environment and run the script
  in the case this is better for your needs.
