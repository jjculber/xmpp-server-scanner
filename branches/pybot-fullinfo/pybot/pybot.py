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

import logging
from os.path import abspath, dirname, join
import pickle
import sys
import urllib

from include.xmpp import simplexml

from include import xmpp_discoverer
from include import database_updater
from include import html_file_generator, xml_file_generator

SCRIPT_DIR = abspath(dirname(sys.argv[0]))



#jabberuser="my_user"
#jabberpassword="password"
#jabberresource="pybot"
#jabberserver="jabberes.org"

# Jabber account
JABBERUSER     = "xxxxxxx"
JABBERPASSWORD = "xxxxxxx"
JABBERRESOURCE = "pybot"
JABBERSERVER   = "jabber.example.com"

# Database
DBUSER         = "user"
DBPASSWORD     = "sql_password"
DBHOST         = "localhost"
DBDATABASE     = "server_list"

# Server list
USEURL         = False
SERVERS_URL    = "http://www.jabber.org/basicservers.xml"
#SERVERS_FILE   = "servers-fixed.xml"
SERVERS_FILE   = join(SCRIPT_DIR, 'servers-fixed.xml')

# Logs
#LOGFILE        = 'out.log'
LOGFILE        = join(SCRIPT_DIR, 'out.log')
#LOGFILE        = None





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

#server_list=['jabberes.org', 'jab.undernet.cz', '12jabber.com', 'allchitchat.com', 'jabber.dk', 'amessage.be', 'jabber-hispano.org']
#server_list=['jabberes.org']

#servers = xmpp_discoverer.discover_servers( JABBERUSER, JABBERPASSWORD,
                                            #JABBERRESOURCE, JABBERSERVER,
                                            #server_list
                                          #)
#print servers

#f = open('servers.dump', 'wb')
#pickle.dump(servers, f)

f = open('servers.dump', 'rb')
servers = pickle.load(f)

f.close()


#for server in servers:
	#print
	#print 'Server: ' + server[u'jid']
	#print "Available:",
	#for service in server[u'available_services']:
		#print "\n " + service + " provided by:",
		#for jid in server[u'available_services'][service]:
			#print jid,
		
	#print "\nUnavailable:",
	#for service in server[u'unavailable_services']:
		#print "\n " + service + " provided by:",
		#for jid in server[u'unavailable_services'][service]:
			#print jid,
	#print ''



database_updater.update_database( DBUSER, DBPASSWORD, DBHOST,
                                  DBDATABASE, servers )


columns = [ 'muc', 'irc', 'aim', 'gadu-gadu', 'icq', 'msn',
            'sms', 'smtp', 'tlen', 'yahoo', 'jud', 'pep',
            'presence', 'file', 'newmail', 'rss', 'weather', 'proxy' ]

#known_types.sort()
#html_file_generator.generate('../servers-pybot.html', servers, known_types)
html_file_generator.generate_all( directory='..',
                                  filename_prefix='servers-pybot',
                                  servers=servers, types=columns,
                                  compress=True )

xml_file_generator.generate(join('..', 'servers-fullinfo.xml'), servers)
