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
import sys

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

            if self.dev_name.os == 'ios' or self.dev_name.os == 'iosxe' or self.dev_name.os == 'iosxr' or self.dev_name.os == 'nxos':
                try:
                    bgp = self.dev_name.learn('bgp')
                    if "info" in dir(bgp):
                        bgp = bgp.info
                    else:
                        bgp = {}
                except SchemaEmptyParserError:
                    bgp = {}


                if bgp:
                    for instance in bgp['instance'].keys():
                        vrfs = bgp['instance'][instance]['vrf']
                        my_as = bgp['instance'][instance]['bgp_id']
                        for vrf in vrfs.keys():
                            if vrf == 'management':
                                continue
                            neighbors = vrfs[vrf]['neighbor']
                            for neighbor in neighbors.keys():
                                state = neighbors[neighbor]['session_state']
                                peer_as = neighbors[neighbor]['remote_as']
                                self.pre_dic[self.name].update({neighbor: {'ip': neighbor, 'state': state, 'local_as': my_as, 'peer_as': peer_as }})

            else:
                sys.exit(f'{self.dev_name.os} OS type not supported')

        print(self.pre_dic)


    @aetest.test
    def test02(self):
        #getpass.getpass("wait until enter is pressed....")
        time.sleep(30)


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

                if self.dev_name.os == 'ios' or self.dev_name.os == 'iosxe' or self.dev_name.os == 'iosxr' or self.dev_name.os == 'nxos':
                    try:
                        bgp = self.dev_name.learn('bgp')
                        if "info" in dir(bgp):
                            bgp = bgp.info
                        else:
                            bgp = {}
                    except SchemaEmptyParserError:
                        bgp = {}

                    if bgp:
                        for instance in bgp['instance'].keys():
                            vrfs = bgp['instance'][instance]['vrf']
                            my_as = bgp['instance'][instance]['bgp_id']
                            for vrf in vrfs.keys():
                                if vrf == 'management':
                                    continue
                                neighbors = vrfs[vrf]['neighbor']
                                for neighbor in neighbors.keys():
                                    state = neighbors[neighbor]['session_state']
                                    peer_as = neighbors[neighbor]['remote_as']
                                    self.post_dic[self.name].update({neighbor: {'ip': neighbor, 'state': state,
                                                                                'local_as': my_as, 'peer_as': peer_as}})

                else:
                    sys.exit(f'{self.dev_name.os} OS type not supported')

            print(self.post_dic)

    @aetest.test
    def test04(self, steps):
        with steps.start(f"Compare pre-state to post interface states", continue_=True) as step:
            # Verification
            diff = Diff(self.pre_dic, self.post_dic)
            diff.findDiff()
            diff = str(diff)
            print(diff)

            print("pre and post....")
            print(self.pre_dic)
            print(self.post_dic)

            if not diff:
                log.info(f'No BGP neighbor changes detected - Test Passed')
            else:
                log.info(f'BGP neighbor changes detected - Test Failed')


                for device in self.devices.keys():


                    #identify missing peers
                    missing_peer = [x for x in self.pre_dic[device].keys() if x not in self.post_dic[device].keys()]

                    if missing_peer:
                        for x in missing_peer:
                            log.info(f"{device} -- BGP neighbor {x} is missing")

                    #identify new peers
                    new_peer = [x for x in self.post_dic[device].keys() if x not in self.pre_dic[device].keys()]

                    if new_peer:
                        for x in new_peer:
                            log.info(f"{device} -- BGP neighbor {x} has been added")

                    #Identify existing peers with changes in state

                    common_neighbors = [x for x in self.pre_dic[device].keys() if x in self.post_dic[device].keys()]

                    for neighbor in common_neighbors:

                        #ccheck for changes in peering state
                        if self.pre_dic[device][neighbor]['state'] !=  self.post_dic[device][neighbor]['state']:
                            log.info(f"{device} -- Change in BGP peering state detected. State change from {self.pre_dic[device][neighbor]['state']} to {self.post_dic[device][neighbor]['state']}")

                        #check for local AS change
                        if self.pre_dic[device][neighbor]['local_as'] != self.post_dic[device][neighbor]['local_as']:
                            log.info(
                                f"{device} -- Local BGP AS changed. Changed from {self.pre_dic[device][neighbor]['state']} to {self.post_dic[device][neighbor]['state']}")

                        #Check for neighbor AS change

                            if self.pre_dic[device][neighbor]['peer_as'] != self.post_dic[device][neighbor]['peer_as']:
                                log.info(
                                    f"{device} -- The AS number of neighbor {neighbor} has changed.  change from {self.pre_dic[device][neighbor]['state']} to {self.post_dic[device][neighbor]['state']}")

                step.failed()


class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass