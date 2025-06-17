# GolfBot-EV3 Installation and Setup Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Hardware Setup](#hardware-setup)
3. [Software Installation](#software-installation)
4. [Configuration](#configuration)
5. [Running the Project](#running-the-project)
6. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **PC**: Windows 10/11, macOS, or Linux with Python 3.8+
- **EV3 Brick**: LEGO Mindstorms EV3 with MicroPython support
- **Camera**: Samsung S23 Ultra or compatible smartphone with camera
- **Network**: WiFi connection for communication between PC and EV3

### Hardware Components
- LEGO Mindstorms EV3 brick
- 2x Large Motors (for wheel drive)
- 2x Medium Motors (for gate and ball pusher)
- Color sensor
- Touch sensor
- Ultrasonic sensor
- Gyro sensor
- Various LEGO parts, gears, and cables
- 12V blower motor with external power supply and control relay

## Hardware Setup

### 1. EV3 Brick Assembly
1. Mount all motors and sensors on the EV3 brick according to the port definitions in `config.py`
2. Connect the 12V blower motor via external power supply and control relay
3. Ensure all cables are properly connected and secured

### 2. Camera Setup
1. Position the Samsung S23 Ultra so the camera has a clear view of the competition area
2. Ensure the camera is stable and won't move during operation
3. Connect the phone to the same WiFi network as your PC

### 3. Competition Area Setup
- Competition area: 180x120 cm with center obstacle (cross)
- 11 table tennis balls including one orange VIP ball
- Exit opening (goal A/B) for ball delivery
- Time limit: 8 minutes

## Software Installation

### 1. PC Setup

#### Install Python Dependencies
```bash
# Clone the repository
git clone <repository-url>
cd GolfBot-EV3

# Create a virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Install Additional Software
- **Iriun Webcam**: For using smartphone as webcam
  - Download from [iriun.com](https://iriun.com)
  - Install on both PC and smartphone
  - Configure to use Samsung S23 Ultra as webcam

### 2. EV3 Brick Setup

#### Install MicroPython
1. Follow the [Pybricks EV3 MicroPython installation guide](https://pybricks.com/ev3-micropython/)
2. Download the latest firmware for your EV3 brick
3. Install using the Pybricks installer

#### Install EV3 Dependencies
```python
# On the EV3 brick, install required packages
import upip
upip.install('ev3dev2')
```

### 3. File Transfer
1. Transfer all project files to the EV3 brick
2. Ensure the file structure matches the repository
3. Verify all files are accessible on the EV3 brick

## Configuration

### 1. Network Configuration
Update the network settings in the code:
- **PC Client**: Update IP address and port in `src/Movement/PCClient060625.py`
- **EV3 Server**: Update IP address in `src/Movement/main.py`

### 2. Camera Configuration
1. Configure Iriun Webcam to use the correct camera index
2. Update camera index in `src/main.py` if needed
3. Test camera connection

### 3. API Configuration
1. Obtain Roboflow API key
2. Update API key in `src/main.py`
3. Configure model ID for ball detection

### 4. Homography Setup
1. Run `src/create-homography.py` to create the homography matrix
2. Follow the interactive prompts to select four corner points
3. The homography matrix will be saved as `homography.npy`

## Running the Project

### 1. Start the EV3 Server
```bash
# On the EV3 brick, run:
python src/Movement/main.py
```

### 2. Start the PC Client
```bash
# On the PC, run:
python src/Movement/PCClient060625.py
```

### 3. Start the Main Application
```bash
# On the PC, run:
python src/main.py
```

### 4. Start Vision Processing
```bash
# On the PC, run (if separate vision module exists):
python src/vision.py
```

## Project Structure

```
GolfBot-EV3/
├── src/
│   ├── main.py                 # Main application
│   ├── cdio_utils.py           # Core utilities
│   ├── create-homography.py    # Homography creation tool
│   ├── ImageRecognition/       # Image processing modules
│   ├── PathFinding/           # Path planning algorithms
│   ├── Movement/              # Motor control and movement
│   └── tests/                 # Test files
├── transformed_images/         # Output directory for processed images
├── homography.npy             # Homography matrix
├── requirements.txt           # Python dependencies
├── INSTALLATION_GUIDE.md      # This file
└── README.md                  # Project documentation
```

## Testing

### 1. Hardware Tests
```bash
# Run hardware tests
python src/tests/test_motors.py
python src/tests/test_sensors.py
```

### 2. Vision Tests
```bash
# Test image processing
python src/tests/test_vision.py
```

### 3. Integration Tests
```bash
# Test complete system
python src/tests/test_integration.py
```

## Troubleshooting

### Common Issues

#### 1. Camera Not Detected
- **Problem**: Camera index incorrect
- **Solution**: Update camera index in `src/main.py`
- **Alternative**: Use Iriun Webcam for smartphone camera

#### 2. Network Connection Issues
- **Problem**: EV3 and PC can't communicate
- **Solution**: 
  - Verify both devices are on same WiFi network
  - Check firewall settings
  - Update IP addresses in configuration files

#### 3. Motor Control Problems
- **Problem**: Motors not responding
- **Solution**:
  - Check motor connections
  - Verify port assignments in `config.py`
  - Test individual motors

#### 4. API Key Issues
- **Problem**: Roboflow API errors
- **Solution**:
  - Verify API key is correct
  - Check internet connection
  - Ensure model ID is valid

#### 5. Homography Errors
- **Problem**: Image transformation not working
- **Solution**:
  - Recreate homography matrix using `create-homography.py`
  - Ensure four points are selected in correct order (TL → TR → BR → BL)

### Performance Optimization

#### 1. Frame Rate Issues
- Adjust `TARGET_FPS` in `src/main.py`
- Reduce image resolution if needed
- Optimize image processing algorithms

#### 2. Memory Issues
- Clear `transformed_images/` directory regularly
- Monitor memory usage during operation
- Restart application if memory leaks occur

## Support

For additional support:
1. Check the project README.md
2. Review test files for examples
3. Contact the development team
4. Check Pybricks documentation for EV3-specific issues

## Contributing

To contribute to the project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

---

**Note**: This project is developed for the CDIO competition 2025. Ensure all hardware and software configurations comply with competition rules and regulations. 