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
                    eigrp = self.dev_name.learn('eigrp')
                    if "info" in dir(eigrp):
                        eigrp = eigrp.info
                    else:
                        eigrp = {}
                except SchemaEmptyParserError:
                    eigrp = {}


                if eigrp:
                    print(eigrp)
                    eigrp_peers = self.dev_name.api.get_dict_items(eigrp, 'eigrp_nbr')
                    print(eigrp_peers)

                    self.pre_dic[self.name].update({'neighbors': eigrp_peers})


            else:
                sys.exit(f'{self.dev_name.os} OS type not supported')

        print(self.pre_dic)


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
                if self.dev_name.os == 'ios' or self.dev_name.os == 'iosxe' or self.dev_name.os == 'iosxr' or self.dev_name.os == 'nxos':
                    try:
                        eigrp = self.dev_name.learn('eigrp')
                        if "info" in dir(eigrp):
                            eigrp = eigrp.info
                        else:
                            eigrp = {}
                    except SchemaEmptyParserError:
                        eigrp = {}

                    if eigrp:

                        eigrp_peers = self.dev_name.api.get_dict_items(eigrp, 'eigrp_nbr')


                        self.post_dic[self.name].update({'neighbors': eigrp_peers})


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
                log.info(f'No EIGRP changes detected - Test Passed')
            else:
                log.info(f'EIGRP changes detected - Test Failed')


                for device in self.devices.keys():

                    #EIGRP neighbor results could be string or list. Do a conversion to list to ensure consistent data type
                    if self.pre_dic[device]:

                        pre_peer_list = []
                        post_peer_list = []

                        if isinstance(self.pre_dic[device]['neighbors'], str):
                            pre_peer_list.append(self.pre_dic[device]['neighbors'])
                        elif isinstance(self.pre_dic[device]['neighbors'], list):
                            pre_peer_list = [str(x[0]) for x in self.pre_dic[device]['neighbors']]

                        if isinstance(self.post_dic[device]['neighbors'], str):
                            post_peer_list.append(self.post_dic[device]['neighbors'])
                        elif isinstance(self.post_dic[device]['neighbors'], list):
                            post_peer_list = [str(x[0]) for x in self.post_dic[device]['neighbors']]

                        missing_peer = [x for x in pre_peer_list if x not in post_peer_list]

                        if missing_peer:
                            log.info(f"{device} -- The following neighbors are missing {missing_peer}")


                        new_peer = [x for x in post_peer_list if x not in pre_peer_list]

                        if new_peer:
                            log.info(f"{device} -- The following eigrp peers have been added {new_peer}")

                step.failed()


class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass