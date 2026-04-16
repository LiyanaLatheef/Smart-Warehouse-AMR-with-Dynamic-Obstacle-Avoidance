import os
from launch import LaunchDescription
from launch.actions import ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():

    # =========================================================================
    # PATHS — update these if your workspace is in a different location
    # =========================================================================
    ws_dir     = os.path.expanduser('~/digital_twin_ws')
    urdf_file  = os.path.join(ws_dir, 'src/two_wheel_robot/urdf/two_wheel_robot.urdf')
    world_file = os.path.join(ws_dir, 'src/two_wheel_robot/worlds/warehouse.world')
    map_file   = os.path.expanduser('/home/liyana/my_warehouse_map.yaml')
    nav2_params = os.path.join(ws_dir, 'src/two_wheel_robot/config/nav2_params.yaml')

    # Read URDF
    with open(urdf_file, 'r') as f:
        robot_description_content = f.read()

    # =========================================================================
    # 1. Gazebo — with ROS2 bridge plugins
    # =========================================================================
    start_gazebo = ExecuteProcess(
        cmd=[
            'gazebo', '--verbose',
            '-s', 'libgazebo_ros_init.so',
            '-s', 'libgazebo_ros_factory.so',
            world_file
        ],
        additional_env={
            'GAZEBO_PLUGIN_PATH': '/opt/ros/humble/lib:'
        },
        output='screen'
    )

    # =========================================================================
    # 2. Robot State Publisher
    # =========================================================================
    start_robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': True
        }]
    )

    # =========================================================================
    # 3. Joint State Publisher
    # =========================================================================
    start_joint_state_publisher = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    # =========================================================================
    # 4. Spawn Robot (delayed 5 seconds to let Gazebo fully open)
    # =========================================================================
    spawn_robot = TimerAction(
        period=5.0,
        actions=[
            Node(
                package='gazebo_ros',
                executable='spawn_entity.py',
                arguments=[
                    '-file', urdf_file,
                    '-entity', 'robot1',
                    '-x', '0',
                    '-y', '0',
                    '-z', '0.1'
                ],
                output='screen'
            )
        ]
    )

    # =========================================================================
    # 5. Nav2 Stack (delayed 8 seconds to let TF frames be ready)
    #    NOTE: avoid.py is NOT launched here — Nav2 controls cmd_vel
    # =========================================================================
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    start_nav2 = TimerAction(
        period=8.0,
        actions=[
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')
                ),
                launch_arguments={
                    'use_sim_time': 'true',
                    'map': map_file,
                    'params_file': nav2_params
                }.items()
            )
        ]
    )

    # =========================================================================
    # 6. RViz (delayed 10 seconds to let Nav2 start first)
    # =========================================================================
    start_rviz = TimerAction(
        period=10.0,
        actions=[
            Node(
                package='rviz2',
                executable='rviz2',
                output='screen',
                parameters=[{'use_sim_time': True}]
            )
        ]
    )

    # =========================================================================
    # LAUNCH EVERYTHING
    # =========================================================================
    return LaunchDescription([
        start_gazebo,                   # T=0s  — Gazebo opens
        start_robot_state_publisher,    # T=0s  — TF publisher starts
        start_joint_state_publisher,    # T=0s  — Joint states start
        spawn_robot,                    # T=5s  — Robot spawns in Gazebo
        start_nav2,                     # T=8s  — Nav2 + AMCL + map server
        start_rviz,                     # T=10s — RViz opens
    ])
