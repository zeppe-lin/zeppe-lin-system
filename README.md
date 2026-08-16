# zeppe-lin-system

`zeppe-lin-system` is the host-side system-construction project for the native
Zeppe-Lin toolchain. It binds a reproducible controller source set and, in later
milestones, will drive bootstrap and system-product construction without asking
the operator to assemble dozens of sibling repositories or source private build
environments by hand.

The initial `0.1.x` milestone deliberately provides one product only:
`controller`.

```text
pinned Zeppe-Lin source set
          |
          v
       Meson
          |
          v
pkgctl + pkgstate-init
```

It does not bootstrap packages, compose a root filesystem, or build installation
media yet. Those products will consume this controller boundary after the
controller build is boring on both Zeppe-Lin and foreign Linux hosts.

## Controller build

The controller source set is recorded by exact Git commits in
`subprojects/*.wrap`. Zeppe-Lin library dependencies are forced to those wraps;
an installed `libpkg*` with a compatible-looking version is not controller
source authority.

Host dependencies are intentionally not wrapped. The current controller needs a
C++ toolchain plus Meson/Ninja and the following development dependencies:

- OpenSSL `libcrypto`
- `libarchive`
- `libcurl` >= 7.85.0
- `libyaml` >= 0.2.5 (`yaml-0.1`)
- POSIX threads
- Python 3 for project contracts and the future host frontend

Configure and build:

```sh
meson setup build
meson compile -C build controller
meson test -C build --suite contract --print-errorlogs
```

Meson downloads missing Zeppe-Lin subprojects from the pinned wraps. For a
prefetched/offline source tree, use `--wrap-mode=nodownload`; the explicit
`force_fallback_for` source-set policy still prevents substitution by installed
Zeppe-Lin libraries.

`build/controller-paths.ini` records the exact build-tree controller executables
from Meson target objects:

```ini
[controller]
pkgctl = /.../build/subprojects/pkgctl/cli/pkgctl
pkgstate_init = /.../build/subprojects/libpkgstate-posix/tools/pkgstate-init
```

Consumers must use that manifest or the target objects that produced it, rather
than reconstructing paths from the build-tree layout.

## Seed descriptors

`seeds/` records known Zeppe-Lin rootfs archives suitable for future bootstrap
campaigns. A descriptor includes the canonical release URL, archive SHA-256,
detached-signature URL, and signature-file SHA-256. The descriptor is source
configuration; downloading, signature verification, extraction, and campaign
admission are not implemented in the controller milestone.

The current default is the fixed v1.2 rootfs published on 2026-02-22. The
original v1.2 rootfs remains available as an explicitly selectable historical
seed.

## Product direction

The intended product chain is:

```text
controller
    |
    v
bootstrap
    |
    v
rootfs
   / \
  v   v
iso-install   iso-live
```

This is product composition, not package dependency policy. Package selection
belongs to native collection/profile authority; `zeppe-lin-system` owns the
host-side construction of system artifacts from those authorities.

See `DESIGN.md` for the boundary and `TESTING.md` for the current assault model.

## License

GPL-3.0-or-later. See `COPYING` and `COPYRIGHT`.
