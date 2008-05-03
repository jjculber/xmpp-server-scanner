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


# TODO: Si falla un query, reintentar?
# TODO: Multithread
# TODO: Testing
# TODO: Make the code more prettier, pylint
# TODO: Check for SQL injections
# TODO: Simplify discover_item()



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
DBTABLE        = "pyservers"

USEURL         = False
SERVERS_URL    = "http://www.jabber.org/basicservers.xml"
SERVERS_FILE   = "servers-fixed.xml"

LOGFILE        = 'out.log'

#from xmpp import *
import logging
import pickle
import re
from sets import Set
import urllib
import xml.parsers.expat

import MySQLdb

from xmpp import Client, features, simplexml
from xmpp.protocol import Message

if LOGFILE is None:
	logging.basicConfig(
	    level=logging.WARNING,
	    format='%(asctime)s %(levelname)s %(message)s'
	    )
else:
	logging.basicConfig(
	    level=logging.DEBUG,
	    format='%(asctime)s %(levelname)s %(message)s',
	    filename=LOGFILE,
	    filemode='w'
	    )



URLREGEXP = re.compile(
	r'(?P<fullsubdomain>' +
		r'(?:(?P<subdomain>\w+)\.(?=\w+\.\w))?' +
		r'(?P<fulldomain>'+
			r'(?:(?P<domain>\w+)\.)?(?P<tld>\w+)$' +
	   r')' +
	r')'
	)


def in_same_domain(parent, child):
	'''Check if parent and child are in the same domain'''
	
	if child.count('@') > 0:
		return False
	
	parent_match = URLREGEXP.search(parent)
	child_match = URLREGEXP.search(child)
	
	if child_match.group('tld') == 'localhost':
		return True
	elif 'domain' not in child_match.groupdict():
		return True
	elif child_match.group('domain') in ('com', 'net', 'org',
		                                'co', 'gov', 'edu'):
		# It's a country code second level domain, until the third level
		return (parent_match.group('fullsubdomain') == 
		        child_match.group('fullsubdomain'))
	else:
		# It's a usual domain name, check until the second level
		return (parent_match.group('fulldomain') == child_match.group('fulldomain'))
	


def add_service_available(identities, service_set):
	'''Process identity and update the set of server service_set'''
	
	for identity in identities:
		if identity[u'category'] == u'conference':
			if identity[u'type'] == u'text':
				#if u'http://jabber.org/protocol/muc' in service[u'info'][1]:
					service_set.add('muc')
			elif identity[u'type'] == u'irc':
				service_set.add('irc')
			
		if identity[u'category'] == u'gateway':
			if identity[u'type'] == u'aim':
				service_set.add('aim')
			elif identity[u'type'] == u'gadu-gadu':
				service_set.add('gadu-gadu')
			elif identity[u'type'] == u'http-ws':
				service_set.add('http-ws')
			elif identity[u'type'] == u'icq':
				service_set.add('icq')
			elif identity[u'type'] == u'msn':
				service_set.add('msn')
			elif identity[u'type'] == u'qq':
				service_set.add('qq')
			elif identity[u'type'] == u'sms':
				service_set.add('sms')
			elif identity[u'type'] == u'smtp':
				service_set.add('smtp')
			elif identity[u'type'] == u'tlen':
				service_set.add('tlen')
			elif identity[u'type'] == u'yahoo':
				service_set.add('yahoo')
			
		if identity[u'category'] == u'directory':
			if identity[u'type'] == u'user':
				service_set.add('jud')
			
		if identity[u'category'] == u'pubsub':
			if identity[u'type'] == u'service': # XEP
				service_set.add('pubsub')
			elif identity[u'type'] == u'generic': # ejabberd 1.1.3
				service_set.add('pubsub')
			elif identity[u'type'] == u'pep':
				service_set.add('pep')
			
		if identity[u'category'] == u'component':
			if identity[u'type'] == u'presence':
				service_set.add('presence')
			
		if identity[u'category'] == u'headline':
			if identity[u'type'] == u'newmail':
				service_set.add('newmail')
			elif identity[u'type'] == u'rss':
				service_set.add('rss')
			elif identity[u'type'] == u'weather':
				service_set.add('weather')
			
		if identity[u'category'] == u'proxy':
			if identity[u'type'] == u'bytestreams':
				service_set.add('proxy')
			
		# Non standard service_set
		
		if identity[u'category'] == u'agent': 
			if identity[u'type'] == u'weather':
				service_set.add('weather')
			
		if identity[u'category'] == u'x-service':
			if identity[u'type'] == u'x-rss': # PyRSS
				service_set.add('rss')


def add_service_unavailable(jid, service_set):
	'''Guess the service using the JIDs and update the set of servers
	service_set'''
	
	logging.debug('Guessing type of %s', jid)
	
	# Conference
	if jid.startswith((u'conference.', u'conf.', u'muc.', u'chat.', u'rooms.')):
		service_set.add('muc')
	elif jid.startswith(u'irc.'):
		service_set.add('irc')
	
	# Transports
	elif jid.startswith((u'aim.', u'aim-jab.')):
		service_set.add('aim')
	elif jid.startswith(u'aim-icq.'):
		service_set.add('aim')
		service_set.add('icq')
	elif jid.startswith((u'gg.', u'gadugadu.', u'gadu-gadu.')):
		service_set.add('gg')
	elif jid.startswith(u'http-ws.'):
		service_set.add('http-ws')
	elif jid.startswith((u'icq.', u'icqt.', u'jit-icq.', u'icq-jab.', u'icq2')):
		service_set.add('icq')
	elif jid.startswith((u'msn.', u'msnt.', u'pymsnt.')):
		service_set.add('msn')
	elif jid.startswith(u'qq.'):
		service_set.add('qq')
	elif jid.startswith(u'sms.'):
		service_set.add('sms')
	elif jid.startswith(u'smtp.'):
		service_set.add('smtp')
	elif jid.startswith(u'tlen.'):
		service_set.add('tlen')
	elif jid.startswith(u'yahoo.'):
		service_set.add('yahoo')
	
	# Directories
	elif jid.startswith((u'jud.', u'vjud.', u'search.', u'users.')):
		service_set.add('jud')
	
	# PubSub
	elif jid.startswith(u'pubsub.'):
		service_set.add('pubsub')
	elif jid.startswith(u'pep.'):
		service_set.add('pep')
	
	# Presence
	elif jid.startswith((u'presence.', u'webpresence.')):
		service_set.add('presence')
	
	# Headline
	elif jid.startswith((u'newmail.', u'mail.', u'jmc.')):
		service_set.add('newmail')
	elif jid.startswith(u'rss.'):
		service_set.add('rss')
	elif jid.startswith(u'weather.'):
		service_set.add('weather')
	
	# Proxy
	elif jid.startswith((u'proxy.', u'proxy65')):
		service_set.add('proxy')



def get_item_info(dispatcher, service):
	'''Query the information about the item'''
	
	# Some components adresses ends in .localhost so the querys
	# will end on a 404 error
	# Then, we don't need to waste resources querying them
	if not service[u'jid'].endswith('.localhost'):
		try:
			if u'node' in service:
				logging.debug('Discovering service %s (node %s)',
				              service[u'jid'], service[u'node'])
				return features.discoverInfo(dispatcher, service[u'jid'],
				                             service[u'node'])
			else:
				logging.debug('Discovering service %s', service[u'jid'])
				return features.discoverInfo(dispatcher, service[u'jid'])
		except xml.parsers.expat.ExpatError:
			logging.warning('%s sent malformed XMPP', service[u'jid'],
			                exc_info=True)
			#return ([], [])
			#add_service_unavailable(service[u'jid'],
			                        #server[u'unavailableServices'])
			raise
			
	else:
		logging.debug('Ignoring %s', service[u'jid'])
		return  ([], [])


def get_items(dispatcher, service):
	'''Query the child items and nodes of service.
	Only returns items whose address it's equal or a subdomain of service'''
	
	try:
		if u'node' in service:
			items = features.discoverItems(dispatcher,
				                           service[u'jid'], service[u'node'])
		else:
			items = features.discoverItems(dispatcher,
			                               service[u'jid'])
	except xml.parsers.expat.ExpatError:
		logging.warning('%s sent malformed XMPP', service[u'jid'],
		                exc_info=True)
		#items = []
		raise
	
	# Process items
	
	for item in list(items):
		if not in_same_domain(service[u'jid'], item[u'jid']):
			items.remove(item)
	
	return items


def discover_item(dispatcher, service, server):
	'''Explore the service and its childs and 
	update the service list in server.
	Both, service and server, variables are modified.'''
	
	needs_to_query_items = False
	#cl.Process(1)
	
	try:
		service[u'info'] = get_item_info(dispatcher, service)
	except xml.parsers.expat.ExpatError:
		service[u'info'] = ([], [])
		add_service_unavailable(service[u'jid'], server[u'unavailableServices'])
		raise
	
	# Detect if it's a server or a branch (if it have child items)
	
	if (  (u'http://jabber.org/protocol/disco#info' in service[u'info'][1]) |
	      (u'http://jabber.org/protocol/disco' in service[u'info'][1])  ):
		needs_to_query_items = False
		add_service_available(service[u'info'][0], server[u'availableServices'])
		for identity in service[u'info'][0]:
			if ( (identity['category'] == u'server') | (
			        (identity['category'] == u'hierarchy') &
			        (identity['type'] == u'branch')
			   ) ):
				needs_to_query_items = True
	
	elif u'jabber:iq:agents' in service[u'info'][1]:
		#Fake identities. But we aren't really sure that it's a server?
		service[u'info'] = ( ({u'category': u'server', u'type': u'im'}),
		                     service[u'info'][1] )
		needs_to_query_items = True
	
	elif u'jabber:iq:browse' in service[u'info'][1]: #Not sure if it's really used
		# Adapt the information
		# Process items
		service[u'items'] = []
		for item in service[u'info'][0]:
			if in_same_domain(service[u'jid'], item[u'jid']):
				service[u'items'].append(discover_item(dispatcher, item, server))
		
		needs_to_query_items = False # We already have the items
		#Fake identities. But we aren't really sure that it's a server?
		service[u'info'] = ( ({u'category': u'server', u'type': u'im'}),
		                     service[u'info'][1] )
	
	elif (service[u'info'] == ([], [])):
		# We have to guess what feature is using the JID
		add_service_unavailable(service[u'jid'], server[u'unavailableServices'])
	
	else:
		if u'availableServices' in service:
			# It's a server. It probably uses jabber:iq:browse
			# Adapt the information
			# Process items
			service[u'items'] = []
			for item in service[u'info'][0]:
				if in_same_domain(service[u'jid'], item[u'jid']):
					service[u'items'].append(discover_item(dispatcher, item,
					                                       server))
			
			needs_to_query_items = False # We already have the items
			#Fake identities. But we aren't really sure that it's a server?
			service[u'info'] = ( ({u'category': u'server', u'type': u'im'}),
			                    service[u'info'][1] )
		else:
			#try:
				add_service_available(service[u'info'][0],
				                      server[u'availableServices'])
			#except:
				#add_service_unavailable(service[u'jid'],
				                        #server[u'unavailableServices'])
	
	# If it's a server or a branch node, get the child items
	
	if needs_to_query_items:
		try:
			service[u'items'] = get_items(dispatcher, service)
		except xml.parsers.expat.ExpatError:
			service[u'items'] = []
			raise
		
		for item in list(service[u'items']):
			if (service[u'jid'] != item[u'jid']):
				item = discover_item(dispatcher, item, server)
			elif u'node' in service:
				if (  (service[u'jid'] == item[u'jid']) &
					  (service[u'node'] != item[u'node'])  ):
					item = discover_item(dispatcher, item, server)
	
	return service


def show_node(node, indent=0):
	'''Print the node and its childs'''
	print node
	print ' '*indent,
	print 'JID:     ' + node[u'jid']
	
	print ' '*indent,
	print 'node:     ' + node[u'node']
	
	if u'info' in node:
		for identity in node[u'info'][0]:
			print ' '*indent,
			print 'INFO: id: ' + str(identity)
		for feature in node[u'info'][1]:
			print ' '*indent,
			print 'INFO: ft: ' + str(feature)
	
	if u'items' in node:
		for item in node[u'items']:
			show_node(item, indent+4)
	


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

servers = []

for item in items:
	if {u'jid': item.getAttr("jid")} not in servers:
		servers.append({ u'jid': item.getAttr("jid"),
		                 u'availableServices': Set(), 
	                     u'unavailableServices': Set() })

#servers=[{u'jid': u'jabberes.org', u'availableServices': Set(), u'unavailableServices': Set()}, {u'jid': u'jab.undernet.cz', u'availableServices': Set(), u'unavailableServices': Set()}, {u'jid': u'12jabber.com', u'availableServices': Set(), u'unavailableServices': Set()}, {u'jid': u'allchitchat.com', u'availableServices': Set(), u'unavailableServices': Set()}]
#servers=[{u'jid': u'jabber.dk', u'availableServices': Set(), u'unavailableServices': Set()}, {u'jid': u'amessage.be', u'availableServices': Set(), u'unavailableServices': Set()}]



# Connect to server

cl = Client(JABBERSERVER, debug=[])
if not cl.connect(secure=0):
	raise IOError('Can not connect to server.')
if not cl.auth(JABBERUSER, JABBERPASSWORD, JABBERRESOURCE):
	raise IOError('Can not auth with server.')

cl.sendInitPresence()
cl.Process(1)

logging.info('Begin discovery')

for server in servers:
	try:
		discover_item(cl.Dispatcher, server, server)
	
	except xml.parsers.expat.ExpatError: # Restart the client
		#cl.disconnect()
		logging.warning('Aborting discovery of %s server. ' +
		                'Restarting the client.', server[u'jid'])
		cl = Client(JABBERSERVER, debug=[])
		if not cl.connect(secure=0):
			raise IOError('Can not connect to server.')
		if not cl.auth(JABBERUSER, JABBERPASSWORD, JABBERRESOURCE):
			raise IOError('Can not auth with server.')
		cl.sendInitPresence()
		cl.Process(1)
	
cl.Process(10)
#for server in servers:
#	show_node(server)
cl.disconnect()

logging.info('Discovery Finished')

for server in servers:
	print
	print 'Server: ' + server[u'jid']
	print "Available:",
	for service in server[u'availableServices']: print " " + service,
	print "\nUnavailable:",
	for service in server[u'unavailableServices']: print " " + service
	print ''
	
#f = open('servers.dump', 'wb')
#pickle.dump(servers, f)

#f = open('servers.dump', 'rb')
#servers = pickle.load(f)


logging.info('Updating Database')

db = MySQLdb.Connection( user=DBUSER, passwd=DBPASSWORD, host=DBHOST,
                         db=DBDATABASE )

#f.close()

# feature: database field
dbfields = {
	'muc':       'has_muc',
	'irc':       'has_irc',
	'aim':       'has_aim',
	'gg':        'has_gg',
	'http-ws':   'has_httpws',
	'icq':       'has_icq',
	'msn':       'has_msn',
	'qq':        'has_qq',
	'sms':       'has_sms',
	'smtp':      'has_smtp',
	'tlen':      'has_tlen',
	'yahoo':     'has_yahoo',
	'jud':       'has_jud',
	'pubsub':    'has_pubsub',
	'pep':       'has_pep',
	'presence':  'has_presence',
	'newmail':   'has_newmail',
	'rss':       'has_rss',
	'weather':   'has_weather',
	'proxy':     'has_proxy'
}

# u'muc', u'irc', u'aim', u'gg', u'http-ws', u'icq', u'msn', u'qq',
# u'sms', u'smtp', u'tlen', u'yahoo', u'jud', u'pubsub', u'pep', u'presence',
# u'newmail', u'rss', u'weather', u'proxy'

for server in servers:
	if server[u'info'] != ([], []):
		
		query = "`name` = '" + server[u'jid'] + "', "
		
		for service in dbfields.keys():
			if service in server[u'availableServices']:
				query += "`" + dbfields[service] + "` = 255, "
			elif service in server[u'unavailableServices']:
				query += "`" + dbfields[service] + "` = 1, "
			else:
				query += "`" + dbfields[service] + "` = 0, "
		
		query += "`times_offline` = 0"
		
		query = ( "INSERT " + DBTABLE + " SET " + query +
		          " ON DUPLICATE KEY UPDATE " + query )
		
	else:
		
		query = "`name` = '" + server[u'jid'] + "', "
		for service in dbfields.keys():
			query += "`" + dbfields[service] + "` = 0, "
		query += "`times_offline` = `times_offline` + 1"
		
		query = ( "INSERT " + DBTABLE+" SET " + query +
		         " ON DUPLICATE KEY UPDATE " + query )
	
	logging.debug('Executing query: %s', query)
	db.query(query)

# Clean the table
c = db.cursor(MySQLdb.cursors.DictCursor)
c.execute("SELECT name FROM " + DBTABLE)
resulset = c.nextset()
while resulset is not None:
	exists = False
	for server in servers:
		if resulset[u'name'] == server['jid']:
			exists = True
			break
		
	if not exists:
		query = ( "DELETE FROM " + DBTABLE + " WHERE name = '" +
		          resulset[u'name'] + "'" )
		logging.debug('Executing query: %s', query)
		db.execute(query)

c.close()

logging.info('Database updated')
