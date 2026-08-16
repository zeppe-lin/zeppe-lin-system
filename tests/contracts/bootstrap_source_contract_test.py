#!/usr/bin/env python3
from __future__ import annotations

import configparser
import re
import sys
from pathlib import Path

EXPECTED_REVISION = 'd247718c6405f9f6e0a95b9681ab9b677ecda750'


def fail(message: str) -> None:
    raise SystemExit(f'bootstrap-source-authority: {message}')


def main() -> None:
    if len(sys.argv) != 2:
        fail('usage: bootstrap_source_contract_test.py SOURCE_ROOT')
    root = Path(sys.argv[1])
    descriptor = root / 'collections' / 'foundation.ini'
    parser = configparser.ConfigParser(interpolation=None)
    with descriptor.open(encoding='utf-8') as stream:
        parser.read_file(stream)
    if parser.sections() != ['collection']:
        fail('foundation source descriptor does not have one [collection] section')
    source = parser['collection']
    if set(source) != {'protocol', 'name', 'url', 'revision'}:
        fail('foundation source descriptor vocabulary differs')
    if source['protocol'] != 'zeppe-lin.system.collection-source/1':
        fail('foundation source protocol differs')
    if source['name'] != 'foundation':
        fail('foundation source descriptor names another collection')
    if source['url'] != 'https://github.com/zeppe-lin/pkgsrc-foundation.git':
        fail('foundation source authority is not the canonical repository')
    if source['revision'] != EXPECTED_REVISION or not re.fullmatch(r'[0-9a-f]{40}', source['revision']):
        fail('foundation source is not pinned to the admitted migration commit')

    if (root / 'subprojects' / 'pkgsrc-foundation.wrap').exists():
        fail('package-source metadata was smuggled into the controller subproject graph')

    qualification = root / 'products' / 'bootstrap' / 'qualification' / 'collection'
    recipes = sorted(path.relative_to(qualification).as_posix()
                     for path in qualification.glob('*/recipe.yml'))
    if recipes != ['runtime-cohort-probe/recipe.yml', 'seed-probe/recipe.yml']:
        fail(f'bootstrap qualification collection differs: {recipes}')
    if (root / 'products' / 'bootstrap' / 'collection').exists():
        fail('qualification recipes are presented as ordinary bootstrap product inputs')

    for name in ('seed-probe', 'runtime-cohort-probe'):
        text = (qualification / name / 'recipe.yml').read_text(encoding='utf-8')
        if f'name: {name}' not in text:
            fail(f'{name} recipe identity differs')


if __name__ == '__main__':
    main()
