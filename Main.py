#! /usr/bin/env python2

"""
This is the ORIGINAL FILE THAT IS GOING TO BE USED. Please copy any changes made
to this file to the backup file, create new file for each version and update the
current version that is used here.
Version 1.2
"""

import ari
import logging
import threading
from group import group
from gpio import gpio
from DBHelper import DBHelper
from UdpListener import UdpListener
from ComFun import ComFun

logging.basicConfig()

client = ari.connect('http://localhost:8088', 'asterisk', 'asterisk')
#Create the object of the classes
grp = group(client)
func = ComFun()
gpo = gpio(func) #Handover the communication function class, so it doesn't need
                 #to instantiate a new communication function
udp = UdpListener(func)
helper = DBHelper()

def ari_start(grup):
    #Set the listener for Asterisk ARI
    client.on_channel_event('StasisStart', grup.stasis_start)
    client.on_channel_event('StasisEnd', grup.stasis_end)
    #Run the app for asterisk, for easy config, I use channel-dump as all of the app name
    client.run(apps='channel-dump')

def start(g):
    #Create a thread to handle input
    t = threading.Thread(target=gpo.start_listen)
    t.setDaemon(True) #Run the input listener as a background process
    t.start()
    #Create a thread to listen for UDP packets
    z = threading.Thread(target=udp.start_udp_listener)
    z.setDaemon(True)
    z.start()
    grp.getname(helper.getData())
    func.getList(grp.list)
    ari_start(g) #!!!IMPORTANT!!! Run the ARI listener AFTER you start the other
                 #necessary thread! Lest the other function won't start before
                 #you stop the ARI listener!
start(grp)
