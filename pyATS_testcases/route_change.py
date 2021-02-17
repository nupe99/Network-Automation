from pyats import aetest
from genie.testbed import load
from genie.conf.base import Interface
import time
from genie.utils.diff import Diff
import logging
import pprint
from unicon.core.errors import ConnectionError
from genie.metaparser.util.exceptions import SchemaEmptyParserError

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
            #create empty list to store route entries emdeded within complete_dic dictionary
            route_entries = []

            #create enbedded dictionary entry per device
            self.pre_dic.update({self.name: []})

            #learn routes from device
            routing = self.dev_name.learn('routing')
            print(routing.info)
            for vrf in routing.info['vrf'].keys():
                af = routing.info['vrf'][vrf]['address_family']
                for protocol in af.keys():
                    routes = af[protocol]['routes']
                    print(routes)


                    #Loop through list of learned routes, one interation per route
                    for network in routes.keys():

                        #extract rotue and add to string variable
                        route = routes[network]['route']
                        #attempt to extract next hop info. If not available, use next-hop
                        outgoing_int = self.dev_name.api.get_dict_items(routes[network]['next_hop'], 'outgoing_interface')
                        next_hop = self.dev_name.api.get_dict_items(routes[network]['next_hop'], 'next_hop')
                        source_protocol =  self.dev_name.api.get_dict_items(routes[network], 'source_protocol')

                        # Add route entry to list
                        route_entries.append({route: {'outgoing_int': outgoing_int, 'next_hop': next_hop,
                                                      'source_protocol': source_protocol, 'route': route}})

            #Add group of routes to dictionary per-device
            self.pre_dic[self.name] = route_entries

        pprint.pprint(self.pre_dic)


    @aetest.test
    def test02(self):
        ###Perform Action Here###
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
                route_entries = []

                # create enbedded dictionary entry per device
                self.post_dic.update({self.name: []})

                # learn routes from device
                routing = self.dev_name.learn('routing')

                # Loop through list of learned routes, one interation per route
                for vrf in routing.info['vrf'].keys():
                    af = routing.info['vrf'][vrf]['address_family']
                    for protocol in af.keys():
                        routes = af[protocol]['routes']
                        print(routes)

                        # Loop through list of learned routes, one interation per route
                        for network in routes.keys():
                            # extract rotue and add to string variable
                            route = routes[network]['route']
                            # attempt to extract next hop info. If not available, use next-hop
                            outgoing_int = self.dev_name.api.get_dict_items(routes[network]['next_hop'],
                                                                            'outgoing_interface')
                            next_hop = self.dev_name.api.get_dict_items(routes[network]['next_hop'], 'next_hop')
                            source_protocol = self.dev_name.api.get_dict_items(routes[network], 'source_protocol')

                            # Add route entry to list
                            route_entries.append({route: {'outgoing_int': outgoing_int, 'next_hop': next_hop,
                                                          'source_protocol': source_protocol, 'route': route}})

                # Add group of routes to dictionary per-device
                self.post_dic[self.name] = route_entries

            pprint.pprint(self.post_dic)

        with steps.start(f"Compare Pre-state to Post-state to very routes haven't changed", continue_=True) as step:
            #Verification
            diff = Diff(self.pre_dic, self.post_dic)
            diff.findDiff()
            diff = str(diff)
            if not diff:
                log.info(f'No routing table change - Test Passed')
            else:
                for dev in self.devices.keys():
                    log.info(f'Route Table Change Summary for device - {dev}')
                    pre_list_of_route = self.pre_dic[dev]
                    post_list_of_route = self.post_dic[dev]

                    # Create master pre-chenge route list
                    before_route_list = []
                    for pre_route in pre_list_of_route:
                        for pre_subnet in pre_route.keys():
                            before_route_list.append(pre_subnet)

                    # Create master pre-chenge route list
                    after_route_list = []
                    for post_route in post_list_of_route:
                        for post_subnet in post_route.keys():
                            after_route_list.append(post_subnet)

                    # Find missing routes from pre change to post
                    missing_routes = [x for x in before_route_list if x not in after_route_list]
                    if missing_routes:
                        for missing_route in missing_routes:
                            print(f'Route {missing_route} is missing post-change')

                    # Find added routes from pre change to post
                    added_routes = [x for x in after_route_list if x not in before_route_list]
                    if added_routes:
                        for added_route in added_routes:
                            print(f'Route {added_route} has been added post-change')

                    # Find routers that haven't changes from pre to post
                    # common_routes = [x for x in before_route_list if in after_route_list]

                    # evaluate route parameter differences
                    for pre_route in pre_list_of_route:
                        for pre_subnet in pre_route.keys():
                            for post_route in post_list_of_route:
                                for post_subnet in post_route.keys():
                                    if pre_route[pre_subnet]['route'] == post_route[post_subnet]['route']:
                                        if pre_route[pre_subnet]['outgoing_int'] == post_route[post_subnet][
                                            'outgoing_int']:
                                            pass
                                        else:
                                            log.info(
                                                f"Outgoing interface of route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['outgoing_int']} to {post_route[post_subnet]['outgoing_int']}")

                                        if pre_route[pre_subnet]['next_hop'] == post_route[post_subnet]['next_hop']:
                                            pass
                                        else:
                                            log.info(
                                                f"Next-hop of route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['next_hop']} to {post_route[post_subnet]['next_hop']}")

                                        if pre_route[pre_subnet]['source_protocol'] == post_route[post_subnet][
                                            'source_protocol']:
                                            pass
                                        else:
                                            log.info(
                                                f"Source Protocol for route {pre_route[pre_subnet]['route']} changed from {pre_route[pre_subnet]['source_protocol']} has changed to {post_route[post_subnet]['source_protocol']}")

                                    else:
                                        pass

                step.failed()




class CommonCleanup(aetest.CommonCleanup):

    #Cleanup seciton
    pass