import shlex
import subprocess
import sys
from subprocess import PIPE
import time

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

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = list()
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            allFiles = allFiles + getListOfFiles(fullPath)
        else:
            allFiles.append(fullPath)
                
    return allFiles



def pyfmt(path, skip="", check=False, line_length=100, extra_isort_args="", extra_black_args="") -> int:
    """Run isort and black with the given params and print the results."""
    timer_start = time.time()
    if skip:
        # Map out all sub directories with files
        all_files = []
        all_dirs = []
        for root, dirs, files in os.walk("."):
            for name in files:
                # Saving filename
                all_files.append(name)
            for name in dirs:
                # Saving directory name
                all_dirs.append(os.path.abspath(os.path.join(root, name)))
        # Remove duplicates
        all_files = list(set(all_files))

        # Parse comma seperated input
        skips = skip.split(',')
        filenames_to_skip = []
        for item in skips:
            if item in all_files:
                if item.split('.')[-1] == 'py':
                    filenames_to_skip.extend([item])
            elif os.path.abspath(item) in all_dirs:
                # Saving all filenames in directory
                files_in_dir = list()
                for (dirpath, dirnames, filenames) in os.walk(item):
                    for filename in filenames:
                        if filename.split('.')[-1] == 'py' or filename.split('.')[-1] == 'pyi':
                            files_in_dir.append(filename)
                    # files_in_dir += [file for file in filenames]
                filenames_to_skip.extend(files_in_dir)
            else:
                print('ERROR: File or directory marked as skipped not found! Aborting pyfmt ...')

        # Remove duplicate filenames
        # filenames_to_skip = list(set(filenames_to_skip))

        print(filenames_to_skip)
        print('Number of files to be skipped: {}'.format(len(filenames_to_skip)))

        # for file in filenames_to_skip:
        #     print(file.split('.')[-1])

        # filenames_to_skip.append('black')

        # Make a continous string
        filenames_to_skip_str = ""
        for filename in filenames_to_skip:
            filenames_to_skip_str += '--skip=' + filename + " "
        filenames_to_skip_str = filenames_to_skip_str[:-1]

        # Adding to the isort arguments
        extra_isort_args += filenames_to_skip_str




    input('stop here')

    if check:
        extra_isort_args += " --check-only"
        extra_black_args += " --check"

    isort_exitcode = run_formatter(
        ISORT_CMD, path, line_length=line_length, extra_isort_args=extra_isort_args
    )
    # black_exitcode = run_formatter(
    #     BLACK_CMD, path, line_length=line_length, extra_black_args=extra_black_args
    # )


    print('Execution Time: {} seconds'.format(time.time() - timer_start))
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
