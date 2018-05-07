"""
This is the ORIGINAL FILE THAT IS GOING TO BE USED. Please copy any changes made
to this file to the backup file, create new file for each version and update the
current version that is used here. ONLY CREATE BACKUP IF THE FUNCTION WORKED!!!!
Version 1.25
"""
import requests
import re

class group:
    def __init__(self, connect):
        self.connect = connect
        self.bridge = None #Create a placeholder variable for the bridge
        self.caller = None #Create a placeholder variable for the caller, it will used to check whether it's the caller or not
        self.check = False #Set a variable to check whether we can make a call or not
        self.list = None #Set an empty dictionary to contain the channels
        self.div = re.compile(r'SIP/\d\d\d\d') #Set a function to separate the needed info

    def check_bridge(self):
        #Get existing bridges with the type of mixing
        bridges = [b for b in self.connect.bridges.list() if
                   b.json['bridge_type'] == 'mixing']
        #Check whether there's already a bridge that we can use or do we need to create a new one
        if bridges:
            self.bridge = bridges[0]
            print "Using bridge %s" % self.bridge.id
        else:
            self.bridge = self.connect.bridges.create(type='mixing')
            print "Created bridge %s " % self.bridge.id

    def getname(self, sL):
        #Set a function to get the dictionary of channel data from DBHelper
        self.list = sL

    def getChannel(self,channel):
        #Get current active channels in group then write it in a dictionary
        tmp = self.div.findall(channel.json.get('name'))
        self.list[tmp[0]].setChan(channel)
        return self.list

    def chan_hangup(self, channel):
        try: #A safe way to hangup a channel
            channel.hangup()
            print "Channel %s hanged up" % channel.json.get('name')
        except requests.HTTPError as e:
            if e.response.status_code != requests.codes.not_found:
                raise e

    def chan_remove(self, channel):
        try: #A safe way to remove a channel from a bridge
            self.bridge.removeChannel(self.bridge.id, channel.id)
        except:
            print "Whoops, either it is removed or something wrong happen, shit sucks"

    def destr_bridge(self):
        try: #A safe way to delete a bridge
            self.bridge.destroy()
            print "Bridge %s deleted" % self.bridge.json.get('id')
        except requests.HTTPError as e:
            if e.response.status_code != requests.codes.not_found:
                raise e

    def outgoing_call(self,sipname):
        #Start a call
        try:
            outgoing = self.connect.channels.originate(endpoint=sipname,
                extension='1000', context='group', priority=1,
                callerId='1000', timeout=30)
        except requests.HTTPError:
        #    channel.hangup()
            return

    def invite_call(self):
        #Invite other user to the calls, asterisk will ignore user that is not
        #registered by the time they are invited
        for i,j in self.list.items():
            if self.list[i].getName() == self.caller[0]:
                print "This is the caller ", self.caller[0]
            else:
                self.outgoing_call(self.list[i].getName())

    def outgoing_start(self, channel):
        print "Adding %s to bridge %s" % (channel.json.get('name'), self.bridge.json.get('id'))
        channel.answer()
        try: #Add channels to the current bridge
            self.bridge.addChannel(channel=channel.json.get('id'))
            print "Added Channel with ID %s" % (channel.json.get('id'))
        except:
            print "Sorry, unable to add the channel"
            return

    def stasis_start(self, channel, ev):
        self.check_bridge() #Check whether there's a bridge available or not
        chan = channel.get('channel') #Get the channel info as json
        print "Channel %s entered the application" % chan.json.get('name')
        tmp = self.div.findall(chan.json.get('name'))
        self.getChannel(chan)
        print self.list[tmp[0]].getChan()
        self.outgoing_start(chan) #Add the channels to the bridge first
        if self.check == False: #A barrier to make the next channel not make another call
            self.caller = tmp #Set the caller name into the variable
            self.check = True #Set to true, so the next channel can't make a call
            self.invite_call()

    def stasis_end(self, channel, ev):
        print "Channel %s left the application, first channel %s" % (channel.json.get('name'), self.caller)
        self.chan_remove(channel)
        if self.caller == self.div.findall(channel.json.get('name')):
            self.check = False #Set the variable back to false so we can make another call if needed
            #Add a function to kick and hangup all channel(?)
            self.destr_bridge()
        self.chan_hangup(channel)
