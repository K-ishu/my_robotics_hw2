from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():
    pkg_share = get_package_share_directory("ros2_kdl_package")
    params_file = os.path.join(pkg_share, "config", "kdl_params.yaml")

    ctrl_arg = DeclareLaunchArgument(
        "ctrl",
        default_value="velocity_ctrl",
        description="Controller mode: velocity_ctrl or velocity_ctrl_null"
    )

    log_path_arg = DeclareLaunchArgument(
        "log_path",
        default_value="/tmp/kdl_control_log.csv",
        description="CSV log path"
    )

    use_action_server_arg = DeclareLaunchArgument(
        "use_action_server",
        default_value="false",
        description="If true, wait for action goal instead of starting trajectory automatically"
    )

    ros2_kdl_node = Node(
        package="ros2_kdl_package",
        executable="ros2_kdl_node",
        name="ros2_kdl_node",
        output="screen",
        parameters=[
            params_file,
            {
                "ctrl": LaunchConfiguration("ctrl"),
                "log_path": LaunchConfiguration("log_path"),
                "use_action_server": LaunchConfiguration("use_action_server"),
            },
        ],
    )

    return LaunchDescription([
        ctrl_arg,
        log_path_arg,
        use_action_server_arg,
        ros2_kdl_node,
    ])
