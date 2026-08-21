# Zeppe-Lin Native Toolchain Zoo — State, Architecture, Audit and Continuation Record

**Snapshot date:** 2026-08-21  
**Purpose:** durable engineering time capsule and AI/LLM restart authority  
**Input bundle:** `project-bundles.tar(20260821-012126).gz`  
**Input SHA-256:** `b8856190c5605171ceeae2e7053a36ea7003ab41d188ed77a037c2903e2e92cd`  
**Repositories inspected:** 40  
**Source modifications made by this audit:** none

> This document is intentionally written so that a future maintainer or AI can continue the work without this conversation history. It distinguishes inspected source truth, tests executed during this audit, operator context, and future recommendations. Do not collapse those evidence classes.

## 1. Evidence model

Every statement in this record should be interpreted through one of four evidence classes:

- **S — source-observed:** inspected directly in the uploaded Git bundles at the exact commits recorded below.
- **Q — audit-qualified:** executed by this audit against the extracted source. This is stronger than reading source, but narrower than a full zoo rebuild.
- **O — operator-observed context:** a result reported during the surrounding engineering session but not independently reproduced from this bundle. It is useful for locating the frontier, never a replacement for retained program evidence.
- **R — recommendation/inference:** the audit’s proposed future direction. It is not implemented merely because it appears here.

The uploaded bundles were extracted and all 40 repositories were cloned. Every clone was clean at its bundle head. This audit inspected repository history, Meson metadata, public/source documentation, controller source locks, product bootstrap code and foundation recipes. It did **not** recompile and execute every library test suite or every privileged integration suite. Therefore this document does not claim “all 40 current binaries are green” merely from past runs.

The following source-level qualifications were executed during this audit and passed:

- **Q:** `pkgsrc-foundation/.tests/contracts/foundation_boundary_test.py` → `pkgsrc-foundation:foundation-boundary: PASS`.
- **Q:** `zeppe-lin-system/tests/contracts/bootstrap_source_contract_test.py` → status 0.
- **Q:** `zeppe-lin-system/tests/contracts/seed_contract_test.py` → status 0.
- **Q:** `zeppe-lin-system/tests/bootstrap/bootstrap_model_test.py` → status 0 against its synthetic model collection.

## 2. Executive judgement

The native Zeppe-Lin package-management architecture has crossed the boundary from “library design project” into a real control system. The important semantic authorities are already separated, the controller composes them rather than replacing them, durable restart/evidence semantics are explicit, Linux execution is capability-driven, and the first system-product composer is exercising the stack against real toolchain construction.

The existential risk is therefore **no longer that the package manager lacks enough libraries**. The risk has moved upward: product composition can accidentally invent a second model while trying to interpret controller output; bootstrap policy can fossilize historical seed assumptions; convenience changes can let `pkgctl` become a semantic gravity well; and future rootfs/media work can contaminate collection authority with product policy. The next phase must consolidate boundaries at the system level, not blur the library boundaries that made the current progress possible.

The current architecture should be treated as fundamentally sound. There are 40 repositories, which is operationally expensive, but the split is mostly justified by independent ownership of semantics, codecs, projections, physical providers, execution adapters, sensors and product policy. Do **not** merge repositories merely to reduce the count. Merge only if two repositories genuinely have one authority, one lifecycle, one ABI/protocol and no independent consumer. Conversely, do not split again just because a file is large: extract only when a real new owner or reusable boundary exists.

The development frontier is now, in order:

1. reconcile the product composer with the latest foundation authority and close the current Stage-B GCC handoff acceptance path;
2. stop relying on an unversioned diagnostic report grammar as the long-term `zeppe-lin-system` ↔ `pkgctl` machine boundary;
3. derive and prove a complete seed-independent construction capability, then make S0 physically unavailable and continue a new native transaction;
4. build rootfs as ordinary explicit-profile desired-state convergence into an empty managed target, with independent feedback/qualification;
5. build install/live media as products consuming a qualified rootfs, not as dependency edges;
6. close operational trust/lifecycle concerns—signing-key authority, object/store retention and garbage collection, reconciliation UX—only when their owners and product responsibilities are explicit.

## 3. Project doctrine: invariants a future AI must not “simplify” away

These are the rules that make the architecture cybernetic rather than archaeological:

1. **Authority is owned.** Each semantic fact has one owner. An adapter may translate or realize authority; it may not silently redefine it.
2. **Identity is not the body.** A digest, pathname, release coordinate or journal identity may select evidence, but it is not enough to fabricate the semantic value that produced it. Rehydrate through the owner codec/body when historical semantics are required.
3. **Retained evidence describes admitted history, not present reality.** Do not reopen stale artifacts or filesystem residue and call that “truth.” Present external conditions require an observation path owned for that purpose.
4. **Decode/rehydrate, derive/project, realize, observe are different verbs.** Use them literally. “Reconstruct truth” is a boundary smell.
5. **Catalog truth and installed-state truth are different domains.** Available packages are not installed packages; neither may be inferred from the other.
6. **Resolver authority selects; transaction authority orders.** `libpkgresolve` owns deterministic selection/closure. `libpkgtransaction` owns cross-package operation relationships. Neither executes work.
7. **BUILD and CHECK are phase-local authorities.** Build-only inputs reach BUILD. Check-only inputs reach CHECK. CHECK consumes the exact retained successful build/package/source authority it is defined against and realizes its own resources; it does not rediscover a “world.”
8. **Execution is not package semantics.** `libpkgexec` describes executable capability/evidence. Linux isolation is a provider. Package build/check/lifecycle adapters project package semantics into that execution domain.
9. **Planning is pure.** `libpkgplan` decides one package mutation from immutable facts. No filesystem I/O, locks, execution or state publication belong there.
10. **Application semantics and physical mutation are separate.** `libpkgapply` owns accepted-plan application semantics and restart evidence. `libpkgapply-posix` owns concrete target mechanics and byte stores.
11. **Canonical state publication follows authoritative application.** Publication is a separate transition and must remain lease/precondition bound. Visible bytes alone do not authorize “completed.”
12. **The controller coordinates; it does not become another semantic model.** A `pkgctl` session proves exact authorities were composed and progressed. Prefer delegation to existing owners over controller-owned duplicate types/codecs.
13. **Product composition is not package semantics.** `zeppe-lin-system` owns pins, seed acquisition, workspaces, overlays, qualification and final product assembly. It must not reproduce resolver/transaction/build/apply/state policy.
14. **Sensors are feedback, not authority.** Audit/impact/diff results may inform humans or explicit policy, but observation does not retroactively become desired-state authority.
15. **Fail closed on incompatible private evidence.** The native toolchain is still pre-first-real-distribution-transaction. Do not accumulate compatibility ghosts for private formats merely to preserve development archaeology.
16. **Capability drives bootstrap membership.** Do not create bootstrap packages because LFS, CRUX, an old `core` set or intuition says they “belong.” Add a construction edge only when a sealed post-seed workload proves the capability is required.
17. **Profiles name desired membership, never execution order.** Dependency/transaction authorities derive ordering. Product-specific overlays or media preparation do not belong in package dependency edges.

## 4. Ecosystem map

The system can be understood as a chain of authorities with side planes rather than as one package-manager call graph:

```text
collection files/YAML
      |  libpkgsource-yaml + libpkgcatalog-acquire
      v
sealed source authority -----> immutable catalog authority
      |                               |
      |                               +---- catalog + canonical state + goals/policy
      |                                                   |
      |                                                   v
      |                                            libpkgresolve
      |                                                   | exact selection
      |                                                   v
      |                                         libpkgtransaction
      |                                                   | operation graph
      |          +----------------------------------------+-------------------+
      |          |                                                            |
      v          v                                                            v
 libpkgfetch -> libpkgsource-exec -> libpkgbuild -> libpkgbuild-exec -> image authority
                                                       |              |
                                                       |              +-> libpkgobject resource plane
                                                       v
                                                 libpkgcheck
                                                       |
                                                       v
                                                libpkgcheck-exec

 source/state/build/image projections -> libpkgplan -> libpkgapply -> libpkgapply-posix
                                                     |              |
                                                     |              +-> rejected/completed bytes
                                                     v
                                               libpkgstate-apply
                                                     |
                                                     v
                                            canonical libpkgstate

 side planes:
   completed application -> libpkgreconcile-* -> durable rejected-object inventory
   canonical object/state -> libpkgaudit / libpkgimpact -> independent observations

 pkgctl composes the owner boundaries above.
 zeppe-lin-system pins a controller closure and composes products around it.
```

This graph is more important than any individual CLI command. A future feature should enter at the owner whose authority it changes. If no existing owner fits, define the missing semantic boundary before adding a `pkgctl` option.

## 5. Repository ledger — exact 2026-08-21 bundle heads

`Product closure` means inclusion in the exact `zeppe-lin-system/subprojects/*.wrap` source lock, not necessarily runtime production linkage. The system lock intentionally contains qualification/test dependencies as well. `outside` means the repository is in the zoo bundle but not in that controller source lock. `input` is product data authority rather than a Meson controller dependency.

| Repository | Version | Exact head | Tag state | Class | Product closure | Role / current note |
|---|---:|---|---|---|---|---|
| `liblinediff` | `0.2.1` | `5d4a34afcf9a5d77c98dc6f56f6009502ca97635` | ahead 3 | utility | outside | Exact byte-line differencing/rendering utility; independent diagnostic support. |
| `libpkgapply` | `4.0.1` | `36aa530ae07dc1c2a7f1ee999a7626977fc8a53e` | exact v4.0.1 | semantic core | wrapped | Semantic application authority for one accepted package plan: lease-bound precondition revalidation, effect schedule, owner journal, restart/recovery and completed-application evidence. |
| `libpkgapply-exec` | `3.0.2` | `efbae2415b93ef001dad8aa8cdd34365cadd304b` | exact v3.0.2 | execution adapter | wrapped | Lifecycle execution adapter from application semantics to libpkgexec. |
| `libpkgapply-posix` | `4.0.0` | `61b0595e11edb4c072e3f05aa8672f3e4c8569e5` | exact v4.0.0 | POSIX provider | wrapped | Descriptor-anchored POSIX provider for target observation/mutation, staging, capture, rejected/completed objects and owner application-journal storage. |
| `libpkgaudit` | `0.1.0` | `0a3e1603e801519006b57257f17e39e0f632334f` | exact v0.1.0 | sensor | wrapped | Independent filesystem drift sensor comparing immutable object inventory with typed filesystem observations. |
| `libpkgbuild` | `3.0.3` | `8dc3f17ec152330e98391eb747a377e9c2bb6db8` | exact v3.0.3 | semantic core | wrapped | Pure logical build-request/outcome authority bound to an exact resolver selection and phase-local BUILD/CHECK inputs. |
| `libpkgbuild-exec` | `3.3.1` | `b85bcf580ece9969c687d67b92dcbe239e298a87` | exact v3.3.1 | execution adapter | wrapped | Concrete build realization through libpkgexec; source workspace expansion and sealed build result/artifact production. |
| `libpkgbuild-image` | `1.0.1` | `93bf644c107bd46a5b9da4b56d51e06f3becc649` | exact v1.0.1 | binding adapter | wrapped | Pure admission/binding between a successful build payload and an independently inspected package image. |
| `libpkgbuild-plan` | `1.1.0` | `912de8c3b4b3fa692f493e1833da32b4635bf248` | exact v1.1.0 | projection adapter | wrapped | Projection from admitted build/image authority into planner artifact facts and bindings. |
| `libpkgcatalog` | `4.0.0` | `f7c3f5683d7c9c0a5c0f7774ab626db8d4e93350` | exact v4.0.0 | semantic core | wrapped | Immutable available-package universe with collection precedence, effective/shadowed candidates and canonical codec. |
| `libpkgcatalog-acquire` | `4.0.0` | `7b65017902e531fd8f29576d0a4343aa68b0cd9a` | exact v4.0.0 | acquisition adapter | wrapped | Mutable filesystem/YAML acquisition adapter that produces a sealed catalog. |
| `libpkgcheck` | `0.3.0` | `0d6b22a79ae1706357f726e34a99870848a09300` | ahead 1 | semantic core | wrapped | Pure CHECK request/result semantic authority after a corresponding successful build. |
| `libpkgcheck-exec` | `0.9.0` | `a265a8dfd1e96a96632184041713ab3fca4a8e3a` | exact v0.9.0 | execution adapter | wrapped | Concrete CHECK execution adapter with exact check resources/environment through libpkgexec. |
| `libpkgexec` | `2.2.0` | `aa32726045c3ad7325a13c8ca4bb4cbefdbcd254` | exact v2.2.0 | semantic core | wrapped | Backend-neutral execution semantic contract: process request, resources, cancellation and capability evidence. |
| `libpkgexec-linux` | `0.7.1` | `54e060948f60e411ac2b5ffeb7e4c0165f7cc140` | exact v0.7.1 | Linux provider | wrapped | Linux execution backend providing isolated root/resource views, namespace/mount policy, rlimits, pidfd cancellation and truthful capability rejection. |
| `libpkgfetch` | `3.0.0` | `b01b47ed20fc2dba6c34cca48f0ba35e2a0d9f8b` | ahead 1 | semantic/service | wrapped | Digest-verified source acquisition/materialization and durable fetch receipt; does not unpack archives. |
| `libpkgimage` | `0.4.1` | `179f14759b48f006dc922579314d56637f0522a8` | ahead 1 | semantic core | wrapped | Exact package archive inspection/normalization into package-image authority and replay data; no installation or policy. |
| `libpkgimage-exec` | `0.1.0` | `6dd401fc70b78d824be21dd5c9ea515cb64f0c70` | ahead 1 | execution resource provider | wrapped | Fresh private checked-package tree realization from an exact archive + normalized image for execution consumers. |
| `libpkgimpact` | `0.3.0` | `62a85dad2bd6dc960df647529e79d3790e63f926` | exact v0.3.0 | sensor | outside | ELF linkage-impact sensor / revdep-style diagnostic; not package-selection authority. |
| `libpkgobject` | `0.1.0` | `022917659cb7d042d4a5b8814629d208235f4977` | exact v0.1.0 | resource service | wrapped | Durable reusable exact package-archive byte store keyed by complete archive digest; no package/state semantics. |
| `libpkgplan` | `0.3.1` | `406dc58d44854b6a3363c77b4087e953a45ad395` | ahead 1 | semantic core | wrapped | Pure deterministic one-package install/upgrade/remove plan or refusal from immutable facts; no I/O or execution. |
| `libpkgreconcile` | `0.3.0` | `ac9b056dd638512c912a1e30ac0c5c91dc97f1bd` | exact v0.3.0 | semantic side-plane | wrapped | Semantic pending/resolved rejected-object reconciliation values using provider-qualified opaque locators. |
| `libpkgreconcile-apply` | `0.1.2` | `e5d03cd518b25d01a462aaf411980cf02af0a4f9` | exact v0.1.2 | projection adapter | wrapped | Projection from completed application rejected consequences into package-independent pending reconciliation. |
| `libpkgreconcile-apply-posix` | `0.1.2` | `1cf029d8f3626bb3544b0f14092f5806d92a0f5b` | exact v0.1.2 | POSIX composition adapter | wrapped | Composition of apply-posix rejected bytes, semantic reconciliation projection and reconcile-posix durable publication. |
| `libpkgreconcile-posix` | `0.1.0` | `cb7f2dac2e6eaa0767f6458d5d7dacd448d6c9fb` | exact v0.1.0 | POSIX provider | wrapped | Durable target-bound reconciliation inventory generation store with anti-resurrection semantics. |
| `libpkgresolve` | `4.0.0` | `fe64f261919f79abf5b93a8167fccd54432d0a19` | ahead 1 | semantic core | wrapped | Selection authority: deterministic closure and witnesses from catalog, installed state, goals, architecture and resolution policy. |
| `libpkgsource` | `4.1.0` | `c29bcb4ed78fd8ff0bedc0fe0f14185b723735db` | exact v4.1.0 | semantic core | wrapped | Parser-neutral semantic package-source authority and canonical source codec; declarations become sealed source snapshots. |
| `libpkgsource-exec` | `0.1.0` | `6467b64a44bc4187b3a38d8d4ce8e8f92b26b951` | ahead 1 | execution adapter | wrapped | Phase-neutral realization of admitted source objects into an exact read-only execution tree; archive objects remain archive objects. |
| `libpkgsource-plan` | `2.0.0` | `49702392b916e38e610c6c4097913a3491b13acd` | exact v2.0.0 | projection adapter | wrapped | Projection from sealed source authority into planner candidate facts. |
| `libpkgsource-yaml` | `2.0.0` | `5e8c71042cbad072140af6ba47c4820aaf3782be` | exact v2.0.0 | syntax adapter | wrapped | Strict bounded YAML grammar frontend producing source declarations; owns syntax, not semantic discovery/sealing. |
| `libpkgstate` | `3.1.0` | `94e59e64b842a396bf5bb9eacc0f262c1e266c5f` | ahead 1 | semantic core | wrapped | Canonical durable installed truth for one exact target, complete generations only, stale-safe compare-and-publish and codecs. |
| `libpkgstate-apply` | `3.1.3` | `6af8af6547612e096e07acdb27daaeb3ee530711` | exact v3.1.3 | projection adapter | wrapped | Projection from lease-bound state + completed application into canonical state-publication request. |
| `libpkgstate-build` | `3.1.0` | `9ce185fe576a47083aa025c48190a394c8583322` | exact v3.1.0 | projection adapter | wrapped | Projection of admitted build/image authority into installed-state build provenance. |
| `libpkgstate-plan` | `3.0.0` | `abbba3eae47b5d0f201d4e46f9f212163eaf7b6d` | ahead 2 | projection adapter | wrapped | Projection of canonical installed state into planner facts. |
| `libpkgstate-posix` | `3.1.0` | `908ba941d9e60d99b4e6b631cec4b7bc4cb4ecfb` | exact v3.1.0 | POSIX provider | wrapped | Descriptor-anchored immutable-generation POSIX state provider plus explicit state initialization/inspection tools. |
| `libpkgstate-source` | `4.0.0` | `3150bc302b13bbdcc2d4437d7fb0c775078c4e13` | exact v4.0.0 | projection adapter | wrapped | Projection of sealed package-source authority into installed-state source records. |
| `libpkgtransaction` | `4.1.0` | `5e9b78ec702a96ee477c8d342824d9c6b5253022` | exact v4.1.0 | semantic core | wrapped | Cross-package operation graph/partial-order authority for build/check/install/upgrade/retain/remove/lifecycle, including explicit reciprocal runtime cohorts. |
| `pkgctl` | `0.43.0` | `ef52450096dd5aec88897fc34ea5c70f609e9a52` | exact v0.43.0 | controller | wrapped | Native controller: sequences owner authorities and durable progression; controller session is composition evidence, not a parallel package model. |
| `pkgsrc-foundation` | `n/a` | `d6d4451dfaaaf9e57ff1d62a4c215c61685e2626` | untagged | collection/product input | input (separately pinned) | Product input collection for the seed-to-native transition: stable ABI/runtime substrate plus temporary construction authority. |
| `zeppe-lin-system` | `0.1.0` | `7238707c5f6caaf4247c19c7c1c8e14e0d6a3704` | untagged | product composer | product root | Host-side system-product composer: pins an exact controller closure and presents exact product authority for bootstrap, later rootfs and media. |

All repository source files sampled for SPDX declarations use `GPL-3.0-or-later`; package recipes correctly retain their upstream package licensing separately. Do not confuse tool source licensing with licenses of constructed packages.

### 5.1 Unreleased/post-tag deltas

Most library heads are exact release tags. The following heads intentionally contain development after the latest tag:

- `liblinediff` — 3 commit(s) beyond `v0.2.1`: header/doc modernization; header tests refactored to template; 0.2.2 unreleased changes documented.
- `libpkgcheck` — 1 commit(s) beyond `v0.3.0`: documentation separates semantic check binding from resource realization.
- `libpkgfetch` — 1 commit(s) beyond `v3.0.0`: documentation names phase-neutral source realization.
- `libpkgimage` — 1 commit(s) beyond `v0.4.1`: documentation authority normalization.
- `libpkgimage-exec` — 1 commit(s) beyond `v0.1.0`: Meson subproject dependency publication.
- `libpkgplan` — 1 commit(s) beyond `v0.3.1`: planner documentation authority normalization.
- `libpkgresolve` — 1 commit(s) beyond `v4.0.0`: additional adversarial reciprocal-runtime-cohort resolution test.
- `libpkgsource-exec` — 1 commit(s) beyond `v0.1.0`: Meson subproject dependency publication.
- `libpkgstate` — 1 commit(s) beyond `v3.1.0`: state documentation authority normalization.
- `libpkgstate-plan` — 2 commit(s) beyond `v3.0.0`: Meson/style normalization and planner-state authority documentation.

This matters for future release work: `zeppe-lin-system` pins those exact post-tag commits where they are in its closure. “Build from released versions” and “build this product source lock” are therefore not identical statements.

## 6. Subsystem audit

### 6.1 Source, catalog and acquisition

**State: structurally mature.** `libpkgsource` is the parser-neutral semantic source owner; its YAML grammar is isolated in `libpkgsource-yaml`; catalog semantics live in `libpkgcatalog`; mutable filesystem/YAML acquisition lives in `libpkgcatalog-acquire`; source-to-planner projection and execution realization are separately owned by `libpkgsource-plan` and `libpkgsource-exec`. This is the correct shape: syntax, semantic snapshot, available-universe semantics, planner facts and execution resources have different volatility and should not be collapsed.

The critical future invariant is that no product/controller code begins reparsing recipe YAML, walking collections or interpreting source objects ad hoc. If rootfs/system work needs new collection metadata, extend the source/catalog authority explicitly and propagate it through projections. Do not create a “system shortcut” parser.

### 6.2 Canonical state and projections

**State: mature semantic core with intentionally explicit adapters.** `libpkgstate` owns complete canonical installed generations for one exact target and stale-safe publication. `libpkgstate-posix` owns physical immutable-generation storage. Source/build/planner/application bindings are separate projection repositories. This split prevents the old package-manager pattern where a filesystem database becomes source, observation, planner input and transaction log simultaneously.

Current source uses the canonical `libpkgstate-generation-v1` protocol. Historical migration/history documents contain older development lineage; treat those as history, not as evidence that the current provider must accept old private bytes. Incompatible private evidence should continue to fail closed unless an actual public compatibility obligation is deliberately created.

### 6.3 Resolution and transaction

**State: strong.** `libpkgresolve` owns deterministic selection, dependency closure and witnesses. Its current head adds an adversarial test around reciprocal runtime cohorts. `libpkgtransaction` 4.1.0 lifts runtime requirements over explicit reciprocal cohorts and owns cross-package operation relationships. This is a substantial architectural achievement: cycles are not hidden by incidental build order and “transaction” does not mean an impossible claim of transaction-wide filesystem atomicity.

Do not move dependency sorting or cohort interpretation into `pkgctl`, bootstrap scripts or profiles. A profile names desired members. Resolver/transaction authority determines the consequence.

### 6.4 Build, source realization, fetch and package image

**State: strong and recently hardened by real bootstrap pressure.** `libpkgbuild` defines the logical build request/outcome from exact resolver selection. `libpkgfetch` admits source bytes. `libpkgsource-exec` realizes exact source objects. `libpkgbuild-exec` executes through `libpkgexec`, including exact timestamp/build policy. `libpkgimage` independently interprets archive contents. `libpkgbuild-image` binds successful build payload to inspected image authority. `libpkgobject` stores exact reusable archive bytes without pretending they are installed/package-state truth.

The key vocabulary correction is already present in current docs: CHECK does not “reconstruct truth.” It consumes retained owner authority and realizes a fresh phase-local resource world. That wording should remain enforced in documentation and code review because “reconstruction” invites stale-evidence seances.

### 6.5 CHECK

**State: semantically separated and operationally real.** `libpkgcheck` is pure request/result authority; `libpkgcheck-exec` realizes the exact CHECK environment through execution semantics. The build/check split is now important enough that foundation recipes carry independent `build`, `check` and `run` requirement sets. Do not regress to making CHECK inherit every BUILD input or ambient target path. If a check needs an executable/library/resource, it must be named by the proper phase authority.

### 6.6 Execution

**State: advanced, capability-bounded, truthful.** `libpkgexec` is backend-neutral. `libpkgexec-linux` provides the current Linux backend with isolated root/resource views, mount-namespace policy, descriptor/open-tree/mount-setattr work, rlimits and pidfd-based cancellation. Unsupported capabilities reject rather than silently weaken execution.

Current intentional capability gaps include user/PID namespaces, Landlock, cgroup-backed controls, CPU-millisecond accounting and per-execution process-count enforcement. These are **not automatically defects**. Add them only when a product/build/check policy needs a guarantee that cannot be truthfully expressed today. The correct failure mode before then is capability refusal, not fake isolation.

### 6.7 Planning, application and publication

**State: mature semantic split; generation-4 application work is a major closure.** `libpkgplan` remains pure. `libpkgapply` generation 4 owns the semantic application progression and append-only owner journal. `libpkgapply-posix` owns physical mutation and stores. `libpkgapply-exec` owns lifecycle execution. `libpkgstate-apply` projects completed application + lease-bound state into publication authority.

One documentation defect was found: current `libpkgapply/DESIGN.md` still says `pkgman acquires outer target lease` and `pkgman selects finalization or recovery`. That is a vocabulary fossil in an otherwise current design document. The native owner is the controller composition (`pkgctl`), and this should be corrected so a future AI does not infer that legacy `pkgman` remains architectural authority.

### 6.8 Reconciliation side plane

**State: semantically implemented and qualified, intentionally not a production `pkgctl` responsibility.** The `libpkgreconcile*` family gives rejected-object consequences a package-independent semantic/persistence path. `pkgctl/tests` directly composes the family for package-pipeline qualification, while `pkgctl/MAINTAINING.md` explicitly says this seam may remain test-only until the controller has a real orchestration responsibility. This is correct restraint.

Do not add a pass-through `pkgctl reconcile` layer merely to make the graph look integrated. Integrate the side plane only when an actual product/user workflow needs to enumerate, resolve or retain rejected objects. At that time the controller should compose the existing owners rather than duplicate their model.

### 6.9 Sensors and utilities

`libpkgaudit`, `libpkgimpact` and `liblinediff` are deliberately not all in the normal product/controller path. `libpkgaudit` is included in the system controller source closure because qualification uses it; `libpkgimpact` and `liblinediff` are outside that source lock. This is healthy. Observability tools should be independently reusable and should not be promoted into state/resolution authority merely because their output is useful.

For rootfs qualification, `libpkgaudit` is the obvious independent feedback path after convergence. `libpkgimpact` may later support diagnostics or explicit policy around ABI/linkage consequences, but it should not silently become dependency truth.

### 6.10 `pkgctl` controller

**State: advanced pre-1.0 controller, heavily qualified, now the largest concentration of complexity.** The current release is `0.43.0`; the bundle head is exactly `v0.43.0`. Meson declares 117 tests across unit/contract/integration/privileged surfaces. The current command surface documented by the repository includes catalog/resolve/transaction/run/build and read-only inspection commands; rootfs remains a product pattern, not a `pkgctl rootfs` verb.

Release progression has closed several formerly dangerous concerns: durable run/effect progression, exact lifecycle authority, lease loss, application journal ownership, execution-root identity, source/build/check realization, and in 0.43 an installed-package resource side plane through `libpkgobject` + `libpkgimage-exec`. The controller is now capable enough that the primary maintenance rule must be **resist authority gravity**. New features should first ask “which existing owner decides this?” rather than adding another durable controller record.

A particularly important current design statement is explicit in `pkgctl/DESIGN.md`: deterministic line-oriented reports expose identities but **are not authority themselves**, and a machine protocol requires a separate versioned contract. That statement becomes directly relevant at the system-product boundary; see §9.2.

The controller's current declared production/build dependency ranges are another useful compatibility snapshot. They are not a substitute for the exact product source lock, but they show the ABI generations expected by `pkgctl 0.43.0`:

| Dependency | Accepted range |
|---|---|
| `libpkgsource` | `>=4.1.0 <5.0.0` |
| `libpkgsource-yaml` | `>=2.0.0 <3.0.0` |
| `libpkgcatalog` / `libpkgcatalog-codec` / `libpkgcatalog-acquire` | `>=4.0.0 <5.0.0` |
| `libpkgstate` | `>=3.1.0 <4.0.0` |
| `libpkgstate-posix` / `libpkgstate-plan` | `>=3.0.0 <4.0.0` |
| `libpkgresolve` | `>=4.0.0 <5.0.0` |
| `libpkgfetch` | `>=3.0.0 <4.0.0` |
| `libpkgbuild` | `>=3.0.3 <4.0.0` |
| `libpkgbuild-exec` | `>=3.3.1 <4.0.0` |
| `libpkgbuild-image` | `>=1.0.1 <2.0.0` |
| `libpkgsource-plan` | `>=2.0.0 <3.0.0` |
| `libpkgbuild-plan` | `>=1.1.0 <2.0.0` |
| `libpkgimage` | `>=0.4.0 <1.0.0` |
| `libpkgplan` | `>=0.3.0 <1.0.0` |
| `libpkgexec` | `>=2.2.0 <3.0.0` |
| `libpkgexec-linux` | `>=0.7.1 <1.0.0` |
| `libpkgapply` | `>=4.0.1 <5.0.0` |
| `libpkgapply-posix` | `>=4.0.0 <5.0.0` |
| `libpkgapply-exec` | `>=3.0.2 <4.0.0` |
| `libpkgstate-apply` | `>=3.1.3 <4.0.0` |
| `libpkgtransaction` | `>=4.1.0 <5.0.0` |
| `libpkgcheck` | `>=0.3.0 <1.0.0` |
| `libpkgcheck-exec` | `>=0.9.0 <1.0.0` |
| `libpkgsource-exec` | `>=0.1.0 <1.0.0` |
| `libpkgimage-exec` | `>=0.1.0 <1.0.0` |
| `libpkgobject` | `>=0.1.0 <1.0.0` |

`libpkgreconcile*` is absent from the production dependency list and appears in `pkgctl/tests` only, matching the documented side-plane boundary. `libpkgaudit` is also not a controller-core semantic dependency; it is used in qualification paths.

### 6.11 `pkgsrc-foundation`

**State: active seed-retirement construction frontier, not a general base collection.** The collection owns the bounded transition from historical seed authority to stable native target authority. It deliberately contains both stable deployable foundation members and temporary construction recipes, while refusing to confuse recipe existence with desired-state membership.

Current `@foundation` membership is exactly:

- `filesystem`
- `glibc`
- `libgcc`

There is intentionally **no `@construction` profile yet**. The repository says the present recipes do not constitute a complete seed-independent construction root. That absence is an architectural assertion, not an unfinished YAML chore.

The current bundle HEAD `d6d4451dfaaaf9e57ff1d62a4c215c61685e2626` advances `gcc-bootstrap` to `16.1.0-5` and seals GCC 16 static `libatomic`/`libatomic_asneeded` authority rather than suppressing the compiler’s implicit atomic-link capability. This is the latest foundation-source truth in the uploaded zoo.

Current package coordinates and direct requirements at that head are:

| Package | Coordinate | BUILD | CHECK | RUN |
|---|---|---|---|---|
| `binutils-bootstrap` | `2.44-1` | — | — | glibc |
| `filesystem` | `1.0.0-1` | — | — | — |
| `gcc-bootstrap` | `16.1.0-5` | filesystem, glibc, linux-api-headers, gmp-bootstrap, mpfr-bootstrap, mpc-bootstrap | filesystem, glibc, linux-api-headers, binutils-bootstrap | filesystem, glibc, linux-api-headers, binutils-bootstrap |
| `glibc` | `2.44-6` | linux-api-headers | — | filesystem, libgcc |
| `glibc-bootstrap` | `2.44-1` | linux-api-headers | — | — |
| `gmp-bootstrap` | `6.3.0-1` | — | — | glibc |
| `libgcc` | `16.1.0-1` | glibc-bootstrap | — | glibc |
| `linux-api-headers` | `7.1.8-1` | — | — | — |
| `mpc-bootstrap` | `1.4.1-1` | gmp-bootstrap, mpfr-bootstrap | gmp-bootstrap, mpfr-bootstrap | glibc, gmp-bootstrap, mpfr-bootstrap |
| `mpfr-bootstrap` | `4.2.2-1` | gmp-bootstrap | gmp-bootstrap | glibc, gmp-bootstrap |

The construction shape is therefore intentionally explicit: Linux UAPI → bootstrap/final libc; `glibc <-> libgcc` is a final runtime cohort; GMP→MPFR→MPC and Binutils provide bounded compiler construction authority; Stage-B `gcc-bootstrap` consumes exact BUILD inputs and separate CHECK/RUN inputs. Temporary arithmetic/binutils/GCC recipes are not promoted into `@foundation`.

### 6.12 `zeppe-lin-system`

**State: early but real product composer.** It builds one exact native controller from pinned Meson subprojects, then uses that controller to construct products. The current implemented products are `controller` and `bootstrap`; `rootfs`, `iso-install` and `iso-live` are explicitly future.

The controller source closure is strong: every committed wrap revision in this bundle matches the corresponding uploaded repository HEAD. `force_fallback_for` prevents an installed `libpkg*` from silently replacing wrapped source authority. `pkgsrc-foundation` is correctly separate product input authority rather than a Meson code dependency.

The bootstrap product is deliberately **seed-assisted**. Its current model records:

- `foundation-stage seed-assisted-foundation-root-qualified`
- `construction-handoff-stage seed-assisted-gcc-handoff-qualified`
- `seed-retirement-qualified no`

It downloads or accepts exact descriptor-matching historical seed bytes, snapshots the exact foundation revision, initializes private native state stores, qualifies the seed with a product-only probe, converges the stable foundation target, constructs/checks the bounded GCC handoff and emits a versioned bootstrap manifest. The detached signature is retained and hash-qualified, but the product explicitly does **not** claim cryptographic publication trust because no signing-key authority has been specified yet.

## 7. Exact system source-lock state

The `zeppe-lin-system` controller source lock contains 36 exact wrapped repositories. Every wrap SHA matches the corresponding uploaded bundle HEAD:

| Wrapped project | Revision |
|---|---|
| `libpkgapply` | `36aa530ae07dc1c2a7f1ee999a7626977fc8a53e` |
| `libpkgapply-exec` | `efbae2415b93ef001dad8aa8cdd34365cadd304b` |
| `libpkgapply-posix` | `61b0595e11edb4c072e3f05aa8672f3e4c8569e5` |
| `libpkgaudit` | `0a3e1603e801519006b57257f17e39e0f632334f` |
| `libpkgbuild` | `8dc3f17ec152330e98391eb747a377e9c2bb6db8` |
| `libpkgbuild-exec` | `b85bcf580ece9969c687d67b92dcbe239e298a87` |
| `libpkgbuild-image` | `93bf644c107bd46a5b9da4b56d51e06f3becc649` |
| `libpkgbuild-plan` | `912de8c3b4b3fa692f493e1833da32b4635bf248` |
| `libpkgcatalog` | `f7c3f5683d7c9c0a5c0f7774ab626db8d4e93350` |
| `libpkgcatalog-acquire` | `7b65017902e531fd8f29576d0a4343aa68b0cd9a` |
| `libpkgcheck` | `0d6b22a79ae1706357f726e34a99870848a09300` |
| `libpkgcheck-exec` | `a265a8dfd1e96a96632184041713ab3fca4a8e3a` |
| `libpkgexec` | `aa32726045c3ad7325a13c8ca4bb4cbefdbcd254` |
| `libpkgexec-linux` | `54e060948f60e411ac2b5ffeb7e4c0165f7cc140` |
| `libpkgfetch` | `b01b47ed20fc2dba6c34cca48f0ba35e2a0d9f8b` |
| `libpkgimage` | `179f14759b48f006dc922579314d56637f0522a8` |
| `libpkgimage-exec` | `6dd401fc70b78d824be21dd5c9ea515cb64f0c70` |
| `libpkgobject` | `022917659cb7d042d4a5b8814629d208235f4977` |
| `libpkgplan` | `406dc58d44854b6a3363c77b4087e953a45ad395` |
| `libpkgreconcile` | `ac9b056dd638512c912a1e30ac0c5c91dc97f1bd` |
| `libpkgreconcile-apply` | `e5d03cd518b25d01a462aaf411980cf02af0a4f9` |
| `libpkgreconcile-apply-posix` | `1cf029d8f3626bb3544b0f14092f5806d92a0f5b` |
| `libpkgreconcile-posix` | `cb7f2dac2e6eaa0767f6458d5d7dacd448d6c9fb` |
| `libpkgresolve` | `fe64f261919f79abf5b93a8167fccd54432d0a19` |
| `libpkgsource` | `c29bcb4ed78fd8ff0bedc0fe0f14185b723735db` |
| `libpkgsource-exec` | `6467b64a44bc4187b3a38d8d4ce8e8f92b26b951` |
| `libpkgsource-plan` | `49702392b916e38e610c6c4097913a3491b13acd` |
| `libpkgsource-yaml` | `5e8c71042cbad072140af6ba47c4820aaf3782be` |
| `libpkgstate` | `94e59e64b842a396bf5bb9eacc0f262c1e266c5f` |
| `libpkgstate-apply` | `6af8af6547612e096e07acdb27daaeb3ee530711` |
| `libpkgstate-build` | `9ce185fe576a47083aa025c48190a394c8583322` |
| `libpkgstate-plan` | `abbba3eae47b5d0f201d4e46f9f212163eaf7b6d` |
| `libpkgstate-posix` | `908ba941d9e60d99b4e6b631cec4b7bc4cb4ecfb` |
| `libpkgstate-source` | `3150bc302b13bbdcc2d4437d7fb0c775078c4e13` |
| `libpkgtransaction` | `5e9b78ec702a96ee477c8d342824d9c6b5253022` |
| `pkgctl` | `ef52450096dd5aec88897fc34ea5c70f609e9a52` |

The two zoo repositories not present in this controller lock are `liblinediff` and `libpkgimpact`. `pkgsrc-foundation` is not supposed to appear here: it is separately pinned product data authority. `zeppe-lin-system` itself is the product root.

## 8. Current product inconsistency: foundation HEAD versus composer pin

This is the clearest concrete current-state issue in the uploaded snapshot.

**S:** `zeppe-lin-system/collections/foundation.ini` pins:

```text
df1c1b01827858845c3d9111edd8c8318febbe5c
```

**S:** the uploaded `pkgsrc-foundation` HEAD is:

```text
d6d4451dfaaaf9e57ff1d62a4c215c61685e2626
```

The latter is one commit ahead and changes `gcc-bootstrap` from release 4 to release 5, adding the static libatomic handoff authority/checks. Meanwhile **S:** `zeppe-lin-system/zlsystem/bootstrap.py` still expects `gcc-bootstrap 16.1.0-4`. Thus the bundle contains a **next foundation source** and a **current product composer that has not yet admitted it**.

This is not necessarily repository corruption: exact pinning is doing its job. It is, however, the first task for continuation. A future AI must not “solve” it by allowing arbitrary clean foundation HEADs or weakening coordinate checks. The product must deliberately advance its foundation descriptor and exact expected coordinate together, then qualify that new product source lock.

Because the current zlsystem source tests are written against its committed pin/model, they pass in this audit. That proves internal consistency of the **old pin**, not qualification of the d6 foundation head under the product composer.

## 9. Current frontier and risk register

### 9.1 P0 — advance product authority to the libatomic-fixed foundation revision

**Problem:** the product composer is pinned to `df1c1b0…` / `gcc-bootstrap-4`; the zoo’s foundation head is `d6d4451…` / `gcc-bootstrap-5`.

**Required resolution:** deliberately update the product collection pin and exact expected GCC bootstrap coordinate, then run product qualification from a workspace admitted under that new product authority. Do not reuse a workspace whose retained marker/source lock names the previous foundation authority.

**Acceptance:** all zlsystem source/model tests pass; fresh bootstrap reaches a terminal successful transaction; `bootstrap check` independently validates the exact artifact set/coordinates/digests, target handoff invariants and manifest; no construction-only package is mistaken for `@foundation`; seed-retirement remains explicitly `no` at this milestone.

### 9.2 P0 — stabilize the system ↔ controller machine-result boundary

**S:** `pkgctl/DESIGN.md` says reports are deterministic line-oriented diagnostics, are not authority themselves, and that a machine protocol needs a separate versioned contract.

**S:** `zeppe-lin-system` currently parses the diagnostic report and builds a package-name keyed artifact map. `_artifact_map()` throws if a package name appears twice. This is a real abstraction tension: a product composer now depends on report grammar and assumes one reported construction artifact per package name.

**O, not independently requalified here:** the surrounding bootstrap work reported a Stage-B GCC transaction that had succeeded far enough for product acceptance to encounter a duplicate artifact-name report. Treat this only as a frontier clue until the exact retained report is captured again.

The immediate fix must begin by examining the exact duplicate records—release identity, build-result identity, artifact digest/path, operation/dispatch context—and deciding **which owner is wrong**:

- if `pkgctl` is incorrectly emitting the same authoritative construction result more than once, fix the controller report/progression source;
- if multiple records are semantically legitimate (for example distinct constructions/attempts that share a package name), then `zeppe-lin-system` must select/bind them by the actual authoritative identity required by its expected artifact, not by “last package name wins”;
- never silence the error by overwriting a dictionary entry, deduplicating by pathname, or choosing the newest record. That would create product truth from presentation order.

**Longer-term R:** introduce a separate, versioned machine result contract for product consumers. This can be a structured `pkgctl` output mode or another deliberately versioned boundary, but it must expose exact typed construction-result identities and terminal state without promoting the presentation bytes themselves into package authority. `zeppe-lin-system` is source-lock pinned today, so the current parser is acceptable as a co-versioned implementation detail; it should not become the permanent inter-product protocol.

### 9.3 P1 — historical seed is still construction authority

The bootstrap has not proved seed retirement. The current manifest truthfully records `seed-retirement-qualified no`, and `pkgsrc-foundation` refuses to publish `@construction`. This is the main architectural milestone after Stage-B handoff: make native construction self-sufficient enough that S0 can become physically inaccessible and a **new** transaction still constructs a sealed package.

The important word is “new.” Continuing an already-admitted transaction after hiding a directory is weaker evidence because it may retain seed-derived execution/resources. Seed retirement requires explicit composition of the new construction root, freeze/admission of its authority, revocation of historical seed access, and successful continuation of fresh native work.

### 9.4 P1 — supply-chain signing-key authority is not yet defined

The seed descriptor binds both archive and detached-signature bytes by SHA-256, but the product deliberately does not verify the signature as trusted publication authority. Before a production bootstrap claims supply-chain signature verification, define the signing-key owner, key material/rotation/revocation policy and what exact object the signature authenticates. Do not bolt `gpg --verify` into the script without an authority model; that would verify with ambient host trust rather than product authority.

### 9.5 P1 — rootfs and media are product gaps, not package-manager gaps

The controller already contains a privileged synthetic rootfs campaign proving that an empty managed target can converge from explicit profile policy and then be independently audited. The missing work is now distribution/product authority: package membership, construction root, configuration/overlays, qualification and artifact composition. Do not create a special `pkgctl rootfs` semantic path unless ordinary desired-state convergence proves insufficient for a reason that belongs to the controller domain.

### 9.6 P2 — controller complexity / authority gravity

`pkgctl` is the largest and most rapidly evolving repository. Its extensive test surface is a strength, but size creates pressure to put convenience semantics in the controller. Every future durable controller field should pass this test: “Is this progression/composition evidence, or is it actually an owner semantic value that should live in an existing/new library?” If the latter, keep it out of the controller journal.

### 9.7 P2 — reconciliation has no production workflow yet

This is intentional, not a missing dependency. Leave it test-only until there is a concrete product/user responsibility for rejected objects. When that responsibility appears, design the orchestration around exact completed application evidence and the existing side-plane stores.

### 9.8 P2 — Linux execution policy may eventually require more capabilities

Do not pre-emptively expand the backend. Add user/PID namespace, Landlock, cgroup or resource-accounting support only when a named execution policy requires it, and qualify the capability independently. Until then truthful rejection is preferable to nominal “sandbox” coverage.

### 9.9 P3 — documentation fossil in `libpkgapply`

Replace the two `pkgman` references in the current outer-lease design sequence with architecture-neutral/controller-correct wording. Audit adjacent docs for the same kind of legacy noun, but do not erase intentional historical references in HISTORY/MIGRATION documents.

## 10. Bootstrap state in detail

### 10.1 Current default seed

`seeds/default` selects `zeppe-lin-1.2.1-20260222-x86_64.ini`:

- name: `zeppe-lin-1.2.1-20260222-x86_64`
- architecture: `x86_64`
- release field: `v1.2`
- archive SHA-256: `2ceb61b2c89304b6c0771e0de7ea354e328af74d472dda0791178fd2ebac12b8`
- detached-signature SHA-256: `b6e005f9675c2d20427d428b82c34ce7d89bdd160f97e5c2a420f4f6989c0232`

The seed is historical external construction authority, not current installed-state truth. Local `--seed-file` / `--seed-signature-file` are acquisition overrides only: bytes must still equal the committed descriptor identities.

### 10.2 Current product model

`zeppe-lin-system` records `BOOTSTRAP_PRODUCT_MODEL = seed-assisted-stage-b-gcc-handoff`, expects `pkgctl 0.43.0`, and uses `exact-compatible-sharing` for the foundation operation profile. Stable foundation membership is exactly filesystem/glibc/libgcc. Construction artifacts are qualification evidence, not desired members.

At the composer’s current old foundation pin it expects these ten construction artifacts: binutils-bootstrap, filesystem, gcc-bootstrap, glibc, glibc-bootstrap, gmp-bootstrap, libgcc, linux-api-headers, mpc-bootstrap and mpfr-bootstrap. The d6 source head keeps the same names but advances gcc-bootstrap’s release coordinate.

### 10.3 Workspace semantics

A workspace is admitted under exact controller source lock, product inputs and build policy. New workspaces must be absent/cleanly created; resume is for the same retained authority, not a mechanism for swapping foundation revisions, seed hashes, controller binaries or policy. After advancing a product source pin, use a newly admitted workspace for qualification. Do not “resume through” a source-lock change.

## 11. Future development — gate-driven roadmap

This roadmap deliberately avoids calendar estimates. Each gate produces authority required by the next one.

### Gate A — close the current Stage-B product milestone

1. Advance `zeppe-lin-system` foundation pin from `df1c1b0…` to the intended reviewed foundation commit (`d6d4451…` in this snapshot) and update exact `gcc-bootstrap` coordinate from release 4 to release 5.
2. Update only source/model expectations that genuinely changed; do not weaken exactness checks.
3. Reproduce the duplicate-artifact/report condition and retain the complete exact report plus identities. Fix the semantic owner, not the symptom.
4. Run zlsystem contract/model tests.
5. Start a fresh product workspace under the new source lock. Run full bootstrap and then independent `bootstrap check`.
6. Require the final manifest to truthfully remain seed-assisted and seed-retirement `no`. This gate is about a valid GCC handoff, not about pretending the seed is gone.
7. Once stable, create a product release/checkpoint so future work has a clean qualified baseline before broadening construction.

**Exit criterion:** the exact d6-equivalent foundation source is a committed product input; Stage-B GCC handoff passes its real build/check and zlsystem acceptance from a fresh workspace; no unresolved report ambiguity remains.

### Gate B — define the post-seed construction capability contract

Do **not** begin by writing an `@construction` members list. Begin with hostile capability discovery.

1. Choose a sealed representative native construction workload that should run after seed retirement.
2. Enumerate what execution capabilities it actually invokes: interpreter/shell, compiler driver, assembler/linker/binutils, libc/runtime, archive/patch/build tools, compression tools, generated-language tools, etc. Record each as an exact executable/resource edge, not as “base system.”
3. Compose those capabilities only from admitted native artifacts. Every missing edge becomes a candidate bootstrap recipe **only when proven by the workload**.
4. For each added temporary recipe, constrain its payload to the capability needed for seed retirement and assert that no accidental seed search path/runtime dependency survives.
5. Keep stable target substrate and temporary construction authority separate. A package can exist in the collection without being a final `@foundation` member.

The collection README already gives the correct heuristic: xz, make, shell, Python, etc. are not automatically bootstrap packages. Add one only when a sealed native construction transaction proves the edge.

### Gate C — compose and freeze `@construction` only when it is true

Once the required capability closure is known, create the construction profile as desired membership of a native construction root. It should contain the exact packages whose installed artifacts provide the proven post-seed construction capabilities. Profiles still do not encode order; resolver/transaction authority handles that.

The product composer should converge an empty managed construction target, audit it independently, and freeze exact canonical state + resource/object authority needed to use it. Only at that point is `@construction` a truthful profile rather than a speculative name.

### Gate D — hostile seed-retirement proof

1. Admit/freeze the exact native construction root and execution authority.
2. Make S0 inaccessible in a way the product can demonstrate—not merely “do not reference its path.” The proof should fail if any execution/resource path still depends on S0.
3. Start a **new** sealed construction transaction whose source/build/check resources come from native authority only.
4. Build and CHECK a meaningful package with the native construction root.
5. Verify resulting artifact/image and canonical state through the normal owner pipeline.
6. Only then change product truth to `seed-retirement-qualified yes`.

If this gate fails, add only the capability that the evidence proves missing. Do not import an old distribution base set wholesale.

### Gate E — rootfs product

Rootfs should be a `zeppe-lin-system` product, not a special package-manager mode:

```text
explicit collection/profile policy
          +
empty managed target
          |
          v
ordinary pkgctl resolve/transaction/run convergence
          |
          v
canonical installed state + exact package objects
          |
          +--> independent libpkgaudit feedback
          |
          v
product-owned configuration/overlays/qualification
          |
          v
qualified rootfs artifact
```

Important policy: **collection membership is not rootfs membership**. The rootfs profile should name what the product wants, not simply mirror all packages in a collection. Conversely, dependency packages pulled by resolver authority need not be manually repeated to encode order.

Do not resurrect the old `mkrootfs` model as an imperative script that loops over “core” and installs packages. The replacement is a product composer presenting desired state to the native controller, with canonical state and independent qualification.

### Gate F — installation and live media

`iso-install` and `iso-live` consume a qualified rootfs plus media-specific overlays/configuration and artifact assembly. Bootloader choices, installer scripts, live-session configuration and image layout belong to those product layers. They are not package dependency edges and should not pollute collection metadata.

### Gate G — operational hardening after self-hosting

After the seed-independent construction/rootfs path is real, address operational lifecycle in owner order:

- define signing-key publication/trust authority for source/seed/product artifacts where signatures are claimed;
- define retention/garbage-collection semantics for content, package-object, execution-resource and journal stores before adding deletion commands;
- integrate reconciliation only when a concrete product/user workflow exists;
- consider `libpkgimpact` as an explicit diagnostic/policy input for upgrade consequences if required, never as hidden resolver truth;
- add Linux execution capabilities only for named guarantees;
- stabilize externally consumed machine protocols before independent component versioning makes co-versioned text parsing brittle.

## 12. What must *not* happen next

A future maintainer/AI should reject the following tempting shortcuts:

- Do not loosen `zeppe-lin-system` foundation revision matching so it accepts “latest” or arbitrary clean HEAD.
- Do not change duplicate artifact handling to “last record wins.”
- Do not infer a package artifact from an archive path or filename when exact retained build/image authority exists.
- Do not treat `bootstrap.manifest` or CLI text as the semantic package truth it summarizes.
- Do not call the historical seed “trusted” because its detached signature bytes exist; the key trust boundary is still absent.
- Do not declare `@construction` until native construction survives physical seed revocation.
- Do not define `@rootfs` by copying historical `pkgsrc-core` membership. Derive explicit product policy.
- Do not encode build/install order in profiles.
- Do not add rootfs/ISO special cases to resolver/transaction semantics to accommodate product ceremony.
- Do not integrate `libpkgreconcile*` into production merely because it is available.
- Do not turn `libpkgaudit` or `libpkgimpact` observations into installed-state or dependency authority.
- Do not reintroduce compatibility paths for legacy CRUX/Zeppe-Lin private filesystem databases into the native model.
- Do not bump private schema numbers mechanically during unreleased reshaping; protocol/version changes should reflect real compatibility domains, not development chronology.
- Do not “fix” execution capability gaps by silently weakening requested isolation/resource policy.
- Do not add new controller-owned semantic codecs if an owner library can encode/rehydrate the value.
- Do not assume a past green suite proves current source after a pin/ABI/recipe change; qualify the changed boundary.

## 13. Testing and qualification strategy from here

The zoo now has enough synthetic tests that the next value comes from **boundary-hostile qualification**, not raw test count. Keep unit/contracts, but prioritize tests that attack model assumptions before a multi-hour bootstrap finds them.

For each future change, ask for four layers where applicable:

1. **Owner contract:** invalid semantic combinations reject; canonical identities/codecs round-trip; no adjacent owner semantics leak in.
2. **Adapter/provider assault:** paths, symlinks, descriptors, stale handles, unsupported capabilities, partial writes, interruption and conflicting evidence fail closed.
3. **Cross-boundary integration:** exact authority crosses the intended adapter and cannot be substituted by identity/path residue or an ambient host resource.
4. **Real product qualification:** a representative package/rootfs/bootstrap transaction exercises the same control path users will run.

The foundation recipe checks are good examples: they inspect exact dynamic dependencies, RPATH/RUNPATH absence, loader topology, source digests and executable handoff behavior. Continue making real bootstrap boring by first turning each discovered model failure into a cheaper hostile test at the owner boundary.

A full zoo rebuild remains the release gate after ABI or public dependency changes. Privileged `pkgctl`/`libpkgexec-linux` suites remain necessary because namespace/mount/credential behavior cannot be established by unprivileged unit models alone.

## 14. Release/versioning state

The current source lock intentionally mixes exact tags and reviewed post-tag commits. For future releases:

- tag semantic/ABI changes before downstream products claim a stable release closure when practical;
- documentation-only post-tag pins are acceptable in a source-locked product, but record them as such;
- a Meson `project(version:)`, SONAME/soversion and `.pc` dependency range are separate compatibility claims—review all three when an ABI owner changes;
- product pins are stronger than “minimum dependency versions.” The exact system source lock is the build authority for that product; installed libraries are not substitutes.

No current task requires manufacturing compatibility with old private development evidence. Released public ABIs/protocols are different: change those deliberately with explicit consumer updates and qualification.

## 15. Long-term maintainability assessment

### What is strong

- semantic ownership is much clearer than in the CRUX-era monolith/tool scripts;
- pure semantic libraries are separated from mutable providers and syntax adapters;
- restart/durable evidence is a first-class design problem, not an afterthought;
- execution capability is explicit and rejectable;
- exact source-lock composition prevents accidental development-prefix substitution;
- build/check phase separation is now reflected all the way into real package recipes;
- product qualification is explicitly distinguished from developer tests;
- bootstrap temporary authority is not being mislabeled as desired final state;
- controller qualification is broad enough to catch many authority/lease/uncertainty failures before product use.

### What is fragile

- `pkgctl` is large and therefore the easiest place for future semantic duplication to accumulate;
- product consumption of human-oriented/deterministic diagnostic report grammar is reaching its limit;
- seed retirement is not yet proven, so historical tool authority still exists at the most important system boundary;
- the product layer has only one real product campaign so far, so rootfs/media may reveal ceremony/authority seams not yet exercised;
- supply-chain signing trust remains intentionally unspecified;
- many repositories increase release choreography and make exact dependency graphs important operational infrastructure.

### Overall

The architecture should be preserved, but the next year of work should make it **boring to operate**. The proof of success is not more abstractions; it is that a future maintainer can pin one controller closure, admit product inputs, construct a seed-independent root, converge a rootfs, audit it and compose media without needing to reinterpret hidden state or remember why a path exists.

## 16. Restart protocol for a future AI/LLM

If this document is opened in 2027/2028 with a new set of project bundles, use this sequence exactly:

1. **Do not assume chat memory.** Treat this document as baseline context, then inspect the new source.
2. Compute SHA-256 of the new aggregate bundle/archive and record the date.
3. Enumerate repositories and clone/extract every Git bundle. Refuse to hallucinate missing repository bodies.
4. For each repository, record exact HEAD, latest tag, commits since tag, Meson project version, public dependency ranges and clean/dirty status.
5. Diff each new HEAD against the exact baseline SHA in §5. Group changes by semantic owner, codec/protocol, projection, physical provider, execution adapter, controller or product input.
6. Read current `README.md`, `DESIGN.md`, `MAINTAINING.md`, `TESTING.md`, `HISTORY.md`/`MIGRATION.md` where present **for every changed owner**. Do not let this old document override newer source.
7. Reconstruct `zeppe-lin-system` wrap revisions and verify every wrapped SHA exists in the supplied zoo. Separately inspect collection/seed product pins.
8. Re-run source-level contracts first. Then build/test changed libraries in dependency order. After public ABI changes, rebuild the whole zoo to eliminate stale-link illusions.
9. Run privileged provider/controller tests on a machine capable of the required namespaces/mounts/credentials. A skip is evidence of unavailable capability, not a pass.
10. Find the latest product frontier by reading the current zlsystem product model, manifests and retained run/effect reports. Distinguish source expectation from operator report and from retained program evidence.
11. Resume at the first **unmet gate** in §11, unless newer source explicitly supersedes the gate. Do not skip seed-retirement truth merely because later rootfs code exists.
12. When a failure appears, identify the semantic owner before patching. If the needed body/API is not present, ask for that repository/bundle instead of inventing it.
13. Deliver code changes only after the tranche is independently qualified. For patch workflows, generate clean `git am` mboxes from inspected source; do not make the operator debug speculative half-patches.
14. Update this state document after each major gate with exact commits and evidence. Keep “implemented,” “qualified,” “operator observed” and “planned” separate.

### 16.1 Suggested prompt to prepend when feeding this document to a future AI

```text
You are continuing the Zeppe-Lin native toolchain from the attached state/continuation record.
Treat that record as a historical baseline, not as authority over current source.
Inspect every supplied current repository/bundle before claiming APIs or implementation state.
Diff current exact heads against the baseline commit ledger and re-audit every changed authority boundary.
Preserve the project invariants: one semantic owner per fact; retained evidence is admitted history, not present truth;
decode/rehydrate owner evidence rather than fabricate semantics from identities; keep syntax/providers/projections/execution separate;
keep pkgctl a controller rather than a parallel package model; keep zeppe-lin-system product ceremony outside package semantics;
fail closed on incompatible private evidence; do not add legacy compatibility ghosts.
Identify the first unmet roadmap gate and current blocking defect from actual source/evidence before proposing patches.
If implementation bodies are missing, ask for them; never hallucinate repository state.
```

## 17. Concrete next tranche from this exact snapshot

If work resumes immediately from the uploaded 2026-08-21 zoo, the next tranche should be deliberately narrow:

1. `zeppe-lin-system`: advance the foundation revision to `d6d4451dfaaaf9e57ff1d62a4c215c61685e2626` and `gcc-bootstrap` expected release to `5`, with corresponding contract/model updates.
2. Reproduce and capture the exact artifact report that triggers package-name duplication. Do not patch `_artifact_map()` until the duplicate records are semantically classified.
3. If the report duplication is a controller defect, inspect the relevant `pkgctl` report/progress sources at `ef52450096dd5aec88897fc34ea5c70f609e9a52` and fix there. If it is valid multi-record evidence, define exact product selection by owner identity and start the versioned machine-result-contract design.
4. Run source tests, affected library/controller tests, then a fresh real bootstrap. Finish with `zlsystem bootstrap check` and preserve the manifest/report as the Stage-B baseline.
5. Separately fix `libpkgapply/DESIGN.md` legacy `pkgman` vocabulary; this is independent documentation hygiene and should not be coupled to bootstrap semantics.
6. Only after the Stage-B baseline is clean, begin Gate B capability discovery for seed retirement. Do not widen `pkgsrc-foundation` speculatively beforehand.

That is the shortest path that advances the system without undoing the architecture.

## Appendix A — baseline commit matrix

This is duplicated from §5 in a machine-friendly TSV-style block so a future script/AI can diff without parsing prose.

```text
repository	version	head	latest-tag	tag-state	head-subject
liblinediff	0.2.1	5d4a34afcf9a5d77c98dc6f56f6009502ca97635	v0.2.1	ahead:3	docs: add 0.2.2 (unreleased) changes
libpkgapply	4.0.1	36aa530ae07dc1c2a7f1ee999a7626977fc8a53e	v4.0.1	exact:v4.0.1	release: expose owner journal rehydration
libpkgapply-exec	3.0.2	efbae2415b93ef001dad8aa8cdd34365cadd304b	v3.0.2	exact:v3.0.2	release: bind lifecycle execution to apply ABI 4
libpkgapply-posix	4.0.0	61b0595e11edb4c072e3f05aa8672f3e4c8569e5	v4.0.0	exact:v4.0.0	journal: persist owner append-only history
libpkgaudit	0.1.0	0a3e1603e801519006b57257f17e39e0f632334f	v0.1.0	exact:v0.1.0	audit: confine intermediate symlink traversal
libpkgbuild	3.0.3	8dc3f17ec152330e98391eb747a377e9c2bb6db8	v3.0.3	exact:v3.0.3	release: libpkgbuild 3.0.3
libpkgbuild-exec	3.3.1	b85bcf580ece9969c687d67b92dcbe239e298a87	v3.3.1	exact:v3.3.1	release: libpkgbuild-exec 3.3.1
libpkgbuild-image	1.0.1	93bf644c107bd46a5b9da4b56d51e06f3becc649	v1.0.1	exact:v1.0.1	release: bind image admission to resolver-4 build
libpkgbuild-plan	1.1.0	912de8c3b4b3fa692f493e1833da32b4635bf248	v1.1.0	exact:v1.1.0	build: require source-plan ABI 2 authority
libpkgcatalog	4.0.0	f7c3f5683d7c9c0a5c0f7774ab626db8d4e93350	v4.0.0	exact:v4.0.0	release: rebuild catalog for source ABI 4
libpkgcatalog-acquire	4.0.0	7b65017902e531fd8f29576d0a4343aa68b0cd9a	v4.0.0	exact:v4.0.0	release: rebuild catalog acquisition for ABI 4
libpkgcheck	0.3.0	0d6b22a79ae1706357f726e34a99870848a09300	v0.3.0	ahead:1	docs: separate check binding from resource realization
libpkgcheck-exec	0.9.0	a265a8dfd1e96a96632184041713ab3fca4a8e3a	v0.9.0	exact:v0.9.0	tests: close check environment vocabulary over build policy
libpkgexec	2.2.0	aa32726045c3ad7325a13c8ca4bb4cbefdbcd254	v2.2.0	exact:v2.2.0	execution: add checked-package resource role
libpkgexec-linux	0.7.1	54e060948f60e411ac2b5ffeb7e4c0165f7cc140	v0.7.1	exact:v0.7.1	release: publish 0.7.1
libpkgfetch	3.0.0	b01b47ed20fc2dba6c34cca48f0ba35e2a0d9f8b	v3.0.0	ahead:1	docs: name phase-neutral source realization
libpkgimage	0.4.1	179f14759b48f006dc922579314d56637f0522a8	v0.4.1	ahead:1	docs: normalize image documentation authority
libpkgimage-exec	0.1.0	6dd401fc70b78d824be21dd5c9ea515cb64f0c70	v0.1.0	ahead:1	build: publish Meson subproject dependency
libpkgimpact	0.3.0	62a85dad2bd6dc960df647529e79d3790e63f926	v0.3.0	exact:v0.3.0	impact: harden public and native client boundaries
libpkgobject	0.1.0	022917659cb7d042d4a5b8814629d208235f4977	v0.1.0	exact:v0.1.0	tests: honor automatic test enablement
libpkgplan	0.3.1	406dc58d44854b6a3363c77b4087e953a45ad395	v0.3.1	ahead:1	docs: normalize planner documentation authority
libpkgreconcile	0.3.0	ac9b056dd638512c912a1e30ac0c5c91dc97f1bd	v0.3.0	exact:v0.3.0	tests: house native reconciliation qualification
libpkgreconcile-apply	0.1.2	e5d03cd518b25d01a462aaf411980cf02af0a4f9	v0.1.2	exact:v0.1.2	build: derive pkg-config closure from dependencies
libpkgreconcile-apply-posix	0.1.2	1cf029d8f3626bb3544b0f14092f5806d92a0f5b	v0.1.2	exact:v0.1.2	release: bind POSIX reconciliation to apply generation 4
libpkgreconcile-posix	0.1.0	cb7f2dac2e6eaa0767f6458d5d7dacd448d6c9fb	v0.1.0	exact:v0.1.0	reconcile-posix: refuse blocking special-file corruption
libpkgresolve	4.0.0	fe64f261919f79abf5b93a8167fccd54432d0a19	v4.0.0	ahead:1	tests: assault reciprocal runtime cohort resolution
libpkgsource	4.1.0	c29bcb4ed78fd8ff0bedc0fe0f14185b723735db	v4.1.0	exact:v4.1.0	release: advance source codec ABI for source 4
libpkgsource-exec	0.1.0	6467b64a44bc4187b3a38d8d4ce8e8f92b26b951	v0.1.0	ahead:1	build: publish Meson subproject dependency
libpkgsource-plan	2.0.0	49702392b916e38e610c6c4097913a3491b13acd	v2.0.0	exact:v2.0.0	release: rebuild source-plan for source ABI 4
libpkgsource-yaml	2.0.0	5e8c71042cbad072140af6ba47c4820aaf3782be	v2.0.0	exact:v2.0.0	release: rebuild YAML adapter for source ABI 4
libpkgstate	3.1.0	94e59e64b842a396bf5bb9eacc0f262c1e266c5f	v3.1.0	ahead:1	docs: normalize state documentation authority
libpkgstate-apply	3.1.3	6af8af6547612e096e07acdb27daaeb3ee530711	v3.1.3	exact:v3.1.3	release: libpkgstate-apply 3.1.3
libpkgstate-build	3.1.0	9ce185fe576a47083aa025c48190a394c8583322	v3.1.0	exact:v3.1.0	build: require state-source ABI 2 authority
libpkgstate-plan	3.0.0	abbba3eae47b5d0f201d4e46f9f212163eaf7b6d	v3.0.0	ahead:2	docs: normalize planner-state authority tree
libpkgstate-posix	3.1.0	908ba941d9e60d99b4e6b631cec4b7bc4cb4ecfb	v3.1.0	exact:v3.1.0	tools: add explicit empty-state bootstrap
libpkgstate-source	4.0.0	3150bc302b13bbdcc2d4437d7fb0c775078c4e13	v4.0.0	exact:v4.0.0	release: rebuild state-source for source ABI 4
libpkgtransaction	4.1.0	5e9b78ec702a96ee477c8d342824d9c6b5253022	v4.1.0	exact:v4.1.0	release: libpkgtransaction 4.1.0
pkgctl	0.43.0	ef52450096dd5aec88897fc34ea5c70f609e9a52	v0.43.0	exact:v0.43.0	release: pkgctl 0.43.0
pkgsrc-foundation	n/a	d6d4451dfaaaf9e57ff1d62a4c215c61685e2626	none	untagged	gcc-bootstrap: seal GCC 16 static libatomic authority
zeppe-lin-system	0.1.0	7238707c5f6caaf4247c19c7c1c8e14e0d6a3704	none	untagged	bootstrap: require exclusive workspace ownership
```

## Appendix B — audit reproduction notes

The aggregate input SHA is part of this document so the baseline can be verified even if filenames are copied or renamed. The audit cloned the Git bundles rather than inferring source from conversation summaries. The only run-time assertions marked **Q** are the four source/model contract executions listed in §1. Full compilation and privileged qualification should be repeated before using this record as a release certificate.

The most important epistemic rule for future work is simple: **when source, retained evidence and remembered narrative disagree, stop and identify the owner. Do not average them into a plausible story.**

