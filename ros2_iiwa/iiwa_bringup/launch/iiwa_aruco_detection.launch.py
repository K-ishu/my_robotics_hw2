from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, EnvironmentVariable
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
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

    marker_id = LaunchConfiguration("marker_id")
    marker_size = LaunchConfiguration("marker_size")

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            FindPackageShare("ros_gz_sim"),
            "/launch/gz_sim.launch.py",
        ]),
        launch_arguments={
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
            "/world/iiwa_aruco_world/set_pose@ros_gz_interfaces/srv/SetEntityPose@ignition.msgs.Pose@ignition.msgs.Boolean",
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
            ("/image", "/iiwa_camera/image"),
            ("/camera_info", "/iiwa_camera/camera_info"),
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument("marker_id", default_value="25"),
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

        gz_sim,
        camera_bridge,
        set_pose_bridge,
        aruco_single,
    ])
