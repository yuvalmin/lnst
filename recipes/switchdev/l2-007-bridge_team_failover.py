"""
Copyright 2016 Mellanox Technologies. All rights reserved.
Licensed under the GNU General Public License, version 2 as
published by the Free Software Foundation; see COPYING for details.
"""

__author__ = """
jiri@mellanox.com (Jiri Pirko)
"""

from lnst.Controller.Task import ctl
from TestLib import TestLib
from time import sleep

def do_task(ctl, hosts, ifaces, aliases):
    m1, m2, sw = hosts
    m1_if1, m1_if2, m2_if1, m2_if2, sw_if1, sw_if2, sw_if3, sw_if4 = ifaces

    team_config = '{"runner" : {"name" : "lacp"}}'
    m1_lag1 = m1.create_team(slaves=[m1_if1, m1_if2],
                             config=team_config,
                             ip=["192.168.101.10/24", "2002::1/64"])

    m2_lag1 = m2.create_team(slaves=[m2_if1, m2_if2],
                             config=team_config,
                             ip=["192.168.101.11/24", "2002::2/64"])

    sw_lag1 = sw.create_team(slaves=[sw_if1, sw_if2],
                             config=team_config)

    sw_lag2 = sw.create_team(slaves=[sw_if3, sw_if4],
                             config=team_config)

    sw.create_bridge(slaves=[sw_lag1, sw_lag2], options={"vlan_filtering": 1,
                                                         "multicast_snooping": 0})

    sleep(30)

    tl = TestLib(ctl, aliases)
    tl.ping_simple(m1_lag1, m2_lag1)

    sw_if1.set_link_down()
    tl.ping_simple(m1_lag1, m2_lag1)

    sw_if1.set_link_up()
    # Wait for link to come up. Otherwise we start the ping when both
    # links are down.
    sleep(30)
    sw_if2.set_link_down()
    tl.ping_simple(m1_lag1, m2_lag1)

    sw_if2.set_link_up()
    sleep(30)
    sw_if1.set_link_down()
    sw_if3.set_link_down()
    tl.ping_simple(m1_lag1, m2_lag1)

    sw_if1.set_link_up()
    sw_if3.set_link_up()
    sleep(30)
    sw_if2.set_link_down()
    sw_if4.set_link_down()
    tl.ping_simple(m1_lag1, m2_lag1)

do_task(ctl, [ctl.get_host("machine1"),
              ctl.get_host("machine2"),
              ctl.get_host("switch")],
        [ctl.get_host("machine1").get_interface("if1"),
         ctl.get_host("machine1").get_interface("if2"),
         ctl.get_host("machine2").get_interface("if1"),
         ctl.get_host("machine2").get_interface("if2"),
         ctl.get_host("switch").get_interface("if1"),
         ctl.get_host("switch").get_interface("if2"),
         ctl.get_host("switch").get_interface("if3"),
         ctl.get_host("switch").get_interface("if4")],
        ctl.get_aliases())
