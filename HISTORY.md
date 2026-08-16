# History

## 0.1.0 — unreleased

- Establish the pinned 35-project native controller source set.
- Build `pkgctl` and `pkgstate-init` directly from Meson subproject targets.
- Qualify external host dependencies without a private installed-prefix loop.
- Record canonical historical rootfs seed descriptors.
- Admit `pkgsrc-foundation` as a separately pinned product-input authority.
- Move seed/runtime-cohort qualification recipes out of the package collection
  and into bootstrap product qualification.
- Add the Python `zlsystem bootstrap` frontend with seed acquisition,
  verification, restart, retained build policy, and independent terminal
  artifact qualification.
