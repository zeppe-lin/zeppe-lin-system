#!/usr/bin/env python3
from __future__ import annotations

import io
import shutil
import stat
import subprocess
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
    if bootstrap.EXPECTED_PACKAGE_COORDINATES.get('glibc') != ('2.44', '6'):
        fail('bootstrap model does not require the filesystem-bound glibc release')
    if bootstrap.FOUNDATION_STAGE != 'seed-assisted-foundation-root-qualified':
        fail('bootstrap model misstates the current foundation stage')
    if bootstrap.FOUNDATION_MEMBERS != ('filesystem', 'glibc', 'libgcc'):
        fail('bootstrap model foundation membership differs from @foundation authority')
    if bootstrap.EXPECTED_ARTIFACTS != (
            'filesystem', 'glibc', 'glibc-bootstrap', 'libgcc',
            'linux-api-headers'):
        fail('bootstrap model retains a duplicate/probe construction closure')
    if bootstrap.SEED_RETIREMENT_QUALIFIED:
        fail('bootstrap model claims seed retirement before the hostile gate exists')
    for required_runtime in (
            'artifacts', 'target-locks', 'application-journals',
            'application-checkpoints', 'lifecycle-sessions'):
        if required_runtime not in bootstrap.RUNTIME_DIRS:
            fail(f'mixed run runtime omits required private hierarchy: {required_runtime}')
    seed = bootstrap.load_seed_descriptor(root, None)
    if seed.architecture != 'x86_64' or len(seed.sha256) != 64:
        fail('default seed descriptor does not load')

    marker = {
        'seed': {'sha256': seed.sha256},
        'foundation': {
            'revision': foundation.revision,
            'target_root': '/tmp/bootstrap-workspace/main/foundation-root',
        },
        'qualification': {'sha256': '1' * 64},
        'operation_policy_profile': bootstrap.FOUNDATION_OPERATION_PROFILE,
        'build_policy': {
            'parallelism': 7,
            'source_date_epoch': 0,
            'file_creation_mask': '0022',
            'output_layout': 'package-root',
        },
    }
    main_nonce = bootstrap.nonce_for('foundation-root', marker)
    marker['build_policy']['parallelism'] = 11
    if bootstrap.nonce_for('foundation-root', marker) == main_nonce:
        fail('build policy does not contribute to bootstrap request identity')
    marker['build_policy']['parallelism'] = 7
    main_nonce = bootstrap.nonce_for('foundation-root', marker)
    main_identity = bootstrap.identity_for('managed-target', marker)
    qualification_identity = bootstrap.identity_for('qualification-managed-target', marker)
    admitted_profile = bootstrap.FOUNDATION_OPERATION_PROFILE
    try:
        bootstrap.FOUNDATION_OPERATION_PROFILE = 'strict-exclusive'
        marker['operation_policy_profile'] = bootstrap.FOUNDATION_OPERATION_PROFILE
        if bootstrap.nonce_for('foundation-root', marker) == main_nonce:
            fail('operation-policy profile does not contribute to bootstrap request identity')
        if bootstrap.identity_for('managed-target', marker) == main_identity:
            fail('operation-policy profile does not contribute to managed target identity')
        if bootstrap.identity_for('qualification-managed-target', marker) != qualification_identity:
            fail('foundation operation-policy profile contaminates qualification target identity')
    finally:
        bootstrap.FOUNDATION_OPERATION_PROFILE = admitted_profile
        marker['operation_policy_profile'] = admitted_profile
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
        git=Path('/usr/bin/git'), readelf=Path('/usr/bin/readelf'),
        controller_source_lock=bootstrap.controller_source_lock_digest(root))
    original_run_command = bootstrap.run_command
    try:
        bootstrap.run_command = lambda *args, **kwargs: bootstrap.CommandResult(
            0, f'pkgctl {bootstrap.EXPECTED_PKGCTL_VERSION}\n', '')
        bootstrap._validate_controller_release(context)
        bootstrap.run_command = lambda *args, **kwargs: bootstrap.CommandResult(
            0, 'pkgctl 0.40.1\n', '')
        try:
            bootstrap._validate_controller_release(context)
        except bootstrap.BootstrapError:
            pass
        else:
            fail('stale configured pkgctl release was accepted as product authority')
    finally:
        bootstrap.run_command = original_run_command
    stale_context = BuildContext(
        source_root=root, build_root=Path('/tmp/build'),
        pkgctl=Path('/controller/pkgctl'), pkgstate_init=Path('/controller/pkgstate-init'),
        git=Path('/usr/bin/git'), readelf=Path('/usr/bin/readelf'),
        controller_source_lock='v1:sha256:' + '0' * 64)
    try:
        bootstrap._validate_controller_release(stale_context)
    except bootstrap.BootstrapError as error:
        if 'configured controller source lock differs' not in str(error):
            fail(f'stale configured source-lock refusal is opaque: {error}')
    else:
        fail('stale configured source lock was accepted as controller authority')

    marker['controller'] = {
        'source_lock': context.controller_source_lock,
        'pkgctl': {'path': str(context.pkgctl.resolve()), 'sha256': 'a' * 64},
        'pkgstate_init': {
            'path': str(context.pkgstate_init.resolve()), 'sha256': 'b' * 64},
    }
    original_validate_controller_release = bootstrap._validate_controller_release
    original_controller_digest = bootstrap.controller_digest
    try:
        bootstrap._validate_controller_release = lambda value: None
        bootstrap.controller_digest = lambda path: (
            'a' * 64 if Path(path) == context.pkgctl else 'b' * 64)
        bootstrap._validate_controller(context, marker)

        admitted_source_lock = marker['controller']['source_lock']
        marker['controller']['source_lock'] = 'v1:sha256:' + '0' * 64
        try:
            bootstrap._validate_controller(context, marker)
        except bootstrap.BootstrapError as error:
            if 'controller source lock differs from admitted bootstrap authority' not in str(error):
                fail(f'workspace controller source-lock drift refusal is opaque: {error}')
        else:
            fail('workspace accepted a controller closure different from admission')

        del marker['controller']['source_lock']
        try:
            bootstrap._validate_controller(context, marker)
        except bootstrap.BootstrapError as error:
            if 'controller source lock differs from admitted bootstrap authority' not in str(error):
                fail(f'pre-source-lock workspace refusal is opaque: {error}')
        else:
            fail('pre-source-lock workspace remained resumable after closure admission')
        marker['controller']['source_lock'] = admitted_source_lock
    finally:
        bootstrap._validate_controller_release = original_validate_controller_release
        bootstrap.controller_digest = original_controller_digest

    start_args = bootstrap._start_pkgctl_args(
        context, marker, qualification=False, maximum_steps=8)
    resume_args = bootstrap._resume_pkgctl_args(
        context, marker, qualification=False, maximum_steps=8)
    qualification_args = bootstrap._start_pkgctl_args(
        context, marker, qualification=True, maximum_steps=8)
    if start_args[1] != 'run':
        fail('main bootstrap stage is not one mixed native run transaction')
    if qualification_args[1] != 'build':
        fail('seed qualification lost the restricted build frontend')
    expected_goals = {
        'run=@foundation', 'check=libgcc',
    }
    observed_goals = {
        start_args[index + 1]
        for index, token in enumerate(start_args[:-1]) if token == '--goal'
    }
    if observed_goals != expected_goals:
        fail(f'mixed run goals differ: {sorted(observed_goals)}')
    if any(goal.startswith('build=') for goal in observed_goals):
        fail('mixed run reintroduced a parallel explicit construction root')
    for token in ('--prefer-catalog', '--converge-exact', '--operation-policy',
                  '--lifecycle-root', '--target-root'):
        if token not in start_args:
            fail(f'mixed run omits required composition authority: {token}')
    if '--artifact-root' in start_args:
        fail('mixed run exposes construction artifacts as build-frontend authority')
    if '--artifact-root' not in qualification_args:
        fail('seed qualification lost its explicit public artifact root')
    policy_index = start_args.index('--operation-policy')
    if start_args[policy_index + 1] != bootstrap.FOUNDATION_OPERATION_PROFILE:
        fail('mixed run does not select the admitted complete operation-policy profile')
    if '--operation-policy' in qualification_args:
        fail('build-only seed qualification was contaminated by target operation-policy profile')
    parallelism_index = start_args.index('--build-parallelism')
    if start_args[parallelism_index + 1] != '7':
        fail('mixed run did not preserve non-default admitted build parallelism')
    target_index = start_args.index('--target-root')
    if start_args[target_index + 1] != '/tmp/bootstrap-workspace/main/foundation-root':
        fail('mixed run target is not the private foundation managed root')
    lifecycle_index = start_args.index('--lifecycle-root')
    if start_args[lifecycle_index + 1] != '/tmp/bootstrap-workspace/seed-root':
        fail('seed-assisted lifecycle authority is not explicitly bounded to S0')
    for token in ('--collection', '--build-parallelism', '--build-source-date-epoch',
                  '--goal', '--prefer-catalog', '--converge-exact',
                  '--operation-policy', '--start'):
        if token not in start_args:
            fail(f'start command omits admitted semantic option: {token}')
        if token in resume_args:
            fail(f'resume command redeclares start-only semantic option: {token}')
    if resume_args[1] != 'run' or '--resume' not in resume_args:
        fail('main resume does not recover the retained mixed run request')
    for token in ('--lifecycle-root', '--target-root'):
        if token not in resume_args:
            fail(f'main resume omits live physical authority: {token}')
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

    marker['qualification']['sha256'] = '1' * 64
    marker['operation_policy_profile'] = 'strict-exclusive'
    try:
        bootstrap._foundation_operation_profile(marker)
    except bootstrap.BootstrapError:
        pass
    else:
        fail('unsupported retained foundation operation-policy profile was accepted')
    marker['operation_policy_profile'] = bootstrap.FOUNDATION_OPERATION_PROFILE

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

        git = shutil.which('git')
        if git is None:
            fail('git is unavailable for foundation source model test')
        origin = temp / 'foundation-origin'
        subprocess.run([git, 'init', '-q', origin], check=True)
        subprocess.run(
            [git, '-C', origin, 'config', 'user.email', 'bootstrap-model@example.invalid'],
            check=True)
        subprocess.run(
            [git, '-C', origin, 'config', 'user.name', 'bootstrap-model'], check=True)
        (origin / 'recipe.yml').write_text('name: model\n', encoding='utf-8')
        subprocess.run([git, '-C', origin, 'add', 'recipe.yml'], check=True)
        subprocess.run([git, '-C', origin, 'commit', '-q', '-m', 'model'], check=True)
        revision = subprocess.run(
            [git, '-C', origin, 'rev-parse', 'HEAD'], check=True,
            text=True, stdout=subprocess.PIPE).stdout.strip()
        descriptor = bootstrap.CollectionDescriptor(
            name='foundation', url=str(origin), revision=revision)
        cached = bootstrap.canonical_git_source(
            descriptor, git=Path(git), cache_root=temp / 'collection-cache', override=None)
        if (cached / 'recipe.yml').read_text(encoding='utf-8') != 'name: model\n':
            fail('fresh exact-HEAD foundation clone was not materialized')
        cached_status = subprocess.run(
            [git, '-C', cached, 'status', '--porcelain', '--untracked-files=all'],
            check=True, text=True, stdout=subprocess.PIPE).stdout
        if cached_status.strip():
            fail('fresh exact-HEAD foundation clone is dirty after materialization')
        (cached / 'recipe.yml').write_text('name: mutated\n', encoding='utf-8')
        try:
            bootstrap.canonical_git_source(
                descriptor, git=Path(git), cache_root=temp / 'collection-cache', override=None)
        except bootstrap.BootstrapError:
            pass
        else:
            fail('dirty cached foundation source was silently repaired')

        failed_workspace = temp / 'failed-bootstrap'
        original_run_command = bootstrap.run_command
        bootstrap.run_command = lambda *args, **kwargs: bootstrap.CommandResult(
            0, f'pkgctl {bootstrap.EXPECTED_PKGCTL_VERSION}\n', '')
        try:
            try:
                bootstrap.initialize(
                    context,
                    bootstrap.BootstrapOptions(
                        workspace=failed_workspace, seed_name='missing-bootstrap-model-seed'))
            except bootstrap.BootstrapError:
                pass
            else:
                fail('invalid seed unexpectedly initialized a bootstrap workspace')
        finally:
            bootstrap.run_command = original_run_command
        if failed_workspace.exists():
            fail('failed new bootstrap initialization retained an unmarked workspace')

        foundation_root = temp / 'foundation-root'
        (foundation_root / 'usr/lib').mkdir(parents=True)
        (foundation_root / 'usr/bin').mkdir(parents=True)
        (foundation_root / 'lib64').symlink_to('usr/lib64')
        (foundation_root / 'usr/lib64').symlink_to('lib')
        bootstrap._validate_foundation_root_scope(foundation_root)

        loader = foundation_root / 'usr/lib/ld-linux-x86-64.so.2'
        localedef = foundation_root / 'usr/bin/localedef'
        libgcc = foundation_root / 'usr/lib/libgcc_s.so.1'
        libc = foundation_root / 'usr/lib/libc.so.6'
        for path in (loader, localedef, libgcc, libc):
            path.write_bytes(b'model\n')

        commands: list[list[str]] = []
        original_run_command = bootstrap.run_command

        def managed_runtime_command(args, **kwargs):
            command = [str(value) for value in args]
            commands.append(command)
            if '--list-archive' in command:
                return bootstrap.CommandResult(0, 'C.utf8\n', '')
            if '--list' in command:
                return bootstrap.CommandResult(
                    0,
                    f'libc.so.6 => {libc} (0x1)\n{loader} (0x2)\n',
                    '')
            if '--dyn-syms' in command:
                return bootstrap.CommandResult(0, '_Unwind_Backtrace\n', '')
            fail(f'unexpected managed-runtime command: {command}')

        bootstrap.run_command = managed_runtime_command
        try:
            bootstrap._validate_foundation_runtime(context, foundation_root)
        finally:
            bootstrap.run_command = original_run_command
        list_commands = [command for command in commands if '--list' in command]
        if len(list_commands) != 1:
            fail('managed runtime qualification did not issue exactly one loader list')
        if '--inhibit-cache' not in list_commands[0]:
            fail('managed runtime qualification permits host loader cache authority')
        library_index = list_commands[0].index('--library-path')
        if list_commands[0][library_index + 1] != str(foundation_root / 'usr/lib'):
            fail('managed runtime qualification uses non-foundation library search authority')

        def hostile_runtime_command(args, **kwargs):
            command = [str(value) for value in args]
            if '--list-archive' in command:
                return bootstrap.CommandResult(0, 'C.utf8\n', '')
            if '--list' in command:
                return bootstrap.CommandResult(
                    0,
                    f'libc.so.6 => /usr/lib/libc.so.6 (0x1)\n{loader} (0x2)\n',
                    '')
            if '--dyn-syms' in command:
                return bootstrap.CommandResult(0, '_Unwind_Backtrace\n', '')
            fail(f'unexpected hostile managed-runtime command: {command}')

        bootstrap.run_command = hostile_runtime_command
        try:
            try:
                bootstrap._validate_foundation_runtime(context, foundation_root)
            except bootstrap.BootstrapError:
                pass
            else:
                fail('managed runtime qualification admitted host libc resolution')
        finally:
            bootstrap.run_command = original_run_command

        (foundation_root / 'usr/bin/gcc').write_text('poison\n', encoding='utf-8')
        try:
            bootstrap._validate_foundation_root_scope(foundation_root)
        except bootstrap.BootstrapError:
            pass
        else:
            fail('foundation managed root admitted seed/toolchain residue')

        unmarked_workspace = temp / 'unmarked-bootstrap'
        unmarked_workspace.mkdir()
        (unmarked_workspace / 'foreign').write_text('keep\n', encoding='utf-8')
        try:
            bootstrap.clean(
                context, bootstrap.BootstrapOptions(workspace=unmarked_workspace))
        except bootstrap.BootstrapError:
            pass
        else:
            fail('bootstrap clean removed an unmarked workspace')
        if not (unmarked_workspace / 'foreign').is_file():
            fail('bootstrap clean mutated an unmarked workspace')

        stale_workspace = temp / 'stale-bootstrap'
        stale_workspace.mkdir()
        (stale_workspace / 'obsolete').write_text('remove\n', encoding='utf-8')
        bootstrap.atomic_json(bootstrap.marker_path(stale_workspace), {
            'format': bootstrap.WORKSPACE_FORMAT,
            'workspace': str(stale_workspace),
        })
        bootstrap.clean(
            context, bootstrap.BootstrapOptions(workspace=stale_workspace))
        if stale_workspace.exists():
            fail('bootstrap clean retained a marker-bound pre-policy workspace')

        misbound_workspace = temp / 'misbound-bootstrap'
        misbound_workspace.mkdir()
        (misbound_workspace / 'foreign').write_text('keep\n', encoding='utf-8')
        bootstrap.atomic_json(bootstrap.marker_path(misbound_workspace), {
            'format': bootstrap.WORKSPACE_FORMAT,
            'workspace': str(temp / 'different-bootstrap'),
        })
        try:
            bootstrap.clean(
                context, bootstrap.BootstrapOptions(workspace=misbound_workspace))
        except bootstrap.BootstrapError:
            pass
        else:
            fail('bootstrap clean removed a workspace with a copied/misbound marker')
        if not (misbound_workspace / 'foreign').is_file():
            fail('bootstrap clean mutated a workspace with a misbound marker')


if __name__ == '__main__':
    main()
