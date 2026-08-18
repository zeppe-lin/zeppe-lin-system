#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f'wrapped-pkgctl-release: {message}')


def main() -> None:
    if len(sys.argv) != 3:
        fail('usage: wrapped_pkgctl_release_test.py PKGCTL VERSION')
    pkgctl = Path(sys.argv[1]).resolve()
    version = sys.argv[2]
    process = subprocess.run(
        [str(pkgctl), '--version'],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        fail(f'pkgctl --version failed with status {process.returncode}: {process.stderr.strip()}')
    expected = f'pkgctl {version}\n'
    if process.stdout != expected:
        fail(f'expected {expected.strip()!r}, observed {process.stdout.strip()!r}')
    if process.stderr:
        fail(f'pkgctl --version wrote stderr: {process.stderr.strip()}')


if __name__ == '__main__':
    main()
