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

logging.basicConfig()

client = ari.connect('http://localhost:8088', 'asterisk', 'asterisk')
#Create the object of the classes
grp = group(client)

def ari_start(grup):
    #Set the listener for Asterisk ARI
    client.on_channel_event('StasisStart', grup.stasis_start)
    client.on_channel_event('StasisEnd', grup.stasis_end)
    #Run the app for asterisk, for easy config, I use channel-dump as all of the app name
    client.run(apps='channel-dump')

ari_start(grp)
