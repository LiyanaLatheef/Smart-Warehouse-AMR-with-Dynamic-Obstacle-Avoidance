#!/bin/bash
# =============================================================================
#  🤖 Smart Warehouse AMR — Raspberry Pi One-Command Launcher
#  Project: Smart Warehouse AMR with Dynamic Obstacle Avoidance
#  Student: Nafeesath Liyana Latheef (23BCARI117)
#  Guide:   Rakesh K K
# =============================================================================
# HOW TO SAVE AND RUN:
#   1. Copy this file to your Raspberry Pi:
#      scp start_robot.sh pi@172.20.10.2:~/start_robot.sh
#   2. SSH into RPi:
#      ssh pi@172.20.10.2
#   3. Make it executable:
#      chmod +x ~/start_robot.sh
#   4. Run it:
#      cd ~/robot_ws && ./start_robot.sh
# =============================================================================

echo -e "\n\033[1;36m"
echo "  ███████╗███╗   ███╗ █████╗ ██████╗ ████████╗"
echo "  ██╔════╝████╗ ████║██╔══██╗██╔══██╗╚══██╔══╝"
echo "  ███████╗██╔████╔██║███████║██████╔╝   ██║   "
echo "  ╚════██║██║╚██╔╝██║██╔══██║██╔══██╗   ██║   "
echo "  ███████║██║ ╚═╝ ██║██║  ██║██║  ██║   ██║   "
echo "  ╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   "
echo -e "\033[1;33m  Smart Warehouse AMR — Dynamic Obstacle Avoidance\033[0m"
echo -e "\033[0m"

# =============================================================================
# CLEANUP — kills all nodes when CTRL+C is pressed
# =============================================================================
cleanup() {
    echo -e "\n\033[1;33m[!] CTRL+C detected. Stopping all nodes...\033[0m"
    pkill -f rplidar
    pkill -f serial_bridge
    pkill -f vel_smoother
    pkill -f avoid
    echo -e "\033[1;32m[✔] All nodes stopped. Robot is safe!\033[0m"
    exit 0
}
trap cleanup SIGINT SIGTERM

# =============================================================================
# STEP 1 — Hardware Permissions
# =============================================================================
echo -e "\033[1;34m[STEP 1/5]\033[0m Checking hardware permissions..."

# LiDAR — RPLiDAR A1
if [ -e /dev/ttyUSB0 ]; then
    sudo chmod 777 /dev/ttyUSB0
    echo "  ✅ /dev/ttyUSB0 — LiDAR ready"
elif [ -e /dev/ttyUSB1 ]; then
    sudo chmod 777 /dev/ttyUSB1
    echo "  ✅ /dev/ttyUSB1 — LiDAR ready (on USB1)"
    # Update launch to use USB1
    export RPLIDAR_PORT=/dev/ttyUSB1
else
    echo "  ⚠️  LiDAR not found! Check USB connection."
fi

# Arduino Mega
if [ -e /dev/ttyACM0 ]; then
    sudo chmod 666 /dev/ttyACM0
    echo "  ✅ /dev/ttyACM0 — Arduino ready"
else
    echo "  ⚠️  Arduino not found! Check USB connection."
fi

# =============================================================================
# STEP 2 — Source ROS2 and workspace
# =============================================================================
echo -e "\n\033[1;34m[STEP 2/5]\033[0m Sourcing ROS2 environment..."

source /opt/ros/humble/setup.bash

if [ -f "$HOME/robot_ws/install/setup.bash" ]; then
    source $HOME/robot_ws/install/setup.bash
    echo "  ✅ robot_ws sourced successfully"
else
    echo "  ❌ ERROR: ~/robot_ws/install/setup.bash not found!"
    echo "  Run: cd ~/robot_ws && colcon build"
    exit 1
fi

# =============================================================================
# STEP 3 — Launch LiDAR (Eyes)
# =============================================================================
echo -e "\n\033[1;34m[STEP 3/5]\033[0m Launching RPLiDAR A1 (Eyes)..."
ros2 launch rplidar_ros rplidar_a1_launch.py &
LIDAR_PID=$!
sleep 3

# Check if LiDAR started
if ros2 topic list 2>/dev/null | grep -q "/scan"; then
    echo "  ✅ /scan topic is publishing!"
else
    echo "  ⚠️  /scan not detected yet — give LiDAR a gentle flick if needed"
fi

# =============================================================================
# STEP 4 — Launch Serial Bridge (Nervous System)
# =============================================================================
echo -e "\n\033[1;34m[STEP 4/5]\033[0m Launching Serial Bridge (Arduino communication)..."
ros2 run obstacle_avoidance serial_bridge &
BRIDGE_PID=$!
sleep 2
echo "  ✅ Serial bridge started → /dev/ttyACM0 @ 57600 baud"

# =============================================================================
# STEP 5 — Launch Navigation Nodes (Brain + Muscles)
# =============================================================================
echo -e "\n\033[1;34m[STEP 5/5]\033[0m Launching Velocity Smoother + Obstacle Avoidance Brain..."
ros2 run obstacle_avoidance vel_smoother &
SMOOTHER_PID=$!
sleep 1

ros2 run obstacle_avoidance avoid &
AVOID_PID=$!
sleep 2

# =============================================================================
# STATUS REPORT
# =============================================================================
echo -e "\n\033[1;32m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo -e "\033[1;32m✅ ALL NODES LAUNCHED — Robot is now autonomous!\033[0m"
echo -e "\033[1;32m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\033[0m"
echo ""
echo "  📡 Topics:  /scan → avoid.py → /cmd_vel_raw"
echo "              → vel_smoother → /cmd_vel"
echo "              → serial_bridge → Arduino → Motors"
echo ""
echo "  🔧 Nodes running:"
echo "     /rplidar_node    — LiDAR scanning at 10Hz"
echo "     /serial_bridge   — RPi ↔ Arduino @ 57600 baud"
echo "     /vel_smoother    — Velocity ramping"
echo "     /obstacle_avoidance — Zone-based avoidance"
echo ""
echo "  ⚡ Safe distance: 0.3m | Caution: 0.6m | Speed: 0.5 m/s"
echo ""
echo -e "  Press \033[1;31m[CTRL+C]\033[0m to stop all nodes safely\n"

# Keep running and show live avoid node output
wait
