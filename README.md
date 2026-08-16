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

`build/controller-paths.ini` records the exact build-tree `pkgctl` and
`pkgstate-init` targets. Meson also generates the executable
`build/zlsystem` frontend from those same target objects.

For a prefetched controller source set, `--wrap-mode=nodownload` disables wrap
network acquisition while the committed `force_fallback_for` policy continues
to forbid installed Zeppe-Lin substitutes.

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
8. admits and runs the checked `runtime-cohort-probe` transaction against
   `pkgsrc-foundation`; and
9. independently re-hashes and audits the six published bootstrap artifacts,
   then emits `bootstrap.manifest`.

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
start-only authority. Resume/check recover them from the workspace and reject
their re-declaration.

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

`seed-probe` and `runtime-cohort-probe` are executed by real bootstrap products
but are never distribution package membership.

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
