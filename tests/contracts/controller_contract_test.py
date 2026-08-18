#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f'controller-boundary: {message}')


def require(text: str, needle: str, label: str) -> None:
    if needle not in text:
        fail(f'missing {label}: {needle}')


def forbid(text: str, needle: str, label: str) -> None:
    if needle in text:
        fail(f'forbidden {label}: {needle}')


def main() -> None:
    if len(sys.argv) != 2:
        fail('usage: controller_contract_test.py SOURCE_ROOT')
    root = Path(sys.argv[1])
    meson = (root / 'meson.build').read_text(encoding='utf-8')

    require(meson, "meson_version: '>=1.8.3'", 'Meson floor')
    require(meson, "license: 'GPL-3.0-or-later'", 'project license')
    require(meson, 'force_fallback_for=', 'pinned dependency forcing')
    match = re.search(r"force_fallback_for=([^']+)", meson)
    if match is None:
        fail('cannot parse force_fallback_for source set')
    forced = set(match.group(1).split(','))
    expected_forced = {
        'libpkgapply', 'libpkgapply-exec', 'libpkgapply-posix', 'libpkgaudit',
        'libpkgbuild', 'libpkgbuild-exec', 'libpkgbuild-image', 'libpkgbuild-plan',
        'libpkgcatalog', 'libpkgcatalog-acquire', 'libpkgcatalog-codec',
        'libpkgcheck', 'libpkgcheck-exec', 'libpkgexec', 'libpkgexec-linux',
        'libpkgfetch', 'libpkgimage', 'libpkgimage-exec', 'libpkgplan',
        'libpkgreconcile', 'libpkgreconcile-apply',
        'libpkgreconcile-apply-posix', 'libpkgreconcile-posix', 'libpkgresolve',
        'libpkgsource', 'libpkgsource-codec', 'libpkgsource-exec',
        'libpkgsource-plan', 'libpkgsource-yaml', 'libpkgstate',
        'libpkgstate-apply', 'libpkgstate-build', 'libpkgstate-plan',
        'libpkgstate-posix', 'libpkgstate-source', 'libpkgtransaction',
    }
    if forced != expected_forced:
        fail(f'force_fallback_for mismatch; missing={sorted(expected_forced - forced)} '
             f'extra={sorted(forced - expected_forced)}')
    for dep in ('libcrypto', 'libarchive', 'libcurl', 'yaml-0.1', 'threads'):
        require(meson, f"dependency('{dep}'", f'host dependency {dep}')

    require(meson, "subproject('libpkgstate-posix')", 'state adapter subproject')
    require(meson, "get_variable('pkgstate_init_tool')", 'pkgstate-init target export')
    require(meson, "subproject('pkgctl')", 'pkgctl subproject')
    require(meson, "get_variable('pkgctl_exe')", 'pkgctl target export')
    require(meson, "dependency('libpkgexec-linux', required: true)",
            'wrapped Linux execution dependency')
    require(meson, "alias_target('controller', pkgctl_exe, pkgstate_init_tool)",
            'controller alias')
    require(meson, "pkgctl_exe.full_path()", 'pkgctl target path authority')
    require(meson, "pkgstate_init_tool.full_path()", 'pkgstate-init path authority')
    require(meson, "find_program('git', required: true)", 'product source acquisition tool')
    require(meson, "find_program('readelf', required: true)", 'bootstrap qualification tool')
    require(meson, "input: 'tools/zlsystem.in'", 'system frontend template')
    require(meson, "output: 'zlsystem'", 'system frontend output')
    require(meson, "frontend_configuration.set('PKGCTL', pkgctl_exe.full_path())",
            'frontend pkgctl target authority')
    require(meson, "frontend_configuration.set('PKGSTATE_INIT', pkgstate_init_tool.full_path())",
            'frontend pkgstate-init target authority')
    require(meson, "frontend_configuration.set('CONTROLLER_SOURCE_LOCK', controller_source_lock)",
            'frontend configured source-lock authority')
    require(meson, "'tests/controller/controller_source_lock_digest.py'",
            'configured source-lock identity')
    require(meson, "'tests/controller/wrapped_source_authority_test.py'",
            'resolved fallback source authority test')
    require(meson, 'wrapped_source_authority_test,',
            'configure-time fallback source attestation')
    require(meson, "'wrapped-source-authority'",
            'wrapped source authority test registration')
    require(meson, "'tests/controller/wrapped_source_authority_model_test.py'",
            'hostile wrapped source authority model')
    require(meson, "'wrapped-source-authority-model'",
            'wrapped source authority hostile test registration')
    require(meson, "'wrapped-pkgctl-start'", 'wrapped controller startup test')
    require(meson, "'tests/controller/wrapped_pkgctl_release_test.py'",
            'wrapped pkgctl release witness')
    require(meson, "'0.40.2'", 'admitted wrapped pkgctl release')
    require(meson, "'wrapped-isolation'", 'wrapped privileged isolation test')
    require(meson, "suite: 'integration-privileged'", 'privileged wrapper test suite')

    # Controller composition must not recreate the historical installed-prefix
    # feedback loop or begin privileged system construction inside Meson.
    for token in (
        '.toolchain', 'PKG_CONFIG_PATH', 'LD_LIBRARY_PATH',
        'CMAKE_PREFIX_PATH', 'NEW_TOOLCHAIN_PREFIX',
        'build-new-toolchain.sh', 'sudo ', 'bootstrap_campaign.sh',
    ):
        forbid(meson, token, 'legacy or privileged orchestration')

    wraps = sorted((root / 'subprojects').glob('*.wrap'))
    for wrap in wraps:
        name = wrap.stem
        if name == 'pkgctl':
            require(meson, "'pkgctl:tests=disabled'", 'pkgctl test suppression')
            require(meson, "'pkgctl:man_pages=disabled'", 'pkgctl docs suppression')
            continue
        # Every library project in the controller source set currently defines
        # a tests option; source composition must not pull its maintainer suite.
        require(meson, f"'{name}:tests=disabled'", f'{name} test suppression')

    require(meson, "'libpkgstate-posix:tools=enabled'", 'pkgstate-init build')
    require(meson, "'libpkgstate-posix:install_tools=false'", 'build-tree tool ownership')
    require(meson, "'libpkgaudit:tools=disabled'", 'audit reference tool suppression')
    require(meson, "'libpkgcatalog-acquire:scan_tool=disabled'", 'scan tool suppression')
    require(meson, "'libpkgplan:reference_tools=disabled'", 'plan tool suppression')

    # Product execution remains outside the Meson/Ninja build graph.
    for forbidden_target in ("run_target('bootstrap'", "run_target('rootfs'",
                             "alias_target('bootstrap'", "alias_target('rootfs'"):
        forbid(meson, forbidden_target, 'premature product target')


if __name__ == '__main__':
    main()
