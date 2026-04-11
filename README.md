# 🤖 Smart Warehouse AMR with Dynamic Obstacle Avoidance

<div align="center">

![ROS2](https://img.shields.io/badge/ROS2-Humble-blue?style=for-the-badge&logo=ros)
![Python](https://img.shields.io/badge/Python-3.10-yellow?style=for-the-badge&logo=python)
![Gazebo](https://img.shields.io/badge/Gazebo-11-orange?style=for-the-badge)
![Arduino](https://img.shields.io/badge/Arduino-Mega-teal?style=for-the-badge&logo=arduino)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**A fully functional Autonomous Mobile Robot (AMR) with real-time LiDAR-based obstacle avoidance,**  
**SLAM mapping, and Nav2 navigation — running in both Gazebo simulation and physical hardware.**

[Simulation](#-simulation-digital-twin) • [Physical Robot](#-physical-robot) • [Setup](#-installation) • [Run](#-running-the-project)

</div>

---

## ⚡ Quick Start

### 🖥️ Simulation (One Command)
```bash
git clone https://github.com/LiyanaLatheef/Smart-Warehouse-AMR-with-Dynamic-Obstacle-Avoidance.git
cd Smart-Warehouse-AMR-with-Dynamic-Obstacle-Avoidance
colcon build && source install/setup.bash
ros2 launch two_wheel_robot warehouse_nav2.launch.py
```
This automatically launches Gazebo → spawns robot → starts Nav2 → opens RViz!

Then in RViz:
1. Fixed Frame → `map`
2. Add Map → `/map` → Durability: `Transient Local`
3. Click **2D Pose Estimate** → click on map → drag
4. Click **2D Goal Pose** → click destination → robot navigates! 🤖

---

### 🤖 Physical Robot (One Command)
```bash
# Copy script to RPi
scp start_robot.sh pi@<RPi-IP>:~/start_robot.sh

# SSH into RPi
ssh pi@<RPi-IP>

# Run everything with one command
chmod +x ~/start_robot.sh
cd ~/robot_ws && ~/start_robot.sh
```
This automatically starts LiDAR → Serial Bridge → Velocity Smoother → Obstacle Avoidance!

---

## 📌 Project Overview

This project implements a **Smart Warehouse AMR** capable of:

- 🔍 **360° LiDAR sensing** using RPLiDAR A1
- 🧠 **Zone-based obstacle avoidance** (front, left, right zones)
- 🗺️ **SLAM mapping** using `slam_toolbox`
- 🚀 **Autonomous navigation** using Nav2
- 🔄 **Seamless simulation-to-hardware transition** — same ROS2 nodes run on both Gazebo and physical robot

| Feature | Simulation | Physical Robot |
|---|---|---|
| Platform | Ubuntu 22.04 (Laptop) | Raspberry Pi 4 (Ubuntu 22.04) |
| Sensor | Simulated LiDAR | RPLiDAR A1 |
| Motor Driver | Gazebo Diff Drive Plugin | L298N + Arduino Mega |
| Navigation | Nav2 + SLAM Toolbox | avoid.py + vel_smoother |
| Communication | ROS2 Topics | ROS2 + Serial (57600 baud) |

---

## 🎥 Demonstrations

> Add your screenshots and GIFs here after recording

### Gazebo Simulation
<!-- Replace with your actual screenshot -->
![Gazebo Simulation](docs/gazebospwn.png)
*Robot navigating warehouse in Gazebo 11 with LiDAR scan visible*

### RViz Visualization
<!-- Replace with your actual screenshot -->
![RViz LiDAR](docs/rviz_laserscan.png)
*Live LiDAR scan and robot model in RViz2*

### SLAM Map
<!-- Replace with your actual screenshot -->
![SLAM Map](docs/slam_ma.png)
*2D occupancy grid map generated using slam_toolbox*

### Nav2 Navigation
<!-- Replace with your actual screenshot -->
![Nav2](docs/nav2_map.png)
*Robot localizing and navigating using Nav2 with saved warehouse map*

### Circuit Diagram
<!-- Replace with your actual photo -->
![Physical Robot](docs/diagram.jpeg)


### Physical Robot
<!-- Replace with your actual photo -->
![Physical Robot](docs/physical_robot.jpeg)
*Physical AMR with RPLiDAR A1, Arduino Mega, L298N motor driver on circular chassis*

---

## 📁 Repository Structure

```
digital_twin_ws/
├── src/
│   ├── two_wheel_robot/                    # Simulation package
│   │   ├── urdf/
│   │   │   └── two_wheel_robot.urdf        # Robot description (diff drive + LiDAR)
│   │   ├── worlds/
│   │   │   └── warehouse.world             # Gazebo warehouse environment
│   │   ├── maps/
│   │   │   ├── my_warehouse_map.pgm        # SLAM-generated map image
│   │   │   └── my_warehouse_map.yaml       # Map metadata
│   │   ├── config/
│   │   │   ├── nav2_params.yaml            # Nav2 navigation parameters
│   │   │   └── slam_params.yaml            # SLAM toolbox parameters
│   │   └── launch/
│   │       └── spawn_robot.launch.py       # Robot spawn launch file
│   └── obstacle_avoidance/                 # Core logic package (shared: sim + real)
│       └── obstacle_avoidance/
│           ├── avoid.py                    # Zone-based obstacle avoidance node
│           ├── vel_smoother.py             # Velocity ramping for smooth motion
│           └── serial_bridge.py            # RPi ↔ Arduino serial communication
└── firmware/
    └── motor_control.ino                   # Arduino Mega motor control code
```

---

## 🧠 System Architecture

```
┌──────────────────────────────────────────────────────┐
│                  RASPBERRY PI 4                        │
│                                                        │
│  RPLiDAR A1 ──► /scan ──► avoid.py ──► /cmd_vel_raw  │
│                                │                       │
│                          vel_smoother.py               │
│                                │                       │
│                           /cmd_vel ──► serial_bridge   │
│                                              │         │
└──────────────────────────────────────────────┼─────────┘
                                               │ USB Serial
                                               ▼
                                       ARDUINO MEGA
                                               │
                              ┌────────────────┴────────────────┐
                              ▼                                  ▼
                         LEFT MOTOR                        RIGHT MOTOR
                       (L298N OUT1/2)                    (L298N OUT3/4)
```

---

## 🔧 Hardware Components

| Component | Model | Purpose |
|---|---|---|
| Single Board Computer | Raspberry Pi 4 (4GB) | Main robot brain |
| Microcontroller | Arduino Mega 2560 | Motor PWM control |
| Motor Driver | L298N Dual H-Bridge | Drive 2x DC motors |
| LiDAR Sensor | RPLiDAR A1 | 360° obstacle detection |
| Motors | 2x DC Geared Motors | Differential drive |
| Chassis | Circular (custom) | Robot base with caster wheel |

### Wiring Diagram

```
Arduino Pin 5  → L298N IN1     Left Motor  → L298N OUT1, OUT2
Arduino Pin 6  → L298N IN2     Right Motor → L298N OUT3, OUT4
Arduino Pin 7  → L298N IN3
Arduino Pin 8  → L298N IN4     12V Adapter → L298N 12V terminal
Arduino Pin 9  → L298N ENA     L298N GND   → Arduino GND
Arduino Pin 10 → L298N ENB     L298N 5V    → Arduino 5V

RPi USB → Arduino Mega (communication)
RPi USB → RPLiDAR A1 (data)
RPi powered by separate 5V USB-C adapter
```

---

## 💻 Software Stack

| Software | Version | Purpose |
|---|---|---|
| Ubuntu | 22.04 LTS | OS (laptop + RPi) |
| ROS2 | Humble Hawksbill | Robotics middleware |
| Gazebo | 11 | 3D simulation |
| RViz2 | - | Visualization |
| slam_toolbox | - | SLAM mapping |
| Nav2 | - | Autonomous navigation |
| rplidar_ros | ros2 branch | LiDAR driver |
| Python | 3.10 | Node scripting |
| pyserial | - | Arduino communication |

---

## ⚙️ Installation

### Prerequisites

```bash
# Install ROS2 Humble
sudo apt update
sudo apt install ros-humble-desktop -y
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup -y
sudo apt install ros-humble-slam-toolbox -y
source /opt/ros/humble/setup.bash
```

### Clone and Build

```bash
# Clone the repository
git clone https://github.com/LiyanaLatheef/Smart-Warehouse-AMR-with-Dynamic-Obstacle-Avoidance.git
cd Smart-Warehouse-AMR-with-Dynamic-Obstacle-Avoidance

# Build
colcon build
source install/setup.bash
```

### RPi Setup (Physical Robot Only)

```bash
# Install ROS2 Humble on Raspberry Pi (Ubuntu 22.04 aarch64)
sudo apt update && sudo apt install ros-humble-ros-base -y

# Install pyserial
pip3 install pyserial --break-system-packages

# Clone repo on RPi
git clone https://github.com/LiyanaLatheef/Smart-Warehouse-AMR-with-Dynamic-Obstacle-Avoidance.git ~/robot_ws/src/
cd ~/robot_ws
colcon build
source install/setup.bash

# Build RPLiDAR driver from source (fixes buffer overflow on RPi)
cd ~/robot_ws/src
git clone -b ros2 https://github.com/Slamtec/rplidar_ros.git
cd ~/robot_ws
colcon build --packages-select rplidar_ros
source install/setup.bash
```

---

## 🚀 Running the Project

### Simulation (Gazebo + RViz)

Open 6 terminals:

```bash
# T1 — Launch Gazebo warehouse
source /opt/ros/humble/setup.bash && source ~/digital_twin_ws/install/setup.bash
gazebo ~/digital_twin_ws/src/two_wheel_robot/worlds/warehouse.world \
  --verbose -s libgazebo_ros_init.so -s libgazebo_ros_factory.so

# T2 — Spawn robot
ros2 run gazebo_ros spawn_entity.py \
  -file ~/digital_twin_ws/src/two_wheel_robot/urdf/two_wheel_robot.urdf \
  -entity robot1 -x 0 -y 0 -z 0.1

# T3 — Robot state publisher
ros2 run robot_state_publisher robot_state_publisher \
  --ros-args \
  -p robot_description:="$(cat ~/digital_twin_ws/src/two_wheel_robot/urdf/two_wheel_robot.urdf)" \
  -p use_sim_time:=true

# T4 — Joint state publisher
ros2 run joint_state_publisher joint_state_publisher \
  --ros-args -p use_sim_time:=true

# T5 — Obstacle avoidance
ros2 run obstacle_avoidance vel_smoother &
ros2 run obstacle_avoidance avoid

# T6 — RViz visualization
rviz2
```

### SLAM Mapping

```bash
# While simulation is running, launch SLAM
ros2 run slam_toolbox async_slam_toolbox_node --ros-args \
  -p use_sim_time:=true \
  -p odom_frame:=odom \
  -p base_frame:=base_link \
  -p scan_topic:=/scan \
  -p mode:=mapping

# Save map when complete
ros2 run nav2_map_server map_saver_cli -f ~/my_warehouse_map
```

### Nav2 Autonomous Navigation

```bash
# Load saved map and launch Nav2
ros2 launch nav2_bringup bringup_launch.py \
  use_sim_time:=true \
  map:=/home/liyana/my_warehouse_map.yaml \
  params_file:=/home/liyana/digital_twin_ws/src/two_wheel_robot/config/nav2_params.yaml
```

In RViz: set Fixed Frame → `map`, click **2D Pose Estimate**, then **2D Goal Pose**.

### Physical Robot (Raspberry Pi)

SSH into RPi and open 4 terminals:

```bash
# T1 — LiDAR (give it a gentle flick to help motor start)
sudo chmod 777 /dev/ttyUSB0
ros2 launch rplidar_ros rplidar_a1_launch.py

# T2 — Serial bridge to Arduino
sudo chmod 666 /dev/ttyACM0
ros2 run obstacle_avoidance serial_bridge

# T3 — Velocity smoother
ros2 run obstacle_avoidance vel_smoother

# T4 — Obstacle avoidance brain
ros2 run obstacle_avoidance avoid
```

---

## 🔍 Core Nodes

### `avoid.py` — Obstacle Avoidance Brain

Subscribes to `/scan`, divides the 360° scan into 3 zones, and publishes velocity commands.

```
Zone Layout (top-down view):
        FRONT (42%–58%)
   LEFT  ←  ROBOT  →  RIGHT
  (58%–75%)          (25%–42%)
```

| Parameter | Value | Description |
|---|---|---|
| `safe_distance` | 0.3m | Full stop + turn threshold |
| `caution_distance` | 0.6m | Slow down + steer threshold |
| `forward_speed` | 0.5 m/s | Normal forward speed |
| `turn_speed` | 0.5 rad/s | Turning angular velocity |

### `vel_smoother.py` — Velocity Smoother

Ramps velocity gradually to prevent jerky motion on physical hardware.

| Parameter | Value |
|---|---|
| Linear acceleration | 0.05 m/s per tick |
| Angular acceleration | Direct (no ramp) |
| Timer rate | Callback-based |

### `serial_bridge.py` — Arduino Communication

Converts ROS2 `/cmd_vel` Twist messages to 2-byte serial commands for Arduino.

```
linear.x → left_byte + right_byte (0–255, center=127)
127 = stop, >127 = forward, <127 = backward
Baud rate: 57600
```

### Arduino `motor_control.ino`

Receives 2 bytes over serial and drives L298N motor driver with PWM.

```cpp
float speed_limit = 1.5;  // 75% max speed (safe for warehouse)
// Deadzone: 124–130 = stop (prevents motor hum)
// constrain(pwm, 0, 255) prevents rollover bug
```

---

## 🗺️ SLAM Map

The warehouse map was generated using `slam_toolbox` in async mapping mode.

![Warehouse Map](docs/images/warehouse_map.png)

- **Black lines** = walls and shelves detected by LiDAR
- **White areas** = free space (robot can navigate)
- **Grey areas** = unexplored regions
- Map saved as: `src/two_wheel_robot/maps/my_warehouse_map.pgm`

---

## 🐛 Known Issues & Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| LiDAR buffer overflow | Pre-compiled binary bug on RPi | Rebuild rplidar_ros from source |
| LiDAR timeout error | Power sag on USB | Give LiDAR a gentle flick; unplug Arduino temporarily |
| `/map` frame not found | AMCL not running | Use `bringup_launch.py` not `navigation_launch.py` |
| Robot not moving | `vel_smoother` not running | Always run vel_smoother before avoid |
| Permission denied `/dev/ttyACM0` | Linux USB permissions | Run `sudo chmod 666 /dev/ttyACM0` |
| One motor not working | Thin wire on L298N output | Replace with thicker wire of equal gauge |
| Robot drifts left/right | Motor mismatch | Adjust `right_limit` in Arduino code |

---

## 📊 Project Status

| Feature | Status |
|---|---|
| URDF robot model | ✅ Complete |
| Gazebo warehouse world | ✅ Complete |
| Zone-based obstacle avoidance | ✅ Complete |
| Velocity smoother | ✅ Complete |
| SLAM map generation | ✅ Complete |
| Nav2 navigation (simulation) | ✅ Working (minor tuning needed) |
| Physical robot assembly | ✅ Complete |
| RPLiDAR integration | ✅ Complete |
| Arduino motor control | ✅ Complete |
| Physical obstacle avoidance | ✅ Complete |
| Demo video | ⬜ Pending |

---

## 🔮 Future Work

- Integrate Nav2 goal navigation on physical robot
- Add camera-based object detection for package identification
- Implement multi-robot coordination for fleet management
- Add waypoint-based delivery path planning
- Battery monitoring and auto-docking

---

## 👥 Team

| Name | Register No | Role |
|---|---|---|
| Nafeesath Liyana Latheef | 23BCARI117 | Simulation, Hardware Integration, ROS2 |
| Muhammed Mishal | - | Hardware Assembly, Testing |




