#!/usr/bin/env python3
from __future__ import annotations

import configparser
import re
import sys
from pathlib import Path

EXPECTED = {
    'libpkgapply', 'libpkgapply-exec', 'libpkgapply-posix', 'libpkgaudit',
    'libpkgbuild', 'libpkgbuild-exec', 'libpkgbuild-image', 'libpkgbuild-plan',
    'libpkgcatalog', 'libpkgcatalog-acquire', 'libpkgcheck', 'libpkgcheck-exec',
    'libpkgexec', 'libpkgexec-linux', 'libpkgfetch', 'libpkgimage',
    'libpkgimage-exec', 'libpkgplan', 'libpkgreconcile',
    'libpkgreconcile-apply', 'libpkgreconcile-apply-posix',
    'libpkgreconcile-posix', 'libpkgresolve', 'libpkgsource',
    'libpkgsource-exec', 'libpkgsource-plan', 'libpkgsource-yaml',
    'libpkgstate', 'libpkgstate-apply', 'libpkgstate-build',
    'libpkgstate-plan', 'libpkgstate-posix', 'libpkgstate-source',
    'libpkgtransaction', 'pkgctl',
}
HEX40 = re.compile(r'^[0-9a-f]{40}$')
EXPECTED_PKGCTL_REVISION = '436f1382f5f5dcb6093e11b6074fbc15a7826f19'
EXPECTED_APPLY_POSIX_REVISION = 'ec03cdb9a268465668e72f05e5fe60c046ee3d5e'
EXPECTED_TRANSACTION_REVISION = '5e9b78ec702a96ee477c8d342824d9c6b5253022'


def fail(message: str) -> None:
    raise SystemExit(f'source-lock: {message}')


def load_wrap(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with path.open(encoding='utf-8') as stream:
            parser.read_file(stream)
    except (OSError, configparser.Error) as error:
        fail(f'{path.name}: cannot parse wrap: {error}')
    return parser


def main() -> None:
    if len(sys.argv) != 2:
        fail('usage: source_lock_test.py SOURCE_ROOT')
    root = Path(sys.argv[1])
    wrap_dir = root / 'subprojects'
    wraps = {path.stem: path for path in wrap_dir.glob('*.wrap')}
    if set(wraps) != EXPECTED:
        missing = sorted(EXPECTED - set(wraps))
        extra = sorted(set(wraps) - EXPECTED)
        fail(f'controller closure mismatch; missing={missing} extra={extra}')

    revisions: set[str] = set()
    for name in sorted(EXPECTED):
        parser = load_wrap(wraps[name])
        if parser.sections()[0:1] != ['wrap-git']:
            fail(f'{name}: source must be a wrap-git lock')
        section = parser['wrap-git']
        expected_url = f'https://github.com/zeppe-lin/{name}.git'
        if section.get('url') != expected_url:
            fail(f'{name}: unexpected source URL')
        revision = section.get('revision', '')
        if not HEX40.fullmatch(revision):
            fail(f'{name}: revision is not an exact 40-hex commit')
        if revision in revisions:
            fail(f'{name}: duplicate revision unexpectedly reused')
        revisions.add(revision)
        for forbidden in ('depth', 'push-url'):
            if forbidden in section:
                fail(f'{name}: {forbidden} is forbidden in canonical source lock')

    pkgctl = load_wrap(wraps['pkgctl'])
    if pkgctl['wrap-git'].get('revision') != EXPECTED_PKGCTL_REVISION:
        fail('pkgctl is not pinned to the admitted 0.40.2 release authority')
    apply_posix = load_wrap(wraps['libpkgapply-posix'])
    if apply_posix['wrap-git'].get('revision') != EXPECTED_APPLY_POSIX_REVISION:
        fail('libpkgapply-posix is not pinned to the admitted 3.2.2 release authority')
    transaction = load_wrap(wraps['libpkgtransaction'])
    if transaction['wrap-git'].get('revision') != EXPECTED_TRANSACTION_REVISION:
        fail('libpkgtransaction is not pinned to the admitted 4.1.0 release authority')

    catalog = load_wrap(wraps['libpkgcatalog'])
    if catalog.get('provide', 'dependency_names', fallback='') != \
            'libpkgcatalog, libpkgcatalog-codec':
        fail('libpkgcatalog must provide catalog and codec dependency names')
    source = load_wrap(wraps['libpkgsource'])
    if source.get('provide', 'dependency_names', fallback='') != \
            'libpkgsource, libpkgsource-codec':
        fail('libpkgsource must provide source and codec dependency names')


if __name__ == '__main__':
    main()
