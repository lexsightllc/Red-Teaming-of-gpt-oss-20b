# SPDX-License-Identifier: MPL-2.0

"""Compatibility shim that delegates to :mod:`red_teaming.cli`."""
from __future__ import annotations

from red_teaming.cli import main


if __name__ == "__main__":  # pragma: no cover - compatibility path
    main()
