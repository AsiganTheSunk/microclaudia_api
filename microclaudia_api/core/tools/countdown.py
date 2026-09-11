import re
import sys
import time

HIDE_CURSOR: str = "\033[?25l"
SHOW_CURSOR: str = "\033[?25h"
CLEAR_LINE: str = "\033[2K"
CURSOR_UP: str = "\033[1A"

_ANSI_CSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def is_tty(stream=None) -> bool:
    """
    This function, will report whether the given stream is an interactive terminal.
    :param stream: Stream to inspect; defaults to sys.stdout.
    :return: True when the stream is a TTY.
    """
    stream = stream or sys.stdout
    try:
        return stream.isatty()
    except Exception:
        return False


def tty_write(text: str, tty: bool) -> None:
    """
    This function, will write text to stdout and flush, stripping ANSI codes when not on a terminal.
    :param text: Text to write, possibly containing ANSI escape sequences.
    :param tty: When False, ANSI control codes are removed before writing.
    """
    if not tty:
        text = _ANSI_CSI_RE.sub("", text)
    sys.stdout.write(text)
    sys.stdout.flush()


def countdown(max_timer: int = 30, max_dashes: int = 30, tty: bool | None = None) -> None:
    """
    This function, will block for a countdown timer, redrawing in place on a TTY and sleeping silently otherwise.
    :param max_timer: Seconds to count down from.
    :param max_dashes: Width of the progress bar when redrawing on a TTY.
    :param tty: Force TTY behavior; when None, detect via is_tty().
    """
    tty = is_tty() if tty is None else tty
    tty_write(HIDE_CURSOR, tty)
    try:
        for _timer in range(max_timer, -1, -1):
            if tty:
                _dash_len: int = int(max_dashes * _timer / max(max_timer, 1))
                _dashes: str = "-" * _dash_len
                _blank_spaces: str = " " * (max_dashes - _dash_len)
                _trailing_blank_spaces: str = " " * max_dashes
                _bar: str = f"{_blank_spaces}{_dashes} {_timer} {_dashes}{_blank_spaces}{_trailing_blank_spaces}"
                tty_write("\r" + _bar, tty)
            if _timer:
                time.sleep(1)
    finally:
        tty_write(SHOW_CURSOR + "\r", tty)
