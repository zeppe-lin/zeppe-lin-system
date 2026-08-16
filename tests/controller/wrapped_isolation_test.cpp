// SPDX-FileCopyrightText: 2026 Alexandr Savca
// SPDX-License-Identifier: GPL-3.0-or-later
#include <libpkgexec-linux/libpkgexec-linux.h>

#include <algorithm>
#include <iostream>

namespace {

int fail(const char* message)
{
  std::cerr << "wrapped-isolation: " << message << '\n';
  return 1;
}

bool has_guarantee(
    const pkgexec::backend_capability_profile& profile,
    pkgexec::execution_guarantee guarantee)
{
  return std::find(profile.guarantees().begin(), profile.guarantees().end(),
                   guarantee) != profile.guarantees().end();
}

} // namespace

int main()
{
  using pkgexec_linux::capability_kind;
  using pkgexec_linux::capability_state;

  const auto first = pkgexec_linux::capability_report::probe_isolated();
  const auto second = pkgexec_linux::capability_report::probe_isolated();
  if (first.profile().identity() != second.profile().identity()) {
    return fail("wrapped isolated capability identity is unstable");
  }

  const auto mount_state = first.state(capability_kind::mount_namespace);
  if (mount_state == capability_state::policy_restricted) {
    std::cerr << "wrapped-isolation: privileged mount authority unavailable; "
                 "run the integration-privileged suite with the admitted "
                 "privilege context\n";
    return 77;
  }
  if (mount_state != capability_state::available) {
    for (const auto& observation : first.observations()) {
      if (observation.state() == capability_state::available) {
        continue;
      }
      std::cerr << "  " << pkgexec_linux::to_string(observation.capability())
                << '=' << pkgexec_linux::to_string(observation.state());
      if (!observation.diagnostic().empty()) {
        std::cerr << ": " << observation.diagnostic();
      }
      std::cerr << '\n';
    }
    return fail("wrapped controller cannot realize isolated filesystem authority");
  }

  for (const auto capability : {
           capability_kind::current_root_view,
           capability_kind::writable_resources,
           capability_kind::private_mount_propagation,
           capability_kind::open_tree,
           capability_kind::move_mount,
           capability_kind::mount_setattr,
           capability_kind::chroot,
       }) {
    if (first.state(capability) != capability_state::available) {
      return fail("wrapped isolated filesystem capability set is incomplete");
    }
  }

  for (const auto guarantee : {
           pkgexec::execution_guarantee::root_view,
           pkgexec::execution_guarantee::read_only_resources,
           pkgexec::execution_guarantee::writable_resources,
           pkgexec::execution_guarantee::cleanup_verified,
       }) {
    if (!has_guarantee(first.profile(), guarantee)) {
      return fail("wrapped isolated backend omitted required filesystem guarantee");
    }
  }

  return 0;
}
