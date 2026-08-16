# zeppe-lin-system design

## Boundary

`zeppe-lin-system` owns host-side construction of Zeppe-Lin system products. It
does not become a package resolver, package builder, transaction engine, state
store, or package-source collection.

```text
source-set authority        product input authority
(pinned wraps)              (seed / collection / policy)
        \                    /
         \                  /
          v                v
           system orchestrator
                  |
                  v
         native controller APIs/CLI
                  |
                  v
             product artifact
```

The native package libraries remain the semantic owners of package operations.
The system project composes them into host-facing products.

## Controller source set

The controller is built from exact repository commits recorded in
`subprojects/*.wrap`. A wrap is source authority, not a hint. All Zeppe-Lin
library dependency names in the controller closure are listed in Meson's
`force_fallback_for` option so an installed library cannot satisfy a wrapped
controller edge.

The current recursive closure contains 35 projects including `pkgctl`. `pkgctl`
and `libpkgstate-posix` are explicit terminal subprojects because their
executable target objects are needed by the system project. The remaining
libraries are admitted lazily through ordinary Meson `dependency()` calls and
their wrap-provided `meson.override_dependency()` values.

Two repositories provide more than one dependency name:

```text
libpkgsource  -> libpkgsource, libpkgsource-codec
libpkgcatalog -> libpkgcatalog, libpkgcatalog-codec
```

Those aliases are stated in the corresponding wrap `[provide]` sections. No
controller repository is discovered by scanning GitHub or a sibling checkout.
Changing the source set means changing a committed wrap revision.

## Host authority

The controller source set does not vendor general host toolchain libraries. The
host supplies the C++ compiler, Meson/Ninja, Python 3, threads, OpenSSL
`libcrypto`, libarchive, libcurl and libyaml. Meson qualifies these before the
controller subprojects are configured.

Maintainer tests, generated manuals, HTML documentation, and reference tools of
wrapped libraries are explicitly disabled. They remain obligations of the
individual repositories and must not turn a foreign-host controller build into
a demand for Pandoc, Doxygen, scdoc, clang-format, or privileged integration
facilities.

`pkgstate-init` is the one non-pkgctl reference tool enabled because it is part
of controller provisioning. It is used directly from the build graph and is not
installed merely to make another subproject discover it.

## No private installed-prefix feedback loop

The controller build must not recreate the historical development harness:

```text
build A -> install into .toolchain -> mutate PKG_CONFIG_PATH -> build B
```

Meson target/dependency objects connect the source projects in one build graph.
No `.toolchain`, generated shell environment, `PKG_CONFIG_PATH`,
`LD_LIBRARY_PATH`, or `CMAKE_PREFIX_PATH` is controller source authority.

The generated `controller-paths.ini` records exact executable paths from Meson
target objects for the future system frontend. It is a build-tree projection,
not durable package evidence.

## Seed authority

A bootstrap seed is an external historical rootfs artifact, not current package
truth and not controller source authority. A committed seed descriptor names:

```text
protocol
logical seed name
architecture
release namespace
archive URL
archive SHA-256
signature URL
signature-file SHA-256
```

Future bootstrap code must verify downloaded bytes before extracting them and
must bind the verified seed identity into campaign admission. A successful past
seed use must never be treated as observation that an unverified local file is
still the same seed.

The initial descriptor protocol is x86_64-only because the current native
bootstrap recipes are x86_64-only.

## Product boundaries

### Controller

Pure host build. No privilege. No package transaction. Output is the exact
build-tree `pkgctl` and `pkgstate-init` controller pair plus its source-set
context.

### Bootstrap

Future product. It will provision a verified seed root, admit a complete native
build policy, and drive a bounded `pkgsrc-core-native` campaign through the
controller. Stateful transaction/restart semantics remain inside `pkgctl` and
its libraries.

### Rootfs

Future product. It will converge an empty target to explicit native profile
policy and emit/audit a rootfs artifact. Directory enumeration of a collection
is not rootfs membership policy.

### Installation and live media

Future products consuming a sealed rootfs artifact and their own media-specific
inputs. They are not package dependency edges and are intentionally out of the
initial design milestone.
