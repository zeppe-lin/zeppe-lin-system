#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f'controller-source-lock-digest: {message}')


def main() -> None:
    if len(sys.argv) != 2:
        fail('usage: controller_source_lock_digest.py SOURCE_ROOT')
    root = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(root))
    from zlsystem.source_lock import controller_source_lock_digest
    try:
        print(controller_source_lock_digest(root))
    except (OSError, ValueError) as error:
        fail(str(error))


if __name__ == '__main__':
    main()
