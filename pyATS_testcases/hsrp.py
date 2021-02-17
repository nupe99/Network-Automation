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
                    hsrp = self.dev_name.learn('hsrp')
                    if "info" in dir(hsrp):
                        hsrp = hsrp.info
                    else:
                        hsrp = {}
                except SchemaEmptyParserError:
                    hsrp = {}

                print(hsrp)
                if hsrp:
                    for hsrp_int in hsrp.keys():
                        try:
                            self.pre_dic[self.name][hsrp_int] = {}
                            address_fams = hsrp[hsrp_int]['address_family']
                            for addr_fam in address_fams.keys():
                                hsrp_versions = address_fams[addr_fam]['version']
                                for version in hsrp_versions.keys():
                                    hsrp_groups = hsrp_versions[version]['groups']
                                    for group in hsrp_groups.keys():
                                        priority = hsrp_groups[group]['priority']
                                        virtual_mac = hsrp_groups[group]['virtual_mac_address']
                                        state = hsrp_groups[group]['hsrp_router_state']
                                        active_router = hsrp_groups[group]['active_router']

                                        self.pre_dic[self.name][hsrp_int].update({addr_fam: {group: {'priority': priority, 'v_mac': virtual_mac, 'state': state, 'active_router': active_router}}})
                        except KeyError:
                            self.pre_dic[self.name] = {}

            else:
                sys.exit(f'{self.dev_name.os} OS type not supported')


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

                # determine if OS type is XE or XR and unpack interface output and add to dictionary
                if self.dev_name.os == 'ios' or self.dev_name.os == 'iosxe' or self.dev_name.os == 'iosxr' or self.dev_name.os == 'nxos':
                    try:
                        hsrp = self.dev_name.learn('hsrp')
                        if "info" in dir(hsrp):
                            hsrp = hsrp.info
                        else:
                            hsrp = {}
                    except SchemaEmptyParserError:
                        hsrp = {}

                    if hsrp:
                        for hsrp_int in hsrp.keys():
                            try:
                                self.post_dic[self.name][hsrp_int] = {}
                                address_fams = hsrp[hsrp_int]['address_family']
                                for addr_fam in address_fams.keys():
                                    hsrp_versions = address_fams[addr_fam]['version']
                                    for version in hsrp_versions.keys():
                                        hsrp_groups = hsrp_versions[version]['groups']
                                        for group in hsrp_groups.keys():
                                            priority = hsrp_groups[group]['priority']
                                            virtual_mac = hsrp_groups[group]['virtual_mac_address']
                                            state = hsrp_groups[group]['hsrp_router_state']
                                            active_router = hsrp_groups[group]['active_router']

                                            self.post_dic[self.name][hsrp_int].update({addr_fam: {
                                                group: {'priority': priority, 'v_mac': virtual_mac, 'state': state,
                                                        'active_router': active_router}}})
                            except KeyError:
                                self.post_dic[self.name] = {}

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
                log.info(f'No HSRP changes detected - Test Passed')
            else:
                log.info(f'HSRP changes detected - Test Failed')


                for device in self.devices.keys():

                    missing_hsrp_int = [x for x in self.pre_dic[device].keys() if x not in self.post_dic[device].keys()]

                    if missing_hsrp_int:
                        for interface in missing_hsrp_int:
                            log.info(f"{device} -- Interface {interface} no longer has HSRP enabled ")


                    added_hsrp_int = [x for x in self.post_dic[device].keys() if x not in self.pre_dic[device].keys()]

                    if added_hsrp_int:
                        for interface in added_hsrp_int:
                            log.info(f"{device} -- HSRP enabled on new interface - {interface}")

                    common_hsrp_ints = [x for x in self.post_dic[device].keys() if x in self.pre_dic[device].keys()]

                    for pre_int in common_hsrp_ints:
                        for post_int in common_hsrp_ints:

                            if 'ipv4' in self.pre_dic[device][pre_int].keys() and 'ipv4' not in self.post_dic[device][pre_int].keys():
                                log.info(f"{device} -- IPv4 no longer enabled on interface {pre_int}")

                            if 'ipv6' in self.pre_dic[device][pre_int].keys() and 'ipv6' not in self.post_dic[device][pre_int].keys():
                                log.info(f"{device} -- IPv6 no longer enabled on interface {pre_int}")

                            if 'ipv4' in self.post_dic[device][pre_int].keys() and 'ipv4' not in self.pre_dic[device][pre_int].keys():
                                log.info(f"{device} -- IPv4 now enabled on interface {pre_int}")

                            if 'ipv6' in self.post_dic[device][pre_int].keys() and 'ipv6' not in self.pre_dic[device][pre_int].keys():
                                log.info(f"{device} -- IPv6 now enabled on interface {pre_int}")

                            #execute ipv4 flow
                            if 'ipv4' in self.post_dic[device][pre_int].keys() and 'ipv4' in self.pre_dic[device][pre_int].keys():

                                missing_hsrp_group = [ x for x in self.pre_dic[device][pre_int]['ipv4'].keys() if x not in self.post_dic[device][pre_int]['ipv4'].keys()]


                                #identify missing HSRP groups
                                if missing_hsrp_group:
                                    for group in missing_hsrp_group:
                                        log.info(f"{device} -- IPv4 HSRP group {group} has been removed")

                                #identify added HSRP groups
                                added_hsrp_group = [x for x in self.post_dic[device][pre_int]['ipv4'].keys() if x not in self.pre_dic[device][pre_int]['ipv4'].keys()]

                                if added_hsrp_group:
                                    for group in missing_hsrp_group:
                                        log.info(f"{device} -- IPv4 HSRP group {group} has been added")

                                common_hsrp_groups = [x for x in self.post_dic[device][pre_int]['ipv4'].keys() if
                                                    x in self.pre_dic[device][pre_int]['ipv4'].keys()]

                                for indi_group in common_hsrp_groups:
                                    pre_priority = self.pre_dic[device][pre_int]['ipv4'][indi_group]['priority']
                                    pre_vmac =  self.pre_dic[device][pre_int]['ipv4'][indi_group]['v_mac']
                                    pre_state = self.pre_dic[device][pre_int]['ipv4'][indi_group]['state']
                                    pre_pri_router = self.pre_dic[device][pre_int]['ipv4'][indi_group]['active_router']
                                    post_priority = self.post_dic[device][pre_int]['ipv4'][indi_group]['priority']
                                    post_vmac = self.post_dic[device][pre_int]['ipv4'][indi_group]['v_mac']
                                    post_state = self.post_dic[device][pre_int]['ipv4'][indi_group]['state']
                                    post_pri_router = self.post_dic[device][pre_int]['ipv4'][indi_group]['active_router']

                                    if pre_priority != post_priority:
                                        log.info(f"{device} -- IPv4 HSRP group {indi_group} priority changed from {pre_priority} to {post_priority}")

                                    if pre_vmac != post_vmac:
                                        log.info(
                                            f"{device} -- IPv4 HSRP group {indi_group} virtual mac changed from {pre_vmac} to {post_vmac}")

                                    if pre_state != post_state:
                                        log.info(
                                            f"{device} -- IPv4 HSRP group {indi_group} HSRP state changed from {pre_state} to {post_state}")

                                    if pre_pri_router != post_pri_router:
                                        log.info(
                                            f"{device} -- IPv4 HSRP group {indi_group} primary router changed from {pre_pri_router} to {post_pri_router}")

                            # execute ipv6 flow
                            if 'ipv6' in self.post_dic[device][pre_int].keys() and 'ipv6' in \
                                    self.pre_dic[device][pre_int].keys():

                                missing_hsrp_group = [x for x in
                                                      self.pre_dic[device][pre_int]['ipv6'].keys() if
                                                      x not in self.post_dic[device][pre_int][
                                                          'ipv6'].keys()]

                                # identify missing HSRP groups
                                if missing_hsrp_group:
                                    for group in missing_hsrp_group:
                                        log.info(f"{device} -- IPv6 HSRP group {group} has been removed")

                                # identify added HSRP groups
                                added_hsrp_group = [x for x in self.post_dic[device][pre_int]['ipv6'].keys()
                                                    if
                                                    x not in self.pre_dic[device][pre_int]['ipv6'].keys()]

                                if added_hsrp_group:
                                    for group in missing_hsrp_group:
                                        log.info(f"{device} -- IPv6 HSRP group {group} has been added")

                                common_hsrp_groups = [x for x in
                                                      self.post_dic[device][pre_int]['ipv6'].keys() if
                                                      x in self.pre_dic[device][pre_int]['ipv6'].keys()]

                                for indi_group in common_hsrp_groups:
                                    pre_priority = self.pre_dic[device][pre_int]['ipv6'][indi_group][
                                        'priority']
                                    pre_vmac = self.pre_dic[device][pre_int]['ipv6'][indi_group]['v_mac']
                                    pre_state = self.pre_dic[device][pre_int]['ipv6'][indi_group]['state']
                                    pre_pri_router = self.pre_dic[device][pre_int]['ipv6'][indi_group][
                                        'active_router']
                                    post_priority = self.post_dic[device][pre_int]['ipv6'][indi_group][
                                        'priority']
                                    post_vmac = self.post_dic[device][pre_int]['ipv6'][indi_group]['v_mac']
                                    post_state = self.post_dic[device][pre_int]['ipv6'][indi_group]['state']
                                    post_pri_router = self.post_dic[device][pre_int]['ipv6'][indi_group][
                                        'active_router']

                                    if pre_priority != post_priority:
                                        log.info(
                                            f"{device} -- IPv6 HSRP group {indi_group} priority changed from {pre_priority} to {post_priority}")

                                    if pre_vmac != post_vmac:
                                        log.info(
                                            f"{device} -- IPv6 HSRP group {indi_group} virtual mac changed from {pre_vmac} to {post_vmac}")

                                    if pre_state != post_state:
                                        log.info(
                                            f"{device} -- IPv6 HSRP group {indi_group} HSRP state changed from {pre_state} to {post_state}")

                                    if pre_pri_router != post_pri_router:
                                        log.info(
                                            f"{device} -- IPv6 HSRP group {indi_group} primary router changed from {pre_pri_router} to {post_pri_router}")

                step.failed()


class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass