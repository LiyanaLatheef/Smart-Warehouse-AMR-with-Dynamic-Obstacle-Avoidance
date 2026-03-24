# 🤖 Smart Warehouse AMR with Dynamic Obstacle Avoidance

A ROS2 Humble simulation of an Autonomous Mobile Robot (AMR) navigating a warehouse environment with LiDAR-based dynamic obstacle avoidance, built in Gazebo 11 and visualized in RViz2.

---

## 📋 Project Overview

| Item | Details |
|---|---|
| **Platform** | Ubuntu 22.04 |
| **ROS Version** | ROS2 Humble |
| **Simulator** | Gazebo 11 |
| **Visualizer** | RViz2 |
| **Robot Type** | Differential Drive AMR |
| **Sensor** | LiDAR (360°) |
| **Workspace** | `~/digital_twin_ws` |

---

## 📁 Repository Structure

```
digital_twin_ws/
├── src/
│   ├── two_wheel_robot/
│   │   ├── urdf/
│   │   │   └── two_wheel_robot.urdf       # Robot model
│   │   └── worlds/
│   │       └── warehouse.world            # Warehouse environment
│   │
│   └── obstacle_avoidance/
│       ├── obstacle_avoidance/
│       │   ├── avoid.py                   # Zone-based obstacle avoidance
│       │   ├── waypoint_nav.py            # Waypoint navigation
│       │   └── vel_smoother.py            # Velocity smoother
│       ├── package.xml
│       ├── setup.py
│       └── setup.cfg
```

---

## ⚙️ System Setup

### 1. Install ROS2 Humble

```bash
sudo apt update && sudo apt install -y curl gnupg lsb-release
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(lsb_release -cs) main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
sudo apt update
sudo apt install -y ros-humble-desktop
echo "source /opt/ros/humble/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 2. Install Gazebo and dependencies

```bash
sudo apt install -y gazebo ros-humble-gazebo-ros-pkgs \
  ros-humble-gazebo-ros2-control python3-colcon-common-extensions
```

### 3. Create the workspace

```bash
mkdir -p ~/digital_twin_ws/src
cd ~/digital_twin_ws
colcon build
source install/setup.bash
```

---

## 🤖 Robot Model (URDF)

The robot (`two_wheel_robot`) is a differential drive AMR with:
- **Base link** — rectangular box chassis
- **Left & Right wheels** — continuous joints
- **Caster wheel** — passive front support
- **LiDAR sensor** — 360° ray sensor publishing to `/scan`
- **Camera link** — mounted at front

### Key URDF parameters:
| Parameter | Value |
|---|---|
| Wheel separation | 0.30 m |
| Wheel diameter | 0.10 m |
| LiDAR range | 0.12 – 8.0 m |
| LiDAR samples | 720 |

### LiDAR Plugin (fix for single type output):
```xml
<plugin name="gazebo_ros_laser" filename="libgazebo_ros_ray_sensor.so">
  <ros>
    <remapping>~/out:=/scan</remapping>
  </ros>
  <output_type>sensor_msgs/LaserScan</output_type>
  <frame_name>lidar_link</frame_name>
</plugin>
```

---

## 🏭 Warehouse Environment

The warehouse world (`warehouse.world`) contains:
- 4 boundary walls
- 6 shelf units arranged in 3 rows
- 4 coloured box obstacles scattered in aisles

---

## 🧠 Nodes

### 1. `avoid.py` — Zone-Based Obstacle Avoidance

Subscribes to `/scan` (LaserScan), divides the scan into **3 zones** (front, left, right), and publishes velocity commands to `/cmd_vel_raw`.

| Zone | Action |
|---|---|
| Front < 0.5m (safe distance) | Stop, turn away from closer side |
| Front < 1.0m (caution zone) | Slow down, steer away |
| All clear | Move forward at full speed |

### 2. `waypoint_nav.py` — Waypoint Navigation

Subscribes to `/odom`, drives the robot to a sequence of (x, y) waypoints using angle error correction.

Default waypoints:
```python
(2.0, 0.0) → (2.0, 3.0) → (0.0, 3.0) → (0.0, 0.0)
```

### 3. `vel_smoother.py` — Velocity Smoother

Sits between navigation nodes and the robot. Subscribes to `/cmd_vel_raw`, applies acceleration ramping, and publishes smooth velocity to `/cmd_vel`.

| Parameter | Value |
|---|---|
| Linear acceleration | 0.02 m/s per tick |
| Angular acceleration | 0.05 rad/s per tick |
| Timer rate | 20 Hz |

---

## 🚀 How to Run

### Step 1 — Build the workspace
```bash
cd ~/digital_twin_ws
colcon build
source install/setup.bash
```

### Step 2 — Launch Gazebo with warehouse world
```bash
gazebo ~/digital_twin_ws/src/two_wheel_robot/worlds/warehouse.world \
  --verbose -s libgazebo_ros_factory.so
```

### Step 3 — Spawn the robot
```bash
ros2 run gazebo_ros spawn_entity.py \
  -file ~/digital_twin_ws/src/two_wheel_robot/urdf/two_wheel_robot.urdf \
  -entity robot1 -x 0 -y 0 -z 0.1
```

### Step 4 — Launch RViz2
```bash
rviz2
```
Add displays: **RobotModel**, **LaserScan** (topic: `/scan`), **TF**. Set fixed frame to `base_link`.

### Step 5 — Run all nodes (separate terminals)
```bash
# Terminal 1 — Velocity smoother
ros2 run obstacle_avoidance vel_smoother

# Terminal 2 — Waypoint navigation
ros2 run obstacle_avoidance waypoint_nav

# Terminal 3 — Obstacle avoidance
ros2 run obstacle_avoidance avoid
```

The robot will now **automatically navigate waypoints** while **avoiding obstacles dynamically**! 🎉

---

## 📡 ROS Topics

| Topic | Type | Description |
|---|---|---|
| `/scan` | `sensor_msgs/LaserScan` | LiDAR data |
| `/cmd_vel` | `geometry_msgs/Twist` | Final robot velocity |
| `/cmd_vel_raw` | `geometry_msgs/Twist` | Raw velocity (before smoothing) |
| `/odom` | `nav_msgs/Odometry` | Robot odometry |
| `/clock` | `rosgraph_msgs/Clock` | Simulation clock |

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|---|---|
| Gazebo server already running | `killall gzserver gzclient` |
| spawn_entity service unavailable | Wait for Gazebo to fully load, retry |
| `/scan` has multiple types | Add `<output_type>sensor_msgs/LaserScan</output_type>` to URDF plugin |
| Package not found after build | `source ~/digital_twin_ws/install/setup.bash` |
| RViz robot model not visible | Set fixed frame to `base_link` |
| SharedMemory RTPS warning | Harmless warning, can be ignored |

---

## 👩‍💻 Author

**Liyana**
Smart Warehouse AMR with Dynamic Obstacle Avoidance
ROS2 Humble | Gazebo 11 | Ubuntu 22.04
