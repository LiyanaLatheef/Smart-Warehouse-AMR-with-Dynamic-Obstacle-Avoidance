import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import serial
import time

class PhysicalAMR(Node):
    def __init__(self):
        super().__init__('physical_robot_avoidance')
        self.subscription = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        # Settings
        self.safe_distance = 0.5  # Reduced slightly for better stability
        self.last_action = None
        self.last_send_time = 0.0 # To track command timing

        # Open Serial to Arduino Mega
        try:
            # Matches the 115200 baud rate we put in your Arduino code
            self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=0.1)
            time.sleep(2) 
            self.get_logger().info('--- PHYSICAL AMR READY ---')
        except Exception as e:
            self.get_logger().error(f'Serial Error: {e}')
            exit()

    def scan_callback(self, msg):
        ranges = msg.ranges
        total = len(ranges)

        # 1. Improved Filter: Ignore chassis (anything closer than 0.3m)
        def get_min_dist(data):
            valid = [r for r in data if 0.3 < r < 8.0]
            return min(valid) if valid else 8.0 

        # 2. Refined Slices (matching your physical LiDAR zones)
        front = get_min_dist(ranges[int(total*0.44): int(total*0.56)])
        left  = get_min_dist(ranges[int(total*0.56): int(total*0.75)])
        right = get_min_dist(ranges[int(total*0.25): int(total*0.44)])

        # 3. Decision Logic
        if front < self.safe_distance:
            if left > right:
                current_action = 'L'
            else:
                current_action = 'R'
        else:
            current_action = 'F'

        # 4. Serial Command with Protection Logic
        current_time = time.time()
        
        # Only send if the action CHANGED or if it's been 0.1s since last command
        if (current_action != self.last_action) or (current_time - self.last_send_time > 0.1):
            try:
                self.ser.write(current_action.encode())
                self.last_send_time = current_time
                
                # Only log when the movement actually changes to keep terminal clean
                if current_action != self.last_action:
                    dist_display = "CLEAR" if front == 8.0 else f"{front:.2f}m"
                    self.get_logger().info(f'NEW ACTION: {current_action} | DIST: {dist_display}')
                
                self.last_action = current_action
            except Exception as e:
                self.get_logger().error(f"Serial Error: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = PhysicalAMR()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Stopping...')
    finally:
        # Emergency Stop on Shutdown
        if hasattr(node, 'ser'):
            try:
                node.ser.write(b'S') 
                node.ser.close()
            except:
                pass
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
