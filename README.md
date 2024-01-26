# Delphi ESR Radar in Raspberry Pi running in Ubunty 22.04 with ROS2 Humble OS.

## Pre-Requisites:

  Install the required Delphi ESR drivers for ros2 humble OS designed for ARM architecture (for RasPi) using their contact info. In case of regular computers running in AMD architecture, then use the following link:         https://autonomoustuff.atlassian.net/wiki/spaces/RW/pages/17475947/Driver+Pack+Installation+or+Upgrade+Instructions.

## Starting the drivers:
  Once the drivers are installed, use the following set of codes for the CAN bus communication and starting the nodes.

      sudo ip link set up can0 type can bitrate 500000

      ros2 launch delphi_esr delphi_esr_can.launch.xml

      ros2 launch delphi_esr delphi_esr_viz.launch.xml
