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
   environment;
6. qualify the same commit set on at least one foreign Linux host before calling
   the controller milestone portable.

If a new controller dependency is introduced, add its wrap and add every
provided dependency name to `force_fallback_for`. The source-lock contract must
fail until closure membership and forcing policy agree.

## Wrapped project options

Wrapped repositories are consumed as product dependencies, not as maintainer
worktrees. Their tests and generated documentation are disabled deliberately.
Do not solve a missing host tool by installing another documentation generator
unless that tool is genuinely required by the production controller target.

When a subproject adds a new default-enabled reference tool or developer-only
feature, classify it here before enabling it. `libpkgstate-posix:tools` is the
intentional exception because `pkgstate-init` belongs to controller
provisioning.

## Seed descriptors

A seed descriptor may be added only for a published immutable archive with a
known SHA-256. Keep the detached-signature coordinates when the release
publishes them. Changing the default seed is a source-policy change and must be
reviewed separately from controller wrap bumps.

Descriptors do not grant trust to local files. Future acquisition code must
verify bytes every time it admits a new workspace.

## Scope discipline

Do not put package resolution, package build logic, state reconciliation, or
filesystem application logic in this repository. If orchestration needs to
understand a private package-library schema to continue, the boundary is wrong.
Use a public native controller/library interface or fix the owning component.
