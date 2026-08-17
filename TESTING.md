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
meson test -C build --suite controller --print-errorlogs
```

The wrapped controller also has a privileged product-composition gate:

```sh
sudo meson test -C build --suite integration-privileged --print-errorlogs
```

This does not enable or import wrapped maintainer suites. It exercises the exact
`libpkgexec-linux` body linked into the pinned controller composition and requires
its end-to-end isolated filesystem capability probe to realize the root/resource
mount and cleanup guarantees that `pkgctl build` will later require. An
unprivileged or policy-restricted invocation skips this gate; a realization
failure such as an internal cleanup `EBUSY` is a test failure, not a capability
absence.

## Contract suite

`source-lock` requires the exact 35-project controller closure, canonical GitHub
URLs, exact revisions and codec providers.

`controller-boundary` requires host dependency qualification, pinned fallback
forcing, build-tree controller target extraction, executable `zlsystem`
generation, suppression of wrapped maintainer features, and registration of the
product-level wrapped startup/isolation gates. It rejects the old
`.toolchain`/pkg-config feedback loop and privileged product execution inside
Meson.

`wrapped-pkgctl-start` proves that the composed build-tree `pkgctl` executable and
its wrapped shared-library closure can start without falling back to an installed
native stack. `wrapped-isolation` is the privilege-sensitive mechanism gate
described above.

`seed-descriptors` requires closed seed vocabulary, canonical release authority,
SHA-256 archive/signature identities and an explicit default.

`bootstrap-source-authority` requires the exact `pkgsrc-foundation` Git source
revision, forbids treating it as a controller wrap, and requires the seed probe
to live under product qualification rather than an ordinary product collection.
The finished foundation runtime is qualified from the managed target and retained
construction evidence, not through a second package closure that duplicates
build- and target-environment selections.

## Bootstrap suite

`bootstrap-model` attacks private authority primitives without requiring
privilege or a real package transaction. It checks descriptor loading,
policy-sensitive request identity, qualification-sensitive target identity,
controller report parsing, safe archive extraction, path traversal refusal and
write-through-symlink refusal. It also requires the main stage to be one mixed
`pkgctl run` transaction with exact `@foundation` convergence, attacks a non-default
build parallelism value so the frontend cannot fall back to one job, rejects public
main-stage artifact authority, rejects an explicit build goal that would recreate
the target substrate in a parallel build environment, and poisons a synthetic
foundation root with compiler residue. Seed retirement remains explicitly unproven.

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
- interrupted foundation construction/check/convergence;
- corrupted published artifact before `bootstrap check`; and
- privilege-context drift.


The current bootstrap manifest must say:

```text
foundation-stage seed-assisted-foundation-root-qualified
foundation-profile @foundation
foundation-members filesystem,glibc,libgcc
seed-retirement-qualified no
```

Bootstrap qualification also requires final glibc to retain
`usr/share/locale/locale.alias` exactly alongside the sealed `C.UTF-8` locale
archive, while translated message catalogs remain absent by collection policy.

This is intentional negative evidence. A correctly converged `@foundation` root while
the S0 seed remains reachable is still not proof that higher construction has ceased
to depend on that seed. The future seed-retirement test must make S0 inaccessible
before a native construction session and fail on any attempted fallback.

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
