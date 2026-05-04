# Robotics Lab 2025 - Homework 2

Student: Kishu  
Repository: https://github.com/K-ishu/my_robotics_hw2

This repository contains the implementation for Robotics Lab 2025 Homework 2.

The goal of this homework is to develop kinematic and vision-based control tools for a robotic manipulator arm in simulation using KDL, the IIWA robot stack, Gazebo/Ignition Gazebo, `ros_gz_bridge`, and `aruco_ros`.

The repository is based on the provided starting packages:

- `ros2_kdl_package`
- `ros2_iiwa`
- `aruco_ros`

## Implemented Parts

- **1(a)** ROS 2 parameters, YAML configuration, and launch file for `ros2_kdl_node`
- **1(b)** Velocity controller with joint-limit null-space term: `velocity_ctrl_null`
- **2(a)** Gazebo world with ArUco marker and ArUco detection using `aruco_ros`
- **2(c)** ROS 2 service bridge for moving the ArUco marker in Gazebo

## Tested Environment

- Ubuntu 22.04
- ROS 2 Humble
- Ignition Gazebo / Gazebo Sim
- `ros_gz_sim`
- `ros_gz_bridge`
- `ros2_control`
- `aruco_ros`

## Repository Structure

    my_robotics_hw2/
    - aruco_ros/
    - ros2_iiwa/
      - iiwa_bringup/
        - launch/
          - iiwa.launch.py
          - iiwa_aruco_detection.launch.py
      - iiwa_description/
        - gazebo/
          - models/
            - aruco_tag/
          - worlds/
            - iiwa_aruco_world.sdf
          - iiwa_camera.xacro
        - config/
          - iiwa.config.xacro
          - iiwa_controllers.yaml
    - ros2_kdl_package/
      - config/
        - kdl_params.yaml
      - launch/
        - ros2_kdl.launch.py
      - include/
        - kdl_control.h
      - src/
        - kdl_control.cpp
        - ros2_kdl_node.cpp
    - README.md

## Required Dependencies

Install the required packages:

    sudo apt update

    sudo apt install -y \
      ros-humble-ros-gz-sim \
      ros-humble-ros-gz-bridge \
      ros-humble-ros-gz-interfaces \
      ros-humble-ros2-controllers \
      ros-humble-ros2controlcli \
      ros-humble-controller-manager \
      ros-humble-xacro \
      ros-humble-kdl-parser \
      ros-humble-orocos-kdl-vendor \
      ros-humble-rqt-image-view

## Build Instructions

Place the repository inside a ROS 2 workspace:

    mkdir -p ~/ros2_hw2_ws/src
    cd ~/ros2_hw2_ws/src
    git clone https://github.com/K-ishu/my_robotics_hw2.git

Build the workspace:

    cd ~/ros2_hw2_ws
    source /opt/ros/humble/setup.bash
    colcon build --symlink-install
    source install/setup.bash

## 1(a) KDL Parameterized Launch

The following variables were converted into ROS 2 parameters:

- `traj_duration`
- `acc_duration`
- `total_time`
- `trajectory_len`
- `Kp`
- `end_position_x`
- `end_position_y`
- `end_position_z`

The parameters are stored in:

    ros2_kdl_package/config/kdl_params.yaml

The KDL node is launched through:

    ros2_kdl_package/launch/ros2_kdl.launch.py

First, start the IIWA simulation with the velocity command interface:

    cd ~/ros2_hw2_ws
    source install/setup.bash

    ros2 launch iiwa_bringup iiwa.launch.py \
      use_sim:=true \
      command_interface:=velocity \
      robot_controller:=velocity_controller \
      start_rviz:=false

In another terminal, run the KDL node:

    cd ~/ros2_hw2_ws
    source install/setup.bash

    ros2 launch ros2_kdl_package ros2_kdl.launch.py

## 1(b) Velocity Controller with Null-Space Joint-Limit Avoidance

A new controller mode named `velocity_ctrl_null` was added.

The controller can be selected through the ROS 2 parameter:

    ctrl:=velocity_ctrl|velocity_ctrl_null

Run the standard velocity controller:

    cd ~/ros2_hw2_ws
    source install/setup.bash

    ros2 launch ros2_kdl_package ros2_kdl.launch.py \
      ctrl:=velocity_ctrl \
      log_path:=/tmp/kdl_velocity_ctrl.csv

Run the null-space velocity controller:

    cd ~/ros2_hw2_ws
    source install/setup.bash

    ros2 launch ros2_kdl_package ros2_kdl.launch.py \
      ctrl:=velocity_ctrl_null \
      log_path:=/tmp/kdl_velocity_ctrl_null.csv

Generate comparison plots:

    cd ~/ros2_hw2_ws
    python3 results/plot_kdl_results.py

The generated plots compare:

- commanded joint velocities
- measured joint positions
- end-effector position error norm

## 2(a) ArUco Marker Detection in Gazebo

A custom Gazebo world was created:

    ros2_iiwa/iiwa_description/gazebo/worlds/iiwa_aruco_world.sdf

The ArUco marker model is stored in:

    ros2_iiwa/iiwa_description/gazebo/models/aruco_tag

The world contains:

- a static ArUco marker model named `aruco_tag`
- a static observer camera named `aruco_observer_camera`
- Gazebo camera topics bridged to ROS 2
- an `aruco_ros single` detector node

Launch the ArUco detection setup:

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
    /aruco_single/position
    /aruco_single/transform

Check camera information:

    ros2 topic echo /iiwa_camera/camera_info --once

Visualize the camera or ArUco result image:

    ros2 run rqt_image_view rqt_image_view

Select one of:

    /iiwa_camera/image
    /aruco_single/debug
    /aruco_single/result

## 2(c) Move the ArUco Marker Through a ROS 2 Service

The launch file also starts a ROS 2 bridge for the Gazebo `/set_pose` service.

Launch the detection setup:

    cd ~/ros2_hw2_ws
    source install/setup.bash

    ros2 launch iiwa_bringup iiwa_aruco_detection.launch.py

Check that the service exists:

    ros2 service find ros_gz_interfaces/srv/SetEntityPose
    ros2 service type /world/iiwa_aruco_world/set_pose

Expected output:

    /world/iiwa_aruco_world/set_pose
    ros_gz_interfaces/srv/SetEntityPose

Move the marker:

    ros2 service call /world/iiwa_aruco_world/set_pose ros_gz_interfaces/srv/SetEntityPose "{
      entity: {name: 'aruco_tag', type: 2},
      pose: {
        position: {x: 0.75, y: 0.0, z: 0.65},
        orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
      }
    }"

Expected response:

    success: true

Verify the marker pose in Gazebo:

    ign model -m aruco_tag --pose

Expected result after the service call:

    Pose [ XYZ (m) ]:
    [0.750000 0.000000 0.650000]

A second test position can be sent with:

    ros2 service call /world/iiwa_aruco_world/set_pose ros_gz_interfaces/srv/SetEntityPose "{
      entity: {name: 'aruco_tag', type: 2},
      pose: {
        position: {x: 0.55, y: 0.15, z: 0.75},
        orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}
      }
    }"

## Useful Verification Commands

List active controllers:

    ros2 control list_controllers

Check camera and ArUco topics:

    ros2 topic list | grep -E "iiwa_camera|aruco"

Check Gazebo models:

    ign model --list

Check ArUco marker pose:

    ign model -m aruco_tag --pose

Check the set-pose bridge:

    ros2 service find ros_gz_interfaces/srv/SetEntityPose

## Notes

The ArUco detection launch file is:

    ros2_iiwa/iiwa_bringup/launch/iiwa_aruco_detection.launch.py

The KDL launch file is:

    ros2_kdl_package/launch/ros2_kdl.launch.py

The KDL parameter YAML file is:

    ros2_kdl_package/config/kdl_params.yaml

The current implementation completes parts 1(a), 1(b), 2(a), and 2(c). Parts 1(c) and 2(b) are still under development.
