# SPDX-FileCopyrightText: 2026 Alexandr Savca
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

import configparser
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

from .model import BuildContext
from .source_lock import controller_source_lock_digest

WORKSPACE_FORMAT = 'zeppe-lin.system.bootstrap-workspace/1'
MANIFEST_FORMAT = 'zeppe-lin.system.bootstrap-manifest/1'
SEED_PROTOCOL = 'zeppe-lin.system.seed/1'
COLLECTION_PROTOCOL = 'zeppe-lin.system.collection-source/1'
DOMAIN = 'zeppe-lin/system/bootstrap/1'
HOUSE_UMASK = '0022'
OUTPUT_LAYOUT = 'package-root'
FOUNDATION_OPERATION_PROFILE = 'exact-compatible-sharing'
EXPECTED_PKGCTL_VERSION = '0.42.0'
HEX40 = re.compile(r'^[0-9a-f]{40}$')
HEX64 = re.compile(r'^[0-9a-f]{64}$')
RUNTIME_DIRS = (
    'command-evidence', 'run', 'evidence', 'effects',
    'target-locks', 'application-journals',
    'payload', 'capture', 'rejected', 'completed', 'effect-bodies',
    'content', 'construction-sessions', 'package-outputs', 'artifacts',
    'check-resources', 'check-temporary', 'lifecycle-sessions',
)
SEED_ROOT_DIRS = (
    ('dev', 0o755),
    ('build/source', 0o755),
    ('build/work', 0o755),
    ('build/package', 0o755),
    ('build/inputs', 0o755),
    ('check/source', 0o755),
    ('check/package', 0o755),
    ('check/inputs', 0o755),
    ('target', 0o755),
    ('tmp', 0o1777),
)
EXPECTED_ARTIFACTS = (
    'filesystem', 'glibc', 'glibc-bootstrap', 'libgcc',
    'linux-api-headers',
)
FOUNDATION_MEMBERS = ('filesystem', 'glibc', 'libgcc')
FOUNDATION_STAGE = 'seed-assisted-foundation-root-qualified'
SEED_RETIREMENT_QUALIFIED = False
EXPECTED_PACKAGE_COORDINATES = {
    'filesystem': ('1.0.0', '1'),
    'glibc': ('2.44', '6'),
    'glibc-bootstrap': ('2.44', '1'),
    'libgcc': ('16.1.0', '1'),
    'linux-api-headers': ('7.1.8', '1'),
}


class BootstrapError(RuntimeError):
    pass


@dataclass(frozen=True)
class SeedDescriptor:
    file_name: str
    name: str
    architecture: str
    release: str
    url: str
    sha256: str
    signature_url: str
    signature_sha256: str


@dataclass(frozen=True)
class CollectionDescriptor:
    name: str
    url: str
    revision: str


@dataclass(frozen=True)
class CommandResult:
    status: int
    stdout: str
    stderr: str


@dataclass
class BootstrapOptions:
    workspace: Path
    seed_name: str | None = None
    seed_file: Path | None = None
    seed_signature_file: Path | None = None
    foundation_source: Path | None = None
    jobs: int | None = None
    source_date_epoch: int | None = None
    maximum_steps: int = 8
    privilege: str | None = None



def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(root: Path) -> str:
    digest = hashlib.sha256()
    files = sorted(path for path in root.rglob('*') if path.is_file() and not path.is_symlink())
    symlinks = sorted(path for path in root.rglob('*') if path.is_symlink())
    for path in files:
        relative = path.relative_to(root).as_posix().encode()
        digest.update(b'F\0' + relative + b'\0')
        digest.update(path.read_bytes())
        digest.update(b'\0')
    for path in symlinks:
        relative = path.relative_to(root).as_posix().encode()
        digest.update(b'L\0' + relative + b'\0')
        digest.update(os.readlink(path).encode())
        digest.update(b'\0')
    return digest.hexdigest()


def material_digest(*fields: object) -> str:
    text = ':'.join(str(field) for field in fields)
    return hashlib.sha256(text.encode()).hexdigest()


def _foundation_operation_profile(marker: Mapping[str, object]) -> str:
    profile = marker.get('operation_policy_profile')
    if profile != FOUNDATION_OPERATION_PROFILE:
        raise BootstrapError(
            'bootstrap workspace operation-policy profile differs from product authority')
    return profile


def _operation_policy_binding(domain: str, marker: Mapping[str, object]) -> str:
    if domain == 'seed-probe' or domain.startswith('qualification-'):
        return ''
    return _foundation_operation_profile(marker)


def identity_for(domain: str, marker: Mapping[str, object]) -> str:
    digest = material_digest(
        DOMAIN,
        domain,
        marker['seed']['sha256'],
        marker['foundation']['revision'],
        marker['qualification']['sha256'],
        _operation_policy_binding(domain, marker),
    )
    return f'v1:sha256:{digest}'


def seed_execution_root_view_digest(marker: Mapping[str, object]) -> str:
    layout = tuple(f'{relative}:{mode:o}' for relative, mode in SEED_ROOT_DIRS)
    return material_digest(
        DOMAIN,
        'seed-execution-root-view',
        SEED_PROTOCOL,
        marker['seed']['sha256'],
        *layout,
    )


def seed_execution_root_view_identity(marker: Mapping[str, object]) -> str:
    return f'v1:sha256:{seed_execution_root_view_digest(marker)}'


def nonce_for(domain: str, marker: Mapping[str, object]) -> str:
    policy = marker['build_policy']
    return material_digest(
        DOMAIN,
        domain,
        marker['seed']['sha256'],
        marker['foundation']['revision'],
        marker['qualification']['sha256'],
        policy['parallelism'],
        policy['source_date_epoch'],
        policy['file_creation_mask'],
        policy['output_layout'],
        _operation_policy_binding(domain, marker),
    )


def _read_exact_ini(path: Path, section_name: str, expected: set[str]) -> Mapping[str, str]:
    parser = configparser.ConfigParser(interpolation=None)
    try:
        with path.open(encoding='utf-8') as stream:
            parser.read_file(stream)
    except (OSError, configparser.Error) as error:
        raise BootstrapError(f'cannot read descriptor {path}: {error}') from error
    if parser.sections() != [section_name]:
        raise BootstrapError(f'{path}: expected exactly one [{section_name}] section')
    section = parser[section_name]
    if set(section) != expected:
        raise BootstrapError(f'{path}: descriptor vocabulary differs from protocol')
    return section


def load_seed_descriptor(source_root: Path, requested: str | None) -> SeedDescriptor:
    seed_dir = source_root / 'seeds'
    if requested is None:
        requested = (seed_dir / 'default').read_text(encoding='utf-8').strip()
    candidate = Path(requested).name
    if not candidate.endswith('.ini'):
        candidate += '.ini'
    path = seed_dir / candidate
    expected = {
        'protocol', 'name', 'architecture', 'release', 'url', 'sha256',
        'signature_url', 'signature_sha256',
    }
    section = _read_exact_ini(path, 'seed', expected)
    if section['protocol'] != SEED_PROTOCOL:
        raise BootstrapError(f'{path}: unsupported seed protocol')
    if section['architecture'] != 'x86_64':
        raise BootstrapError(f'{path}: bootstrap currently supports x86_64 only')
    for key in ('sha256', 'signature_sha256'):
        if not HEX64.fullmatch(section[key]):
            raise BootstrapError(f'{path}: {key} is not a SHA-256 digest')
    return SeedDescriptor(
        file_name=path.name,
        name=section['name'],
        architecture=section['architecture'],
        release=section['release'],
        url=section['url'],
        sha256=section['sha256'],
        signature_url=section['signature_url'],
        signature_sha256=section['signature_sha256'],
    )


def load_foundation_descriptor(source_root: Path) -> CollectionDescriptor:
    path = source_root / 'collections' / 'foundation.ini'
    section = _read_exact_ini(
        path, 'collection', {'protocol', 'name', 'url', 'revision'})
    if section['protocol'] != COLLECTION_PROTOCOL:
        raise BootstrapError(f'{path}: unsupported collection source protocol')
    if section['name'] != 'foundation':
        raise BootstrapError(f'{path}: foundation descriptor names another collection')
    if not HEX40.fullmatch(section['revision']):
        raise BootstrapError(f'{path}: collection revision is not an exact Git commit')
    return CollectionDescriptor(
        name=section['name'], url=section['url'], revision=section['revision'])


def resolve_program(requested: str) -> Path:
    if '/' in requested:
        path = Path(requested).expanduser().resolve()
        if not path.is_file() or not os.access(path, os.X_OK):
            raise BootstrapError(f'executable is unavailable: {requested}')
        return path
    resolved = shutil.which(requested)
    if resolved is None:
        raise BootstrapError(f'executable is unavailable: {requested}')
    return Path(resolved).resolve()


def run_command(
    args: Sequence[str | os.PathLike[str]],
    *,
    privilege: Path | None = None,
    cwd: Path | None = None,
    check: bool = False,
) -> CommandResult:
    command = [str(arg) for arg in args]
    if privilege is not None:
        command.insert(0, str(privilege))
    process = subprocess.run(
        command,
        cwd=None if cwd is None else str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    result = CommandResult(process.returncode, process.stdout, process.stderr)
    if check and result.status != 0:
        detail = result.stderr.strip() or result.stdout.strip() or f'exit status {result.status}'
        raise BootstrapError(f'command failed: {" ".join(command)}: {detail}')
    return result


def print_result(result: CommandResult) -> None:
    if result.stdout:
        print(result.stdout, end='')
    if result.stderr:
        print(result.stderr, end='', file=sys.stderr)


def acquire_url(url: str, expected_sha256: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        observed = sha256_file(destination)
        if observed == expected_sha256:
            return destination
        raise BootstrapError(
            f'cached input differs from admitted SHA-256: {destination}; '
            f'expected {expected_sha256}, observed {observed}')
    temporary = destination.with_name(destination.name + '.partial')
    temporary.unlink(missing_ok=True)
    request = urllib.request.Request(url, headers={'User-Agent': 'zeppe-lin-system/0.1'})
    try:
        with urllib.request.urlopen(request) as response, temporary.open('wb') as output:
            shutil.copyfileobj(response, output)
    except Exception as error:
        temporary.unlink(missing_ok=True)
        raise BootstrapError(f'cannot acquire {url}: {error}') from error
    observed = sha256_file(temporary)
    if observed != expected_sha256:
        temporary.unlink(missing_ok=True)
        raise BootstrapError(
            f'acquired input differs from admitted SHA-256; '
            f'expected {expected_sha256}, observed {observed}')
    temporary.replace(destination)
    return destination


def _safe_member_name(member: tarfile.TarInfo) -> PurePosixPath:
    name = PurePosixPath(member.name)
    if name.is_absolute() or '..' in name.parts or not name.parts:
        raise BootstrapError(f'seed archive contains escaping path: {member.name}')
    return name


def _archive_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members: list[tarfile.TarInfo] = []
    root_seen = False
    for member in archive.getmembers():
        if member.name.rstrip('/') == '.':
            if root_seen:
                raise BootstrapError('seed archive contains duplicate root entry')
            if not member.isdir():
                raise BootstrapError('seed archive root entry is not a directory')
            root_seen = True
            continue
        members.append(member)
    return members


def _extract_admitted_member(
    archive: tarfile.TarFile,
    member: tarfile.TarInfo,
    destination: Path,
) -> None:
    if hasattr(tarfile, 'fully_trusted_filter'):
        # Archive admission is owned by _extract_archive_bytes(). The tarfile
        # filter is disabled here so a host Python release cannot reinterpret
        # already-admitted rootfs link topology as extraction policy.
        archive.extract(
            member,
            path=destination,
            set_attrs=True,
            numeric_owner=False,
            filter=tarfile.fully_trusted_filter,
        )
    else:
        # Extraction filters were added in Python 3.12. Older interpreters
        # already provide the unrestricted extraction mechanism required here.
        archive.extract(member, path=destination, set_attrs=True, numeric_owner=False)


def _extract_archive_bytes(data: bytes, destination: Path) -> None:
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:*') as archive:
        members = _archive_members(archive)
        declared_links: set[PurePosixPath] = set()
        names: set[PurePosixPath] = set()
        for member in members:
            name = _safe_member_name(member)
            if name in names:
                raise BootstrapError(f'archive contains duplicate member: {member.name}')
            names.add(name)
            if member.issym():
                declared_links.add(name)
            if member.islnk():
                target = PurePosixPath(member.linkname)
                if target.is_absolute() or '..' in target.parts:
                    raise BootstrapError(
                        f'archive hard link escapes extraction root: {member.name}')
        for name in names:
            parents = list(name.parents)[:-1]
            if any(parent in declared_links for parent in parents):
                raise BootstrapError(
                    f'archive member descends through a declared symlink: {name.as_posix()}')

        # Extract material paths before symlinks. This prevents a symlink entry
        # from becoming pathname authority for a later regular member.
        ordinary = [m for m in members if not m.issym() and not m.islnk()]
        hardlinks = [m for m in members if m.islnk()]
        symlinks = [m for m in members if m.issym()]
        for member in ordinary + hardlinks + symlinks:
            if member.ischr() or member.isblk() or member.isfifo():
                # Device semantics are supplied privately by execution. They are
                # not needed from the historical construction seed.
                continue
            _extract_admitted_member(archive, member, destination)


def extract_seed_archive(archive_path: Path, destination: Path) -> None:
    if destination.exists():
        if any(destination.iterdir()):
            raise BootstrapError(f'seed root is not empty: {destination}')
    else:
        destination.mkdir(parents=True)
    with archive_path.open('rb') as stream:
        data = stream.read()
    try:
        _extract_archive_bytes(data, destination)
    except Exception as error:
        try:
            shutil.rmtree(destination)
        except OSError as cleanup_error:
            raise BootstrapError(
                f'seed extraction failed and partial root cannot be removed: '
                f'{destination}: {cleanup_error}') from error
        raise


def canonical_git_source(
    descriptor: CollectionDescriptor,
    *,
    git: Path,
    cache_root: Path,
    override: Path | None,
) -> Path:
    local_override = override is not None
    cloned = False
    if local_override:
        repository = override.expanduser().resolve()
        if not repository.is_dir():
            raise BootstrapError(f'foundation source is not a directory: {repository}')
    else:
        repository = cache_root / f'{descriptor.name}-{descriptor.revision}'
        if not repository.exists():
            repository.parent.mkdir(parents=True, exist_ok=True)
            result = run_command([git, 'clone', '--no-checkout', descriptor.url, repository])
            print_result(result)
            if result.status != 0:
                shutil.rmtree(repository, ignore_errors=True)
                raise BootstrapError('cannot clone admitted foundation source')
            cloned = True
        if not (repository / '.git').exists():
            raise BootstrapError(f'cached foundation source is not a Git repository: {repository}')

    head = run_command([git, '-C', repository, 'rev-parse', 'HEAD'])
    if head.status != 0 or head.stdout.strip() != descriptor.revision or cloned:
        if local_override:
            raise BootstrapError(
                f'local foundation source HEAD differs from admitted revision {descriptor.revision}')
        checkout = run_command(
            [git, '-C', repository, 'checkout', '--detach', descriptor.revision])
        print_result(checkout)
        if checkout.status != 0:
            raise BootstrapError(
                f'foundation source cannot select admitted revision {descriptor.revision}')
    status = run_command(
        [git, '-C', repository, 'status', '--porcelain', '--untracked-files=all'],
        check=True,
    )
    if status.stdout.strip():
        raise BootstrapError('foundation source worktree is not clean')
    head = run_command([git, '-C', repository, 'rev-parse', 'HEAD'], check=True)
    if head.stdout.strip() != descriptor.revision:
        raise BootstrapError('foundation source HEAD differs from admitted revision')
    return repository


def snapshot_git_tree(repository: Path, revision: str, destination: Path, git: Path) -> None:
    archive = subprocess.run(
        [str(git), '-C', str(repository), 'archive', '--format=tar', revision],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if archive.returncode != 0:
        raise BootstrapError(
            'cannot snapshot admitted foundation revision: ' +
            archive.stderr.decode(errors='replace').strip())
    destination.mkdir(parents=True, exist_ok=True)
    _extract_archive_bytes(archive.stdout, destination)


def snapshot_qualification(source_root: Path, destination: Path) -> str:
    source = source_root / 'products' / 'bootstrap' / 'qualification' / 'collection'
    if destination.exists():
        raise BootstrapError(f'qualification snapshot already exists: {destination}')
    shutil.copytree(source, destination, symlinks=True)
    return sha256_tree(destination)


def ensure_seed_root_layout(root: Path) -> None:
    for relative, mode in SEED_ROOT_DIRS:
        path = root / relative
        if path.exists() and (path.is_symlink() or not path.is_dir()):
            raise BootstrapError(f'seed root path is not an exact directory: {path}')
        path.mkdir(parents=True, exist_ok=True)
        path.chmod(mode)
    for relative in ('build/inputs', 'check/inputs'):
        path = root / relative
        if any(path.iterdir()):
            raise BootstrapError(f'seed input namespace must be empty: {path}')


def resolve_seed_interpreter(root: Path) -> Path:
    for relative in ('usr/bin/bash', 'bin/bash', 'usr/bin/dash', 'bin/dash'):
        candidate = root / relative
        if candidate.is_file() and os.access(candidate, os.X_OK):
            resolved = candidate.resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError as error:
                raise BootstrapError(f'seed interpreter escapes root: {candidate}') from error
            return resolved
    raise BootstrapError('seed root has no executable bash/dash interpreter')


def controller_digest(path: Path) -> str:
    if not path.is_file() or not os.access(path, os.X_OK):
        raise BootstrapError(f'controller executable is unavailable: {path}')
    return sha256_file(path)


def supervisor_credentials(privilege: Path | None) -> tuple[int, int, list[int]]:
    uid_result = run_command(['id', '-u'], privilege=privilege, check=True)
    gid_result = run_command(['id', '-g'], privilege=privilege, check=True)
    groups_result = run_command(['id', '-G'], privilege=privilege, check=True)
    try:
        uid = int(uid_result.stdout.strip())
        gid = int(gid_result.stdout.strip())
        groups = [int(value) for value in groups_result.stdout.split()]
    except ValueError as error:
        raise BootstrapError('cannot parse native supervisor credentials') from error
    return uid, gid, groups


def marker_path(workspace: Path) -> Path:
    return workspace / 'bootstrap-workspace.json'


def atomic_json(path: Path, value: Mapping[str, object]) -> None:
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def _read_workspace_marker(workspace: Path) -> dict[str, object]:
    path = marker_path(workspace)
    if not path.is_file():
        raise BootstrapError(f'bootstrap workspace is not initialized: {workspace}')
    try:
        marker = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError) as error:
        raise BootstrapError(f'cannot read bootstrap workspace authority: {error}') from error
    if not isinstance(marker, dict):
        raise BootstrapError('bootstrap workspace authority is not an object')
    if marker.get('format') != WORKSPACE_FORMAT:
        raise BootstrapError('bootstrap workspace format is incompatible')
    return marker


def load_marker(workspace: Path) -> dict[str, object]:
    marker = _read_workspace_marker(workspace)
    _foundation_operation_profile(marker)
    return marker


def _validate_cleanup_marker(workspace: Path) -> None:
    marker = _read_workspace_marker(workspace)
    if marker.get('workspace') != str(workspace):
        raise BootstrapError('bootstrap workspace marker does not bind cleanup target')


def report_fields(text: str) -> dict[str, list[str]]:
    fields: dict[str, list[str]] = {}
    for line in text.splitlines():
        if not line.strip() or ' ' not in line:
            continue
        key, value = line.split(' ', 1)
        fields.setdefault(key, []).append(value)
    return fields


def report_terminal(text: str) -> tuple[bool, bool]:
    fields = report_fields(text)
    complete = fields.get('complete', ['no'])[-1] == 'yes'
    failed = fields.get('failed', ['no'])[-1] == 'yes'
    return complete, failed


def artifact_records(text: str) -> list[dict[str, str]]:
    records: dict[int, dict[str, str]] = {}
    for line in text.splitlines():
        match = re.match(r'^artifact\.(\d+)\.([^ ]+) (.*)$', line)
        if match is None:
            continue
        index = int(match.group(1))
        records.setdefault(index, {})[match.group(2)] = match.group(3)
    return [records[index] for index in sorted(records)]


def _binding_arguments(marker: Mapping[str, object], qualification: bool) -> list[str]:
    prefix = 'qualification-' if qualification else ''
    return [
        '--managed-target', identity_for(prefix + 'managed-target', marker),
        '--state-store', identity_for(prefix + 'state-store', marker),
        '--root-view', identity_for(prefix + 'root-view', marker),
        '--state-backend', identity_for(prefix + 'state-backend', marker),
        '--publication-domain', identity_for(prefix + 'publication-domain', marker),
    ]


def _controller_args(marker: Mapping[str, object], *, qualification: bool) -> tuple[Path, Path, Path]:
    workspace = Path(marker['workspace'])
    root = Path(marker['seed']['root'])
    if qualification:
        base = workspace / 'qualification'
    else:
        base = workspace / 'main'
    return base, root, Path(marker['seed']['interpreter'])


def _invoke_pkgstate_init(
    context: BuildContext,
    marker: Mapping[str, object],
    *,
    qualification: bool,
    privilege: Path | None,
) -> None:
    base, _, _ = _controller_args(marker, qualification=qualification)
    state = base / 'state'
    args = [context.pkgstate_init, '--canonical-store', state]
    args += _binding_arguments(marker, qualification)
    result = run_command(args, privilege=privilege)
    print_result(result)
    if result.status != 0:
        raise BootstrapError('pkgstate-init refused bootstrap state authority')


def _credential_arguments(
    marker: Mapping[str, object], *, lifecycle: bool = False,
) -> list[str]:
    supervisor = marker['supervisor']
    uid = int(supervisor['user_id'])
    gid = int(supervisor['group_id'])
    groups = [int(value) for value in supervisor['groups']]
    prefix = 'lifecycle' if lifecycle else 'build'
    args = [f'--{prefix}-user-id', str(uid), f'--{prefix}-group-id', str(gid)]
    for group in groups:
        if group != gid:
            args += [f'--{prefix}-supplementary-group', str(group)]
    return args


def _foundation_root(marker: Mapping[str, object]) -> Path:
    root = Path(marker['foundation']['target_root'])
    if not root.is_absolute() or root != Path(os.path.normpath(root)):
        raise BootstrapError('retained foundation root coordinate is not absolute/normalized')
    return root


def _validate_foundation_root_scope(root: Path) -> None:
    if not root.is_dir() or root.is_symlink():
        raise BootstrapError('foundation managed root is absent or not a directory')
    expected_links = {
        'lib64': 'usr/lib64',
        'usr/lib64': 'lib',
    }
    for relative, target in expected_links.items():
        path = root / relative
        if not path.is_symlink() or os.readlink(path) != target:
            raise BootstrapError(
                f'foundation managed root topology differs: {relative}')
    for relative in (
            'usr/bin/bash', 'usr/bin/gcc', 'usr/bin/make',
            'usr/include/linux/types.h', 'usr/libexec/runtime-cohort-probe',
            'runtime-cohort.ok'):
        if (root / relative).exists():
            raise BootstrapError(
                f'foundation managed root contains non-profile/seed residue: {relative}')


def _validate_foundation_runtime(context: BuildContext, root: Path) -> None:
    loader = root / 'usr/lib/ld-linux-x86-64.so.2'
    localedef = root / 'usr/bin/localedef'
    libgcc = root / 'usr/lib/libgcc_s.so.1'
    libc = root / 'usr/lib/libc.so.6'

    locale_listing = run_command([
        loader, '--inhibit-cache', '--library-path', root / 'usr/lib',
        localedef, f'--prefix={root}', '--list-archive',
    ], check=True).stdout.splitlines()
    if 'C.utf8' not in locale_listing:
        raise BootstrapError(
            'foundation managed root lacks usable C.UTF-8 locale authority')

    loaded = run_command([
        loader, '--inhibit-cache', '--library-path', root / 'usr/lib',
        '--list', libgcc,
    ], check=True).stdout
    if f'libc.so.6 => {libc}' not in loaded:
        raise BootstrapError(
            'foundation loader did not resolve libgcc against managed libc')
    if str(loader) not in loaded:
        raise BootstrapError(
            'foundation loader did not retain its managed interpreter path')

    symbols = run_command([
        context.readelf, '--dyn-syms', '--wide', libgcc,
    ], check=True).stdout
    if '_Unwind_Backtrace' not in symbols:
        raise BootstrapError(
            'foundation libgcc lacks the unwind entry point used by native consumers')


def _start_pkgctl_args(
    context: BuildContext,
    marker: Mapping[str, object],
    *,
    qualification: bool,
    maximum_steps: int,
) -> list[str]:
    workspace = Path(marker['workspace'])
    base, root, interpreter = _controller_args(marker, qualification=qualification)
    policy = marker['build_policy']
    if qualification:
        subject = 'seed-probe'
        collections = [
            '--collection', f'bootstrap-qualification={workspace / "qualification" / "collection"}',
        ]
        nonce = nonce_for('seed-probe', marker)
        args = [context.pkgctl, 'build', subject, '--check',
                '--canonical-store', base / 'state']
    else:
        collections = [
            '--collection', f'foundation={workspace / "collections" / "foundation"}',
            '--collection', f'bootstrap-qualification={workspace / "qualification" / "collection"}',
        ]
        nonce = nonce_for('foundation-root', marker)
        args = [
            context.pkgctl, 'run',
            '--canonical-store', base / 'state',
        ]
    args += collections
    args += [
        '--build-architecture', 'x86_64',
        '--target-architecture', 'x86_64',
    ]
    if not qualification:
        args += [
            '--goal', 'run=@foundation',
            '--goal', 'check=libgcc',
            '--prefer-catalog',
            '--converge-exact',
            '--operation-policy', _foundation_operation_profile(marker),
        ]
    args += [
        '--start', nonce,
        '--build-parallelism', str(policy['parallelism']),
        '--build-source-date-epoch', str(policy['source_date_epoch']),
        '--runtime-root', base / 'runtime',
        '--build-root-view', seed_execution_root_view_digest(marker),
        '--build-root', root,
    ]
    if qualification:
        args += ['--artifact-root', base / 'artifacts']
    else:
        args += [
            '--lifecycle-root-view', seed_execution_root_view_digest(marker),
            '--lifecycle-root', root,
            '--target-root', _foundation_root(marker),
        ]
    args += ['--interpreter', interpreter]
    args += _credential_arguments(marker)
    if not qualification:
        args += _credential_arguments(marker, lifecycle=True)
    args += ['--max-steps', str(maximum_steps)]
    args += _binding_arguments(marker, qualification)
    return [str(value) for value in args]


def _resume_pkgctl_args(
    context: BuildContext,
    marker: Mapping[str, object],
    *,
    qualification: bool,
    maximum_steps: int,
) -> list[str]:
    base, root, interpreter = _controller_args(marker, qualification=qualification)
    nonce = nonce_for('seed-probe' if qualification else 'foundation-root', marker)
    args = [
        context.pkgctl, 'build' if qualification else 'run',
        '--canonical-store', base / 'state',
        '--resume', nonce,
        '--runtime-root', base / 'runtime',
        '--build-root', root,
    ]
    if qualification:
        args += ['--artifact-root', base / 'artifacts']
    else:
        args += [
            '--lifecycle-root', root,
            '--target-root', _foundation_root(marker),
        ]
    args += ['--interpreter', interpreter]
    args += _credential_arguments(marker)
    if not qualification:
        args += _credential_arguments(marker, lifecycle=True)
    args += ['--max-steps', str(maximum_steps)]
    return [str(value) for value in args]


def _latest_report(base: Path) -> str | None:
    path = base / 'latest.out'
    if not path.is_file():
        return None
    return path.read_text(encoding='utf-8')


def _run_until_terminal(
    context: BuildContext,
    marker: Mapping[str, object],
    *,
    qualification: bool,
    maximum_steps: int,
    privilege: Path | None,
) -> str:
    workspace = Path(marker['workspace'])
    base = workspace / ('qualification' if qualification else 'main')
    report = _latest_report(base)
    started = report is not None
    for _ in range(1024):
        if report is not None:
            complete, failed = report_terminal(report)
            if complete:
                if failed:
                    raise BootstrapError('bootstrap transaction completed with failure')
                return report
            if failed:
                raise BootstrapError('bootstrap transaction reports failure')
        args = (_resume_pkgctl_args if started else _start_pkgctl_args)(
            context, marker, qualification=qualification, maximum_steps=maximum_steps)
        result = run_command(args, privilege=privilege)
        print_result(result)
        base.mkdir(parents=True, exist_ok=True)
        (base / 'latest.out').write_text(result.stdout, encoding='utf-8')
        (base / 'latest.err').write_text(result.stderr, encoding='utf-8')
        if result.status != 0:
            raise BootstrapError(
                ('seed qualification' if qualification else 'bootstrap construction') +
                f' failed with status {result.status}')
        report = result.stdout
        started = True
        complete, failed = report_terminal(report)
        if failed:
            raise BootstrapError('bootstrap transaction reports failure')
        if not complete:
            disposition = report_fields(report).get('disposition', ['unknown'])[-1]
            if disposition != 'step-limit-reached':
                raise BootstrapError(
                    f'bootstrap transaction stopped non-terminally: {disposition}')
    raise BootstrapError('bootstrap exceeded resume safety bound')


def _validate_controller_release(context: BuildContext) -> None:
    try:
        source_lock = controller_source_lock_digest(context.source_root)
    except (OSError, ValueError) as error:
        raise BootstrapError(f'cannot identify current controller source lock: {error}') from error
    if context.controller_source_lock != source_lock:
        raise BootstrapError(
            'configured controller source lock differs from current product authority; '
            'reconfigure and rebuild the controller')

    result = run_command([context.pkgctl, '--version'])
    expected = f'pkgctl {EXPECTED_PKGCTL_VERSION}\n'
    if result.status != 0 or result.stdout != expected or result.stderr:
        detail = result.stderr.strip() or result.stdout.strip() or f'exit status {result.status}'
        raise BootstrapError(
            'configured pkgctl realization differs from product release authority; '
            f'expected {expected.strip()!r}, observed {detail!r}')


def _validate_controller(context: BuildContext, marker: Mapping[str, object]) -> None:
    _validate_controller_release(context)
    controller = marker.get('controller')
    if not isinstance(controller, dict):
        raise BootstrapError('bootstrap workspace controller authority is incomplete')
    if controller.get('source_lock') != context.controller_source_lock:
        raise BootstrapError(
            'controller source lock differs from admitted bootstrap authority')

    pkgctl = controller.get('pkgctl')
    pkgstate_init = controller.get('pkgstate_init')
    if not isinstance(pkgctl, dict) or not isinstance(pkgstate_init, dict):
        raise BootstrapError('bootstrap workspace controller authority is incomplete')

    current_pkgctl = controller_digest(context.pkgctl)
    current_state = controller_digest(context.pkgstate_init)
    if str(context.pkgctl.resolve()) != pkgctl.get('path') or \
            current_pkgctl != pkgctl.get('sha256'):
        raise BootstrapError('pkgctl differs from admitted bootstrap controller authority')
    if str(context.pkgstate_init.resolve()) != pkgstate_init.get('path') or \
            current_state != pkgstate_init.get('sha256'):
        raise BootstrapError('pkgstate-init differs from admitted bootstrap controller authority')


def _validate_supervisor(marker: Mapping[str, object], privilege: Path | None) -> None:
    observed_uid, observed_gid, observed_groups = supervisor_credentials(privilege)
    recorded = marker['supervisor']
    if observed_uid != recorded['user_id'] or observed_gid != recorded['group_id'] or \
            observed_groups != recorded['groups']:
        raise BootstrapError('native supervisor credentials differ from admitted bootstrap authority')


def _requested_privilege(options: BootstrapOptions, marker: Mapping[str, object] | None) -> Path | None:
    requested = options.privilege
    if marker is None:
        return None if requested is None else resolve_program(requested)
    recorded = marker['privilege']
    if requested is None:
        return None if recorded is None else Path(recorded)
    resolved = resolve_program(requested)
    if recorded is None or str(resolved) != recorded:
        raise BootstrapError('privilege command differs from initialized workspace authority')
    return resolved


def _reject_start_redeclaration(options: BootstrapOptions) -> None:
    if options.seed_name is not None:
        raise BootstrapError('--seed is valid only when initializing a new workspace')
    if options.seed_file is not None:
        raise BootstrapError('--seed-file is valid only when initializing a new workspace')
    if options.seed_signature_file is not None:
        raise BootstrapError('--seed-signature-file is valid only when initializing a new workspace')
    if options.foundation_source is not None:
        raise BootstrapError('--foundation-source is valid only when initializing a new workspace')
    if options.jobs is not None:
        raise BootstrapError('--jobs is valid only when initializing a new workspace')
    if options.source_date_epoch is not None:
        raise BootstrapError('--source-date-epoch is valid only when initializing a new workspace')


def _initialize_attempt(context: BuildContext, options: BootstrapOptions) -> dict[str, object]:
    workspace = options.workspace.expanduser().resolve()
    _validate_controller_release(context)
    if marker_path(workspace).exists():
        marker = load_marker(workspace)
        _validate_controller(context, marker)
        _reject_start_redeclaration(options)
        return marker
    if workspace.exists() and any(workspace.iterdir()):
        raise BootstrapError(f'bootstrap workspace is nonempty and unmarked: {workspace}')
    workspace.mkdir(parents=True, exist_ok=True)

    if options.jobs is not None and options.jobs <= 0:
        raise BootstrapError('--jobs must be positive')
    if options.source_date_epoch is not None and options.source_date_epoch < 0:
        raise BootstrapError('--source-date-epoch must be non-negative')
    jobs = options.jobs if options.jobs is not None else 4
    epoch = options.source_date_epoch if options.source_date_epoch is not None else 0

    seed = load_seed_descriptor(context.source_root, options.seed_name)
    foundation = load_foundation_descriptor(context.source_root)
    cache_root = context.build_root / 'cache'
    seed_cache = cache_root / 'seeds'
    archive_name = Path(urllib.parse.urlparse(seed.url).path).name
    archive_cache = seed_cache / f'{seed.sha256}-{archive_name}'
    if options.seed_file is not None:
        supplied = options.seed_file.expanduser().resolve()
        if not supplied.is_file():
            raise BootstrapError(f'--seed-file is not a file: {supplied}')
        observed = sha256_file(supplied)
        if observed != seed.sha256:
            raise BootstrapError(
                f'--seed-file differs from descriptor SHA-256; expected {seed.sha256}, observed {observed}')
        archive_cache.parent.mkdir(parents=True, exist_ok=True)
        if not archive_cache.exists():
            try:
                os.link(supplied, archive_cache)
            except OSError:
                shutil.copyfile(supplied, archive_cache)
    else:
        acquire_url(seed.url, seed.sha256, archive_cache)
    signature_name = Path(urllib.parse.urlparse(seed.signature_url).path).name
    signature_cache = seed_cache / f'{seed.signature_sha256}-{signature_name}'
    if options.seed_signature_file is not None:
        supplied_signature = options.seed_signature_file.expanduser().resolve()
        if not supplied_signature.is_file():
            raise BootstrapError(f'--seed-signature-file is not a file: {supplied_signature}')
        observed_signature = sha256_file(supplied_signature)
        if observed_signature != seed.signature_sha256:
            raise BootstrapError(
                '--seed-signature-file differs from descriptor SHA-256; '
                f'expected {seed.signature_sha256}, observed {observed_signature}')
        signature_cache.parent.mkdir(parents=True, exist_ok=True)
        if not signature_cache.exists():
            try:
                os.link(supplied_signature, signature_cache)
            except OSError:
                shutil.copyfile(supplied_signature, signature_cache)
    elif options.seed_file is None:
        acquire_url(seed.signature_url, seed.signature_sha256, signature_cache)
    else:
        signature_cache = None

    seed_root = workspace / 'seed-root'
    extract_seed_archive(archive_cache, seed_root)
    ensure_seed_root_layout(seed_root)
    interpreter = resolve_seed_interpreter(seed_root)

    repository = canonical_git_source(
        foundation,
        git=context.git,
        cache_root=cache_root / 'collections',
        override=options.foundation_source,
    )
    foundation_snapshot = workspace / 'collections' / 'foundation'
    snapshot_git_tree(repository, foundation.revision, foundation_snapshot, context.git)

    qualification_snapshot = workspace / 'qualification' / 'collection'
    qualification_sha = snapshot_qualification(context.source_root, qualification_snapshot)

    privilege = _requested_privilege(options, None)
    uid, gid, groups = supervisor_credentials(privilege)
    marker: dict[str, object] = {
        'format': WORKSPACE_FORMAT,
        'workspace': str(workspace),
        'seed': {
            'descriptor': seed.file_name,
            'name': seed.name,
            'release': seed.release,
            'sha256': seed.sha256,
            'signature_sha256': seed.signature_sha256,
            'archive': str(archive_cache),
            'signature': None if signature_cache is None else str(signature_cache),
            'root': str(seed_root),
            'interpreter': str(interpreter),
        },
        'foundation': {
            'url': foundation.url,
            'revision': foundation.revision,
            'snapshot': str(foundation_snapshot),
            'target_root': str(workspace / 'main' / 'foundation-root'),
        },
        'qualification': {
            'sha256': qualification_sha,
            'snapshot': str(qualification_snapshot),
        },
        'controller': {
            'source_lock': context.controller_source_lock,
            'pkgctl': {
                'path': str(context.pkgctl.resolve()),
                'sha256': controller_digest(context.pkgctl),
            },
            'pkgstate_init': {
                'path': str(context.pkgstate_init.resolve()),
                'sha256': controller_digest(context.pkgstate_init),
            },
        },
        'supervisor': {
            'user_id': uid,
            'group_id': gid,
            'groups': groups,
        },
        'operation_policy_profile': FOUNDATION_OPERATION_PROFILE,
        'build_policy': {
            'parallelism': jobs,
            'source_date_epoch': epoch,
            'file_creation_mask': HOUSE_UMASK,
            'output_layout': OUTPUT_LAYOUT,
        },
        'privilege': None if privilege is None else str(privilege),
    }

    for name in ('qualification', 'main'):
        base = workspace / name
        (base / 'runtime').mkdir(parents=True, exist_ok=True)
        for directory in RUNTIME_DIRS:
            (base / 'runtime' / directory).mkdir(parents=True, exist_ok=True)
        if name == 'qualification':
            (base / 'artifacts').mkdir(parents=True, exist_ok=True)
        else:
            _foundation_root(marker).mkdir(parents=True, exist_ok=True)

    try:
        _invoke_pkgstate_init(context, marker, qualification=True, privilege=privilege)
        _invoke_pkgstate_init(context, marker, qualification=False, privilege=privilege)
    except Exception:
        try:
            shutil.rmtree(workspace)
        except OSError:
            if privilege is not None:
                run_command(['rm', '-rf', '--', workspace], privilege=privilege)
        raise
    atomic_json(marker_path(workspace), marker)

    print(f'bootstrap-workspace={workspace}')
    print(f'seed={seed.name}')
    print(f'seed-sha256={seed.sha256}')
    print(f'foundation-revision={foundation.revision}')
    print(f'qualification-sha256={qualification_sha}')
    print(f'build-policy-parallelism={jobs}')
    print(f'build-policy-source-date-epoch={epoch}')
    return marker


def initialize(context: BuildContext, options: BootstrapOptions) -> dict[str, object]:
    workspace = options.workspace.expanduser().resolve()
    created = not workspace.exists()
    try:
        return _initialize_attempt(context, options)
    except BaseException as error:
        if created and workspace.exists() and not marker_path(workspace).exists():
            privilege = None
            if options.privilege is not None:
                try:
                    privilege = resolve_program(options.privilege)
                except BootstrapError:
                    privilege = None
            try:
                shutil.rmtree(workspace)
            except OSError as cleanup_error:
                if privilege is None:
                    raise BootstrapError(
                        'bootstrap initialization failed and partial workspace cannot be removed: '
                        f'{workspace}: {cleanup_error}') from error
                result = run_command(['rm', '-rf', '--', workspace], privilege=privilege)
                if result.status != 0:
                    print_result(result)
                    raise BootstrapError(
                        'bootstrap initialization failed and privileged partial-workspace cleanup failed') \
                        from error
        raise


def _tar_has_member(path: Path, member: str) -> bool:
    with tarfile.open(path, mode='r:*') as archive:
        names = {PurePosixPath(item.name).as_posix().rstrip('/') for item in archive.getmembers()}
    return member.rstrip('/') in names


def _artifact_map(report: str) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for artifact in artifact_records(report):
        package = artifact.get('package')
        if package is None:
            continue
        if package in result:
            raise BootstrapError(f'retained report names artifact twice: {package}')
        result[package] = artifact
    return result


def check(context: BuildContext, options: BootstrapOptions) -> Path:
    marker = load_marker(options.workspace.expanduser().resolve())
    _validate_controller(context, marker)
    _reject_start_redeclaration(options)
    _requested_privilege(options, marker)

    workspace = Path(marker['workspace'])
    qualification_report = _latest_report(workspace / 'qualification')
    main_report = _latest_report(workspace / 'main')
    if qualification_report is None or main_report is None:
        raise BootstrapError('bootstrap workspace lacks retained transaction reports')
    q_complete, q_failed = report_terminal(qualification_report)
    complete, failed = report_terminal(main_report)
    if not q_complete or q_failed:
        raise BootstrapError('seed qualification is not successfully terminal')
    if not complete or failed:
        raise BootstrapError('bootstrap construction is not successfully terminal')

    qualification_artifacts = _artifact_map(qualification_report)
    if set(qualification_artifacts) != {'seed-probe'}:
        raise BootstrapError('seed qualification artifact set differs')
    seed_artifact = qualification_artifacts['seed-probe']
    if seed_artifact.get('version') != '1.0' or seed_artifact.get('release') != '1':
        raise BootstrapError('seed qualification package coordinate differs')
    if 'path' not in seed_artifact or 'sha256' not in seed_artifact:
        raise BootstrapError('seed qualification artifact report is incomplete')
    seed_artifact_path = Path(seed_artifact['path']).resolve()
    qualification_artifact_root = (workspace / 'qualification' / 'artifacts').resolve()
    try:
        seed_artifact_path.relative_to(qualification_artifact_root)
    except ValueError as error:
        raise BootstrapError('seed qualification artifact escaped product authority') from error
    if not seed_artifact_path.is_file() or sha256_file(seed_artifact_path) != seed_artifact['sha256']:
        raise BootstrapError('seed qualification artifact differs from retained result')

    artifacts = _artifact_map(main_report)
    if set(artifacts) != set(EXPECTED_ARTIFACTS):
        raise BootstrapError(
            f'bootstrap artifact set differs; expected={sorted(EXPECTED_ARTIFACTS)} '
            f'observed={sorted(artifacts)}')

    manifest = workspace / 'bootstrap.manifest'
    lines = [
        f'format {MANIFEST_FORMAT}',
        f'seed-descriptor {marker["seed"]["descriptor"]}',
        f'seed-sha256 {marker["seed"]["sha256"]}',
        f'foundation-revision {marker["foundation"]["revision"]}',
        f'qualification-sha256 {marker["qualification"]["sha256"]}',
        f'controller-source-lock {marker["controller"]["source_lock"]}',
        f'pkgctl-sha256 {marker["controller"]["pkgctl"]["sha256"]}',
        f'pkgstate-init-sha256 {marker["controller"]["pkgstate_init"]["sha256"]}',
        f'seed-qualification-sha256 {seed_artifact["sha256"]}',
        f'build-policy-parallelism {marker["build_policy"]["parallelism"]}',
        f'build-policy-file-creation-mask {marker["build_policy"]["file_creation_mask"]}',
        f'build-policy-source-date-epoch {marker["build_policy"]["source_date_epoch"]}',
        f'build-policy-output-layout {marker["build_policy"]["output_layout"]}',
        f'foundation-operation-policy-profile {_foundation_operation_profile(marker)}',
        f'foundation-stage {FOUNDATION_STAGE}',
        'foundation-profile @foundation',
        f'foundation-members {",".join(FOUNDATION_MEMBERS)}',
        f'foundation-managed-target {identity_for("managed-target", marker)}',
        f'foundation-state-store {identity_for("state-store", marker)}',
        f'foundation-root-view {identity_for("root-view", marker)}',
        f'seed-execution-root-view {seed_execution_root_view_identity(marker)}',
        f'seed-retirement-qualified {"yes" if SEED_RETIREMENT_QUALIFIED else "no"}',
    ]

    main_artifact_root = workspace / 'main' / 'runtime' / 'artifacts'
    for package in EXPECTED_ARTIFACTS:
        artifact = artifacts[package]
        expected_version, expected_release = EXPECTED_PACKAGE_COORDINATES[package]
        if (artifact.get('version') != expected_version
                or artifact.get('release') != expected_release):
            raise BootstrapError(
                f'{package}: package coordinate differs; expected='
                f'{expected_version}-{expected_release} observed='
                f'{artifact.get("version")}-{artifact.get("release")}')
        required = {'path', 'sha256', 'binding-identity', 'image-identity'}
        if not required.issubset(artifact):
            raise BootstrapError(f'{package}: retained artifact report is incomplete')
        path = Path(artifact['path']).resolve()
        try:
            path.relative_to(main_artifact_root.resolve())
        except ValueError as error:
            raise BootstrapError(f'{package}: artifact escaped product artifact root') from error
        if not path.is_file():
            raise BootstrapError(f'{package}: retained artifact is absent: {path}')
        observed = sha256_file(path)
        if observed != artifact['sha256']:
            raise BootstrapError(f'{package}: artifact SHA-256 differs from retained result')
        lines.append(
            f'package {package} sha256 {observed} '
            f'binding {artifact["binding-identity"]} image {artifact["image-identity"]}')

    foundation_root = _foundation_root(marker).resolve()
    _validate_foundation_root_scope(foundation_root)
    if (workspace / 'main' / 'artifacts').exists():
        raise BootstrapError('main run retained a public build artifact root')

    required_members = {
        'filesystem': ('lib64', 'usr/lib64'),
        'glibc': (
            'usr/include/gnu/stubs.h', 'usr/lib/crt1.o', 'usr/lib/crti.o',
            'usr/lib/crtn.o', 'usr/lib/libc.so.6', 'usr/lib/libc_nonshared.a',
            'usr/lib/ld-linux-x86-64.so.2', 'usr/bin/localedef',
            'usr/lib/locale/locale-archive', 'usr/share/locale/locale.alias',
        ),
        'linux-api-headers': ('usr/include/linux/types.h',),
        'glibc-bootstrap': (
            'usr/include/gnu/stubs.h', 'usr/lib/crt1.o', 'usr/lib/libc.so.6',
            'usr/lib/ld-linux-x86-64.so.2',
        ),
        'libgcc': ('usr/lib/libgcc_s.so.1',),
    }
    paths = {name: Path(record['path']) for name, record in artifacts.items()}
    for package, members in required_members.items():
        for member in members:
            if not _tar_has_member(paths[package], member):
                raise BootstrapError(f'{package}: required artifact member is absent: {member}')

    with tempfile.TemporaryDirectory(prefix='zeppe-lin-bootstrap-check-') as temporary:
        root = Path(temporary)
        for name in ('filesystem', 'glibc', 'libgcc'):
            (root / name).mkdir()
        _extract_archive_bytes(paths['filesystem'].read_bytes(), root / 'filesystem')
        _extract_archive_bytes(paths['glibc'].read_bytes(), root / 'glibc')
        _extract_archive_bytes(paths['libgcc'].read_bytes(), root / 'libgcc')

        if os.readlink(root / 'filesystem' / 'lib64') != 'usr/lib64':
            raise BootstrapError('filesystem artifact /lib64 topology differs')
        if os.readlink(root / 'filesystem' / 'usr/lib64') != 'lib':
            raise BootstrapError('filesystem artifact /usr/lib64 topology differs')
        if (root / 'glibc' / 'usr/lib/libgcc_s.so.1').exists():
            raise BootstrapError('published glibc package tree contains libgcc runtime bytes')
        if (root / 'libgcc' / 'usr/lib/libc.so.6').exists():
            raise BootstrapError('published libgcc package tree contains glibc runtime bytes')

        for relative, source in (
                ('usr/lib/libc.so.6', root / 'glibc' / 'usr/lib/libc.so.6'),
                ('usr/lib/locale/locale-archive',
                 root / 'glibc' / 'usr/lib/locale/locale-archive'),
                ('usr/share/locale/locale.alias',
                 root / 'glibc' / 'usr/share/locale/locale.alias'),
                ('usr/lib/libgcc_s.so.1', root / 'libgcc' / 'usr/lib/libgcc_s.so.1')):
            target = foundation_root / relative
            if not target.is_file() or sha256_file(target) != sha256_file(source):
                raise BootstrapError(
                    f'foundation managed root differs from selected artifact bytes: {relative}')

        libgcc = root / 'libgcc' / 'usr/lib/libgcc_s.so.1'
        libgcc_dynamic = run_command([context.readelf, '-d', libgcc], check=True).stdout
        if 'Library soname: [libgcc_s.so.1]' not in libgcc_dynamic:
            raise BootstrapError('libgcc artifact has the wrong SONAME')
        if 'Shared library: [libc.so.6]' not in libgcc_dynamic:
            raise BootstrapError('libgcc artifact does not name final libc ABI')
        if 'Shared library: [ld-linux-x86-64.so.2]' not in libgcc_dynamic:
            raise BootstrapError('libgcc artifact does not name final loader ABI')
        if '(RPATH)' in libgcc_dynamic or '(RUNPATH)' in libgcc_dynamic:
            raise BootstrapError('libgcc artifact carries RPATH/RUNPATH')

        _validate_foundation_runtime(context, foundation_root)

    temporary = manifest.with_name(manifest.name + '.tmp')
    temporary.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    temporary.replace(manifest)
    print(manifest.read_text(encoding='utf-8'), end='')
    return manifest


def run(context: BuildContext, options: BootstrapOptions) -> Path:
    marker = initialize(context, options)
    _validate_controller(context, marker)
    privilege = _requested_privilege(options, marker)
    _validate_supervisor(marker, privilege)
    print('bootstrap: qualifying historical seed execution authority')
    _run_until_terminal(
        context, marker, qualification=True,
        maximum_steps=options.maximum_steps, privilege=privilege)
    print('bootstrap: constructing/checking and converging @foundation')
    _run_until_terminal(
        context, marker, qualification=False,
        maximum_steps=options.maximum_steps, privilege=privilege)
    return check(context, BootstrapOptions(
        workspace=options.workspace, maximum_steps=options.maximum_steps,
        privilege=options.privilege))


def resume(context: BuildContext, options: BootstrapOptions) -> Path:
    marker = load_marker(options.workspace.expanduser().resolve())
    _validate_controller(context, marker)
    _reject_start_redeclaration(options)
    privilege = _requested_privilege(options, marker)
    _validate_supervisor(marker, privilege)
    _run_until_terminal(
        context, marker, qualification=True,
        maximum_steps=options.maximum_steps, privilege=privilege)
    _run_until_terminal(
        context, marker, qualification=False,
        maximum_steps=options.maximum_steps, privilege=privilege)
    return check(context, BootstrapOptions(
        workspace=options.workspace, maximum_steps=options.maximum_steps,
        privilege=options.privilege))


def clean(context: BuildContext, options: BootstrapOptions) -> None:
    del context
    workspace = options.workspace.expanduser().resolve()
    if not workspace.exists():
        return
    if not marker_path(workspace).is_file():
        raise BootstrapError(f'refusing to remove unmarked bootstrap workspace: {workspace}')
    _validate_cleanup_marker(workspace)
    _reject_start_redeclaration(options)
    privilege = None if options.privilege is None else resolve_program(options.privilege)
    try:
        shutil.rmtree(workspace)
    except OSError:
        if privilege is None:
            raise BootstrapError(
                'bootstrap workspace contains inaccessible bytes; use --privilege for cleanup')
        result = run_command(['rm', '-rf', '--', workspace], privilege=privilege)
        if result.status != 0:
            print_result(result)
            raise BootstrapError('privileged bootstrap workspace cleanup failed')
