# Testing zeppe-lin-system

`zeppe-lin-system` has two useful test axes: source/composition contracts and
product-specific assaults. Wrapped library maintainer suites remain obligations
of their own repositories and are disabled here.

Run the pure source tests with:

```sh
meson setup build
meson compile -C build controller
meson test -C build --suite contract --print-errorlogs
meson test -C build --suite bootstrap --print-errorlogs
```

## Contract suite

`source-lock` requires the exact 35-project controller closure, canonical GitHub
URLs, exact revisions and codec providers.

`controller-boundary` requires host dependency qualification, pinned fallback
forcing, build-tree controller target extraction, executable `zlsystem`
generation, and suppression of wrapped maintainer features. It rejects the old
`.toolchain`/pkg-config feedback loop and privileged product execution inside
Meson.

`seed-descriptors` requires closed seed vocabulary, canonical release authority,
SHA-256 archive/signature identities and an explicit default.

`bootstrap-source-authority` requires the exact `pkgsrc-foundation` Git source
revision, forbids treating it as a controller wrap, and requires the two
bootstrap qualification recipes to live under product qualification rather than
an ordinary product collection.

## Bootstrap suite

`bootstrap-model` attacks private authority primitives without requiring
privilege or a real package transaction. It checks descriptor loading,
policy-sensitive request identity, qualification-sensitive target identity,
controller report parsing, safe archive extraction, path traversal refusal and
write-through-symlink refusal.

The real product qualification is intentionally separate from this suite:

```sh
./build/zlsystem bootstrap --privilege sudo --jobs 8
```

A release-grade bootstrap qualification must also be exercised on a foreign
Linux host. Important hostile follow-ups include:

- corrupt cached seed bytes;
- wrong local seed archive;
- wrong/dirty foundation checkout;
- controller binary replacement after admission;
- changed build policy after admission;
- interrupted seed qualification;
- interrupted runtime-cohort construction/check;
- corrupted published artifact before `bootstrap check`; and
- privilege-context drift.

## Foreign-host controller qualification

A fresh host with no installed native `libpkg*` stack must either build the
pinned controller source set or fail with a concrete missing host dependency. It
must never succeed by finding stale Zeppe-Lin libraries in `/usr`.

For offline controller qualification, prefetch `subprojects/` and configure with:

```sh
meson setup build-offline --wrap-mode=nodownload
```

The committed `force_fallback_for` policy still requires the pinned controller
subprojects.

Future product suites should use Meson categories `rootfs`, `iso-install`, and
`iso-live`; do not force all product semantics into a generic integration bucket.
