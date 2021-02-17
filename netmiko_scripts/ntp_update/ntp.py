import netmiko
import csv
import re

##############################################################################################################
#   Format for CSV file is "IP,device_type,usename,password,enable_secret". See device_list.csv for example  #
##############################################################################################################

# Add NTP servers
ntp_server1 = '10.55.55.55'
ntp_server2 = '10.55.55.51'

#Open CSV file and read in devices
with open('device_list.csv') as file:
    devices = csv.reader(file, delimiter=',')

    #Loop through device list and start SSH session
    for device in devices:

        try:
            conn = netmiko.ConnectHandler(device_type=device[1], host=device[0], username=device[2], password=device[3],
                               secret=device[4])
            conn.enable()

        except Exception as e:
            print('f Error encountered while attempting to access device {device[0}')
            print(e)

        try:
            #Collect configured NTP server from device
            out = conn.send_command('show run | in ^ntp server')

            #If there are existing NTP servers then remove them
            #If not no NTP servers are configured then create empty list for new NTP servers
            if out:
                #Remove old NTP servers
                dev_list = out.split('\n')
                for ind, dev in enumerate(dev_list):
                    dev_list[ind] = f'no {dev_list[ind]}'
            else:
                dev_list = []

            #Add new NTP servers
            dev_list.append(f'ntp server {ntp_server1}')
            dev_list.append(f'ntp server {ntp_server2}')
            conn.send_config_set(dev_list)
            conn.save_config()

            #Check device's configuration post-config push to verify NTP servers are updated
            out = conn.send_command('show start | in ^ntp server')
            dev_list = out.split('\n')
            for dev in dev_list:
                if re.search('ntp server 10\.55\.55\.5(1|5)', dev):
                    print(f'NTP server IP {dev} updated and verified on device {device[0]}')
                else:
                    print(f'NTP server configuration verification failed for {device[0]} Please check')

            #Disconnect session
            conn.disconnect()

        except Exception as e:
            print('f Error encountered while attempting to configure device {device[0}')
            print(e)
