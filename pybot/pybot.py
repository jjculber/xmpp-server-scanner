#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# $Id$

#
# Under GNU General Public License
#
# Author:   noalwin
# Email:    lambda512@gmail.com
# JabberID: lambda512@jabberes.com
#


# TODO: Make the code prettier, pylint

from ConfigParser import SafeConfigParser
from datetime import datetime, timedelta
import logging
from os.path import abspath, dirname, isabs, join
try:
	import cPickle as pickle
except ImportError:
	import pickle
import sys
import urllib

from include.xmpp import simplexml

from include import xmpp_discoverer

try:
	from include import database_updater
except ImportError:
	CAN_UPDATE_DATABASE = False
else:
	CAN_UPDATE_DATABASE = True
	
from include import html_file_generator, cc_xml_file_generator


# Load the configuration
SCRIPT_DIR = abspath(dirname(sys.argv[0]))
cfg = SafeConfigParser()
cfg.readfp(open(join(SCRIPT_DIR, 'config.cfg')))



# Misc
AVAILABILITY_LOG_DAYS = cfg.getint("Misc", "AVAILABILITY_LOG_DAYS")

# Database
DBUSER              = cfg.get("Database", "USER")
DBPASSWORD          = cfg.get("Database", "PASSWORD")
DBHOST              = cfg.get("Database", "HOST")
DBDATABASE          = cfg.get("Database", "DATABASE")

UPDATE_DATABASE     = cfg.getboolean("Database", "UPDATE_DATABASE")

# Output configuration
OUTPUT_DIRECTORY    = cfg.get("Output configuration", "OUTPUT_DIRECTORY")

GENERATE_HTML_FILES = cfg.getboolean("Output configuration", "GENERATE_HTML_FILES")
GENERATE_XML_FILES  = cfg.getboolean("Output configuration", "GENERATE_XML_FILES")
COMPRESS_FILES      = cfg.getboolean("Output configuration", "COMPRESS_FILES")

XML_UPTIME_FILTER   = cfg.getfloat("Output configuration", "XML_UPTIME_FILTER")

HTML_FILES_PREFIX   = cfg.get("Output configuration", "HTML_FILES_PREFIX")

# Server list
USEURL              = cfg.getboolean("Server list", "USEURL")
SERVERS_URL         = cfg.get("Server list", "SERVERS_URL")
#SERVERS_FILE       = "servers-fixed.xml"
SERVERS_FILE        = cfg.get("Server list", "SERVERS_FILE")

# Logs
#LOGFILE            = 'out.log'
try:
	LOGFILE         = cfg.get("Logs", "LOGFILE")
except NoOptionError:
	LOGFILE         = None
#LOGFILE            = None

# Debug
# If false, load the discovery results from servers.dump file,
# instead waiting while doing the real discovery
DO_DISCOVERY        = cfg.getboolean("Debug", "DO_DISCOVERY")

del(cfg)
# Configuration loaded



if not isabs(LOGFILE):
	LOGFILE = join(SCRIPT_DIR, LOGFILE)

if not isabs(SERVERS_FILE):
	SERVERS_FILE = join(SCRIPT_DIR, SERVERS_FILE)

if not isabs(OUTPUT_DIRECTORY):
	OUTPUT_DIRECTORY = join(SCRIPT_DIR, OUTPUT_DIRECTORY)


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


if DO_DISCOVERY:
	# Get server list
	
	try:
		if USEURL:
			f = urllib.urlopen(SERVERS_URL)
		else:
			f = open(SERVERS_FILE, 'r')
	except IOError:
		logging.critical('The server list can not be loaded', exc_info=sys.exc_info())
		raise
	
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
	
	if len(server_list) == 0:
		logging.critical('The list of servers to check is empty')
		raise Exception('The list of servers to check is empty')

	servers = xmpp_discoverer.discover_servers(server_list)
	
	
	# Manage offline servers and stability information
	
	#offline = lambda server: len(server[u'info'][0]) == 0 and len(server[u'info'][1]) == 0
	offline = lambda server: not server['available']
	now = datetime.utcnow()
	availability_log_days = timedelta(AVAILABILITY_LOG_DAYS)
	
	try:
		f = open(SERVERS_DUMP_FILE, 'rb')
		old_servers = pickle.load(f)
		f.close()
		
	except IOError:
		logging.warning( "Error loading servers data in file servers.dump. Is the script executed for first time?",
		                 exc_info=sys.exc_info() )
		for server in servers.itervalues():
			if offline(server):
				server['offline_since'] = now
				server['availability'] = {now: False}
				server['times_queried_online'] = 0
				server['times_queried'] = 1
			else:
				server['offline_since'] = None
				server['availability'] = {now: True}
				server['times_queried_online'] = 1
				server['times_queried'] = 1
		
	else:
		for jid, server in servers.iteritems():
			if offline(server):
				try:
					servers[jid] = old_servers[jid]
					server = servers[jid]
					#servers[jid]['times_queried'] += 1
					if server['offline_since'] is None:
						server['offline_since'] = now
					server['availability'][now] = False
					logging.warning("%s server seems to be offline, using old data", jid)
				except KeyError: # It's a new server
					logging.debug("Initializing stability data for %s", jid)
					server['availability'] = {now: False}
					server['offline_since'] = now
					#server['times_queried_online'] = 0
					#server['times_queried'] = 1
			else:
				server['offline_since'] = None
				try:
					server['availability'] = old_servers[jid]['availability']
					server['availability'][now] = True
					#server['times_queried_online'] = old_servers[jid]['times_queried_online'] + 1
					#server['times_queried'] =  old_servers[jid]['times_queried'] + 1
				except KeyError: # It's a new server
					logging.debug("Initializing stability data for %s", jid)
					server['availability'] = {now: True}
					#server['times_queried_online'] = 1
					#server['times_queried'] = 1
			
			# Delete old availability information
			
			for log_date in sorted(server['availability']):
				if (now - log_date) > availability_log_days:
					del(server['availability'][log_date])
				else:
					break
			
			#Recalculate times_queried_online and times_queried
			
			server['times_queried_online'] = server['availability'].values().count(True)
			server['times_queried'] = len(server['availability'])
		
	finally:
		try:
			f = open(SERVERS_DUMP_FILE, 'wb')
			pickle.dump(servers, f, -1)
			f.close()
		except IOError:
			logging.error("Error saving servers data in servers.dump")
else:
	try:
		f = open(SERVERS_DUMP_FILE, 'rb')
		servers = pickle.load(f)
		f.close()
	except IOError:
		logging.critical("Error loading servers data in file servers.dump", exc_info=sys.exc_info())
		raise

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

if UPDATE_DATABASE and not CAN_UPDATE_DATABASE:
	logging.error("Can't update the database. Is MySQLdb module available?")
elif UPDATE_DATABASE and CAN_UPDATE_DATABASE:
	database_updater.update_database( DBUSER, DBPASSWORD, DBHOST,
	                                  DBDATABASE, servers )


# And build the HTML pages and the XML

# Take a look to the XMPP Registrar to see the component's category:type
# http://www.xmpp.org/registrar/disco-categories.html
# Pure MUC components are marked as x-muc by the xmpp_discoverer
show_types = [ ('conference','x-muc'), ('conference','irc'),
               ('gateway', 'aim'), ('gateway', 'gadu-gadu'), ('gateway', 'icq'),
               ('gateway', 'msn'), ('gateway', 'sms'), ('gateway', 'smtp'),
               ('gateway', 'tlen'), ('gateway', 'yahoo'),
               ('directory', 'user'), ('pubsub', 'pep'),
               ('component', 'presence'), ('store', 'file'),
               ('headline', 'newmail'), ('headline', 'rss'), ('headline', 'weather'),
               ('proxy', 'bytestreams') ]

#known_types.sort()
#html_file_generator.generate('../servers-pybot.html', servers, known_types)
if GENERATE_HTML_FILES:
	html_file_generator.generate_all( directory=OUTPUT_DIRECTORY,
	                                  filename_prefix=HTML_FILES_PREFIX,
	                                  servers=servers, types=show_types,
	                                  compress=COMPRESS_FILES )


if GENERATE_XML_FILES:
	cc_xml_file_generator.generate( directory=OUTPUT_DIRECTORY,
	                                servers=servers, service_types=show_types,
	                                minimun_uptime=XML_UPTIME_FILTER,
	                                compress=COMPRESS_FILES )
