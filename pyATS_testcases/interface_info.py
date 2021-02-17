from pyats import aetest
from genie.testbed import load
from genie.conf.base import Interface
import time
from genie.utils.diff import Diff
import logging
from pprint import pprint
from unicon.core.errors import ConnectionError
from genie.metaparser.util.exceptions import SchemaEmptyParserError
import getpass

log = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):

    #test case execute section

    @aetest.subsection
    def connect(self, testbed):
        dev_list = {}
        #connect to devices
        testbed = load(testbed)
        devices = testbed.devices
        for name in devices.keys():
            device = devices[name]
            try:
                device.connect(connection_timeout=5)
            except ConnectionError:
                log.info(f'Connection attempt failed to - {name}')
                continue
            dev_list[name] = device
        self.parent.parameters.update(dev=dev_list)

class testcase01(aetest.Testcase):
    @aetest.test
    def test01(self):

#Assign device dictionary list to a local dictionary object
        self.devices = self.parent.parameters['dev']

        #Create empty dictionary for storing all route results
        self.pre_dic = {}


        #Loop over device dictionary
        for self.name, self.dev_name in self.devices.items():

            log.info(f'*******  Learning and Processing details for {self.name}  *******')

            #create outer dictionary entry per device
            self.pre_dic[self.name] = {}



            #determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
            if self.dev_name.os == 'iosxr':
                try:
                    interfaces = self.dev_name.parse('show interfaces')
                except SchemaEmptyParserError:
                    interfaces = {}


                if interfaces:
                    for interface in interfaces.keys():

                        # limited data colleciton for loopback interfaces
                        if 'loop' in interface or 'Loop' in interface:
                            int_oper_state = interfaces[interface]['oper_status']
                            int_enabled = interfaces[interface]['enabled']

                            self.pre_dic[self.name].update(
                                {interface: {'int_oper_state': int_oper_state,
                                             'int_enabled': int_enabled}})
                            continue

                        elif "Null" in interface:
                            continue


                        int_link_state = interfaces[interface]['line_protocol']
                        int_oper_state = interfaces[interface]['oper_status']
                        int_enabled = interfaces[interface]['enabled']
                        mtu = interfaces[interface]['mtu']

                        # We can only pull IP address if it exists in dictionary
                        if 'ipv4' in interfaces[interface]:
                            ipv4_ip = interfaces[interface]['ipv4']
                        else:
                            ipv4_ip = ''

                        # We can only pull portmode info if it exists in dictionary. Only on switches
                        if 'port_mode' in interfaces[interface]:
                            switchport_mode = interfaces[interface]['port_mode']
                        else:
                            switchport_mode = ''

                        # We can only pull duplex mode info if it exists in dictionary
                        if 'duplex_mode' in interfaces[interface]:
                            duplex = interfaces[interface]['duplex_mode']
                        else:
                            duplex = ''

                        # We can only pull port speed info if it exists in dictionary
                        if 'port_speed' in interfaces[interface]:
                            speed = interfaces[interface]['port_speed']
                        else:
                            speed = ''

                        # Some interface details don't apply to MGMT
                        if ('mgmt' not in interface) or ('Mgmt' not in interface):
                            input_errors = interfaces[interface]['counters']['in_errors']
                            output_errors = interfaces[interface]['counters']['out_errors']
                            output_drops = interfaces[interface]['counters']['out_total_drops']
                        else:
                            input_errors = ''
                            output_errors = ''
                            output_drops = ''


                        self.pre_dic[self.name].update(
                            {interface: {'int_link_state': int_link_state, 'int_oper_state': int_oper_state,
                                                 'ipv4_ip': ipv4_ip, 'mtu': mtu, 'input_errors': input_errors,
                                                 'output_errors': output_errors, 'output_drops': output_drops,
                                                 'int_enabled': int_enabled, 'duplex': duplex, 'speed': speed,
                                                 'switchport_mode': switchport_mode}})


            elif self.dev_name.os == 'nxos':
                try:
                    interfaces = self.dev_name.parse('show interface')
                except SchemaEmptyParserError:
                    interfaces = {}


                if interfaces:
                    for interface in interfaces.keys():

                        # limited data colleciton for loopback interfaces
                        if 'loop' in interface or 'Loop' in interface:
                            int_oper_state = interfaces[interface]['oper_status']
                            int_enabled = interfaces[interface]['enabled']

                            self.pre_dic[self.name].update(
                                {interface: {'int_oper_state': int_oper_state,
                                             'int_enabled': int_enabled}})
                            continue

                        int_link_state = interfaces[interface]['link_state']
                        int_oper_state = interfaces[interface]['oper_status']
                        int_enabled = interfaces[interface]['enabled']
                        mtu = interfaces[interface]['mtu']


                        #We can only pull IP address if it exists in dictionary
                        if 'ipv4' in interfaces[interface]:
                            ipv4_ip = interfaces[interface]['ipv4']
                        else:
                            ipv4_ip = ''

                        #We can only pull portmode info if it exists in dictionary. Only on switches
                        if 'port_mode' in interfaces[interface]:
                            switchport_mode = interfaces[interface]['port_mode']
                        else:
                            switchport_mode = ''

                        # We can only pull duplex mode info if it exists in dictionary
                        if 'duplex_mode' in interfaces[interface]:
                            duplex = interfaces[interface]['duplex_mode']
                        else:
                            duplex = ''

                        # We can only pull port speed info if it exists in dictionary
                        if 'port_speed' in interfaces[interface]:
                            speed = interfaces[interface]['port_speed']
                        else:
                            speed = ''


                        #Some interface details don't apply to MGMT
                        if 'mgmt' not in interface:
                            input_errors = interfaces[interface]['counters']['in_errors']
                            output_errors = interfaces[interface]['counters']['out_errors']
                            output_drops = interfaces[interface]['counters']['out_discard']
                        else:
                            input_errors = ''
                            output_errors = ''
                            output_drops = ''


                        self.pre_dic[self.name].update({interface: {'int_link_state': int_link_state, 'int_oper_state': int_oper_state,
                                                                 'ipv4_ip': ipv4_ip, 'mtu': mtu, 'input_errors': input_errors,
                                                                  'output_errors': output_errors, 'output_drops': output_drops,
                                                                  'int_enabled': int_enabled, 'duplex': duplex, 'speed': speed,
                                                                  'switchport_mode': switchport_mode}})

                else:
                    log.info(f'{self.name} Trouble pulling interface data from interface. Skipping')


            elif self.dev_name.os == 'ios' or self.dev_name.os == 'iosxe':
                try:
                    interfaces = self.dev_name.parse('show interfaces')
                except SchemaEmptyParserError:
                    interfaces = {}

                if interfaces:
                    for interface in interfaces.keys():

                        # limited data colleciton for loopback interfaces
                        if 'loop' in interface or 'Loop' in interface:
                            int_oper_state = interfaces[interface]['oper_status']
                            int_enabled = interfaces[interface]['enabled']

                            self.pre_dic[self.name].update(
                                {interface: {'int_oper_state': int_oper_state,
                                             'int_enabled': int_enabled}})
                            continue

                        elif "Null" in interface:
                            continue


                        int_link_state = interfaces[interface]['line_protocol']
                        int_oper_state = interfaces[interface]['oper_status']
                        int_enabled = interfaces[interface]['enabled']
                        mtu = interfaces[interface]['mtu']

                        # We can only pull IP address if it exists in dictionary
                        if 'ipv4' in interfaces[interface]:
                            ipv4_ip = interfaces[interface]['ipv4']
                        else:
                            ipv4_ip = ''

                        # We can only pull portmode info if it exists in dictionary. Only on switches
                        if 'port_mode' in interfaces[interface]:
                            switchport_mode = interfaces[interface]['port_mode']
                        else:
                            switchport_mode = ''

                        # We can only pull duplex mode info if it exists in dictionary
                        if 'duplex_mode' in interfaces[interface]:
                            duplex = interfaces[interface]['duplex_mode']
                        else:
                            duplex = ''

                        # We can only pull port speed info if it exists in dictionary
                        if 'port_speed' in interfaces[interface]:
                            speed = interfaces[interface]['port_speed']
                        else:
                            speed = ''

                        # Some interface details don't apply to MGMT
                        if ('mgmt' not in interface) or ('Mgmt' not in interface):
                            input_errors = interfaces[interface]['counters']['in_errors']
                            output_errors = interfaces[interface]['counters']['out_errors']
                            output_drops = interfaces[interface]['queues']['total_output_drop']
                        else:
                            input_errors = ''
                            output_errors = ''
                            output_drops = ''

                        self.pre_dic[self.name].update(
                            {interface: {'int_link_state': int_link_state, 'int_oper_state': int_oper_state,
                                                 'ipv4_ip': ipv4_ip, 'mtu': mtu, 'input_errors': input_errors,
                                                 'output_errors': output_errors, 'output_drops': output_drops,
                                                 'int_enabled': int_enabled, 'duplex': duplex, 'speed': speed,
                                                 'switchport_mode': switchport_mode}})

                print(self.pre_dic)
            else:
                sys.exit(f'{self.dev_name.os} OS type not supported')


    @aetest.test
    def test02(self):
        #getpass.getpass("wait until enter is pressed....")
        time.sleep(15)


    @aetest.test
    def test03(self, steps):
        with steps.start(f"Re-run test to collect Post-state data", continue_=True) as step:
            # Create empty dictionary for storing all route results
            self.post_dic = {}

            # Loop over device dictionary
            for self.name, self.dev_name in self.devices.items():

                log.info(f'*******  Learning and Processing details for {self.name}  *******')

                # create outer dictionary entry per device
                self.post_dic[self.name] = {}

                # determine if OS type is XE or XR and unpack interface output and add to dictionary
                if self.dev_name.os == 'iosxr':
                    try:
                        interfaces = self.dev_name.parse('show interfaces')
                    except SchemaEmptyParserError:
                        interfaces = {}


                    if interfaces:
                        for interface in interfaces.keys():

                            # limited data colleciton for loopback interfaces
                            if 'loop' in interface or 'Loop' in interface:
                                int_oper_state = interfaces[interface]['oper_status']
                                int_enabled = interfaces[interface]['enabled']

                                self.post_dic[self.name].update(
                                    {interface: {'int_oper_state': int_oper_state,
                                                 'int_enabled': int_enabled}})
                                continue

                            elif "Null" in interface:
                                continue

                            int_link_state = interfaces[interface]['line_protocol']
                            int_oper_state = interfaces[interface]['oper_status']
                            int_enabled = interfaces[interface]['enabled']
                            mtu = interfaces[interface]['mtu']

                            # We can only pull IP address if it exists in dictionary
                            if 'ipv4' in interfaces[interface]:
                                ipv4_ip = interfaces[interface]['ipv4']
                            else:
                                ipv4_ip = ''

                            # We can only pull portmode info if it exists in dictionary. Only on switches
                            if 'port_mode' in interfaces[interface]:
                                switchport_mode = interfaces[interface]['port_mode']
                            else:
                                switchport_mode = ''

                            # We can only pull duplex mode info if it exists in dictionary
                            if 'duplex_mode' in interfaces[interface]:
                                duplex = interfaces[interface]['duplex_mode']
                            else:
                                duplex = ''

                            # We can only pull port speed info if it exists in dictionary
                            if 'port_speed' in interfaces[interface]:
                                speed = interfaces[interface]['port_speed']
                            else:
                                speed = ''

                            # Some interface details don't apply to MGMT
                            if ('mgmt' not in interface) or ('Mgmt' not in interface):
                                input_errors = interfaces[interface]['counters']['in_errors']
                                output_errors = interfaces[interface]['counters']['out_errors']
                                output_drops = interfaces[interface]['counters']['out_total_drops']
                            else:
                                input_errors = ''
                                output_errors = ''
                                output_drops = ''

                            self.post_dic[self.name].update(
                                {interface: {'int_link_state': int_link_state, 'int_oper_state': int_oper_state,
                                                     'ipv4_ip': ipv4_ip, 'mtu': mtu, 'input_errors': input_errors,
                                                     'output_errors': output_errors, 'output_drops': output_drops,
                                                     'int_enabled': int_enabled, 'duplex': duplex, 'speed': speed,
                                                     'switchport_mode': switchport_mode}})


                elif self.dev_name.os == 'nxos':
                    try:
                        interfaces = self.dev_name.parse('show interface')
                    except SchemaEmptyParserError:
                        interfaces = {}

                    if interfaces:
                        for interface in interfaces.keys():
                            print(interface)

                            # limited data colleciton for loopback interfaces
                            if 'loop' in interface or 'Loop' in interface:
                                int_oper_state = interfaces[interface]['oper_status']
                                int_enabled = interfaces[interface]['enabled']

                                self.post_dic[self.name].update(
                                    {interface: {'int_oper_state': int_oper_state,
                                                 'int_enabled': int_enabled}})
                                continue

                            int_link_state = interfaces[interface]['link_state']
                            int_oper_state = interfaces[interface]['oper_status']
                            int_enabled = interfaces[interface]['enabled']
                            mtu = interfaces[interface]['mtu']

                            # We can only pull IP address if it exists in dictionary
                            if 'ipv4' in interfaces[interface]:
                                ipv4_ip = interfaces[interface]['ipv4']
                            else:
                                ipv4_ip = ''

                            # We can only pull portmode info if it exists in dictionary. Only on switches
                            if 'port_mode' in interfaces[interface]:
                                switchport_mode = interfaces[interface]['port_mode']
                            else:
                                switchport_mode = ''

                            # We can only pull duplex mode info if it exists in dictionary
                            if 'duplex_mode' in interfaces[interface]:
                                duplex = interfaces[interface]['duplex_mode']
                            else:
                                duplex = ''

                            # We can only pull port speed info if it exists in dictionary
                            if 'port_speed' in interfaces[interface]:
                                speed = interfaces[interface]['port_speed']
                            else:
                                speed = ''

                            # Some interface details don't apply to MGMT
                            if 'mgmt' not in interface:
                                input_errors = interfaces[interface]['counters']['in_errors']
                                output_errors = interfaces[interface]['counters']['out_errors']
                                output_drops = interfaces[interface]['counters']['out_discard']
                            else:
                                input_errors = ''
                                output_errors = ''
                                output_drops = ''


                            self.post_dic[self.name].update(
                                {interface: {'int_link_state': int_link_state, 'int_oper_state': int_oper_state,
                                                     'ipv4_ip': ipv4_ip, 'mtu': mtu, 'input_errors': input_errors,
                                                     'output_errors': output_errors, 'output_drops': output_drops,
                                                     'int_enabled': int_enabled, 'duplex': duplex, 'speed': speed,
                                                     'switchport_mode': switchport_mode}})


                    else:
                        log.info(f'{self.name} Trouble pulling interface data from interface. Skipping')


                elif self.dev_name.os == 'ios' or self.dev_name.os == 'iosxe':
                    try:
                        interfaces = self.dev_name.parse('show interfaces')
                    except SchemaEmptyParserError:
                        interfaces = {}



                    if interfaces:
                        for interface in interfaces.keys():

                            # limited data colleciton for loopback interfaces
                            if 'loop' in interface or 'Loop' in interface:
                                int_oper_state = interfaces[interface]['oper_status']
                                int_enabled = interfaces[interface]['enabled']

                                self.post_dic[self.name].update(
                                    {interface: {'int_oper_state': int_oper_state,
                                                 'int_enabled': int_enabled}})
                                continue

                            elif "Null" in interface:
                                continue

                            int_link_state = interfaces[interface]['line_protocol']
                            int_oper_state = interfaces[interface]['oper_status']
                            int_enabled = interfaces[interface]['enabled']
                            mtu = interfaces[interface]['mtu']

                            # We can only pull IP address if it exists in dictionary
                            if 'ipv4' in interfaces[interface]:
                                ipv4_ip = interfaces[interface]['ipv4']
                            else:
                                ipv4_ip = ''

                            # We can only pull portmode info if it exists in dictionary. Only on switches
                            if 'port_mode' in interfaces[interface]:
                                switchport_mode = interfaces[interface]['port_mode']
                            else:
                                switchport_mode = ''

                            # We can only pull duplex mode info if it exists in dictionary
                            if 'duplex_mode' in interfaces[interface]:
                                duplex = interfaces[interface]['duplex_mode']
                            else:
                                duplex = ''

                            # We can only pull port speed info if it exists in dictionary
                            if 'port_speed' in interfaces[interface]:
                                speed = interfaces[interface]['port_speed']
                            else:
                                speed = ''

                            # Some interface details don't apply to MGMT
                            if ('mgmt' not in interface) or ('Mgmt' not in interface):
                                input_errors = interfaces[interface]['counters']['in_errors']
                                output_errors = interfaces[interface]['counters']['out_errors']
                                output_drops = interfaces[interface]['queues']['total_output_drop']
                            else:
                                input_errors = ''
                                output_errors = ''
                                output_drops = ''


                            self.post_dic[self.name].update(
                                {interface: {'int_link_state': int_link_state, 'int_oper_state': int_oper_state,
                                                     'ipv4_ip': ipv4_ip, 'mtu': mtu, 'input_errors': input_errors,
                                                     'output_errors': output_errors, 'output_drops': output_drops,
                                                     'int_enabled': int_enabled, 'duplex': duplex, 'speed': speed,
                                                     'switchport_mode': switchport_mode}})

                    print(self.post_dic)

                else:
                    sys.exit(f'{self.dev_name.os} OS type not supported')



    @aetest.test
    def test04(self, steps):
        with steps.start(f"Compare pre-state to post interface states", continue_=True) as step:
            # Verification
            diff = Diff(self.pre_dic, self.post_dic)
            diff.findDiff()
            diff = str(diff)
            print(diff)

            if not diff:
                log.info(f'No interface changes detected - Test Passed')
            else:
                log.info(f'Interface changes detected - Test Failed')

                for device in self.devices.keys():
                    for pre_interface in self.pre_dic[device].keys():
                        # Check to ensure interface exists in both pre and post dictionary. To ensure interface hasn't been removed
                        if pre_interface in self.post_dic[device]:

                            #special handling for loopbacks. They have limited data
                            if 'loop' in pre_interface or 'Loop' in pre_interface:
                                # check Loopback interface operational state
                                if self.pre_dic[device][pre_interface]['int_oper_state'] != self.post_dic[device][pre_interface]['int_oper_state']:
                                    log.info(
                                        f"{device} -- {pre_interface} operational state changed to {self.post_dic[device][pre_interface]['int_oper_state']}")

                                #No further checks for loopbacks
                            else:
                                #All other interfaces that are not loopbacks


                                # check speed
                                if self.pre_dic[device][pre_interface]['speed'] != self.post_dic[device][pre_interface]['speed']:
                                    log.info(f"{device} -- {pre_interface} speed changed to {self.post_dic[device][pre_interface]['speed']}")

                                # check duplex
                                if self.pre_dic[device][pre_interface]['duplex'] != self.post_dic[device][pre_interface]['duplex']:
                                    log.info(f"{device} -- {pre_interface} duplex changed to {self.post_dic[device][pre_interface]['duplex']}")

                                # check interface operational state
                                if self.pre_dic[device][pre_interface]['int_oper_state'] != self.post_dic[device][pre_interface]['int_oper_state']:
                                    log.info(
                                        f"{device} -- {pre_interface} operational state changed to {self.post_dic[device][pre_interface]['int_oper_state']}")

                                # check interface operational state
                                if self.pre_dic[device][pre_interface]['int_link_state'] != self.post_dic[device][pre_interface]['int_link_state']:
                                    log.info(
                                        f"{device} -- {pre_interface} link state changed to {self.post_dic[device][pre_interface]['int_link_state']}")

                                # check ipv4 address
                                if self.pre_dic[device][pre_interface]['ipv4'] != \
                                        self.post_dic[device][pre_interface]['ipv4']:
                                    log.info(
                                        f"{device} -- {pre_interface} ip address changed to {self.post_dic[device][pre_interface]['ipv4']}")

                                # check interface MTU
                                if self.pre_dic[device][pre_interface]['mtu'] != \
                                        self.post_dic[device][pre_interface]['mtu']:
                                    log.info(
                                        f"{device} -- {pre_interface} interface MTU changed to {self.post_dic[device][pre_interface]['mtu']}")

                                # check interface output drops
                                if self.pre_dic[device][pre_interface]['output_drops'] != self.post_dic[device][pre_interface]['output_drops']:
                                    difference = self.post_dic[device][pre_interface]['output_drops'] - self.pre_dic[device][pre_interface]['output_drops']
                                    log.info(
                                        f"{device} -- {pre_interface} interface output drops have increased to {difference}")

                                # check input errors
                                if self.pre_dic[device][pre_interface]['input_errors'] != self.post_dic[device][pre_interface]['input_errors']:
                                    difference = self.post_dic[device][pre_interface]['input_errors'] - self.pre_dic[device][pre_interface]['input_errors']
                                    log.info(
                                        f"{device} -- {pre_interface} interface input errors have increased by {difference}")

                                # check output errors
                                if self.pre_dic[device][pre_interface]['output_errors'] != self.post_dic[device][pre_interface]['output_errors']:
                                    difference = self.post_dic[device][pre_interface]['output_errors'] - self.pre_dic[device][pre_interface]['output_errors']
                                    log.info(
                                        f"{device} -- {pre_interface} interface output errors have increased by {difference}")

                                # check for switchport mode
                                if self.pre_dic[device][pre_interface]['switchport_mode'] != \
                                        self.post_dic[device][pre_interface]['switchport_mode']:
                                    log.info(
                                        f"{device} -- {pre_interface} interface switchport mode changed from {self.pre_dic[device][pre_interface]['switchport_mode']} to {self.post_dic[device][pre_interface]['switchport_mode']}")


                step.failed()




class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass