#!/usr/bin/env python3
from __future__ import annotations

import configparser
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

HEX64 = re.compile(r'^[0-9a-f]{64}$')
EXPECTED_KEYS = {
    'protocol', 'name', 'architecture', 'release', 'url', 'sha256',
    'signature_url', 'signature_sha256',
}


def fail(message: str) -> None:
    raise SystemExit(f'seed-descriptors: {message}')


def main() -> None:
    if len(sys.argv) != 2:
        fail('usage: seed_contract_test.py SOURCE_ROOT')
    root = Path(sys.argv[1])
    seed_dir = root / 'seeds'
    default_name = (seed_dir / 'default').read_text(encoding='utf-8').strip()
    descriptors = sorted(seed_dir.glob('*.ini'))
    if not descriptors:
        fail('no seed descriptors')
    if default_name not in {path.name for path in descriptors}:
        fail('default seed does not name a committed descriptor')

    for path in descriptors:
        parser = configparser.ConfigParser(interpolation=None)
        with path.open(encoding='utf-8') as stream:
            parser.read_file(stream)
        if parser.sections() != ['seed']:
            fail(f'{path.name}: expected exactly one [seed] section')
        seed = parser['seed']
        if set(seed) != EXPECTED_KEYS:
            fail(f'{path.name}: descriptor vocabulary mismatch')
        if seed['protocol'] != 'zeppe-lin.system.seed/1':
            fail(f'{path.name}: unsupported protocol')
        if seed['architecture'] != 'x86_64':
            fail(f'{path.name}: initial seed set is x86_64-only')
        for key in ('sha256', 'signature_sha256'):
            if not HEX64.fullmatch(seed[key]):
                fail(f'{path.name}: {key} is not a SHA-256 digest')
        for key in ('url', 'signature_url'):
            parsed = urlparse(seed[key])
            if parsed.scheme != 'https' or parsed.netloc != 'github.com':
                fail(f'{path.name}: {key} must use canonical GitHub HTTPS authority')
            if not parsed.path.startswith('/zeppe-lin/pkgsrc-core/releases/download/'):
                fail(f'{path.name}: {key} is outside pkgsrc-core release authority')
        if not seed['signature_url'].endswith(seed['url'].split('/')[-1] + '.sig'):
            fail(f'{path.name}: detached signature does not correspond to seed archive')

    if default_name != 'zeppe-lin-1.2.1-20260222-x86_64.ini':
        fail('recommended fixed v1.2 seed is not the default')


if __name__ == '__main__':
    main()
