from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, EnvironmentVariable
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    marker_id = LaunchConfiguration("marker_id")
    marker_size = LaunchConfiguration("marker_size")

    world_file = PathJoinSubstitution([
        FindPackageShare("iiwa_description"),
        "gazebo",
        "worlds",
        "iiwa_aruco_world.sdf",
    ])

    gazebo_models_path = PathJoinSubstitution([
        FindPackageShare("iiwa_description"),
        "gazebo",
        "models",
    ])

    gazebo_resource_path = PathJoinSubstitution([
        FindPackageShare("iiwa_description"),
        "gazebo",
    ])

    iiwa_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("iiwa_bringup"),
            "/launch/iiwa.launch.py",
        ]),
        launch_arguments={
            "use_sim": "true",
            "use_fake_hardware": "false",
            "command_interface": "velocity",
            "robot_controller": "velocity_controller",
            "start_rviz": "false",
            "gz_args": ["-r -v 4 ", world_file],
        }.items(),
    )

    camera_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="iiwa_camera_bridge",
        output="screen",
        arguments=[
            "/iiwa_camera/image@sensor_msgs/msg/Image@gz.msgs.Image",
            "/iiwa_camera/camera_info@sensor_msgs/msg/CameraInfo@gz.msgs.CameraInfo",
        ],
    )

    set_pose_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="aruco_set_pose_bridge",
        output="screen",
        arguments=[
            "/world/iiwa_aruco_world/set_pose@ros_gz_interfaces/srv/SetEntityPose@ignition.msgs.Pose@ignition.msgs.Boolean@ignition.msgs.Pose@ignition.msgs.Boolean",
        ],
    )

    aruco_single = Node(
        package="aruco_ros",
        executable="single",
        name="aruco_single",
        output="screen",
        parameters=[{
            "marker_id": marker_id,
            "marker_size": marker_size,
            "reference_frame": "aruco_observer_camera/camera_link/iiwa_camera",
            "camera_frame": "aruco_observer_camera/camera_link/iiwa_camera",
            "marker_frame": "aruco_marker",
            "image_is_rectified": True,
        }],
        remappings=[
            ("image", "/iiwa_camera/image"),
            ("camera_info", "/iiwa_camera/camera_info"),
        ],
    )

    vision_node = Node(
        package="ros2_kdl_package",
        executable="ros2_kdl_node",
        name="ros2_kdl_node",
        output="screen",
        parameters=[{
            "cmd_interface": "velocity",
            "ctrl": "vision",
        }],
    )

    return LaunchDescription([
        DeclareLaunchArgument("marker_id", default_value="26"),
        DeclareLaunchArgument("marker_size", default_value="0.20"),

        SetEnvironmentVariable(
            name="IGN_GAZEBO_RESOURCE_PATH",
            value=[
                gazebo_resource_path,
                ":",
                gazebo_models_path,
                ":",
                EnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", default_value=""),
            ],
        ),

        iiwa_launch,
        camera_bridge,
        TimerAction(period=5.0, actions=[set_pose_bridge]),
        TimerAction(period=6.0, actions=[aruco_single]),
        TimerAction(period=8.0, actions=[vision_node]),
    ])
