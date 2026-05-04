# Robotics Lab 2025 - Homework 2

Student: Kishu  
Repository: https://github.com/K-ishu/my_robotics_hw2

This repository contains the implementation for Robotics Lab 2025 Homework 2.  
It is based on the provided `ros2_kdl_package`, `ros2_iiwa`, and `aruco_ros` packages.

## Implemented parts

- **1(a)** ROS 2 parameters, YAML configuration, and launch file for `ros2_kdl_node`
- **1(b)** Velocity controller with joint-limit null-space term: `velocity_ctrl_null`
- **2(a)** Gazebo world with ArUco marker and ArUco detection using `aruco_ros`
- **2(c)** ROS 2 service bridge for moving the ArUco marker in Gazebo

## Build

From the workspace root:

```bash
cd ~/ros2_hw2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
1(a) KDL parameterized launch

Start the robot simulation with the velocity controller:
ros2 launch iiwa_bringup iiwa.launch.py \
  use_sim:=true \
  command_interface:=velocity \
  robot_controller:=velocity_controller \
  start_rviz:=false
In another terminal, run the KDL node with parameters loaded from YAML:
cd ~/ros2_hw2_ws
source install/setup.bash

ros2 launch ros2_kdl_package ros2_kdl.launch.py
1(b) Velocity controller comparison

Run the standard velocity controller:ros2 launch ros2_kdl_package ros2_kdl.launch.py \
  ctrl:=velocity_ctrl \
  log_path:=/tmp/kdl_velocity_ctrl.csv
Run the null-space velocity controller:
ros2 launch ros2_kdl_package ros2_kdl.launch.py \
  ctrl:=velocity_ctrl_null \
  log_path:=/tmp/kdl_velocity_ctrl_null.csv
Generate comparison plots:
cd ~/ros2_hw2_ws
python3 results/plot_kdl_results.py
The plots compare:

commanded joint velocities
measured joint positions
end-effector position error norm
2(a) ArUco marker detection in Gazebo

Launch the custom ArUco world, camera bridge, and ArUco detector:
cd ~/ros2_hw2_ws
source install/setup.bash

ros2 launch iiwa_bringup iiwa_aruco_detection.launch.py
Check camera and ArUco topics:
ros2 topic list | grep -E "iiwa_camera|aruco"
Expected topics include:
/iiwa_camera/image
/iiwa_camera/camera_info
/aruco_single/debug
/aruco_single/result
/aruco_single/pose
/aruco_single/marker
To visualize the image stream:
ros2 run rqt_image_view rqt_image_view
select one of:
ros2 service find ros_gz_interfaces/srv/SetEntityPose
ros2 service type /world/iiwa_aruco_world/set_pose
Move the maker:
ros2 service call /world/iiwa_aruco_world/set_pose ros_gz_interfaces/srv/SetEntityPose "{
  entity: {name: 'aruco_tag', type: 2},
  pose: {
    position: {x: 0.75, y: 0.0, z: 0.65},
    orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
  }
}"
Verify the marker pose in Gazebo:
ign model -m aruco_tag --pose
Expected result after the service call:
Pose [ XYZ (m) ]:
[0.750000 0.000000 0.650000]
Notes

The ArUco detection world is stored in:
ros2_iiwa/iiwa_description/gazebo/worlds/iiwa_aruco_world.sdf
The ArUco model is stored in:
ros2_iiwa/iiwa_description/gazebo/models/aruco_tag
The detection launch file is:
ros2_iiwa/iiwa_bringup/launch/iiwa_aruco_detection.launch.py
