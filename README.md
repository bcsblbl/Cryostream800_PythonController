# Python Controller for Oxford CryoSystems 800 Series CryoStream

This repository contains the Python controller for the Oxford CryoSystems 800 Series CryoStream, a device designed to facilitate precise temperature control in scientific experiments. The controller is written in Python2.7 and offers a range of functionalities specific to the CryoStream 800 series.

<div align="center">
<img src="https://pharma-se.ru/upload/iblock/91b/91b9381f29bae53c6b2064fdbb1c7447.jpg" width="50%" height="auto">
</div>

<div align="center">
<img src="https://github.com/bcsblbl/Cryostream800_PythonController/blob/main/cryostream800.png?raw=true" width="50%" height="auto">
</div>

## Authors

- **John Taylor**, Berkeley Center for Structural Biology, Berkeley National Laboratory (jrtaylor_at_lbl.gov)
- **Gabriel Gazolla**, Berkeley Center for Structural Biology, Berkeley National Laboratory (gabrielgazolla_at_lbl.gov)

## Getting Started

### Prerequisites

- Python 2.7.
- Network connection to the CryoStream device.
- Cryostream 800's IP.

### Installation

1. **Clone the Repository**  
   Clone this repository to your local machine.

2. **Configure IP Address**  
   Edit the IP address in the `cryostream800-main.py` file to match the address of your CryoStream device.

3. **XML Configuration Files (Optional)**  
   Ensure that you have the latest versions of [`Cryostream.xml`](https://connect.oxcryo.com/ethernetcomms/Cryostream.xml) and [`OxcryoProperties.xml`](https://connect.oxcryo.com/ethernetcomms/OxcryoProperties.xml). These can be downloaded directly from the provided links.


### Running the Controller

Execute the controller script using Python 2.7:

```bash
python2.7 cryostream800-main.py
```

## Inline Functionality

An inline function is implemented to avoid reading configuration files each time the software loads. If you prefer to use the external configuration:

- Uncomment the relevant functions along the code, and comment the inline functions.
- Update the path to the XML files.
- Refer to comments in the `__init__` constructor for additional guidance.

## Features

### Software Annealing

The CryoStream 800 lacks a built-in annealing function (stopping flow temporarily) unlike the [CryoStream 1000 series](https://github.com/bcsblbl/Cryostream1000_PythonController). We have attempted to implement this feature through software. Detailed instructions are provided in the script.

### Modular Design

The code is structured modularly for ease of expansion and customization. Users can add or modify features as needed.

### Operational Considerations for the CryoStream Device

#### Status Packet Updates

The CryoStream device sends updates about its status over the network at one-second intervals. Therefore, it is not practical to retrieve status packets more frequently than once per second.

#### State Machine Awareness

The CryoStream device operates as a state machine. It is essential to ensure that the device is in a 'ready' state before issuing a `COOL` command. The device must be properly initialized and prepared to respond to this command effectively.

#### Command Execution with Confirmation

Due to the inherent characteristics of the CryoStream device, there are instances where commands sent to the device might not execute as expected. The exact cause of this issue it is not entirely clear, but to address this, we have implemented functions with confirmation. This process involves:

1. Sending a command to the device.
2. Waiting for the command to execute.
3. Retrieving new status data from the device to confirm the command's execution.
4. If the command is not executed, the system automatically retries a few times.

This approach ensures reliability in command execution, as it verifies whether the intended action has been performed and attempts to rectify the situation if it has not.

#### On Using Other Python Versions

While this code is primarily designed for Python 2.7, porting it to other Python versions should be relatively straightforward. It may involve modifying only a few lines of code. However, it's important to note that for this specific project, the use of Python 2.7 was a required condition.

## Contributing

Contributions are welcome. Please email us.

## License

This project is licensed under GNU GPL3.

