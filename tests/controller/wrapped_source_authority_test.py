#!/usr/bin/env python3
from __future__ import annotations

import configparser
import subprocess
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f'wrapped-source-authority: {message}')


def git_output(git: Path, checkout: Path, *args: str) -> str:
    process = subprocess.run(
        [str(git), '-C', str(checkout), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if process.returncode != 0:
        detail = process.stderr.strip() or process.stdout.strip() or f'exit status {process.returncode}'
        fail(f'{checkout.name}: git {" ".join(args)} failed: {detail}')
    return process.stdout


def expected_revision(path: Path) -> str:
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with path.open(encoding='utf-8') as stream:
            parser.read_file(stream)
    except (OSError, configparser.Error) as error:
        fail(f'{path.name}: cannot parse wrap: {error}')
    if 'wrap-git' not in parser:
        fail(f'{path.name}: source is not wrap-git authority')
    revision = parser['wrap-git'].get('revision', '')
    if len(revision) != 40 or any(ch not in '0123456789abcdef' for ch in revision):
        fail(f'{path.name}: revision is not exact 40-hex authority')
    return revision


def main() -> None:
    if len(sys.argv) != 3:
        fail('usage: wrapped_source_authority_test.py SOURCE_ROOT GIT')
    root = Path(sys.argv[1]).resolve()
    git = Path(sys.argv[2]).resolve()
    wraps = sorted((root / 'subprojects').glob('*.wrap'))
    if not wraps:
        fail('controller source lock is empty')

    for wrap in wraps:
        name = wrap.stem
        expected = expected_revision(wrap)
        checkout = root / 'subprojects' / name
        if not checkout.is_dir():
            fail(f'{name}: configured fallback checkout is absent; update Meson subprojects')
        observed = git_output(git, checkout, 'rev-parse', 'HEAD').strip()
        if observed != expected:
            fail(
                f'{name}: configured fallback checkout differs from source lock; '
                f'expected {expected}, observed {observed}; run meson subprojects update --reset')
        dirty = git_output(
            git, checkout, 'status', '--porcelain', '--untracked-files=no').strip()
        if dirty:
            fail(f'{name}: configured fallback checkout has tracked modifications')


if __name__ == '__main__':
    main()
