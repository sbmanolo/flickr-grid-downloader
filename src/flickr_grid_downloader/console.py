from __future__ import annotations

import logging
from typing import Any

from rich.console import Console
from rich.logging import RichHandler

# ---------- console «global» ----------
console = Console(emoji=True, highlight=False)  # highlight = False increases performance a bit

# ---------- logging ----------
LOG_FORMAT = "%(message)s"

def get_logger(name: str | None = None, level: int = logging.INFO) -> logging.Logger:
    """
    Returns a logger with RichHandler only the first time;
    subsequent calls reuse the global configuration.
    """
    if not logging.getLogger().handlers:  # avoid duplicate handlers
        logging.basicConfig(
            level=level,
            format=LOG_FORMAT,
            datefmt="[%X]",
            handlers=[RichHandler(console=console, show_time=True, show_level=True)]
        )
    return logging.getLogger(name)

# ---------- UX helpers ----------
def success(msg: str, **kwargs: Any) -> None:
    console.print(f"[bold green]✔[/] {msg}", **kwargs)

def warn(msg: str, **kwargs: Any) -> None:
    console.print(f"[bold yellow]⚠[/] {msg}", **kwargs)

def error(msg: str, **kwargs: Any) -> None:
    console.print(f"[bold red]✖[/] {msg}", **kwargs)

def info(msg: str, **kwargs: Any) -> None:
    console.print(f"[bold blue]ℹ[bold cyan] {msg}[/]", **kwargs)

def debug(msg: str, **kwargs: Any) -> None:
    console.print(f"[bold magenta]🔍 {msg}[/]", **kwargs)
