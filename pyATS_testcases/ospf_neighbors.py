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
            # create outer dictionary entry per device
            self.pre_dic[self.name] = {}


            #determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
            if self.dev_name.os == 'iosxr':
                try:
                    ospf = self.dev_name.parse('show ospf vrf all-inclusive neighbor detail')
                except SchemaEmptyParserError:
                    ospf = {}

                if ospf:
                    for vrf in ospf['vrf'].keys():
                        ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                        for instance in ospf_instances.keys():
                            areas = ospf_instances[instance]['areas']
                            for area in areas.keys():
                                ospf_interfaces = areas[area]['interfaces']
                                for interface in ospf_interfaces.keys():
                                    neighbors = ospf_interfaces[interface]['neighbors']
                                    for ospf_id in neighbors.keys():
                                        peer_addresses = neighbors[ospf_id]['address']
                                        peer_router_id = neighbors[ospf_id]['neighbor_router_id']
                                        peer_state = neighbors[ospf_id]['state']
                                        self.pre_dic[self.name].update({peer_router_id:{
                                            'peer_router_id': peer_router_id, 'peer_addresses': peer_addresses,
                                            'state': peer_state}})

                else:
                    log.info(f'{self.name} Not running OSPF. Skipping')

            elif (self.dev_name.os == 'iosxe') or (self.dev_name.os == 'ios'):
                try:
                    ospf = self.dev_name.parse('show ip ospf neighbor detail')
                except SchemaEmptyParserError:
                    ospf = {}
                if ospf:
                    for vrf in ospf['vrf'].keys():
                        ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                        for instance in ospf_instances.keys():
                            areas = ospf_instances[instance]['areas']
                            for area in areas.keys():
                                ospf_interfaces = areas[area]['interfaces']
                                for interface in ospf_interfaces.keys():
                                    neighbors = ospf_interfaces[interface]['neighbors']
                                    for ospf_id in neighbors.keys():
                                        peer_addresses = neighbors[ospf_id]['address']
                                        peer_router_id = neighbors[ospf_id]['neighbor_router_id']
                                        peer_state = neighbors[ospf_id]['state']
                                        self.pre_dic[self.name].update({peer_router_id: {
                                            'peer_router_id': peer_router_id, 'peer_addresses': peer_addresses,
                                            'state': peer_state}})

                else:
                    log.info(f'{self.name} Not running OSPF. Skipping')

            elif (self.dev_name.os == 'nxos'):
                try:
                    ospf = self.dev_name.parse('show ip ospf neighbors detail')
                except SchemaEmptyParserError:
                    ospf = {}
                if ospf:
                    for vrf in ospf['vrf'].keys():
                        ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                        for instance in ospf_instances.keys():
                            areas = ospf_instances[instance]['areas']
                            for area in areas.keys():
                                ospf_interfaces = areas[area]['interfaces']
                                for interface in ospf_interfaces.keys():
                                    neighbors = ospf_interfaces[interface]['neighbors']
                                    for ospf_id in neighbors.keys():
                                        peer_addresses = neighbors[ospf_id]['address']
                                        peer_router_id = neighbors[ospf_id]['neighbor_router_id']
                                        peer_state = neighbors[ospf_id]['state']
                                        self.pre_dic[self.name].update({peer_router_id: {
                                            'peer_router_id': peer_router_id, 'peer_addresses': peer_addresses,
                                            'state': peer_state}})


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
                # create outer dictionary entry per device
                self.post_dic[self.name] = {}

                # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
                if self.dev_name.os == 'iosxr':
                    try:
                        ospf = self.dev_name.parse('show ospf vrf all-inclusive neighbor detail')
                    except SchemaEmptyParserError:
                        ospf = {}

                    if ospf:
                        for vrf in ospf['vrf'].keys():
                            ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                            for instance in ospf_instances.keys():
                                areas = ospf_instances[instance]['areas']
                                for area in areas.keys():
                                    ospf_interfaces = areas[area]['interfaces']
                                    for interface in ospf_interfaces.keys():
                                        neighbors = ospf_interfaces[interface]['neighbors']
                                        for ospf_id in neighbors.keys():
                                            peer_addresses = neighbors[ospf_id]['address']
                                            peer_router_id = neighbors[ospf_id]['neighbor_router_id']
                                            peer_state = neighbors[ospf_id]['state']
                                            self.post_dic[self.name].update({peer_router_id: {
                                                'peer_router_id': peer_router_id, 'peer_addresses': peer_addresses,
                                                'state': peer_state}})

                    else:
                        log.info(f'{self.name} Not running OSPF. Skipping')

                elif (self.dev_name.os == 'iosxe') or (self.dev_name.os == 'ios'):
                    try:
                        ospf = self.dev_name.parse('show ip ospf neighbor detail')
                    except SchemaEmptyParserError:
                        ospf = {}
                    if ospf:
                        for vrf in ospf['vrf'].keys():
                            ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                            for instance in ospf_instances.keys():
                                areas = ospf_instances[instance]['areas']
                                for area in areas.keys():
                                    ospf_interfaces = areas[area]['interfaces']
                                    for interface in ospf_interfaces.keys():
                                        neighbors = ospf_interfaces[interface]['neighbors']
                                        for ospf_id in neighbors.keys():
                                            peer_addresses = neighbors[ospf_id]['address']
                                            peer_router_id = neighbors[ospf_id]['neighbor_router_id']
                                            peer_state = neighbors[ospf_id]['state']
                                            self.post_dic[self.name].update({peer_router_id: {
                                                'peer_router_id': peer_router_id, 'peer_addresses': peer_addresses,
                                                'state': peer_state}})

                    else:
                        log.info(f'{self.name} Not running OSPF. Skipping')



                elif (self.dev_name.os == 'nxos'):
                    try:
                        ospf = self.dev_name.parse('show ip ospf neighbors detail')
                    except SchemaEmptyParserError:
                        ospf = {}
                    if ospf:
                        for vrf in ospf['vrf'].keys():
                            ospf_instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                            for instance in ospf_instances.keys():
                                areas = ospf_instances[instance]['areas']
                                for area in areas.keys():
                                    ospf_interfaces = areas[area]['interfaces']
                                    for interface in ospf_interfaces.keys():
                                        neighbors = ospf_interfaces[interface]['neighbors']
                                        for ospf_id in neighbors.keys():
                                            peer_addresses = neighbors[ospf_id]['address']
                                            peer_router_id = neighbors[ospf_id]['neighbor_router_id']
                                            peer_state = neighbors[ospf_id]['state']
                                            self.post_dic[self.name].update({peer_router_id: {
                                                'peer_router_id': peer_router_id, 'peer_addresses': peer_addresses,
                                                'state': peer_state}})

                    else:
                        log.info(f'{self.name} Not running OSPF. Skipping')

                else:
                    sys.exit(f'{self.dev_name.os} OS type not supported')



    @aetest.test
    def test04(self, steps):
        with steps.start(f"Compare pre-state to post state", continue_=True) as step:
            # Verification
            diff = Diff(self.pre_dic, self.post_dic)
            print("pre dic ~~~~~~~~~~~~~")
            print(self.pre_dic)
            print("post dic ~~~~~~~~~~~~~")
            print(self.post_dic)
            diff.findDiff()
            diff = str(diff)
            if not diff:
                log.info(f'No OSPF neighbor adjacency changes detected - Test Passed')
            else:
                log.info(f'There have been OSPF neighbor adjacency changes - Test Failed -  {diff}')

                for device in self.devices.keys():

                    missing_dic = {neighbor: other for (neighbor, other) in self.pre_dic[device].items() if
                               neighbor not in self.post_dic[device].keys()}

                    if missing_dic:

                        for missing in missing_dic.keys():

                            print(f'{device} -- Missing OSPF neighbor: {missing}')

                    added_dic = {neighbor: other for (neighbor, other) in self.post_dic[device].items() if
                             neighbor not in self.pre_dic[device].keys()}

                    if added_dic:

                        for added in added_dic.keys():
                            print(f'{device} -- New OSPF neighbor: {added}')


                    for peer in self.pre_dic[device].keys():
                        pre_peer = self.pre_dic[device][peer]
                        if peer in self.post_dic[device]:
                            post_peer = self.post_dic[device][peer]
                        else:
                            continue

                        #print(f"{device} -- pre-state for peer {peer} is {pre_peer['state']}")
                        #print(f"{device} -- post-state for peer {peer} is {post_peer['state']}")

                        if pre_peer['state'] != post_peer['state']:

                            if not post_peer["state"]:
                                post_peer["state"] = "Down"

                            print(f'{device} -- OSPF neighbor {peer} state changed from {pre_peer["state"]} to {post_peer["state"]}')

                step.failed()



class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass