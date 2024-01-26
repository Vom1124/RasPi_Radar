#!/usr/bin/env python3

import os
import sys
import getpass
import rclpy
from rclpy.node import Node
from delphi_esr_msgs.msg import EsrValid1, EsrValid2
from example_interfaces.msg import Float32MultiArray

global radar_data_left
global mountStatus
  
class RadarNode(Node):
    def __init__(self):
        super().__init__('right_radar_node')


        # Create a subscriber to receive long range and medium range data from the radar
        self.radar_subscriber_l = self.create_subscription(EsrValid1, 'radar_1/esr_valid_1', self.receive_radar_data_l, 10)  
        self.radar_subscriber_l  # Prevent unused variable warning
        self.radar_subscriber_m = self.create_subscription(EsrValid2, 'radar_1/esr_valid_2', self.receive_radar_data_m, 10)  
        self.radar_subscriber_m  # Prevent unused variable warning
        
        # Create a publisher to send commands or information to the robot
        self.radar_publisher = self.create_publisher(Float32MultiArray, 'right_radar_data', 10) 

        # Create a timer to publish commands to the radar (if needed)
        self.timer = self.create_timer(1.0, self.publish_radar_data)  


    def receive_radar_data_l(self, msg):
        # Process the received radar data
        global radar_data_left
        radar_data_l = msg
        radar_data_left[0]=radar_data_l.lr_range
        radar_data_left[1]=radar_data_l.lr_angle 
        #self.get_logger().info('Received long range radar data: %s' % radar_data_l)
        
        
    def receive_radar_data_m(self, msg):
        # Process the received radar data
        global radar_data_left
        radar_data_m = msg
        radar_data_left[2]=radar_data_m.mr_range
        radar_data_left[3]=radar_data_m.mr_angle 
        #self.get_logger().info('Received medium range radar data: %s' % radar_data_m)


    def publish_radar_data(self):
        # Create and publish a message to send to the robot
        global radar_data_left
        global fd
        radar_msg_out = Float32MultiArray()
        radar_msg_out.data=radar_data_left
        self.radar_publisher.publish(radar_msg_out)
        print(radar_msg_out.data)
        fd.write("     " + format(radar_msg_out.data[0],'8f')+ ",         " + format(radar_msg_out.data[1],'8f')+ ",           " + format(radar_msg_out.data[2],'8f')+ ",             " + format(radar_msg_out.data[3],'8f')+ "\n")
        
def data_writer():
    # Create a fileinside the USB drive inserted...
    # Must logging in as sudo user
    os.system("sudo -k") # First exiting the sudo mode if already in sudo mode
    sudoPassword = "123"
    os.system("echo '\e[7m \e[91m Logging in as sudo user...\e[0m'")
    os.system("echo %s | sudo -s --stdin" %(sudoPassword))
    os.system("echo '\e[5m \e[32m*Successfully logged in as sudo user!*\e[0m'")
    current_username = getpass.getuser()
    global mountStatus
    os.system("echo %s | sudo -s --stdin" %(sudoPassword))
    isMountsda = os.path.exists("/dev/sda1")
    isMountsdb = os.path.exists("/dev/sdb1")
    isMountsdc = os.path.exists("/dev/sdc1")
    isMountsdd = os.path.exists("/dev/sdd1")

    print("sda status" + str(isMountsda) + "\nsdb status" + \
        str(isMountsdb) + "\nsdc status" + str(isMountsdc) + \
             "\nsdd status" + str(isMountsdd))
        
    if isMountsda==True or isMountsdb==True or isMountsdc==True:   
        mountStatus = True
        
        #Remove/Unmount existing mountpoint to avoid overlap    
        os.system("echo 123| sudo -S umount -f /dev/sd* > /dev/null  2>&1") # the output will be null.       
        
        #Checking if mount point name already exists (Need to create only on the first run).
        isMountPointName = os.path.exists("/media/ESR_Radar")

        os.system("echo 123 | sudo -S chown %s:%s /media/"%(current_username,current_username))
        os.system("echo 123 | sudo -S chown %s:%s /dev/sd*"%(current_username,current_username))
            
        if isMountPointName==True:
            try:
                os.system("echo 123 | sudo -S rm -r /media/*")
                os.system("mkdir /media/ESR_Radar") # Creating a mount point name
            except:
                pass
        elif isMountPointName==False:      
            os.system("mkdir /media/ESR_Radar") # Creating a mount point name
            '''
            The order of checking the mount is reversed to ensure that there 
            is no problem mounting with already preserved mountpoints by the system.
            For example, if sda is already mounted by the system for some port address, then the access to 
            mount the sda for USB drive won't exist. So, the further options will be checked, by in the mean time, the sda in the 
            alphabetical order will throw an error and stop the code. Therefore, the mount check is initiated with sdc.
            Only three /dev/sd* are used, as atmost three ports will be used simultaneously. 
            '''
        if isMountsdd:
            mountCommand = "echo 123| sudo -S mount /dev/sdd1 /media/ESR_Radar -o umask=022,rw,uid=1000,gid=1000"
        elif isMountsdc:
            mountCommand = "echo 123| sudo -S mount /dev/sdc1 /media/ESR_Radar -o umask=022,rw,uid=1000,gid=1000"   
        elif isMountsdb:
            mountCommand = "echo 123| sudo -S mount /dev/sdb1 /media/ESR_Radar -o umask=022,rw,uid=1000,gid=1000"    
        elif isMountsda:
            mountCommand = "echo 123| sudo -S mount /dev/sda1 /media/ESR_Radar -o umask=022,rw,uid=1000,gid=1000"
            
        os.system(mountCommand)    
        
    else:
       
        mountStatus = False
        return
    
        


def main(args=None):
    rclpy.init(args=args)
    global fd
    global radar_data_left
    radar_data_left=[0.0,0.0,0.0,0.0] 
    radar_node = RadarNode()
    data_writer() # Running this method to mount the USB drive properly.
    if mountStatus==True:
        os.system("echo '\e[33mINFO: Mount status success: a USB drive is found.\e[0m'")
        fd = open("/media/ESR_Radar/radar_data.txt","wt") # Creating the actual file 
    else:
        os.system("echo '\e[33mINFO: Mount status FAILURE: no USB is inserted.\e[0m'")
        fd = open("radar_data.txt","wt") # Creating the actual file
    fd.write("Target LRange [m],   LRange Angle [deg],  Target MRange [m],  MRange Angle [deg]\n") 
    fd.write("================================================================================\n")    
    rclpy.spin(radar_node)
    radar_node.destroy_node()
    rclpy.shutdown()
    fd.close()

if __name__ == '__main__':
    main()
