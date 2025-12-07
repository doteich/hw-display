# HW Display

This project powers a SSD1322 OLED display with a Raspberry Pi Zero 2W, creating a small, desk-side hardware monitor.

## General Info

The project consists of three main parts:
1.  **A Python application** that runs on a Raspberry Pi, which is connected to an OLED display via GPIO. It runs a Flask webserver to listen for incoming data.
2.  **A .NET Windows service** that runs on a host PC. It uses the `LibreHardwareMonitor` library to collect hardware statistics (CPU/GPU load, temperature, etc.).
3.  **A 3D-printable case** to house the Raspberry Pi and the display, turning it into a neat little companion for your desk.

The Windows service periodically sends hardware data to the Python app's API endpoint. The Python app then cycles through this data on the OLED screen. If the host PC goes offline, the display enters a sleep mode and wakes up as soon as it receives new data.

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

## Setting up the Raspberry Pi

The `app` directory contains the Python code for the Raspberry Pi.

### Hardware Prerequisites

*   Raspberry Pi (tested with Zero 2W).
*   A SSD1322-based OLED display (256x64 pixels).
*   Correct wiring between the Pi's GPIO headers and the display.

### Software Setup

1.  **Install Python**: Ensure you have Python 3 installed on your Raspberry Pi.
2.  **Enable SPI**: Use `sudo raspi-config` to enable the SPI interface under `Interface Options`.
3.  **Install Dependencies**: Navigate to the `app` directory and install the required Python packages:
    ```sh
    pip3 install -r requirements.txt
    ```
4.  **Run the Application**: Start the main application:
    ```sh
    python3 main.py
    ```
    The script will start the web server and initialize the display.

For long-term use, it is recommended to set up a `systemd` service on the Pi to automatically run the script on boot.

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
