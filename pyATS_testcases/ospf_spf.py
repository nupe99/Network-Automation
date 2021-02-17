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

            #create outer dictionary entry per device
            self.pre_dic.update({self.name: []})

            #determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
            if self.dev_name.os == 'iosxr':
                try:
                    ospf = self.dev_name.parse('show ospf vrf all-inclusive')
                except SchemaEmptyParserError:
                    ospf = {}

                if ospf:
                    for vrf in ospf['vrf'].keys():
                        instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                        for instance in instances.keys():
                            areas = instances[instance]['areas']
                            for area in areas.keys():
                                spf_runs = areas[area]['statistics']['spf_runs_count']

                    self.pre_dic.update({self.name: spf_runs})
                else:
                    log.info(f'{self.name} Not running OSPF. Skipping')

            elif (self.dev_name.os == 'iosxe') or (self.dev_name.os == 'ios') or (self.dev_name.os == 'nxos'):
                try:
                    ospf = self.dev_name.parse('show ip ospf')
                except SchemaEmptyParserError:
                    ospf = {}

                if ospf:
                    for vrf in ospf['vrf'].keys():
                        instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                        for instance in instances.keys():
                            areas = instances[instance]['areas']
                            for area in areas.keys():
                                spf_runs = areas[area]['statistics']['spf_runs_count']

                    self.pre_dic.update({self.name: spf_runs})

                else:
                    log.info(f'{self.name} Not running OSPF. Skipping')

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
                # create empty list to store route entries emdeded within complete_dic dictionary
                inner_entries = []

                # create outer dictionary entry per device
                self.post_dic.update({self.name: []})

                # determine if OS type is XE or XR and unpack ospf neighbors output and add to dictionary
                if self.dev_name.os == 'iosxr':
                    try:
                        ospf = self.dev_name.parse('show ospf vrf all-inclusive')
                    except SchemaEmptyParserError:
                        ospf = {}

                    if ospf:
                        for vrf in ospf['vrf'].keys():
                            instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                            for instance in instances.keys():
                                areas = instances[instance]['areas']
                                for area in areas.keys():
                                    spf_runs = areas[area]['statistics']['spf_runs_count']

                        self.post_dic.update({self.name: spf_runs})

                    else:
                        log.info(f'{self.name} Not running OSPF. Skipping')
                elif (self.dev_name.os == 'iosxe') or (self.dev_name.os == 'ios') or (self.dev_name.os == 'nxos'):
                    try:
                        ospf = self.dev_name.parse('show ip ospf')
                    except SchemaEmptyParserError:
                        ospf = {}
                    if ospf:
                        for vrf in ospf['vrf'].keys():
                            instances = ospf['vrf'][vrf]['address_family']['ipv4']['instance']
                            for instance in instances.keys():
                                areas = instances[instance]['areas']
                                for area in areas.keys():
                                    spf_runs = areas[area]['statistics']['spf_runs_count']

                        self.post_dic.update({self.name: spf_runs})
                    else:
                        log.info(f'{self.name} Not running OSPF. Skipping')

                else:
                    sys.exit(f'{self.dev_name.os} OS type not supported')



    @aetest.test
    def test04(self, steps):
        with steps.start(f"Compare pre-state to post SPF states", continue_=True) as step:
            # Verification
            diff = Diff(self.pre_dic, self.post_dic)
            diff.findDiff()
            diff = str(diff)
            if not diff:
                log.info(f'No new OSPF SPF executions have occured - Test Passed')
            else:
                log.info(f'New OSPF SPF calculations have occured - Test Failed')
                for name in self.devices.keys():
                    before = self.pre_dic[name]
                    after = self.post_dic[name]
                    if before > after:
                        log.info(
                            f"Hostname {name}: Invalid. Pre state is greater than Post state. Counters may have been cleared. Skipping ")
                    else:
                        delta = after - before
                        if delta >= 1:
                            log.info(
                                f"Hostname {name}: New SPF calculations have occured. There have been {delta} new SPF calculations")

                step.failed()

class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass