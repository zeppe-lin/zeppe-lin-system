# SPDX-FileCopyrightText: 2026 Alexandr Savca
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import hashlib
from pathlib import Path


SOURCE_LOCK_DOMAIN = b'zeppe-lin.system.controller-source-lock/1'


def controller_source_lock_digest(source_root: Path) -> str:
    root = source_root.resolve()
    wraps = sorted((root / 'subprojects').glob('*.wrap'), key=lambda path: path.name)
    if not wraps:
        raise ValueError('controller source lock is empty')
    digest = hashlib.sha256()
    digest.update(SOURCE_LOCK_DOMAIN)
    for path in wraps:
        name = path.name.encode()
        payload = path.read_bytes()
        digest.update(len(name).to_bytes(8, 'big'))
        digest.update(name)
        digest.update(len(payload).to_bytes(8, 'big'))
        digest.update(payload)
    return 'v1:sha256:' + digest.hexdigest()
