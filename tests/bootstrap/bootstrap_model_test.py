#!/usr/bin/env python3
from __future__ import annotations

import io
import stat
import sys
import tarfile
import tempfile
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(f'bootstrap-model: {message}')


def add_file(archive: tarfile.TarFile, name: str, data: bytes = b'x') -> None:
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mode = 0o644
    archive.addfile(info, io.BytesIO(data))


def main() -> None:
    if len(sys.argv) != 2:
        fail('usage: bootstrap_model_test.py SOURCE_ROOT')
    root = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(root))
    from zlsystem import bootstrap

    foundation = bootstrap.load_foundation_descriptor(root)
    if foundation.name != 'foundation':
        fail('foundation descriptor does not load')
    seed = bootstrap.load_seed_descriptor(root, None)
    if seed.architecture != 'x86_64' or len(seed.sha256) != 64:
        fail('default seed descriptor does not load')

    marker = {
        'seed': {'sha256': seed.sha256},
        'foundation': {'revision': foundation.revision},
        'qualification': {'sha256': '1' * 64},
        'build_policy': {
            'parallelism': 4,
            'source_date_epoch': 0,
            'file_creation_mask': '0022',
            'output_layout': 'package-root',
        },
    }
    main_nonce = bootstrap.nonce_for('runtime-cohort-probe', marker)
    marker['build_policy']['parallelism'] = 8
    if bootstrap.nonce_for('runtime-cohort-probe', marker) == main_nonce:
        fail('build policy does not contribute to bootstrap request identity')
    marker['build_policy']['parallelism'] = 4
    marker.update({
        'workspace': '/tmp/bootstrap-workspace',
        'seed': {**marker['seed'], 'root': '/tmp/bootstrap-workspace/seed-root',
                 'interpreter': '/tmp/bootstrap-workspace/seed-root/bin/bash'},
        'supervisor': {'user_id': 0, 'group_id': 0, 'groups': [0]},
    })
    from zlsystem.model import BuildContext
    context = BuildContext(
        source_root=root, build_root=Path('/tmp/build'),
        pkgctl=Path('/controller/pkgctl'), pkgstate_init=Path('/controller/pkgstate-init'),
        git=Path('/usr/bin/git'), readelf=Path('/usr/bin/readelf'))
    start_args = bootstrap._start_pkgctl_args(
        context, marker, qualification=False, maximum_steps=8)
    resume_args = bootstrap._resume_pkgctl_args(
        context, marker, qualification=False, maximum_steps=8)
    for token in ('--collection', '--build-parallelism', '--build-source-date-epoch', '--start'):
        if token not in start_args:
            fail(f'start command omits admitted semantic option: {token}')
        if token in resume_args:
            fail(f'resume command redeclares start-only semantic option: {token}')
    if '--resume' not in resume_args:
        fail('resume command omits retained request identity')
    try:
        bootstrap._reject_start_redeclaration(
            bootstrap.BootstrapOptions(Path('/tmp/work'), jobs=4))
    except bootstrap.BootstrapError:
        pass
    else:
        fail('resume-time build policy redeclaration was accepted')

    old_identity = bootstrap.identity_for('managed-target', marker)
    marker['qualification']['sha256'] = '2' * 64
    if bootstrap.identity_for('managed-target', marker) == old_identity:
        fail('qualification authority does not contribute to target binding')

    report = '''\
disposition step-limit-reached
complete no
failed no
artifact.0.package filesystem
artifact.0.path /tmp/a.tar
artifact.0.sha256 abc
'''
    if bootstrap.report_terminal(report) != (False, False):
        fail('nonterminal report parsing differs')
    artifacts = bootstrap.artifact_records(report)
    if len(artifacts) != 1 or artifacts[0].get('package') != 'filesystem':
        fail('artifact report parsing differs')

    with tempfile.TemporaryDirectory() as temporary:
        temp = Path(temporary)
        good = temp / 'good.tar'
        with tarfile.open(good, 'w') as archive:
            root = tarfile.TarInfo('.')
            root.type = tarfile.DIRTYPE
            root.mode = 0
            archive.addfile(root)
            add_file(archive, './usr/bin/tool', b'ok')
        output = temp / 'good'
        output.mkdir()
        output_mode = stat.S_IMODE(output.stat().st_mode)
        bootstrap._extract_archive_bytes(good.read_bytes(), output)
        if (output / 'usr/bin/tool').read_bytes() != b'ok':
            fail('safe archive extraction lost regular member after root marker')
        if stat.S_IMODE(output.stat().st_mode) != output_mode:
            fail('archive root marker rewrote extraction-root metadata')

        escaping = temp / 'escaping.tar'
        with tarfile.open(escaping, 'w') as archive:
            add_file(archive, '../escape', b'bad')
        escaping_root = temp / 'escaping-root'
        try:
            bootstrap.extract_seed_archive(escaping, escaping_root)
        except bootstrap.BootstrapError:
            pass
        else:
            fail('archive traversal member was admitted')
        if escaping_root.exists():
            fail('rejected seed archive retained a partial extraction root')

        absolute_link = temp / 'absolute-link.tar'
        with tarfile.open(absolute_link, 'w') as archive:
            link = tarfile.TarInfo('./usr/lib/libnsl.so.2')
            link.type = tarfile.SYMTYPE
            link.linkname = '/usr/lib/libnsl.so.2.0.1'
            archive.addfile(link)
        absolute_root = temp / 'absolute-link-root'
        old_extraction_filter = getattr(tarfile.TarFile, 'extraction_filter', None)
        if hasattr(tarfile, 'data_filter'):
            tarfile.TarFile.extraction_filter = staticmethod(tarfile.data_filter)
        try:
            bootstrap._extract_archive_bytes(absolute_link.read_bytes(), absolute_root)
        finally:
            if hasattr(tarfile.TarFile, 'extraction_filter'):
                tarfile.TarFile.extraction_filter = old_extraction_filter
        extracted_link = absolute_root / 'usr/lib/libnsl.so.2'
        if not extracted_link.is_symlink():
            fail('admitted absolute rootfs symlink was not preserved')
        if str(extracted_link.readlink()) != '/usr/lib/libnsl.so.2.0.1':
            fail('admitted absolute rootfs symlink target differs')

        symlink = temp / 'symlink.tar'
        with tarfile.open(symlink, 'w') as archive:
            link = tarfile.TarInfo('alias')
            link.type = tarfile.SYMTYPE
            link.linkname = '/tmp'
            archive.addfile(link)
            add_file(archive, 'alias/escape', b'bad')
        try:
            bootstrap._extract_archive_bytes(symlink.read_bytes(), temp / 'symlink')
        except bootstrap.BootstrapError:
            pass
        else:
            fail('archive member descending through symlink was admitted')


if __name__ == '__main__':
    main()
