from pyats import aetest
from genie.testbed import load
from genie.conf.base import Interface
import time
from genie.utils.diff import Diff
import logging
import pprint
from unicon.core.errors import ConnectionError
from genie.metaparser.util.exceptions import SchemaEmptyParserError
import nested_lookup

log = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):

    #test case execute section

    @aetest.subsection
    def connect(self, testbed):
        dev_list = {}
        name_text = ""
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
            # create empty list to store route entries emdeded within complete_dic dictionary
            acl_entries = []

            # create enbedded dictionary entry per device
            self.pre_dic.update({self.name: []})

            # learn routes from device
            acls = self.dev_name.learn('acl')
            try:
                acl_entries.append(acls.info)
                # Add group of routes to dictionary per-device
                self.pre_dic[self.name] = acl_entries
            except AttributeError:
                pass




    @aetest.test
    def test02(self):
        ###Perform Action Here###
        time.sleep(30)


    @aetest.test
    def test03(self, steps):
        with steps.start(f"Re-run test to collect Post-state data", continue_=True) as step:
            # Create empty dictionary for storing all route results
            self.post_dic = {}

            # Loop over device dictionary
            for self.name, self.dev_name in self.devices.items():
                log.info(f'*******  Learning and Processing details for {self.name}  *******')
                # create empty list to store route entries emdeded within complete_dic dictionary
                acl_entries = []

                # create enbedded dictionary entry per device
                self.post_dic.update({self.name: []})

                # learn routes from device
                acls = self.dev_name.learn('acl')
                try:
                    acl_entries.append(acls.info)
                    # Add group of routes to dictionary per-device
                    self.post_dic[self.name] = acl_entries
                except AttributeError:
                    pass




        with steps.start(f"Compare Pre-state to Post-state to very routes haven't changed", continue_=True) as step:
            #Verification
            # perfrom a pre vs post ACL compare
            diff = Diff(self.pre_dic, self.post_dic, exclude="statistics")
            diff.findDiff()
            diff = str(diff)
            if not diff:
                log.info(f'No ACL changes detected - Test Passed')
            else:
                log.info(f'ACL changes detected {diff}')

                for dev in self.devices.keys():
                    log.info(f'ACL Change Summary for device - {dev}')
                    pre_list_of_acl = self.pre_dic[dev]
                    post_list_of_acl = self.post_dic[dev]

                    self.pre_acl_names = {}
                    self.post_acl_names = {}


                    # Start Pre state validation
                    for acl_set in pre_list_of_acl:
                        if 'acls' in acl_set:
                            acls = acl_set['acls']
                            for acl in acls.keys():
                                self.pre_aces = []
                                self.acl_type = acls[acl]['type']
                                try:
                                    aces = acls[acl]['aces']
                                except KeyError:
                                    print(f"ACL {acl} doesn't have any entries")
                                    self.pre_acl_names.update({acls[acl]['name']:{'type': acls[acl]['type'], 'aces': None}})
                                    continue

                                for ace in aces.keys():
                                    seq = aces[ace]['name']
                                    self.pre_aces.append(aces[ace])

                                self.pre_acl_names.update({acls[acl]['name']:{'type': acls[acl]['type'], 'aces': self.pre_aces}})
                        else:
                            self.pre_acl_names.update(
                                {'name': None, 'type': None, 'aces': None})



                    #Start Post state validation
                    for acl_set in post_list_of_acl:
                        if 'acls' in acl_set:
                            acls = acl_set['acls']
                            for acl in acls.keys():
                                self.post_aces = []
                                self.acl_type = acls[acl]['type']
                                try:
                                    aces = acls[acl]['aces']
                                except KeyError:
                                    print(f"ACL {acl} doesn't have any entries")
                                    self.post_acl_names.update({acls[acl]['name']:{'type': acls[acl]['type'], 'aces': None}})
                                    continue

                                for ace in aces.keys():
                                    seq = aces[ace]['name']
                                    self.post_aces.append(aces[ace])

                                self.post_acl_names.update({acls[acl]['name']:{'type': acls[acl]['type'], 'aces': self.post_aces}})
                        else:
                            self.post_acl_names.update(
                                {'name': None, 'type': None, 'aces': None})



                    # Start comparision


                    #List of ACLs that were removed
                    missing_acls = {x:y for x,y in self.pre_acl_names.items() if x not in self.post_acl_names.keys()}
                    if missing_acls:
                        for miss_acl in  missing_acls.keys(): log.info(f"Hostname: {dev} --- ACL {miss_acl} is missing")
                    else:
                        pass


                    # List of ACLs that were added
                    added_acls = {x:y for x,y in self.post_acl_names.items() if x not in self.pre_acl_names.keys()}
                    if added_acls:
                        for add_acl in added_acls.keys(): log.info(f" Hostname: {dev} --- ACL {add_acl} was added")
                    else:
                        pass


                    #Check for modified ACLs
                    #Loop thru pre ACLs as primary
                    for pre_acl_name in self.pre_acl_names.keys():

                        try:
                            # process each pre ACE individually and compare to post
                            pre_aces_list = self.pre_acl_names[pre_acl_name]['aces']
                            nested_lookup.nested_delete(pre_aces_list, 'statistics', in_place=True)

                            #use pre-acl name as key to ensure we're comparing the same ACL name
                            post_aces_list = self.post_acl_names[pre_acl_name]['aces']
                            nested_lookup.nested_delete(post_aces_list, 'statistics', in_place=True)

                        #if ACL is removed and empty KeyError is thrown.
                        except KeyError:
                            continue

                        if pre_aces_list and post_aces_list:
                            for pre_acl in pre_aces_list:
                                if pre_acl in post_aces_list:

                                    pass
                                else:
                                    print((f"Hostname: {dev} --- ACL {pre_acl_name} seq {pre_acl['name']} has been been modified"))



                    # Check for modified ACLs
                    # Loop thru post ACLs as primary
                    for post_acl_name in self.post_acl_names.keys():

                        try:
                            # process each pre ACE individually and compare to post
                            post_aces_list = self.post_acl_names[post_acl_name]['aces']
                            nested_lookup.nested_delete(post_aces_list, 'statistics', in_place=True)

                            # use pre-acl name as key to ensure we're comparing the same ACL name
                            pre_aces_list = self.pre_acl_names[post_acl_name]['aces']
                            nested_lookup.nested_delete(pre_aces_list, 'statistics', in_place=True)

                        #If ACL is removed/empty then KeyError is thrown
                        except KeyError:
                            continue

                        if post_aces_list and pre_aces_list:
                            for post_acl in post_aces_list:
                                if post_acl in pre_aces_list:

                                    pass
                                else:
                                    log.info((f"Hostname: {dev} --- ACL {post_acl_name} seq {post_acl['name']} has been been modified"))

                step.failed()


class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass