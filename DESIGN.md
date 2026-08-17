# zeppe-lin-system design

## Boundary

`zeppe-lin-system` owns host-side construction and qualification of Zeppe-Lin
system products. It does not become a package resolver, recipe executor,
transaction engine, installed-state store, or distribution package collection.

```text
controller source authority      product input authority
(pinned Meson wraps)             (seed / collections / policy)
             \                    /
              \                  /
               v                v
                system product composer
                         |
                         v
                 pkgctl / pkgstate-init
                         |
                         v
                 qualified product result
```

The controller owns package semantics. The system project owns the mundane and
product-specific ceremony needed to present exact authority to that controller.

## Controller source set

The controller is one Meson graph built from exact repository commits recorded
in `subprojects/*.wrap`. All provided `libpkg*` dependency names are listed in
`force_fallback_for`, so an installed library cannot satisfy a wrapped edge.

The recursive closure contains 35 projects including `pkgctl`.
`libpkgstate-posix` and `pkgctl` are explicit terminal subprojects because the
system frontend consumes their executable target objects. The remaining
libraries are admitted through normal Meson dependency fallback and
`meson.override_dependency()`.

`libpkgsource` and `libpkgcatalog` each provide both their library and codec
dependency name. Those aliases are part of the source lock.

The controller build never recreates the old development feedback loop:

```text
build A -> install .toolchain -> mutate PKG_CONFIG_PATH -> build B
```

There is no `.toolchain`, generated shell environment, `PKG_CONFIG_PATH`,
`LD_LIBRARY_PATH`, or `CMAKE_PREFIX_PATH` controller authority.

## Package-source authority is not a Meson dependency

`pkgsrc-foundation` is deliberately not a wrap/subproject. It is data consumed
by a system product, not code needed to build the controller.

`collections/foundation.ini` therefore records a separate product-input source
protocol with:

```text
logical collection name
canonical Git URL
exact 40-hex revision
```

At bootstrap admission the frontend either acquires that repository or accepts
an explicit local checkout. The checkout must be clean and exactly at the
recorded commit. The frontend then snapshots the commit with `git archive` into
the private product workspace. Later transaction execution never observes a
mutable collection worktree.

Collection profiles and recipes remain distribution package authority.
`zeppe-lin-system` does not infer package membership from directory enumeration.

## Seed authority

A seed is a historical rootfs artifact used as external construction authority.
It is not current installed-state truth.

A committed seed descriptor names the release coordinates and SHA-256 of both
the rootfs archive and its detached-signature file. New workspaces verify the
archive bytes before extraction. Supplying `--seed-file` is only an acquisition
override: those bytes still have to equal the selected descriptor identity.

The product never accepts a pre-extracted arbitrary directory accompanied by a
claimed hash. It extracts the admitted archive itself into a private workspace,
so retained seed identity refers to known source bytes rather than reconstructed
filesystem truth.

The detached signature is retained and hash-qualified but is not yet claimed as
cryptographically verified publication authority. That requires an explicit
signing-key trust boundary first.

## Bootstrap product

The current bootstrap product composes the first managed `@foundation` root
without broadening into native toolchain construction. It consumes the
seed-retirement-oriented `pkgsrc-foundation` boundary, but this stage remains
explicitly seed-assisted: the historical seed still supplies construction tools.

It has two package catalogs:

```text
foundation
    distribution package-source authority

bootstrap-qualification
    product-owned qualification recipes only
```

The qualification catalog lives under:

```text
products/bootstrap/qualification/collection/
```

and currently contains:

```text
seed-probe
```

These recipes are not part of `@foundation`, `@rootfs`, or any distribution
package set. They exist because the bootstrap product requires their successful
execution before it accepts the result.

The first transaction checks the historical seed execution closure. The second is
one mixed native `pkgctl run` transaction. It constructs the exact target
foundation closure and checks the final libgcc selection:

```text
linux-api-headers -> glibc
linux-api-headers -> glibc-bootstrap -> libgcc
                                  glibc <-> libgcc   (run)
filesystem + glibc(release 3, C.UTF-8) + libgcc      (@foundation)
                                           `-> check libgcc
```

Dependency closure is resolved by the native package stack. The transaction
selects `run=@foundation` with exact convergence into `main/foundation-root` and
`check=libgcc` against the same target selection; it does not introduce a second
explicit build/check root for the finished substrate. Construction-only graph
nodes are retained as artifacts/evidence but are not desired installed state. The
system frontend does not order packages or hand-extract archives for application.


### Foundation stage and seed retirement

The current product result is a **seed-assisted qualified foundation root**, not a
claim that the bootstrap parent has been retired. `@foundation` names the stable
deployable substrate (`filesystem`, final `glibc`, and `libgcc`), while
construction-only recipes such as `linux-api-headers` and `glibc-bootstrap`
remain graph nodes/artifacts rather than desired installed state.

The main transaction converges that exact profile into a private managed target and
retains its construction artifacts beneath the run-private runtime hierarchy. It
still executes construction/lifecycle authority from the admitted historical seed.
Therefore `bootstrap.manifest` records:

```text
foundation-stage seed-assisted-foundation-root-qualified
foundation-profile @foundation
foundation-members filesystem,glibc,libgcc
seed-retirement-qualified no
```

The later seed-retirement milestone must compose exact native construction
authority, revoke access to the historical seed, and successfully continue
construction. Only that hostile transition may change the second fact to `yes`.
Directory presence or successful execution while S0 remains reachable is not
seed-retirement evidence.

## Workspace authority and restart

A bootstrap workspace is private durable product authority. At initialization
it retains:

```text
seed descriptor and verified archive identity
foundation Git revision, private snapshot and managed-root coordinate
qualification snapshot digest
exact pkgctl path and SHA-256
exact pkgstate-init path and SHA-256
native supervisor credentials
complete build policy
privilege command coordinate
private seed-root coordinate
```

Command nonces and state-target identities are domain-separated from those
values. Build policy contributes to the start nonce. Replacing either controller
binary in place, changing explicit build policy, changing privilege command, or
substituting collection/qualification authority fails closed.

`pkgctl --resume` remains responsible for transaction restart semantics. The
system frontend only recovers the already admitted physical/product coordinates
and repeatedly resumes when the controller reports the explicit live step bound.

## Bootstrap qualification

A terminal controller report is necessary but not sufficient to accept the
bootstrap product. `zlsystem bootstrap check` independently:

- requires successfully terminal seed qualification and mixed foundation transactions;
- verifies the seed-probe artifact retained by qualification;
- requires exactly the five expected retained construction artifacts;
- re-hashes every private run archive against retained controller evidence;
- checks critical package members;
- verifies final glibc package coordinates and usable `C.UTF-8` locale authority;
- rejects a public main-stage artifact root, verifies selected libc/locale/libgcc bytes
  in the managed foundation root, and rejects obvious seed/build-only residue;
- verifies final libgcc SONAME/dependencies and absence of RPATH/RUNPATH;
- realizes filesystem/glibc/libgcc package trees from retained archives without
  treating realization residue as evidence;
- verifies libgcc's final dynamic ABI and unwind entry point; and
- drives the installed foundation loader in `--list` mode against installed
  `libgcc_s.so.1`, requiring libc resolution to stay inside the managed root.

Success emits `zeppe-lin.system.bootstrap-manifest/1`.

## Product qualification is not developer testing

`products/<product>/qualification/` contains checks a real product must pass.
`tests/<product>/` contains hostile and regression tests that the implementation
must pass. A probe may therefore be production qualification material while a
synthetic corruption test for that probe belongs under `tests/bootstrap/`.

## Future rootfs and media

Rootfs composition will converge an empty managed target to explicit profile
policy through the same controller. Collection membership is not rootfs
membership and profiles never encode execution order.

Installation and live media are later products consuming a qualified rootfs plus
their own media-specific configuration/overlays. They are not package dependency
edges and must not contaminate distribution collection authority.
