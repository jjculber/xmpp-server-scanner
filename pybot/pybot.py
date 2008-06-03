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
from os.path import abspath, dirname, isabs, join
try:
	import cPickle as pickle
except ImportError:
	import pickle
import time
import sys
import urllib

from include.xmpp import simplexml

from include import xmpp_discoverer
from include import database_updater
from include import html_file_generator, xml_file_generator



# Configuration

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

# OUTPUT CONFIGURATION
OUTPUT_DIRECTORY = '..'

# Server list
USEURL         = False
SERVERS_URL    = "http://www.jabber.org/basicservers.xml"
#SERVERS_FILE   = "servers-fixed.xml"
SERVERS_FILE   = 'servers-fixed.xml'

# Logs
#LOGFILE        = 'out.log'
LOGFILE        = 'out.log'
#LOGFILE        = None

# Configuration end



SCRIPT_DIR = abspath(dirname(sys.argv[0]))

if not isabs(LOGFILE):
	LOGFILE = join(SCRIPT_DIR, LOGFILE)

if not isabs(SERVERS_FILE):
	SERVERS_FILE = join(SCRIPT_DIR, SERVERS_FILE)

if not isabs(OUTPUT_DIRECTORY):
	OUTPUT_DIRECTORY = join(SCRIPT_DIR, OUTPUT_DIRECTORY)

HTML_FILES_PREFIX = 'servers-pybot'
XML_FILES_PREFIX = 'servers-pybot'
#XML_FILE = join(OUTPUT_DIRECTORY, 'servers-fullinfo.xml')

#if not isabs(XML_FILE):
	#SERVERS_FILE = join(SCRIPT_DIR, XML_FILE)
	
SERVERS_DUMP_FILE = join(SCRIPT_DIR, 'servers.dump')


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

#server_list=['jabberes.org', 'jab.undernet.cz', '12jabber.com', 'allchitchat.com', 'jabber.dk', 'amessage.be', 'jabber-hispano.org', 'example.net']
#server_list=['jabberes.org']

#servers = xmpp_discoverer.discover_servers( JABBERUSER, JABBERPASSWORD,
                                            #JABBERRESOURCE, JABBERSERVER,
                                            #server_list
                                          #)


# Manage offline servers and stability information

offline = lambda server: len(server[u'info'][0]) == 0 and len(server[u'info'][1]) == 0

try:
	f = open(SERVERS_DUMP_FILE, 'rb')
	old_servers = pickle.load(f)
	f.close()
	
except IOError:
	logging.warning("Error loading servers data in file servers.dump")
	for server in servers.itervalues():
		if offline(server):
			server['offline_since'] = time.gmtime()
			server['times_queried_online'] = 0
			server['times_queried'] = 1
		else:
			server['offline_since'] = None
			server['times_queried_online'] = 1
			server['times_queried'] = 1
	
else:
	for jid, server in servers.iteritems():
		if offline(server):
			try:
				servers[jid] = old_servers[jid]
				servers[jid]['times_queried'] += 1
				if servers[jid]['offline_since'] is None:
					servers[jid]['offline_since'] = time.gmtime()
				logging.warning("%s server seems to be offline, using old data", jid)
			except KeyError: # It's a new server
				logging.debug("Initializing stability data for %s", jid)
				server['offline_since'] = time.gmtime()
				server['times_queried_online'] = 0
				server['times_queried'] = 1
		else:
			server['offline_since'] = None
			try:
				server['times_queried_online'] = old_servers[jid]['times_queried_online'] + 1
				server['times_queried'] =  old_servers[jid]['times_queried'] + 1
			except KeyError: # It's a new server
				logging.debug("Initializing stability data for %s", jid)
				server['times_queried_online'] = 1
				server['times_queried'] = 1
	
finally:
	try:
		f = open(SERVERS_DUMP_FILE, 'wb')
		pickle.dump(servers, f, -1)
		f.close()
	except IOError:
		logging.error("Error saving servers data in servers.dump")


#for jid, server in sorted(servers.iteritems()):
	
	#print 'Server: %s' % server[u'jid']
	#if server['offline_since'] is None:
		#print 'Online'
	#else:
		#print 'Offline Since: %s' % time.strftime('%d-%B-%Y %H:%M', server['offline_since'])
	#print 'Times Online: %s/%s' % (str(server['times_queried_online']), str(server['times_queried']))
	#print "Available:",
	#for service in server[u'available_services']:
		#print "\n %s provided by:" % service,
		#print ' '.join(server[u'available_services'][service]),
		
	#print "\nUnavailable:",
	#for service in server[u'unavailable_services']:
		#print "\n %s provided by: " % service,
		#print ' '.join(server[u'unavailable_services'][service]),
	#print '\n'


# Now dump the information to the dataabase

database_updater.update_database( DBUSER, DBPASSWORD, DBHOST,
                                  DBDATABASE, servers )


# And build the HTML pages and the XML

columns = [ 'muc', 'irc', 'aim', 'gadu-gadu', 'icq', 'msn',
            'sms', 'smtp', 'tlen', 'yahoo', 'jud', 'pep',
            'presence', 'file', 'newmail', 'rss', 'weather', 'proxy' ]

#known_types.sort()
#html_file_generator.generate('../servers-pybot.html', servers, known_types)
html_file_generator.generate_all( directory=OUTPUT_DIRECTORY,
                                  filename_prefix=HTML_FILES_PREFIX,
                                  servers=servers, types=columns,
                                  compress=True )

xml_file_generator.generate_all( directory=OUTPUT_DIRECTORY,
                                 filename_prefix=XML_FILES_PREFIX,
                                 servers=servers, service_types=columns,
                                 only_available_components=True,
                                 minimun_uptime=0.5 )
