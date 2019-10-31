import argparse
import os
import sys

import pyfmt

DEFAULT_PATH = os.getenv("BASE_CODE_DIR", ".")
DEFAULT_LINE_LENGTH = int(os.getenv("MAX_LINE_LENGTH", "100"))


def main():
    parser = argparse.ArgumentParser(prog="pyfmt")
    parser.add_argument(
        "path",
        nargs="?",
        default=DEFAULT_PATH,
        metavar="PATH",
        help="path to base directory where pyfmt will be run;"
        " defaults to $BASE_CODE_DIR or the current directory",
    )
    parser.add_argument(
        "--skip", default="", help="Directory (ie. env/foo) or files (ie. cool.py) to skip."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="don't write changes, just print the files that would be formatted",
    )
    parser.add_argument(
        "--line-length",
        type=int,
        default=DEFAULT_LINE_LENGTH,
        help="max characters per line; defaults to $MAX_LINE_LENGTH or 100",
    )
    parser.add_argument("--extra-isort-args", default="", help="additional args to pass to isort")
    parser.add_argument("--extra-black-args", default="", help="additional args to pass to black")

    opts = parser.parse_args()

    exitcode = pyfmt.pyfmt(
        opts.path,
        skip=opts.skip,
        check=opts.check,
        line_length=opts.line_length,
        extra_isort_args=opts.extra_isort_args,
        extra_black_args=opts.extra_black_args,
    )
    sys.exit(exitcode)


if __name__ == "__main__":
    main()
