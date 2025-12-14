# HW Display

This project powers a SSD1322 OLED display with a Raspberry Pi Zero 2W, creating a small, desk-side hardware monitor.

## General Info

The project consists of three main parts:
1.  **A Python application** that runs on a Raspberry Pi, which is connected to an OLED display via GPIO. It runs a Flask webserver to listen for incoming data.
2.  **A .NET Windows service** that runs on a host PC. It uses the `LibreHardwareMonitor` library to collect hardware statistics (CPU/GPU load, temperature, etc.).
3.  **A 3D-printable case** to house the Raspberry Pi and the display, turning it into a neat little companion for your desk.

The Windows service periodically sends hardware data to the Python app's API endpoint. The Python app then cycles through this data on the OLED screen. If the host PC goes offline, the display enters a sleep mode and wakes up as soon as it receives new data.

The tutorial will guide you, how to set everything up on a windows machine

## Setting up the Raspberry Pi

### Hardware & Software Requirements
#### Hardware
* SSD1322 Display
* Raspberry Pi Zero 2W(H)
* 7 Jumper Wires
* Soldering Iron for changing the Display interface mode
* SD Card

#### Software
* [Balena Etcher](https://etcher.balena.io/) for flashing the SD card with the os
* Docker for testing and bootstrapping the RPi

### Hardware Wiring and Display Setup

* Follow the [Guide](https://github.com/chrisys/train-departure-display/blob/main/docs/02-connecting-the-display-to-the-pi.md) here. Creds [chrisys](https://github.com/chrisys) for this awesome write up.
* Make sure that the 4-SPI interface is active on the display. It required some soldering on my side
* As I have Raspberry 2WH, the rest of the connection can be done via female-2-female jumper wires 


### Optional: Setting up DietPi
* Create a bootable SD card with Balena Etcher
* Change the Dietpi `dietpi.txt` on the SD card so that a headless, auto start is possible. 


### Bootstrapping

1. Build the Docker image inside the root folder
2. Add **SSH_HOST**, **SSH_USER** und **SSH_PASS** as args and start the container to connect from docker to the running raspberry pi to copy over the files, install dependencies and create the systemd config


## Building and Running the Windows Service

The `hardware-service` is a .NET Worker Service that collects and forwards hardware data from your Windows PC.

### Prerequisites

*   .NET 10.0 SDK (or the version targeted in `hardwaremon.csproj`).
*   Administrator rights to install and run the service.

### Configuration

1.  Open the `hardware-service/appsettings.json` file.
2.  Change the `EndpointUrl` value from `"http://localhost:8080/stats"` to the IP address of your Raspberry Pi (e.g., `"http://192.168.1.100:8080/stats"`).
3.  You can also adjust the `IntervalSeconds` to control how frequently data is sent.

### Building and Installation

1.  Build the service using Visual Studio by opening `csharp.sln` or by running the following command in the `hardware-service` directory:
    ```sh
    dotnet publish -c Release
    ```
2.  This will create publish artifacts in `hardware-service/bin/Release/net10.0/publish/`.
3.  Open PowerShell or Command Prompt **as an Administrator** and use `sc.exe` to create the Windows Service:
    ```sh
    sc create HardwareMonitorService binpath="C:\path\to\your\project\hw_display\hardware-service\bin\Release\net10.0\publish\hardwaremon.exe"
    ```
4.  Start the service:
    ```sh
    sc start HardwareMonitorService
    ```

## 3D Printed Case

The `case` directory contains two `.stl` files for a 3D-printable enclosure:
*   `Case_Front.stl`: The front part of the case, which holds the display.
*   `Case_Back.stl`: The back cover for the Raspberry Pi.

You can use any standard slicer software to prepare these files for 3D printing.

## Roadmap

This is an ongoing project. Future plans include:

*   **Improved Configuration**: Adding more flexible configuration options for both the client and server applications.
*   **Rust Migration**: Rewrite everything in Rust 🦀
*   **In-depth Tutorials**: Creating a more detailed guide for the Raspberry Pi setup, including wiring diagrams and `systemd` service configuration.
*   **More Display Screens**: Adding more screens to display a wider variety of hardware information.
