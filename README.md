# System Monitor — Glassmorphism Edition

A desktop system-monitoring application built with Python and PyQt5. It provides a graphical dashboard for viewing live system resource usage, process activity, network and storage information, and hardware details.

## About

System Monitor brings essential performance information into one desktop interface. It tracks CPU, memory, disk, and network activity, presents usage history in charts, and includes tools for inspecting processes and exporting collected data.

## Features

- Live CPU, memory, and disk usage indicators
- Network throughput, traffic statistics, and interface information
- Process list with search, sorting, resource usage, and an option to terminate a selected process
- Charts for CPU, memory, disk, and network activity
- Storage partition and system information views
- Historical data stored locally and exportable to CSV
- Optional GPU, temperature, and battery readings when supported by the hardware and system
- Configurable monitoring refresh rate

## Technologies and Skills

- **Python** — application logic and system integration
- **PyQt5 / Qt Charts** — desktop interface, charts, and UI updates
- **psutil** — system, process, disk, network, temperature, and battery metrics
- **SQLite** — local monitoring history
- **GPUtil** — optional GPU monitoring
- **JSON and CSV** — settings and data export
- **Threading and Qt worker threads** — background monitoring tasks

## Requirements

- Python 3.7 or newer
- Dependencies listed in [`requirements.txt`](requirements.txt)
- A desktop environment capable of running PyQt5

GPU, temperature, and battery readings depend on available hardware, drivers, and operating-system sensor support. GPU monitoring is optional and uses GPUtil.

## Installation and Usage

1. Clone or download this repository.
2. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

   On systems where Python 3 is invoked as `python3`, use:

   ```bash
   python3 -m pip install -r requirements.txt
   ```

3. Start the application:

   ```bash
   python system_monitor_glass.py
   ```

   Alternatively, use the included launch scripts: `run.bat` on Windows or `./run.sh` on Linux/macOS. The matching `install.bat` and `install.sh` scripts install the listed dependencies.

## Local Data

The application keeps its monitoring history in `system_monitor.db` and its refresh-rate setting in `monitor_settings.json`, in the working directory. Historical records can be exported from the application as a CSV file.
