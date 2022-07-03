---
name: Bug report
about: Create a report to help us improve
title: ''
labels: ''
assignees: ''

---
Note: for general support questions, please use the discussions tab. This is the template for bugs in ble-serial.
Make sure you have completely read the [README](https://github.com/Jakeler/ble-serial/blob/master/README.md), searched through the [issues](https://github.com/Jakeler/ble-serial/issues?q=+) and [discussions](https://github.com/Jakeler/ble-serial/discussions).

**Describe the bug**
A clear and concise description of what the bug is.

**Log messages**
The full output of `ble-serial -v` (with your usual parameters like `-d`).
If it is related to BLE chracteristics please also run `ble-scan -d` with you device address.

Put the result into code blocks (wrap with triple backticks) to get proper formatting:
```
your log could be here
```

**Setup (please complete the following information):**
- OS: [Linux Distribution (e.g. Ubuntu, Arch, etc), Windows Build]
- Bluetooth Hardware: [e.g. HM-10, Intel AX200 Bluetooth Adapter]
- BlueZ Version: [Output of `bluetoothctl -v`, Linux only]
- Python Version: [from `python3 -V`]
- ble-serial and dependency versions: [from `pip3 list`]

**Additional Context**
Tricks for reproducing the issue? Results from other things you have already tried? Ideas what might be the cause, etc.