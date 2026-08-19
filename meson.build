project(
  'zeppe-lin-system',
  'cpp',
  version: '0.1.0',
  license: 'GPL-3.0-or-later',
  meson_version: '>=1.8.3',
  default_options: [
    'force_fallback_for=libpkgapply,libpkgapply-exec,libpkgapply-posix,libpkgaudit,libpkgbuild,libpkgbuild-exec,libpkgbuild-image,libpkgbuild-plan,libpkgcatalog,libpkgcatalog-acquire,libpkgcatalog-codec,libpkgcheck,libpkgcheck-exec,libpkgexec,libpkgexec-linux,libpkgfetch,libpkgimage,libpkgimage-exec,libpkgplan,libpkgreconcile,libpkgreconcile-apply,libpkgreconcile-apply-posix,libpkgreconcile-posix,libpkgresolve,libpkgsource,libpkgsource-codec,libpkgsource-exec,libpkgsource-plan,libpkgsource-yaml,libpkgstate,libpkgstate-apply,libpkgstate-build,libpkgstate-plan,libpkgstate-posix,libpkgstate-source,libpkgtransaction',
    'libpkgapply:tests=disabled',
    'libpkgapply:man_pages=disabled',
    'libpkgapply:html_docs=disabled',
    'libpkgapply-exec:tests=disabled',
    'libpkgapply-exec:man_pages=disabled',
    'libpkgapply-posix:tests=disabled',
    'libpkgapply-posix:man_pages=disabled',
    'libpkgapply-posix:html_docs=disabled',
    'libpkgaudit:tests=disabled',
    'libpkgaudit:man_pages=disabled',
    'libpkgaudit:tools=disabled',
    'libpkgbuild:tests=disabled',
    'libpkgbuild:man_pages=disabled',
    'libpkgbuild-exec:tests=disabled',
    'libpkgbuild-exec:man_pages=disabled',
    'libpkgbuild-image:tests=disabled',
    'libpkgbuild-image:man_pages=disabled',
    'libpkgbuild-plan:tests=disabled',
    'libpkgbuild-plan:man_pages=disabled',
    'libpkgcatalog:tests=disabled',
    'libpkgcatalog:man_pages=disabled',
    'libpkgcatalog:html_docs=disabled',
    'libpkgcatalog-acquire:tests=disabled',
    'libpkgcatalog-acquire:man_pages=disabled',
    'libpkgcatalog-acquire:html_docs=disabled',
    'libpkgcatalog-acquire:scan_tool=disabled',
    'libpkgcheck:tests=disabled',
    'libpkgcheck:man_pages=disabled',
    'libpkgcheck-exec:tests=disabled',
    'libpkgcheck-exec:man_pages=disabled',
    'libpkgexec:tests=disabled',
    'libpkgexec:man_pages=disabled',
    'libpkgexec-linux:tests=disabled',
    'libpkgexec-linux:man_pages=disabled',
    'libpkgfetch:tests=disabled',
    'libpkgfetch:man_pages=disabled',
    'libpkgimage:tests=disabled',
    'libpkgimage:man_pages=disabled',
    'libpkgimage:html_docs=disabled',
    'libpkgimage-exec:tests=disabled',
    'libpkgplan:tests=disabled',
    'libpkgplan:man_pages=disabled',
    'libpkgplan:html_docs=disabled',
    'libpkgplan:reference_tools=disabled',
    'libpkgreconcile:tests=disabled',
    'libpkgreconcile:man_pages=disabled',
    'libpkgreconcile-apply:tests=disabled',
    'libpkgreconcile-apply:man_pages=disabled',
    'libpkgreconcile-apply-posix:tests=disabled',
    'libpkgreconcile-apply-posix:man_pages=disabled',
    'libpkgreconcile-posix:tests=disabled',
    'libpkgreconcile-posix:man_pages=disabled',
    'libpkgresolve:tests=disabled',
    'libpkgresolve:man_pages=disabled',
    'libpkgsource:tests=disabled',
    'libpkgsource:man_pages=disabled',
    'libpkgsource:html_docs=disabled',
    'libpkgsource-exec:tests=disabled',
    'libpkgsource-plan:tests=disabled',
    'libpkgsource-plan:man_pages=disabled',
    'libpkgsource-plan:html_docs=disabled',
    'libpkgsource-yaml:tests=disabled',
    'libpkgsource-yaml:man_pages=disabled',
    'libpkgsource-yaml:html_docs=disabled',
    'libpkgstate:tests=disabled',
    'libpkgstate:man_pages=disabled',
    'libpkgstate:html_docs=disabled',
    'libpkgstate-apply:tests=disabled',
    'libpkgstate-apply:man_pages=disabled',
    'libpkgstate-apply:html_docs=disabled',
    'libpkgstate-build:tests=disabled',
    'libpkgstate-build:man_pages=disabled',
    'libpkgstate-build:html_docs=disabled',
    'libpkgstate-plan:tests=disabled',
    'libpkgstate-plan:man_pages=disabled',
    'libpkgstate-plan:html_docs=disabled',
    'libpkgstate-posix:tests=disabled',
    'libpkgstate-posix:man_pages=disabled',
    'libpkgstate-posix:html_docs=disabled',
    'libpkgstate-posix:tools=enabled',
    'libpkgstate-posix:install_tools=false',
    'libpkgstate-source:tests=disabled',
    'libpkgstate-source:man_pages=disabled',
    'libpkgstate-source:html_docs=disabled',
    'libpkgtransaction:tests=disabled',
    'libpkgtransaction:man_pages=disabled',
    'pkgctl:tests=disabled',
    'pkgctl:man_pages=disabled',
  ],
)

# The controller product is a pinned source build. External dependencies remain
# host authority and are qualified here before the wrapped controller graph is
# admitted.
dependency('libcrypto', required: true)
dependency('libarchive', required: true)
dependency('libcurl', version: '>=7.85.0', required: true)
dependency('yaml-0.1', version: '>=0.2.5', required: true)
dependency('threads', required: true)

python3 = find_program('python3', required: true)
git = find_program('git', required: true)
readelf = find_program('readelf', required: true)

# Configure libpkgstate-posix explicitly so the controller can retain the exact
# pkgstate-init target object. Its library dependencies continue to resolve
# through the same pinned wrap source set.
state_posix_project = subproject('libpkgstate-posix')
pkgstate_init_tool = state_posix_project.get_variable('pkgstate_init_tool')

# pkgctl is the terminal controller subproject. Its dependency() calls resolve
# against the wrap-provided overrides rather than installed Zeppe-Lin libraries.
pkgctl_project = subproject('pkgctl')
pkgctl_exe = pkgctl_project.get_variable('pkgctl_exe')
libpkgexec_linux_dep = dependency('libpkgexec-linux', required: true)

wrapped_source_authority_test = files(
  'tests/controller/wrapped_source_authority_test.py',
)
run_command(
  python3,
  wrapped_source_authority_test,
  meson.project_source_root(),
  git.full_path(),
  check: true,
)

alias_target('controller', pkgctl_exe, pkgstate_init_tool)

controller_paths = configuration_data()
controller_paths.set('PKGCTL', pkgctl_exe.full_path())
controller_paths.set('PKGSTATE_INIT', pkgstate_init_tool.full_path())
controller_paths_file = configure_file(
  input: 'controller-paths.ini.in',
  output: 'controller-paths.ini',
  configuration: controller_paths,
)

message('controller paths: ' + controller_paths_file.full_path())

controller_source_lock = run_command(
  python3,
  files('tests/controller/controller_source_lock_digest.py'),
  meson.project_source_root(),
  check: true,
).stdout().strip()

frontend_configuration = configuration_data()
frontend_configuration.set('SOURCE_ROOT', meson.project_source_root())
frontend_configuration.set('CONTROLLER_SOURCE_LOCK', controller_source_lock)
frontend_configuration.set('BUILD_ROOT', meson.project_build_root())
frontend_configuration.set('PKGCTL', pkgctl_exe.full_path())
frontend_configuration.set('PKGSTATE_INIT', pkgstate_init_tool.full_path())
frontend_configuration.set('GIT', git.full_path())
frontend_configuration.set('READELF', readelf.full_path())
zlsystem_frontend = configure_file(
  input: 'tools/zlsystem.in',
  output: 'zlsystem',
  configuration: frontend_configuration,
)
message('system frontend: ' + zlsystem_frontend.full_path())

test(
  'source-lock',
  python3,
  args: [files('tests/contracts/source_lock_test.py'), meson.project_source_root()],
  suite: 'contract',
)
test(
  'controller-boundary',
  python3,
  args: [files('tests/contracts/controller_contract_test.py'), meson.project_source_root()],
  suite: 'contract',
)
test(
  'seed-descriptors',
  python3,
  args: [files('tests/contracts/seed_contract_test.py'), meson.project_source_root()],
  suite: 'contract',
)

test(
  'bootstrap-source-authority',
  python3,
  args: [files('tests/contracts/bootstrap_source_contract_test.py'), meson.project_source_root()],
  suite: 'contract',
)
test(
  'bootstrap-model',
  python3,
  args: [files('tests/bootstrap/bootstrap_model_test.py'), meson.project_source_root()],
  suite: 'bootstrap',
)

wrapped_isolation_test = executable(
  'wrapped-isolation-test',
  'tests/controller/wrapped_isolation_test.cpp',
  dependencies: libpkgexec_linux_dep,
  install: false,
)
test(
  'wrapped-source-authority',
  python3,
  args: [
    wrapped_source_authority_test,
    meson.project_source_root(),
    git.full_path(),
  ],
  suite: 'controller',
)
test(
  'wrapped-source-authority-model',
  python3,
  args: [
    files('tests/controller/wrapped_source_authority_model_test.py'),
    meson.project_source_root(),
  ],
  suite: 'controller',
)
test(
  'wrapped-pkgctl-start',
  python3,
  args: [
    files('tests/controller/wrapped_pkgctl_release_test.py'),
    pkgctl_exe.full_path(),
    '0.42.0',
  ],
  suite: 'controller',
)
test(
  'wrapped-isolation',
  wrapped_isolation_test,
  suite: 'integration-privileged',
)
