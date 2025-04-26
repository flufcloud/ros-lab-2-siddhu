# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import math
import rclpy
import time
import random

from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan


class PubSub(Node):

    def __init__(self):
        super().__init__('minimal_publisher')
        self.publisher_ = self.create_publisher(Twist, '/diff_drive/cmd_vel', 10)
        self.subscriber = self.create_subscription(LaserScan, '/diff_drive/scan', self.scan_callback, 10)
        timer_period = 3  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.state = 0
        self.i = 0
        self.lscan = LaserScan()
        self.low_passed = []
        self.alpha = 0.6

    def timer_callback(self):
        if not self.low_passed: 
            self.get_logger().info('Empty scan received') 
            return
        
        print(self.lscan)
        msg = Twist()
        if (self.low_passed[1] < 1.0):
            # tell it to reverse
            self.state = -1

        if self.state == 0:
            # forward
            msg.linear.x = 5.0
            msg.angular.z = 0.0
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing (STATE = FORWARD): "%s"' % str(msg))
            self.i += 1

            # default state
        elif self.state == -1:
            # reverse
            msg.linear.x = -3.5
            msg.angular.z = 0.0
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: (STATE = REVERSE) "%s"' % str(msg))
            self.i += 1

            # move to turning
            self.state = 1
        elif self.state == 1:
            # turn
            r = random.random()
            if (r > 0.5): r = -1
            else: r = 1

            msg.linear.x = 0.0
            msg.angular.z = r * 0.6    
            self.publisher_.publish(msg)
            self.get_logger().info('Publishing: (STATE = TURNING) "%s"' % str(msg))
            self.i += 1

            # go forward
            self.state = 0
    
    def scan_callback(self, laser_scan):
        self.lscan = laser_scan
        if math.isnan(laser_scan.ranges[0]) or math.isinf(laser_scan.ranges[0]):
            return 
        if not self.low_passed:
            self.low_passed.append(laser_scan.ranges[0])
            self.low_passed.append(laser_scan.ranges[0])
        else:
            self.low_passed[1] = (self.alpha * self.low_passed[0]) +  ((1 - self.alpha) * laser_scan.ranges[0])
            self.low_passed[0] = laser_scan.ranges[0]

def main(args=None):
    rclpy.init(args=args)

    mazeBot = PubSub()

    rclpy.spin(mazeBot)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    mazeBot.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
