import sys

import pyfmt

from .utils import FormattedHelpArgumentParser

SELECT_CHOICES = {
    "all": "all files",
    "staged": "files in the index",
    "modified": "files in the index, working tree, and untracked files",
    "head": "files changed in HEAD",
    "local": "files changed locally but not upstream",
}

COMMIT_CHOICES = {
    "patch": "commit files with --patch",
    "amend": "commit files with --amend",
    "all": "commit all selected files, whether or not they were formatted",
}


def main():
    parser = FormattedHelpArgumentParser(prog="pyfmt")
    parser.add_argument(
        "path",
        nargs="?",
        envvar="BASE_CODE_DIR",
        default=".",
        metavar="PATH",
        help="path to base directory where pyfmt will be run",
    )
    parser.add_choices_argument(
        "-x",
        "--select",
        choices=SELECT_CHOICES,
        default="all",
        metavar="SELECT",
        help="filter which files to format in PATH:",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        help="don't write changes, just print the files that would be formatted",
    )
    parser.add_argument(
        "--line-length",
        type=int,
        envvar="MAX_LINE_LENGTH",
        default=100,
        metavar="N",
        help="max characters per line",
    )
    parser.add_choices_argument(
        "--commit",
        choices=COMMIT_CHOICES,
        nargs="*",
        metavar="ARG",
        help="commit files that were formatted. one or more args can be given to change this"
        " behavior:",
    )
    parser.add_argument(
        "--commit-msg",
        nargs="*",
        metavar="MSG",
        help="auto-commit changes. if args are given, they are concatenated to form the commit"
        " message. otherwise the current commit's log message is reused. if --commit is not"
        " present, a naked `--commit` is implied.",
    )
    parser.add_argument(
        "--extra-isort-args", default="", metavar="ARGS", help="additional args to pass to isort"
    )
    parser.add_argument(
        "--extra-black-args", default="", metavar="ARGS", help="additional args to pass to black"
    )

    opts = parser.parse_args()

    if opts.commit_msg is not None:
        # Concatenate --commit-msg.
        opts.commit_msg = " ".join(opts.commit_msg)
        # Add implicit --commit if --commit-msg is given.
        if opts.commit is None:
            opts.commit = []

    exitcode = pyfmt.pyfmt(
        opts.path,
        opts.select,
        check=opts.check,
        line_length=opts.line_length,
        commit=opts.commit,
        commit_msg=opts.commit_msg,
        extra_isort_args=opts.extra_isort_args,
        extra_black_args=opts.extra_black_args,
    )
    sys.exit(exitcode)


if __name__ == "__main__":
    main()
