import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/bhimirs/Documents/robotics/ros-lab-2-siddhu/install/py_pubsub'
