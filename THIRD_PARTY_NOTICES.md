<!-- SPDX-License-Identifier: MPL-2.0 -->

# Third-Party Notices

This repository does not bundle third-party source code. Runtime dependencies are installed from
PyPI and their license texts can be generated at any time via:

```bash
scripts/license-scan
```

The resulting `reports/pip-licenses.json` and any ScanCode reports produced in CI must accompany
redistributions of the project in accordance with each dependency's license.
