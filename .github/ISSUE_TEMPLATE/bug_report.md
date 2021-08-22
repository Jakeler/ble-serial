---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**Log messages**
The full output of `ble-serial -v` (with your usual parameters like `-d`).
If it is related to BLE chracteristics please also run `ble-scan -d` with you device address.

Put the result into code blocks (wrap with tripple backticks) to get proper formatting:
```
your log could be here
```

**Setup (please complete the following information):**
- OS: [Linux Distribution (e.g. Ubuntu, Arch, etc), Windows Build]
- Bluetooth Hardware: [e.g. HM-10, Intel AX200 Bluetooth Adapter]
- BlueZ Version: [Output of `bluetoothctl -v`, Linux only]
- Python Version: [from `python3 -V`]
- ble-serial and dependency versions: [from `pip3 list`]
