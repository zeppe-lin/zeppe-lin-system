# SPDX-FileCopyrightText: 2026 Alexandr Savca
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class BuildContext:
    source_root: Path
    build_root: Path
    pkgctl: Path
    pkgstate_init: Path
    git: Path
    readelf: Path
    controller_source_lock: str = ''
