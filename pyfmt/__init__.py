import shlex
import subprocess
import sys
from subprocess import PIPE

import os

TARGET_VERSION = f"py{sys.version_info.major}{sys.version_info.minor}"

ISORT_CMD = [
    "isort",
    "--force-grid-wrap=0",
    "--line-width={line_length}",
    "--multi-line=3",
    "--use-parentheses",
    "--recursive",
    "--trailing-comma",
    "{extra_isort_args}",
    "{path}",
]
BLACK_CMD = [
    "black",
    "--line-length={line_length}",
    f"--target-version={TARGET_VERSION}",
    "{extra_black_args}",
    "{path}",
]


def pyfmt(path, skip="", check=False, line_length=100, extra_isort_args="", extra_black_args="") -> int:
    """Run isort and black with the given params and print the results."""
    if skip:
        path_rel = skip
        # path_abs = os.path.join(os.getcwd(), path_rel)

        # Map out all sub directories with files
        all_files = []
        all_dirs = []
        for root, dirs, files in os.walk(".", topdown=False):
            for name in files:
                print(os.path.join(root, name))
                all_files.append(name)
            for name in dirs:
                print(os.path.join(root, name))
                all_dirs.append(name)

        print(all_files)
        print(all_dirs)

        # Parse input
        skips = skip.split(',')

        for item in skips:
            print(item)
            if item in all_files:
                print('FILE THERE')
            elif item in all_dirs:
                print('DIR THERE')
            else:
                print('not found')
            
            # if os.path.isfile(item):
            #     # Is a specific file
            #     print('FILE')
            #     extra_isort_args += "--skip=" + item
            # elif os.path.isdir(item):
            #     # is a directory
            #     print('DIRECTORY')
            # else:
            #     # is bs
            #     print('BS')


    input('stop here')

    if check:
        extra_isort_args += " --check-only"
        extra_black_args += " --check"

    isort_exitcode = run_formatter(
        ISORT_CMD, path, line_length=line_length, extra_isort_args=extra_isort_args
    )
    black_exitcode = run_formatter(
        BLACK_CMD, path, line_length=line_length, extra_black_args=extra_black_args
    )

    return isort_exitcode or black_exitcode


def run_formatter(cmd, path, **kwargs) -> int:
    """Helper to run a shell command and print prettified output."""
    cmd = shlex.split(" ".join(cmd).format(path=path, **kwargs))
    print(cmd)
    result = subprocess.run(cmd, stdout=PIPE, stderr=PIPE)

    prefix = f"{cmd[0]}: "
    sep = "\n" + (" " * len(prefix))
    lines = result.stdout.decode().splitlines() + result.stderr.decode().splitlines()
    if "".join(lines) == "":
        print(f"{prefix}No changes.")
    else:
        print(f"{prefix}{sep.join(lines)}")

    return result.returncode
