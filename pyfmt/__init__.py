import os
import shlex
import subprocess
import sys
import time
from subprocess import PIPE

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


def pyfmt_title():
    """
    Display a cool ascii art title
    """
    pyfmt_splash = [
        "               __           _    ",
        "              / _|         | |   ",
        "  _ __  _   _| |_ _ __ ___ | |_  ",
        " | '_ \| | | |  _| '_ ` _ \| __| ",
        " | |_) | |_| | | | | | | | | |_  ",
        " | .__/ \__, |_| |_| |_| |_|\__| ",
        " | |     __/ |                   ",
        " |_|    |___/                    ",
    ]
    print("\033[94m")
    for part in pyfmt_splash:
        print(f"{part.center(os.get_terminal_size().columns, ' ')}")
    print("\033[0m")


def find_all_files_and_dirs():
    """
    Map out all files and directories in the current
    working directory
    """
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

    return all_files, all_dirs


def display_divider(title="", character="=", color_code="\033[94m"):
    """
    Divider between sections of program.
    """
    if title:
        print(
            "\n"
            + "{}".format(color_code)
            + "  {}  ".format(title.upper()).center(
                os.get_terminal_size().columns, "{}".format(character)
            )
            + "\033[0m"
        )
    else:
        print(
            "\n"
            + "{}".format(color_code)
            + "".center(os.get_terminal_size().columns, "{}".format(character))
            + "\033[0m"
        )


def pyfmt(
    path, skip="", check=False, line_length=100, extra_isort_args="", extra_black_args=""
) -> int:
    """Run isort and black with the given params and print the results."""
    pyfmt_title()  # Display title
    timer_start = time.time()  # Measure how long everything takes

    if skip:
        # Map out current working directory
        all_files, all_dirs = find_all_files_and_dirs()
        # If specified files and directories exist, store the filenames
        skips = skip.split(",")
        filenames_to_skip = []
        for item in skips:
            if item in all_files:
                if item.split(".")[-1] == "py":
                    filenames_to_skip.extend([item])
            elif os.path.abspath(item) in all_dirs:
                # Saving all filenames in directory
                files_in_dir = list()
                for (dirpath, dirnames, filenames) in os.walk(item):
                    for filename in filenames:
                        if filename.split(".")[-1] == "py" or filename.split(".")[-1] == "pyi":
                            files_in_dir.append(filename)
                filenames_to_skip.extend(files_in_dir)
            else:
                print(
                    'CRITICAL: One of the files or directories marked as skipped not found ("{}").'.format(
                        item
                    )
                )
                print("CRITICAL: Check spelling or existence of file or directory")
                print("CRITICAL: Aborting pyfmt ...")
                sys.exit()
        # Display Files skipped
        display_divider(title="SKIPPING FILES")
        for filename_to_skip in filenames_to_skip:
            print(f"SKIPPING: {filename_to_skip}")
        print("\nNumber of files to be skipped: {}".format(len(filenames_to_skip)))
        # Make a continuos string of arguments for
        #   isort - must be separate --skip for each file
        #   black - regex for exact filename (ie. file1|file2|etc.)
        isort_filenames_to_skip = ""
        black_filenames_to_skip = ""
        for filename in filenames_to_skip:
            isort_filenames_to_skip += "--skip=" + filename + " "
            black_filenames_to_skip += filename + "|"
        isort_filenames_to_skip = isort_filenames_to_skip[:-1]
        black_filenames_to_skip = black_filenames_to_skip[:-1]
        # Adding to the isort and black arguments
        extra_isort_args += isort_filenames_to_skip
        extra_black_args += "--exclude=" + black_filenames_to_skip

    if check:
        extra_isort_args += " --check-only"
        extra_black_args += " --check"

    isort_exitcode = run_formatter(
        ISORT_CMD, path, line_length=line_length, extra_isort_args=extra_isort_args
    )
    black_exitcode = run_formatter(
        BLACK_CMD, path, line_length=line_length, extra_black_args=extra_black_args
    )

    print("\npyfmt Execution Time: {0:.2f} seconds".format(time.time() - timer_start))
    return isort_exitcode  # or black_exitcode


def run_formatter(cmd, path, **kwargs) -> int:
    """Helper to run a shell command and print prettified output."""
    cmd = shlex.split(" ".join(cmd).format(path=path, **kwargs))
    result = subprocess.run(cmd, stdout=PIPE, stderr=PIPE)

    prefix = f"{cmd[0]}: "
    display_divider(title=prefix[:-2])
    sep = "\n"
    lines = result.stdout.decode().splitlines() + result.stderr.decode().splitlines()
    if "".join(lines) == "":
        print(f"No changes.")
    else:
        print(f"{sep.join(lines)}")

    return result.returncode
