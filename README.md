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

## Contrib

### Example Use in a Git Hook

Prevent a `git commit` if `pyfmt --check --select staged` comes back dirty:

```console
ln -sf contrib/git_hooks/pre-commit .git/hooks
```

Prevent a `git push` if `pyfmt --check --select local` comes back dirty:

```console
ln -sf contrib/git_hooks/pre-push .git/hooks
```

### Example Use in a Jenkinsfile

You can add [contrib/jenkins/pyfmt.groovy](contrib/jenkins/pyfmt.groovy) to your Jenkins pipeline
library so that you can use `pyfmt` as a function in your `Jenkinsfile`s. For example,
`pyfmt "src/tests/"`. Read more about how to set that up at
https://jenkins.io/doc/book/pipeline/shared-libraries/ in the "Using Libraries" section.

## Usage

*Just FYI*, `isort` works best when your virtual environment is active (if your src relies on one).
*This will then allow imports to sort in the correct way (system packages, 3rd party packages,
*local/project packages). If you are not in your virtual env, the global Python environment will be
*used which might place your local package imports in with the 3rd party package imports.

Also FYI, `git` is not required to use `pyfmt`. However, it is required if you are using `--select`
with anything other than `all` (the default), or if you are using `--commit` or `--commit-msg`,
since these options are all reliant on the status of your git working tree and index.

```console
usage: pyfmt [-h] [-x SELECT] [-c] [--line-length N]
             [--commit [ARG [ARG ...]]] [--commit-msg [MSG [MSG ...]]]
             [--extra-isort-args ARGS] [--extra-black-args ARGS]
             [PATH]

positional arguments:
  PATH                  path to base directory where pyfmt will be run
                        (default: $BASE_CODE_DIR | '.')

optional arguments:
  -h, --help            show this help message and exit
  -x SELECT, --select SELECT
                        filter which files to format in PATH:
                        > all       (default) all files
                        > staged    files in the index
                        > modified  files in the index, working tree, and
                                    untracked files
                        > head      files changed in HEAD
                        > local     files changed locally but not upstream
  -c, --check           don't write changes, just print the files that would be
                        formatted
  --line-length N       max characters per line (default: $MAX_LINE_LENGTH |
                        100)
  --commit [ARG [ARG ...]]
                        commit files that were formatted. one or more args can
                        be given to change this behavior:
                        > patch   commit files with --patch
                        > amend   commit files with --amend
                        > all     commit all selected files, whether or not
                                  they were formatted
  --commit-msg [MSG [MSG ...]]
                        auto-commit changes. if args are given, they are
                        concatenated to form the commit message. otherwise the
                        current commit's log message is reused. if --commit is
                        not present, a naked `--commit` is implied.
  --extra-isort-args ARGS
                        additional args to pass to isort
  --extra-black-args ARGS
                        additional args to pass to black
```

* `--check` returns non-zero exist status if files need formatting, but doesn't modify files. This
  is appropriate for CI systems where you might want to fail a build if the code is not formatted
  correctly.
* If no specific path is specified, all files in the current directory and all sub directories where
  you run the code will be formatted.
* As a matter of convenience, you may set `$BASE_CODE_DIR` in your environment and run the script
  in the case this is better for your needs.
