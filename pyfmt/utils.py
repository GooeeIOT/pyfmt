import argparse
import math
import os
import shlex
import textwrap
from typing import Mapping, Optional

HELP_WIDTH = 55


def round_up_to(x: int, base: int) -> int:
    """Round ``x`` up to the nearest multiple of ``base``."""
    return int(math.ceil(x / base)) * base


class FormattedHelpArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser that adds formatting to help text.

    Adds the following behavior to ``argparse.ArgumentParser``:

    - Uses ``argparse.RawTextHelpFormatter`` by default, but still wraps help text to 79 chars.
    - Automatically adds information about argument defaults to help text.
    - Generates custom help text for arguments with ``choices``.
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("formatter_class", argparse.RawTextHelpFormatter)
        super().__init__(*args, **kwargs)

    @staticmethod
    def _fill(text: str, width=HELP_WIDTH, **kwargs):
        """Calls ``textwrap.fill`` with a default width of ``HELP_WIDTH``."""
        return textwrap.fill(text, width=width, **kwargs)

    def add_argument(self, *name_or_flags: str, envvar: Optional[str] = None, **kwargs):
        """Adds some functionality to ``add_argument``.

        - Optionally take an environment variable as a default.
        - Add any default to the help text.
        - Wrap ``help`` (``argparse.RawTextHelpFormatter`` doesn't auto-wrap help text).

        :param envvar:
            Name of an environment variable to use as the default value.

            If a ``default`` is also given, it will be used as a fallback if the env var isn't set.
            If no ``default`` is given _and_ the env var isn't set, a ValueError will be raised.

            If the argument stores a list of values, the environment variable will be parsed into a
            list using `shlex.split`.
        """
        # If `envvar` given, set argument `default` to its value if set.
        if envvar:
            val = os.getenv(envvar)
            if val:
                type_func = kwargs.get("type") or str
                nargs = kwargs.get("nargs")
                # If argument stores a list, parse envvar as a list.
                if (
                    nargs
                    and (nargs in ("*", "+") or isinstance(nargs, int))
                    or kwargs.get("action") in ("append", "append_const", "extend")
                ):
                    kwargs["default"] = [type_func(item) for item in shlex.split(val)]
                else:
                    kwargs["default"] = type_func(val)
            elif "default" not in kwargs:
                raise ValueError(f"`envvar` ${envvar} not found, and no `default` was given")

        # Add default to help text.
        help_text = kwargs.get("help")
        if help_text:
            default = kwargs.get("default")

            default_list = []
            if envvar:
                default_list.append(f"${envvar}")
            if default and default is not argparse.SUPPRESS:
                default_list.append(f"{default!r}")

            if default_list:
                default_str = " | ".join(default_list)
                if "%(default)" in help_text:
                    help_text = help_text % {"default": default_str}
                else:
                    help_text += f" (default: {default_str})"

            # Wrap help text.
            kwargs["help"] = self._fill(help_text)

        return super().add_argument(*name_or_flags, **kwargs)

    def add_choices_argument(self, *name_or_flags: str, choices: Mapping[str, str], **kwargs):
        """Add an argument with ``choices``.

        The ``choices`` param takes a mapping of choices to help text for each choice, and appends
        a formatted line to the given ``help`` for each choice.

        Note that this will not work if ``formatter_class`` is set to anything other than
        ``argparse.RawTextHelpFormatter`` (the default).
        """
        choices = dict(choices)

        # If ``default`` given, prepend "(default) " to the help text of the default choice.
        default = kwargs.get("default")
        if default and default is not argparse.SUPPRESS and default in choices:
            choices[default] = f"(default) {choices[default]}"

        # Generate help text for choices.
        prefix = "> "
        max_choice_len = max(len(choice) for choice in choices.keys()) + 2
        choice_width = round_up_to(max_choice_len, 2)
        choice_help_width = HELP_WIDTH - choice_width - len(prefix)
        choice_help_indent = " " * (choice_width + len(prefix))
        choice_fmt = "{prefix}{choice:<%d}{help:<%d}" % (choice_width, choice_help_width)
        choices_help = "\n".join(
            choice_fmt.format(
                prefix=prefix,
                choice=choice,
                help=self._fill(
                    text, width=choice_help_width, subsequent_indent=choice_help_indent
                ),
            )
            for choice, text in choices.items()
        )

        # Format final help text.
        help_text = "{}:\n{}".format(
            self._fill(kwargs.pop("help", "choices").rstrip(",.:;")), choices_help
        )
        return super().add_argument(*name_or_flags, choices=choices, help=help_text, **kwargs)
