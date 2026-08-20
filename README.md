# zeppe-lin-system

`zeppe-lin-system` is the host-side product composer for the native Zeppe-Lin
package stack. It builds one exact native controller from pinned Meson
subprojects, then uses that controller to construct system products from
explicit package-source and seed authority.

The project does not resolve dependencies, execute recipes, reconcile package
state, or apply package images itself. Those semantics remain in `pkgctl` and
the native libraries.

The current `0.1.x` milestone provides two surfaces:

```text
controller    exact pkgctl + pkgstate-init build
bootstrap     historical seed qualification + final runtime cohort construction
```

## Build the controller

The controller source set is recorded by exact Git commits in
`subprojects/*.wrap`. Zeppe-Lin library dependencies are forced to those wraps;
an installed `libpkg*` is not controller source authority.

The host supplies a C++ toolchain, Meson/Ninja, Python 3, Git, `readelf`, POSIX
threads, OpenSSL `libcrypto`, libarchive, libcurl >= 7.85.0, and libyaml >=
0.2.5.

```sh
meson setup build
meson compile -C build controller
meson test -C build --suite contract --print-errorlogs
```

When a committed wrap revision changes in an existing checkout, update/reset the
materialized Meson subprojects and reconfigure before using the generated frontend.
Configuration refuses a fallback checkout whose HEAD differs from its wrap or has
tracked modifications. `build/zlsystem` carries a stamp of the configured wrap set
and bootstrap refuses a stale generated frontend or a `pkgctl` release that differs
from current product authority. New workspaces retain that complete source-lock
identity alongside the terminal executable digests; run, resume and check refuse a
workspace admitted under another controller closure. `bootstrap clean` remains
deletion-only and can remove such obsolete private bytes.

`build/controller-paths.ini` records the exact build-tree `pkgctl` and
`pkgstate-init` targets. Meson also generates the executable
`build/zlsystem` frontend from those same target objects.

For a prefetched controller source set, `--wrap-mode=nodownload` disables wrap
network acquisition while the committed `force_fallback_for` policy continues
to forbid installed Zeppe-Lin substitutes.

The pinned closure includes `libpkgobject` alongside `pkgctl` 0.43.0. Bootstrap
keeps package-object byte availability in `qualification/package-objects` and
`main/package-objects`, as durable siblings of each stage's private `runtime`
tree. Those paths are current resource-provider coordinates, not installed-state
or transaction-history authority, and are supplied again on resume.

## Bootstrap

The default bootstrap invocation is deliberately short:

```sh
./build/zlsystem bootstrap --privilege sudo --jobs 8
```

On a new workspace it:

1. reads the committed default historical seed descriptor;
2. downloads and SHA-256-verifies the rootfs archive and detached-signature
   bytes, or accepts exact matching local bytes;
3. extracts a private construction seed root;
4. acquires and snapshots the exact `pkgsrc-foundation` revision declared in
   `collections/foundation.ini`;
5. snapshots the product-owned bootstrap qualification collection;
6. initializes two empty native state authorities with the Meson-built
   `pkgstate-init`;
7. admits and runs the checked `seed-probe` transaction;
8. admits one mixed native transaction under the complete
   `exact-compatible-sharing` target-operation policy, converges exact `@foundation`
   membership into the private `main/foundation-root`, and checks the same target
   `libgcc` selection; and
9. independently re-hashes the five retained construction artifacts, verifies the
   managed foundation root against selected artifact bytes, usable `C.UTF-8`,
   retained `locale.alias`, and managed libc/libgcc loadability, then emits
   `bootstrap.manifest`.


The current bootstrap is deliberately **seed-assisted**. It now composes the stable
`@foundation` substrate (`filesystem`, final `glibc`, `libgcc`) into a real managed
root, but construction and lifecycle execution authority for this transaction still
comes from the admitted historical seed. That S0 execution root has its own
opaque root-view identity, admitted from the exact seed bytes plus product-owned
execution-root layout; it is not inferred from the managed target root. BUILD/CHECK
and lifecycle bind that same S0 identity in distinct controller authority slots.
The manifest therefore records
`foundation-stage seed-assisted-foundation-root-qualified` and
`seed-retirement-qualified no`. A later hostile seed-retirement gate, not root
composition itself, owns the transition to seed-free construction.

The product workspace defaults to `build/products/bootstrap`. Start-only
authority is retained there. Later operations do not require the operator to
repeat the seed hash, foundation revision, build policy, root coordinate, or
controller paths:

```sh
./build/zlsystem bootstrap resume
./build/zlsystem bootstrap check
./build/zlsystem bootstrap clean
```

`--max-steps` is live per-invocation control. `--jobs`,
`--source-date-epoch`, seed selection and collection source overrides are
start-only authority. The product-selected `exact-compatible-sharing` operation
policy is retained in workspace authority and admitted only on the initial
`pkgctl run --start`; resume relies on pkgctl's retained command authority and
does not redeclare the policy. Resume/check reject caller re-declaration of
start-only product authority. Cleanup is different: it validates only that the
workspace marker is in the current private format and binds the exact workspace
path, so an obsolete pre-policy workspace can be deliberately destroyed even
though it cannot be resumed or checked.

For offline seed acquisition, select the same committed descriptor but supply
its exact bytes:

```sh
./build/zlsystem bootstrap \
  --seed-file /path/to/rootfs-v1.2.1-20260222-x86_64.tar.xz \
  --seed-signature-file /path/to/rootfs-v1.2.1-20260222-x86_64.tar.xz.sig \
  --privilege sudo
```

A local `pkgsrc-foundation` checkout may be supplied with `--foundation-source`,
but it must be clean and at the exact committed revision. The frontend snapshots
that Git commit; it never consumes ambient working-tree edits.

The detached signature is retained and hash-qualified because the historical
release publishes it. This milestone does not claim detached-signature trust
verification: no signing-key authority has yet been specified by this product.

## Product qualification versus tests

Real product qualification assets live under:

```text
products/bootstrap/qualification/collection/
```

`seed-probe` is executed by the real bootstrap product but is never distribution
package membership. Foundation runtime qualification is performed against the
managed `@foundation` result itself rather than by manufacturing a parallel probe
closure.

Development tests live separately under `tests/` and are grouped by product:

```text
contract:...
bootstrap:...
rootfs:...        future
iso-install:...   future
iso-live:...      future
```

## Product direction

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

Package membership belongs to collection/profile authority. Product-specific
preparation, overlays, qualification and artifact composition belong here.

See `DESIGN.md` and `TESTING.md` for the exact boundary.

## License

GPL-3.0-or-later. See `COPYING` and `COPYRIGHT`.
