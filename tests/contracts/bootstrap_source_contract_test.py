#!/usr/bin/env python3
from __future__ import annotations

import configparser
import re
import sys
from pathlib import Path

EXPECTED_REVISION = 'df1c1b01827858845c3d9111edd8c8318febbe5c'


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
        fail('foundation source is not pinned to the admitted Stage-B GCC handoff authority')

    if (root / 'subprojects' / 'pkgsrc-foundation.wrap').exists():
        fail('package-source metadata was smuggled into the controller subproject graph')

    qualification = root / 'products' / 'bootstrap' / 'qualification' / 'collection'
    recipes = sorted(path.relative_to(qualification).as_posix()
                     for path in qualification.glob('*/recipe.yml'))
    if recipes != ['seed-probe/recipe.yml']:
        fail(f'bootstrap qualification collection differs: {recipes}')
    if (root / 'products' / 'bootstrap' / 'collection').exists():
        fail('qualification recipes are presented as ordinary bootstrap product inputs')

    seed_probe = (qualification / 'seed-probe' / 'recipe.yml').read_text(
        encoding='utf-8')
    if 'name: seed-probe' not in seed_probe:
        fail('seed-probe recipe identity differs')

    product_sources = '\n'.join(
        path.read_text(encoding='utf-8')
        for path in sorted((root / 'zlsystem').glob('*.py')))
    if product_sources.count("FOUNDATION_OPERATION_PROFILE = 'exact-compatible-sharing'") != 1:
        fail('foundation operation profile is not one product-owned selection')
    if product_sources.count("BOOTSTRAP_PRODUCT_MODEL = 'seed-assisted-stage-b-gcc-handoff'") != 1:
        fail('bootstrap product model is not one exact Stage-B semantic authority')
    if "'product_model': BOOTSTRAP_PRODUCT_MODEL" not in product_sources or \
            "marker.get('product_model') != BOOTSTRAP_PRODUCT_MODEL" not in product_sources:
        fail('workspace admission does not retain/fail-close on the exact product model')
    if "marker['product_model']" not in product_sources:
        fail('bootstrap product model does not bind request identity')
    if "product-model {marker[\"product_model\"]}" not in product_sources:
        fail('bootstrap manifest omits the admitted product model')
    if "foundation-operation-policy-profile {_foundation_operation_profile(marker)}" not in product_sources:
        fail('bootstrap manifest omits the retained foundation operation profile')
    if "'source_lock': context.controller_source_lock" not in product_sources:
        fail('bootstrap workspace omits the configured controller source-lock authority')
    if 'controller-source-lock {marker["controller"]["source_lock"]}' not in product_sources:
        fail('bootstrap manifest omits the admitted controller source-lock authority')
    if "'--goal', f'check={CONSTRUCTION_HANDOFF_SUBJECT}'" not in product_sources:
        fail('bootstrap product never exercises the admitted Stage-B GCC handoff subject')
    if "CONSTRUCTION_HANDOFF_STAGE = 'seed-assisted-gcc-handoff-qualified'" not in product_sources or \
            'construction-handoff-stage {CONSTRUCTION_HANDOFF_STAGE}' not in product_sources:
        fail('bootstrap evidence does not name the Stage-B GCC handoff qualification')
    if "CONSTRUCTION_HANDOFF_SUBJECT = 'gcc-bootstrap'" not in product_sources or \
            'construction-handoff-subject {CONSTRUCTION_HANDOFF_SUBJECT}' not in product_sources:
        fail('bootstrap evidence does not name the exact Stage-B handoff subject')
    if "'--goal', 'run=@construction'" in product_sources:
        fail('bootstrap prematurely promotes the incomplete handoff as a construction profile')
    if 'seed-execution-root-view {seed_execution_root_view_identity(marker)}' not in product_sources:
        fail('bootstrap manifest omits admitted historical seed root-view authority')
    if "'--build-root-view', seed_execution_root_view_digest(marker)" not in product_sources or \
            "'--lifecycle-root-view', seed_execution_root_view_digest(marker)" not in product_sources:
        fail('pkgctl execution root-view options do not receive raw SHA-256 digests')
    if "return f'v1:sha256:{seed_execution_root_view_digest(marker)}'" not in product_sources:
        fail('system evidence does not retain typed seed execution root-view identity')
    if "return base / 'package-objects'" not in product_sources or \
            "'--package-object-store', _package_object_store(base)" not in product_sources:
        fail('bootstrap does not bind the current package-object provider outside retained semantics')
    if "'package_object_store':" in product_sources:
        fail('bootstrap elevated the current package-object pathname into retained product semantics')
    for root_view_option in ('--build-root-view', '--lifecycle-root-view'):
        if root_view_option not in product_sources:
            fail(f'bootstrap start omits explicit execution root-view authority: {root_view_option}')
    if "'seed-execution-root-view'" not in product_sources or \
            "marker['seed']['sha256']" not in product_sources:
        fail('historical seed root-view identity is not derived from admitted seed bytes')
    if "controller.get('source_lock') != context.controller_source_lock" not in product_sources:
        fail('bootstrap semantic admission does not bind retained controller closure')
    if "retained_foundation.get('revision') != current_foundation.revision" not in product_sources:
        fail('resume does not fail closed when pinned foundation source authority changes')
    if "retained_qualification.get('sha256') != current_qualification" not in product_sources:
        fail('resume does not fail closed when product qualification source changes')
    for foreign_vocabulary in (
            'shared_ownership_policy', 'incoming_path_policy', 'obsolete_path_policy',
            'directory_cleanup_policy', 'path_override_policy'):
        if foreign_vocabulary in product_sources:
            fail(f'product frontend copied planner policy vocabulary: {foreign_vocabulary}')


if __name__ == '__main__':
    main()
