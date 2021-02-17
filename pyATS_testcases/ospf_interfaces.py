from pyats import aetest
from genie.testbed import load
from genie.conf.base import Interface
import time
from genie.utils.diff import Diff
import logging
from pprint import pprint
from unicon.core.errors import ConnectionError
from genie.metaparser.util.exceptions import SchemaEmptyParserError

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
            #create empty list to store route entries emdeded within complete_dic dictionary
            inner_entries = []

            #create outer dictionary entry per device
            self.pre_dic.update({self.name: []})

            #determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
            if self.dev_name.os == 'iosxr':
                try:
                    ospf = self.dev_name.parse('show ospf vrf all-inclusive interface')
                    print(ospf)
                except SchemaEmptyParserError:
                    ospf = {}
                if ospf:
                    for vrf in ospf['vrf'].keys():
                        ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                        for instance in ospf_instances.keys():
                            areas = ospf_instances[instance]['areas']
                            for area in areas:
                                ospf_interfaces = areas[area]['interfaces']
                                for ospf_interface in ospf_interfaces.keys():
                                    int_name = ospf_interfaces[ospf_interface]['name']
                                    inner_entries.append(int_name)
                    self.pre_dic.update({self.name: inner_entries})
                else:
                    log.info(f'{self.name} Not running OSPF. Skipping')

            elif (self.dev_name.os == 'iosxe') or (self.dev_name.os == 'ios'):
                try:
                    ospf = self.dev_name.parse('show ip ospf interface')
                except SchemaEmptyParserError:
                    ospf = {}
                if ospf:
                    for vrf in ospf['vrf'].keys():
                        ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                        for instance in ospf_instances.keys():
                            areas = ospf_instances[instance]['areas']
                            for area in areas:
                                ospf_interfaces = areas[area]['interfaces']
                                for ospf_interface in ospf_interfaces.keys():
                                    int_name = ospf_interfaces[ospf_interface]['name']
                                    inner_entries.append(int_name)
                    self.pre_dic.update({self.name: inner_entries})
                else:
                    log.info(f'{self.name} Not running OSPF. Skipping')

            elif self.dev_name.os == 'nxos':
                try:
                    ospf = self.dev_name.parse('show ip ospf interface')
                except SchemaEmptyParserError:
                    ospf = {}
                if ospf:
                    for vrf in ospf['vrf'].keys():
                        ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                        for instance in ospf_instances.keys():
                            areas = ospf_instances[instance]['areas']
                            for area in areas:
                                ospf_interfaces = areas[area]['interfaces']
                                for ospf_interface in ospf_interfaces.keys():
                                    int_name = ospf_interfaces[ospf_interface]['name']
                                    inner_entries.append(int_name)
                    self.pre_dic.update({self.name: inner_entries})
                else:
                    log.info(f'{self.name} Not running OSPF. Skipping')

            else:
                sys.exit(f'{self.dev_name.os} OS type not supported')


    @aetest.test
    def test02(self, steps):
        with steps.start(f"Perform action", continue_=True) as step:
            time.sleep(20)


    @aetest.test
    def test03(self, steps):
        with steps.start(f"Re-run test to collect Post-state data", continue_=True) as step:
            # Create empty dictionary for storing all route results
            self.post_dic = {}

            # Loop over device dictionary
            for self.name, self.dev_name in self.devices.items():

                log.info(f'*******  Learning and Processing details for {self.name}  *******')
                # create empty list to store route entries emdeded within complete_dic dictionary
                inner_entries = []

                # create outer dictionary entry per device
                self.post_dic.update({self.name: []})

                # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
                if self.dev_name.os == 'iosxr':
                    try:
                        ospf = self.dev_name.parse('show ospf vrf all-inclusive interface')
                    except SchemaEmptyParserError:
                        ospf = {}
                    if ospf:
                        for vrf in ospf['vrf'].keys():
                            ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                            for instance in ospf_instances.keys():
                                areas = ospf_instances[instance]['areas']
                                for area in areas:
                                    ospf_interfaces = areas[area]['interfaces']
                                    for ospf_interface in ospf_interfaces.keys():
                                        int_name = ospf_interfaces[ospf_interface]['name']
                                        inner_entries.append(int_name)
                        self.post_dic.update({self.name: inner_entries})
                    else:
                        log.info(f'{self.name} Not running OSPF. Skipping')

                elif (self.dev_name.os == 'iosxe') or (self.dev_name.os == 'ios'):
                    try:
                        ospf = self.dev_name.parse('show ip ospf interface')
                    except SchemaEmptyParserError:
                        ospf = {}
                    if ospf:
                        for vrf in ospf['vrf'].keys():
                            ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                            for instance in ospf_instances.keys():
                                areas = ospf_instances[instance]['areas']
                                for area in areas:
                                    ospf_interfaces = areas[area]['interfaces']
                                    for ospf_interface in ospf_interfaces.keys():
                                        int_name = ospf_interfaces[ospf_interface]['name']
                                        inner_entries.append(int_name)
                        self.post_dic.update({self.name: inner_entries})
                    else:
                        log.info(f'{self.name} Not running OSPF. Skipping')


                elif self.dev_name.os == 'nxos':
                    try:
                        ospf = self.dev_name.parse('show ip ospf interface')
                    except SchemaEmptyParserError:
                        ospf = {}
                    if ospf:
                        for vrf in ospf['vrf'].keys():
                            ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                            for instance in ospf_instances.keys():
                                areas = ospf_instances[instance]['areas']
                                for area in areas:
                                    ospf_interfaces = areas[area]['interfaces']
                                    for ospf_interface in ospf_interfaces.keys():
                                        int_name = ospf_interfaces[ospf_interface]['name']
                                        inner_entries.append(int_name)

                        self.post_dic.update({self.name: inner_entries})

                    else:
                        log.info(f'{self.name} Not running OSPF. Skipping')

                else:
                    sys.exit(f'{self.dev_name.os} OS type not supported')



    @aetest.test
    def test04(self, steps):
        with steps.start(f"Compare pre-state to post-state OSPF interface count", continue_=True) as step:
            # Verification
            diff = Diff(self.pre_dic, self.post_dic)
            print("pre dic ~~~~~~~~~~~~~")
            print(self.pre_dic)
            print("post dic ~~~~~~~~~~~~~")
            print(self.post_dic)
            diff.findDiff()
            diff = str(diff)
            if not diff:
                log.info(f'No OSPF interface changes detected - Test Passed')
            else:
                log.info(f'There have been OSPF interface changes - Test Failed -  {diff}')

                for device in self.devices.keys():

                    missing = [x for x in self.pre_dic[device] if x not in self.post_dic[device]]

                    if missing:

                        for device_missing in missing:
                            print(f'{device} -- OSPF no longer enables on interface {device_missing}')

                    added = [x for x in self.post_dic[device] if x not in self.pre_dic[device]]

                    if added:

                        for device_added in added:
                            print(f'{device} -- New OSPF interface added {device_added}')



                step.failed()



class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass