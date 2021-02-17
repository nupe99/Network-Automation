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
            #create empty list to store route entries emdeded within complete_dic dictionary
            inner_entries = []
            log.info(f' OS type for {self.name} is {self.dev_name.os}')
            #create outer dictionary entry per device
            self.pre_dic.update({self.name: []})

            #determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
            if self.dev_name.os == 'ios' or self.dev_name.os == 'iosxe':
                try:
                    traffic = self.dev_name.parse('show ip traffic')
                except SchemaEmptyParserError:
                    traffic = {}

                print(traffic)

                fragmented = traffic['ip_statistics']['ip_frags_fragmented']
                failed_to_fragment = traffic['ip_statistics']['ip_frags_no_fragmented']

                self.pre_dic.update({self.name: {'ip_frags_fragmented': fragmented,
                                                  'ip_frags_no_fragmented': failed_to_fragment}})

            else:
                continue

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
                # create empty list to store route entries emdeded within complete_dic dictionary
                inner_entries = []
                log.info(f' OS type for {self.name} is {self.dev_name.os}')
                # create outer dictionary entry per device
                self.post_dic.update({self.name: []})

                # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
                if self.dev_name.os == 'ios' or self.dev_name.os == 'iosxe':
                    try:
                        traffic = self.dev_name.parse('show ip traffic')
                    except SchemaEmptyParserError:
                        traffic = {}

                    fragmented = traffic['ip_statistics']['ip_frags_fragmented']
                    failed_to_fragment = traffic['ip_statistics']['ip_frags_no_fragmented']


                    self.post_dic.update({self.name: { 'ip_frags_fragmented': fragmented, 'ip_frags_no_fragmented': failed_to_fragment} })

                else:
                    print(f'{self.dev_name.os} OS type not supported')

            print(self.post_dic)

    @aetest.test
    def test04(self, steps):
        with steps.start(f"Compare pre-state to post fragmentation states", continue_=True) as step:
            # Verification
            diff = Diff(self.pre_dic, self.post_dic)
            diff.findDiff()
            diff = str(diff)
            if not diff:
                log.info(f'No new Fragmentaion cases detected - Test Passed')
            else:
                log.info(f'New Fragmentation cases have occured - Test Failed')
                for name in self.devices.keys():

                    #Checking for fragmentaitons
                    #print(f'the pre dictionary {self.pre_dic[name]}')
                    #print(f'the psot dictionary {self.post_dic[name]}')
                    if self.pre_dic[name] and self.post_dic[name]:
                        before_fragmented = self.pre_dic[name]['ip_frags_fragmented']
                        after_fragmented = self.post_dic[name]['ip_frags_fragmented']

                        if before_fragmented > after_fragmented:
                            log.info(
                                f"Hostname {name}: Invalid. Pre state is greater than Post state. Counters may have been cleared. Skipping ")
                        else:
                            delta = after_fragmented - before_fragmented
                            if delta >= 1:
                                log.info(
                                    f"Hostname {name}: Fragmentation as occured. {delta} packets fragmented")


                        # Checking for drops due to not being able to fragment
                        before_fragmented = self.pre_dic[name]['ip_frags_no_fragmented']
                        after_fragmented = self.post_dic[name]['ip_frags_no_fragmented']

                        if before_fragmented > after_fragmented:
                            log.info(
                                f"Hostname {name}: Invalid. Pre state is greater than Post state. Counters may have been cleared. Skipping ")
                        else:
                            delta = after_fragmented - before_fragmented
                            if delta >= 1:
                                log.info(
                                    f"Hostname {name}: New packet drops have occured due to failure to fragment one or more packets. {delta} new drops")

                step.failed()

class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass