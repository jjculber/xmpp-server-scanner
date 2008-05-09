#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# $id$

#
# Under GNU General Public License
#
# Author:   noalwin
# Email:    lambda512@gmail.com
# JabberID: lambda512@jabberes.com
#


# TODO: Make the code prettier, pylint



#jabberuser="my_user"
#jabberpassword="password"
#jabberresource="pybot"
#jabberserver="jabberes.org"

# Jabber account
JABBERUSER     = "xxxxxxx"
JABBERPASSWORD = "xxxxxxx"
JABBERRESOURCE = "pybot"
JABBERSERVER   = "xmpp.example.net"

# Database
DBUSER         = "user"
DBPASSWORD     = "sql_password"
DBHOST         = "localhost"
DBDATABASE     = "server_list"

# Server list
USEURL         = False
SERVERS_URL    = "http://www.jabber.org/basicservers.xml"
SERVERS_FILE   = "servers-fixed.xml"

# Logs
LOGFILE        = 'out.log'
LOGFILE        = None

#from xmpp import *
import logging
import pickle
import urllib
from xmpp import simplexml

from include import database_updater, xmpp_discoverer


if LOGFILE is None:
	logging.basicConfig(
#	    level=logging.WARNING,
	    level=logging.DEBUG,
	    format='%(asctime)s %(levelname)s %(message)s'
	    )
else:
	logging.basicConfig(
	    level=logging.DEBUG,
	    format='%(asctime)s %(levelname)s %(message)s',
	    filename=LOGFILE,
	    filemode='w'
	    )



# Get server list

if USEURL:
	f = urllib.urlopen(SERVERS_URL)
else:
	f = open(SERVERS_FILE, 'r')

xmldata = f.read()
f.close()

node = simplexml.XML2Node(xmldata)

#items = node.getChildren()
items = node.getTags(name="item")

server_list = []

for item in items:
	if item.getAttr("jid") not in server_list:
		server_list.append(item.getAttr("jid"))

#servers=[{u'jid': u'jabberes.org', u'availableServices': {}, u'unavailableServices': {}}, {u'jid': u'jab.undernet.cz', u'availableServices': {}, u'unavailableServices': {}}, {u'jid': u'12jabber.com', u'availableServices': {}, u'unavailableServices': {}}, {u'jid': u'allchitchat.com', u'availableServices': {}, u'unavailableServices': {}}]
#servers=[{u'jid': u'jabber.dk', u'availableServices': {}, u'unavailableServices': {}}, {u'jid': u'amessage.be', u'availableServices': {}, u'unavailableServices': {}}]
#servers=[
    #{u'jid': u'jabberes.org', u'availableServices': {}, u'unavailableServices': {}},
    #{u'jid': u'jabber.dk', u'availableServices': {}, u'unavailableServices': {}},
    #{u'jid': u'jabber-hispano.org', u'availableServices': {}, u'unavailableServices': {}}
#]

#servers=[]
servers = xmpp_discoverer.discover_servers(
                                           jabber_user=JABBERUSER,
                                           jabber_password=JABBERPASSWORD,
                                           jabber_resource=JABBERRESOURCE,
                                           jabber_server=JABBERSERVER,
                                           server_list=server_list
                                          )

#f = open('servers.dump', 'wb')
#pickle.dump(servers, f)

#f = open('servers.dump', 'rb')
#servers = pickle.load(f)

#f.close()

for server in servers:
	print
	print 'Server: ' + server[u'jid']
	print "Available:",
	for service in server[u'availableServices']:
		print "\n " + service + " provided by:",
		for jid in server[u'availableServices'][service]:
			print jid,
		
	print "\nUnavailable:",
	for service in server[u'unavailableServices']:
		print "\n " + service + " provided by:",
		for jid in server[u'unavailableServices'][service]:
			print jid,
	print ''


servers = database_updater.update_database(
                                           db_user=DBUSER,
                                           db_password=DBPASSWORD,
                                           db_host=DBHOST,
                                           db_database=DBDATABASE,
                                           servers=servers
                                          )

