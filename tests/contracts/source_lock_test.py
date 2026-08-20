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
    'libpkgimage-exec', 'libpkgobject', 'libpkgplan', 'libpkgreconcile',
    'libpkgreconcile-apply', 'libpkgreconcile-apply-posix',
    'libpkgreconcile-posix', 'libpkgresolve', 'libpkgsource',
    'libpkgsource-exec', 'libpkgsource-plan', 'libpkgsource-yaml',
    'libpkgstate', 'libpkgstate-apply', 'libpkgstate-build',
    'libpkgstate-plan', 'libpkgstate-posix', 'libpkgstate-source',
    'libpkgtransaction', 'pkgctl',
}
HEX40 = re.compile(r'^[0-9a-f]{40}$')
EXPECTED_CONTROLLER_REVISIONS = {
    'libpkgapply': (
        '36aa530ae07dc1c2a7f1ee999a7626977fc8a53e', '4.0.1'),
    'libpkgapply-exec': (
        'efbae2415b93ef001dad8aa8cdd34365cadd304b', '3.0.2'),
    'libpkgapply-posix': (
        '61b0595e11edb4c072e3f05aa8672f3e4c8569e5', '4.0.0'),
    'libpkgbuild': (
        '8dc3f17ec152330e98391eb747a377e9c2bb6db8', '3.0.3'),
    'libpkgreconcile-apply': (
        'e5d03cd518b25d01a462aaf411980cf02af0a4f9', '0.1.2'),
    'libpkgreconcile-apply-posix': (
        '1cf029d8f3626bb3544b0f14092f5806d92a0f5b', '0.1.2'),
    'libpkgstate-apply': (
        '6af8af6547612e096e07acdb27daaeb3ee530711', '3.1.3'),
    'libpkgtransaction': (
        '5e9b78ec702a96ee477c8d342824d9c6b5253022', '4.1.0'),
    'libpkgobject': (
        '022917659cb7d042d4a5b8814629d208235f4977', '0.1.0'),
    'pkgctl': (
        'ef52450096dd5aec88897fc34ea5c70f609e9a52', '0.43.0'),
}


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

    for name, (expected_revision, release) in EXPECTED_CONTROLLER_REVISIONS.items():
        actual = load_wrap(wraps[name])['wrap-git'].get('revision')
        if actual != expected_revision:
            fail(f'{name} is not pinned to the admitted {release} release authority')

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
