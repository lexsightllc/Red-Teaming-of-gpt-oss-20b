# SPDX-License-Identifier: MPL-2.0

"""Executable module entrypoint for the red_teaming package."""
from __future__ import annotations

from .cli import main


if __name__ == "__main__":  # pragma: no cover - delegate to CLI
    main()
