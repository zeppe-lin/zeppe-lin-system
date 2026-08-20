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

The recursive closure contains 36 projects including `pkgctl`.
`libpkgstate-posix` and `pkgctl` are explicit terminal subprojects because the
system frontend consumes their executable target objects. The remaining
libraries are admitted through normal Meson dependency fallback and
`meson.override_dependency()`.

A committed wrap is declaration authority, not proof that an existing Meson
fallback worktree realizes that declaration. Configuration therefore attests every
resolved `subprojects/<name>` checkout against the exact wrap revision and rejects
tracked source modifications. The generated `zlsystem` frontend is additionally
stamped with an identity of the complete committed wrap set. Bootstrap admission
compares that stamp with the current source tree and requires the exact admitted
`pkgctl` release before seed or collection work begins. This prevents a new product
source tree from driving a stale previously configured controller. New workspaces
also retain that complete source-lock identity as restart authority; later semantic
admission requires the configured closure to equal the workspace admission rather
than relying only on terminal executable digests.

`libpkgsource` and `libpkgcatalog` each provide both their library and codec
dependency name. Those aliases are part of the source lock.

`libpkgobject` is part of that same pinned controller closure. Its product-use
path is different from semantic package/state authority: each bootstrap stage
owns a durable `package-objects` reservoir beside, not beneath, its private
runtime root. `pkgctl` receives that pathname as current resource availability
on start and resume; the complete controller source lock pins which provider
implementation is allowed, while canonical package state remains authority for
which exact artifact content/image was admitted.

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

The current bootstrap product composes the first managed `@foundation` root and
executes the bounded Stage-B compiler-handoff sensor already admitted by
`pkgsrc-foundation`. It does not yet promote that sensor into a construction root.
This stage remains explicitly seed-assisted: the historical seed still supplies
construction and lifecycle execution authority.

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
foundation closure, checks the final libgcc selection, and constructs/checks the
Stage-B GCC handoff:

```text
linux-api-headers -> glibc
linux-api-headers -> glibc-bootstrap -> libgcc
filesystem -> glibc <-> libgcc                       (run cohort)
filesystem + glibc(release 6, C.UTF-8) + libgcc      (@foundation)
                                           `-> check libgcc

glibc -> gmp-bootstrap -> mpfr-bootstrap -> mpc-bootstrap
   `--> binutils-bootstrap
filesystem + glibc + linux-api-headers + GMP/MPFR/MPC --build--> gcc-bootstrap
filesystem + glibc + linux-api-headers + binutils-bootstrap --check/run--> gcc-bootstrap
                                                              `-> check gcc-bootstrap
```

Dependency closure is resolved by the native package stack. Final glibc's
runtime requirement on `filesystem` is package authority for the merged-/usr
interpreter topology; `libpkgtransaction` 4.1.0 lifts that crossing requirement
across the complete glibc/libgcc runtime cohort, so the system frontend does not
encode cohort scheduling folklore. The transaction selects `run=@foundation`
with exact convergence into `main/foundation-root`,
`check=libgcc` against the same target selection, `check=gcc-bootstrap` as a
construction-only handoff witness, and the complete pkgctl
`exact-compatible-sharing` operation-policy profile. `zeppe-lin-system` owns only
that product-level profile selection; planner policy fields and their codec remain
outside this repository. The transaction does not introduce a second explicit
build/check root for the finished substrate. Construction-only graph nodes—including the arithmetic/Binutils/GCC handoff—are
retained as artifacts/evidence but are not desired installed state. The system
frontend does not order packages, synthesize a construction profile, or hand-extract
archives for application.


### Foundation stage and seed retirement

The current product result is a **seed-assisted qualified foundation root**, not a
claim that the bootstrap parent has been retired. `@foundation` names the stable
deployable substrate (`filesystem`, final `glibc`, and `libgcc`), while
construction-only recipes such as `linux-api-headers`, `glibc-bootstrap`, the
GMP/MPFR/MPC chain, `binutils-bootstrap`, and `gcc-bootstrap` remain graph
nodes/artifacts rather than desired installed state.

The main transaction converges that exact profile into a private managed target,
constructs/checks the Stage-B GCC handoff, and retains all construction artifacts
beneath the run-private runtime hierarchy. It still executes construction/lifecycle
authority from the admitted historical seed.
The S0 execution root is named independently from the managed target: its opaque
root-view identity is derived from the exact admitted seed archive plus the
product-owned execution-root layout. BUILD/CHECK and lifecycle retain that same S0
identity in distinct controller authority slots; resume supplies only current
physical root coordinates and cannot redeclare either semantic identity. Therefore
`bootstrap.manifest` records:

```text
product-model seed-assisted-stage-b-gcc-handoff
foundation-stage seed-assisted-foundation-root-qualified
construction-handoff-stage seed-assisted-gcc-handoff-qualified
foundation-operation-policy-profile exact-compatible-sharing
foundation-profile @foundation
foundation-members filesystem,glibc,libgcc
construction-handoff-subject gcc-bootstrap
seed-execution-root-view v1:sha256:<admitted-seed-root-view>
seed-retirement-qualified no
```

The Stage-B success is deliberately weaker than construction-root promotion. The
collection still publishes no `@construction` profile, and the managed foundation
root must reject all Stage-B-only payload residue. The later seed-retirement
milestone must first complete the required shell/base-tool/interpreter closure,
compose exact native construction authority, freeze that root, revoke access to
the historical seed, and successfully continue a **new** construction transaction.
Only that hostile transition may change `seed-retirement-qualified` to `yes`.
Directory presence or successful execution while S0 remains reachable is not
seed-retirement evidence.

## Workspace authority and restart

A bootstrap workspace is private durable product authority. Fresh initialization
requires the workspace path itself to be absent. The product creates that root
exclusively before any seed/snapshot/state bytes enter it, so any failure before
marker publication occurs only beneath a root the current invocation created and
may clean. Existing empty or nonempty unmarked roots are refused without mutation;
their pathname alone is not deletion authority.

At initialization it retains:

```text
exact bootstrap product-model authority
seed descriptor and verified archive identity
foundation Git revision, private snapshot and managed-root coordinate
qualification snapshot digest
complete configured controller source-lock identity
exact pkgctl path and SHA-256
exact pkgstate-init path and SHA-256
native supervisor credentials
complete build policy
opaque foundation operation-policy profile
privilege command coordinate
private seed-root coordinate
```

Command nonces and state-target identities are domain-separated from those
values. The product model and build policy contribute to the start nonce. The foundation operation
policy contributes to main transaction nonces and target/state identities but
does not contaminate the build-only seed-qualification identities. The controller
source lock is restart/admission authority only; it does not enter package target
identities or transaction nonces. Replacing either controller binary in place,
changing the configured controller closure, changing explicit build or operation
policy, changing privilege command, or substituting collection/qualification
authority fails closed.

`pkgctl --resume` remains responsible for transaction restart semantics. The
system frontend only recovers the already admitted physical/product coordinates
and repeatedly resumes when the controller reports the explicit live step bound.
It does not redeclare the foundation operation policy on resume; pkgctl must
rehydrate the retained complete policy authority admitted at start.

`bootstrap clean` is deliberately outside that semantic admission path. Cleanup
proves only that the current marker format is bound to the exact workspace path
and then destroys the workspace. It does not decode or reconstruct obsolete
product policy, controller or transaction authority. Therefore incompatible
private evidence remains unusable for resume/check while still being removable
without a compatibility decoder. A cleanup `--privilege` value is live deletion
authority, not historical supervisor authority.

## Bootstrap qualification

A terminal controller report is necessary but not sufficient to accept the
bootstrap product. `zlsystem bootstrap check` independently:

- requires successfully terminal seed qualification and mixed foundation transactions;
- verifies the seed-probe artifact retained by qualification;
- requires exactly the ten expected retained construction artifacts, including the Stage-B GCC handoff;
- re-hashes every private run archive against retained controller evidence;
- checks critical foundation and Stage-B handoff package members;
- verifies final glibc package coordinates, usable `C.UTF-8` locale authority, and
  retained `locale.alias`;
- rejects a public main-stage artifact root, verifies selected
  libc/locale/locale-alias/libgcc bytes in the managed foundation root, and rejects
  seed/build-only plus GCC/Binutils/arithmetic handoff residue;
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
