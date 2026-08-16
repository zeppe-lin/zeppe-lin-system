# Testing zeppe-lin-system

The initial milestone tests source-set and composition authority. It does not
pretend that running the standalone unit suites of 34 wrapped libraries inside
the superproject adds confidence; those suites belong to their repositories and
are disabled here.

Run:

```sh
meson setup build
meson compile -C build controller
meson test -C build --suite contract --print-errorlogs
```

## Contract attacks

`source-lock` requires the exact 35-project closure, canonical GitHub URLs, and
40-hex revisions. Moving revisions, shallow wrap policy, unexpected repositories
and missing codec providers are rejected.

`controller-boundary` requires host dependency qualification, pinned fallback
forcing, build-tree target extraction, and suppression of wrapped maintainer
features. It rejects the old `.toolchain`/pkg-config feedback loop and rejects
premature privileged bootstrap/rootfs orchestration inside Meson.

`seed-descriptors` requires a closed descriptor vocabulary, canonical HTTPS
release authority, SHA-256 archive/signature identities, x86_64 qualification,
and an explicit committed default.

## Foreign-host qualification

The controller milestone is not complete merely because it builds on the
Zeppe-Lin development machine. Test a fresh foreign host with no installed
native `libpkg*` stack. The important observation is that the build either:

- qualifies the host compiler and four external development libraries, fetches
  the pinned source set, and produces the controller; or
- fails during host/source qualification with a concrete missing dependency.

It must not succeed by finding stale Zeppe-Lin libraries in `/usr`.

For offline qualification, prefetch/populate `subprojects/` and configure with:

```sh
meson setup build-offline --wrap-mode=nodownload
```

The committed `force_fallback_for` policy still requires the pinned Zeppe-Lin
subprojects rather than installed substitutes.

Future bootstrap/rootfs tests must be added only when those products exist and
must include restart, corruption, seed mismatch, partial product, and privilege
boundary assaults rather than one end-to-end happy path.
