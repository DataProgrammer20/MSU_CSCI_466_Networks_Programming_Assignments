"""
Created on Oct 12, 2016
@author: mwittie
"""
# import network
from assignment_3.network_2 import Router
from assignment_3.network_2 import Host
# import link
from assignment_3.link_2 import LinkLayer
from assignment_3.link_2 import Link
import threading
from time import sleep

# configuration parameters

router_queue_size = 0  # 0 means unlimited
simulation_time = 1  # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads

    # create network nodes
    client = Host(1)
    object_L.append(client)
    server = Host(2)
    object_L.append(server)
    router_a = Router(name='A', intf_count=1, max_queue_size=router_queue_size)
    object_L.append(router_a)

    # create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)

    # add all the links
    # link parameters: from_node, from_intf_num, to_node, to_intf_num, mtu
    link_layer.add_link(Link(client, 0, router_a, 0, 50))
    # Changing from 50 to 30
    link_layer.add_link(Link(router_a, 0, server, 0, 30))

    # start all the objects
    thread_L = []
    thread_L.append(threading.Thread(name=client.__str__(), target=client.run))
    thread_L.append(threading.Thread(name=server.__str__(), target=server.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))

    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()

    # create some send events
    client.udt_send(2, 'Hello! My name is Bob. Bob is very friendly, so you should communicate with Bob and say hello!', 47)

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")

    # writes to host periodically
