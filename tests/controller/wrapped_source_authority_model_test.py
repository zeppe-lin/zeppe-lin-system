#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f'wrapped-source-authority-model: {message}')


def run_checker(checker: Path, root: Path, git: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(checker), str(root), str(git)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def main() -> None:
    if len(sys.argv) != 2:
        fail('usage: wrapped_source_authority_model_test.py SOURCE_ROOT')
    source_root = Path(sys.argv[1]).resolve()
    checker = source_root / 'tests/controller/wrapped_source_authority_test.py'
    git_name = shutil.which('git')
    if git_name is None:
        fail('git is unavailable')
    git = Path(git_name).resolve()

    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        subprojects = root / 'subprojects'
        checkout = subprojects / 'demo'
        checkout.mkdir(parents=True)
        subprocess.run([git, '-C', checkout, 'init', '-q'], check=True)
        subprocess.run([git, '-C', checkout, 'config', 'user.email', 'authority@example.invalid'], check=True)
        subprocess.run([git, '-C', checkout, 'config', 'user.name', 'authority-model'], check=True)
        tracked = checkout / 'tracked'
        tracked.write_text('one\n', encoding='utf-8')
        subprocess.run([git, '-C', checkout, 'add', 'tracked'], check=True)
        subprocess.run([git, '-C', checkout, 'commit', '-q', '-m', 'one'], check=True)
        first = subprocess.run(
            [git, '-C', checkout, 'rev-parse', 'HEAD'], check=True,
            text=True, stdout=subprocess.PIPE).stdout.strip()
        (subprojects / 'demo.wrap').write_text(
            '[wrap-git]\nurl = https://example.invalid/demo.git\nrevision = ' + first + '\n',
            encoding='utf-8')

        accepted = run_checker(checker, root, git)
        if accepted.returncode != 0:
            fail(f'exact clean fallback checkout was rejected: {accepted.stderr.strip()}')

        tracked.write_text('two\n', encoding='utf-8')
        subprocess.run([git, '-C', checkout, 'add', 'tracked'], check=True)
        subprocess.run([git, '-C', checkout, 'commit', '-q', '-m', 'two'], check=True)
        stale = run_checker(checker, root, git)
        if stale.returncode == 0 or 'differs from source lock' not in stale.stderr:
            fail('stale fallback HEAD was not refused')

        subprocess.run([git, '-C', checkout, 'checkout', '-q', first], check=True)
        tracked.write_text('dirty\n', encoding='utf-8')
        dirty = run_checker(checker, root, git)
        if dirty.returncode == 0 or 'tracked modifications' not in dirty.stderr:
            fail('dirty tracked fallback checkout was not refused')


if __name__ == '__main__':
    main()
