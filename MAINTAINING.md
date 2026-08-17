# Maintaining zeppe-lin-system

## Updating the controller source set

Controller wraps are a lock, not floating dependency declarations. Update a
repository only after the corresponding commit is published to
`github.com/zeppe-lin/<repo>` and its standalone tests are green.

For each source-set change:

1. replace the exact 40-hex `revision` in the corresponding wrap;
2. do not use `HEAD`, `master`, tags, shallow `depth`, or local paths;
3. keep `[provide]` aliases synchronized with the subproject's
   `meson.override_dependency()` names;
4. run the contract suite;
5. perform a clean controller build with no Zeppe-Lin development prefix in the
   environment; and
6. qualify the same commit set on a foreign Linux host.

If a new controller dependency is introduced, add its wrap and every provided
dependency name to `force_fallback_for`. The source-lock contract must fail until
closure membership and forcing policy agree.

## Wrapped project options

Wrapped repositories are consumed as product dependencies, not maintainer
worktrees. Their tests and generated documentation are disabled deliberately.
Do not solve a missing host tool by enabling another project's maintainer
surface.

`libpkgstate-posix:tools` is the intentional exception because `pkgstate-init`
is a controller product input.

## Product collection sources

Package-source collections are not Meson controller subprojects. Pin them under
`collections/` with the product collection-source protocol.

A source bump must name an already published exact Git commit. The bootstrap
frontend snapshots the admitted commit; it must never consume a dirty checkout
or a floating branch. A local source override is for development convenience
only and is accepted only when it proves the same exact committed authority.

Do not put product qualification recipes into distribution collections. If a
recipe exists solely to answer whether a bootstrap/rootfs/ISO result is
acceptable, keep it below `products/<product>/qualification/collection/`.

## Seed descriptors

A seed descriptor may be added only for a published archive with known SHA-256.
Keep detached-signature coordinates when the release publishes them. Changing
the default seed is a source-policy change and must be reviewed separately from
controller or collection bumps.

The archive digest is admission authority. Do not accept arbitrary extracted
roots plus a caller assertion that they came from those bytes.

Detached-signature cryptographic verification must not be claimed until the
project defines the signing-key trust authority used for verification.

## Bootstrap workspace compatibility

Bootstrap workspace JSON is private product evidence. During pre-release
architecture work, incompatible old private bytes should fail closed rather than
acquiring compatibility decoders or reconstructing missing authority.
This fail-closed rule governs semantic admission (`run`, `resume`, and `check`),
not destruction. `bootstrap clean` may remove a marker-bound workspace without
decoding stale product semantics; the marker format and exact workspace binding
are sufficient deletion authority. Do not add a compatibility decoder merely so
old workspaces can be cleaned.

A resumed workspace must recover its admitted seed, collection snapshot, build
policy, foundation operation-policy profile and controller identities. The
product owns only the opaque complete pkgctl profile selection; it must not copy
or decode libpkgplan policy vocabulary. Start-only authority is never redeclared
by the frontend on `pkgctl --resume`; `--max-steps` remains live invocation
control.

## Scope discipline

Do not put dependency resolution, recipe execution, installed-state
reconciliation, artifact publication, or package-image application logic in this
repository. If orchestration needs to decode an owning library's private schema,
fix the public controller/library boundary instead.
