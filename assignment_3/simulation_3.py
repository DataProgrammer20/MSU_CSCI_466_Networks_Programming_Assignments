"""
Created on Oct 12, 2016
@author: mwittie
"""
# import network
from assignment_3.network_3 import Router
from assignment_3.network_3 import Host
# import link
from assignment_3.link_3 import LinkLayer
from assignment_3.link_3 import Link
import threading
from time import sleep

# configuration parameters

router_queue_size = 0  # 0 means unlimited
simulation_time = 1  # give the network sufficient time to transfer all packets before quitting

if __name__ == '__main__':
    object_L = []  # keeps track of objects, so we can kill their threads

    # create network nodes
    host_1 = Host(1)
    object_L.append(host_1)
    host_2 = Host(2)
    object_L.append(host_2)
    host_3 = Host(3)
    object_L.append(host_3)
    host_4 = Host(4)
    object_L.append(host_4)

    router_a = Router(name='A', intf_count=2, max_queue_size=router_queue_size, routing_table={3: 0, 4: 1})
    router_b = Router(name='B', intf_count=1, max_queue_size=router_queue_size, routing_table={3: 0, 4: 0})
    router_c = Router(name='C', intf_count=1, max_queue_size=router_queue_size, routing_table={3: 0, 4: 0})
    router_d = Router(name='D', intf_count=2, max_queue_size=router_queue_size, routing_table={3: 0, 4: 1})
    object_L.append(router_a)
    object_L.append(router_b)
    object_L.append(router_c)
    object_L.append(router_d)

    # create a Link Layer to keep track of links between network nodes
    link_layer = LinkLayer()
    object_L.append(link_layer)

    # Create links between routers and hosts
    link_layer.add_link(Link(host_1, 0, router_a, 0, 50))
    link_layer.add_link(Link(host_2, 0, router_a, 0, 50))
    link_layer.add_link(Link(router_a, 0, router_b, 0, 50))
    link_layer.add_link(Link(router_a, 1, router_c, 0, 50))
    link_layer.add_link(Link(router_b, 0, router_d, 0, 50))
    link_layer.add_link(Link(router_c, 0, router_d, 0, 50))
    link_layer.add_link(Link(router_d, 0, host_3, 0, 50))
    link_layer.add_link(Link(router_d, 1, host_4, 0, 50))

    # start all the objects
    thread_L = []
    # Create the thread for each host and router
    thread_L.append(threading.Thread(name=host_1.__str__(), target=host_1.run))
    thread_L.append(threading.Thread(name=host_2.__str__(), target=host_2.run))
    thread_L.append(threading.Thread(name=host_3.__str__(), target=host_3.run))
    thread_L.append(threading.Thread(name=host_4.__str__(), target=host_4.run))
    thread_L.append(threading.Thread(name=router_a.__str__(), target=router_a.run))
    thread_L.append(threading.Thread(name=router_b.__str__(), target=router_b.run))
    thread_L.append(threading.Thread(name=router_c.__str__(), target=router_c.run))
    thread_L.append(threading.Thread(name=router_d.__str__(), target=router_d.run))
    thread_L.append(threading.Thread(name="Network", target=link_layer.run))

    for t in thread_L:
        t.start()

    data = 'Hello! My name is Bob. Bob is very friendly, so you should communicate with Bob and say hello! \
     Bob likes networking, gardening, and star-gazing on cold winter nights!'

    hosts = [host_1, host_2]
    end_points = [3, 4]

    # Very similar to network portion of part 2
    for h in range(len(hosts)):
        if len(data) > 40:
            f_char = 0
            l_char = 40
            while True:
                if l_char > len(data):
                    hosts[h].udt_send(end_points[h], data[f_char:])
                    break
                else:
                    hosts[h].udt_send(end_points[h], data[f_char:l_char])
                f_char += 40
                l_char += 40
        else:
            hosts[h].udt_send(end_points[h], data)

    # give the network sufficient time to transfer all packets before quitting
    sleep(simulation_time)

    # join all threads
    for o in object_L:
        o.stop = True
    for t in thread_L:
        t.join()

    print("All simulation threads joined")

    # writes to host periodically
