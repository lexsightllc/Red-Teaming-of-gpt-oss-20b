<!-- SPDX-License-Identifier: MPL-2.0 -->

# Provenance Audit – MPL-2.0 Relicensing

Date: 2025-10-26

## Summary
- Enumerated repository files via `git ls-tree -r --name-only HEAD` (200 tracked paths).
- Identified contributors with `git shortlog -sne`:
  - Your Name <you@example.com>
  - Augusto Ochoa Ughini <lexsightllc@lexsightllc.com>
  - lexsightllc <lexsightllc@lexsightllc.com>
- Searched for GPL-licensed inbound materials using `rg "GPL" -n` with no matches.
- Reviewed repository contents and confirmed no bundled third-party source directories. Runtime
  dependencies remain covered by their original licenses and are recorded via
  `scripts/license-scan` outputs.

No GPL-only code or untracked third-party additions were detected. Proceeded with MPL-2.0
relicensing steps per directive.
