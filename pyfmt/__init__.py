import shlex
import subprocess
import sys
from subprocess import PIPE
from typing import List, Optional, Tuple

from . import select

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

SELECTOR_MAP = {
    "staged": select.select_staged,
    "modified": select.select_modified,
    "head": select.select_head,
    "local": select.select_local,
    "all": select.select_all,
}


def pyfmt(
    path: str,
    selector: str = "all",
    line_length: int = 100,
    check: bool = False,
    commit: Optional[List[str]] = None,
    commit_msg: Optional[str] = None,
    extra_isort_args: str = "",
    extra_black_args: str = "",
) -> int:
    """Run isort and black with the given params and print the results."""
    # Filter path according to given ``selector``.
    select_files = SELECTOR_MAP[selector]
    files = tuple(select_files(path))
    if not files:
        print("No files need formatting.")
        return 0

    if check:
        extra_isort_args += " --check-only"
        extra_black_args += " --check"

    # Run isort and black.
    files_str = " ".join(files)
    isort_lines, isort_exitcode = run_formatter(
        ISORT_CMD, files_str, line_length=line_length, extra_isort_args=extra_isort_args
    )
    black_lines, black_exitcode = run_formatter(
        BLACK_CMD, files_str, line_length=line_length, extra_black_args=extra_black_args
    )
    exitcode = isort_exitcode or black_exitcode

    # Commit changes if successful.
    if not exitcode and not check and commit is not None:
        cmd = ["git", "commit"]

        if "patch" in commit:
            cmd.append("--patch")
        if "amend" in commit:
            cmd.append("--amend")

        if commit_msg is not None:
            # If no message given, use auto-commit behavior.
            if commit_msg == "":
                # If `amend` given, the commit already has a message, so just skip the editor.
                if "amend" in commit:
                    cmd.append("--no-edit")
                # Otherwise, copy the previous commit's message.
                else:
                    cmd.append("--reuse-message=HEAD")
            else:
                cmd.append(f"--message={commit_msg}")

        # If `all` given, commit all selected files. Otherwise, commit only formatted files.
        if "all" in commit:
            cmd.extend(files)
        else:
            formatted_files = {line.split()[-1] for line in isort_lines + black_lines}
            cmd.extend(formatted_files)

        subprocess.run(cmd)

    return exitcode


def run_formatter(cmd, path, **kwargs) -> Tuple[List[str], int]:
    """Helper to run a shell command and print prettified output."""
    cmd = shlex.split(" ".join(cmd).format(path=path, **kwargs))
    result = subprocess.run(cmd, stdout=PIPE, stderr=PIPE)

    prefix = f"{cmd[0]}: "
    sep = "\n" + (" " * len(prefix))
    lines = result.stderr.decode().splitlines()

    # Remove fluff from black's output.
    if cmd[0] == "black" and result.returncode == 0:
        lines = lines[:-2]

    if "".join(lines) == "":
        print(f"{prefix}No changes.")
    else:
        print(f"{prefix}{sep.join(lines)}")

    return lines, result.returncode
