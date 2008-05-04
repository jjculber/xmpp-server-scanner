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
import re
#from sets import Set
import urllib
import xml.parsers.expat

import MySQLdb

from xmpp import Client, features, simplexml
from xmpp.protocol import Message

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
	


def _add_to_services_list(services_list, service_type, component_jid):
	'''Add the compoenent to the server services list.
	There can be several components providing the same service.'''
	if service_type in services_list:
		services_list[service_type].append(component_jid)
	else:
		services_list[service_type] = [(component_jid)]


def add_component_available(component, services_list):
	'''Process identity and update the set of server services_list'''
	
	for identity in component[u'info'][0]:
		if identity[u'category'] == u'conference':
			if identity[u'type'] == u'text':
				if u'http://jabber.org/protocol/muc' in component[u'info'][1]:
					_add_to_services_list(services_list, 'muc', component['jid'])
			elif identity[u'type'] == u'irc':
				_add_to_services_list(services_list, 'irc', component['jid'])
			
		if identity[u'category'] == u'gateway':
			if identity[u'type'] == u'aim':
				_add_to_services_list(services_list, 'aim', component['jid'])
			elif identity[u'type'] == u'gadu-gadu':
				_add_to_services_list(services_list, 'gadu-gadu', component['jid'])
			elif identity[u'type'] == u'http-ws':
				_add_to_services_list(services_list, 'http-ws', component['jid'])
			elif identity[u'type'] == u'icq':
				_add_to_services_list(services_list, 'icq', component['jid'])
			elif identity[u'type'] == u'msn':
				_add_to_services_list(services_list, 'msn', component['jid'])
			elif identity[u'type'] == u'qq':
				_add_to_services_list(services_list, 'qq', component['jid'])
			elif identity[u'type'] == u'sms':
				_add_to_services_list(services_list, 'sms', component['jid'])
			elif identity[u'type'] == u'smtp':
				_add_to_services_list(services_list, 'smtp', component['jid'])
			elif identity[u'type'] == u'tlen':
				_add_to_services_list(services_list, 'tlen', component['jid'])
			elif identity[u'type'] == u'yahoo':
				_add_to_services_list(services_list, 'yahoo', component['jid'])
			
		if identity[u'category'] == u'directory':
			if identity[u'type'] == u'user':
				_add_to_services_list(services_list, 'jud', component['jid'])
			
		if identity[u'category'] == u'pubsub':
			if identity[u'type'] == u'service': # XEP
				_add_to_services_list(services_list, 'pubsub', component['jid'])
			elif identity[u'type'] == u'generic': # ejabberd 1.1.3
				_add_to_services_list(services_list, 'pubsub', component['jid'])
			elif identity[u'type'] == u'pep':
				_add_to_services_list(services_list, 'pep', component['jid'])
			
		if identity[u'category'] == u'component':
			if identity[u'type'] == u'presence':
				_add_to_services_list(services_list, 'presence', component['jid'])
			
		if identity[u'category'] == u'headline':
			if identity[u'type'] == u'newmail':
				_add_to_services_list(services_list, 'newmail', component['jid'])
			elif identity[u'type'] == u'rss':
				_add_to_services_list(services_list, 'rss', component['jid'])
			elif identity[u'type'] == u'weather':
				_add_to_services_list(services_list, 'weather', component['jid'])
			
		if identity[u'category'] == u'proxy':
			if identity[u'type'] == u'bytestreams':
				_add_to_services_list(services_list, 'proxy', component['jid'])
			
		# Non standard services_list
		
		if identity[u'category'] == u'agent': 
			if identity[u'type'] == u'weather':
				_add_to_services_list(services_list, 'weather', component['jid'])
			
		if identity[u'category'] == u'x-service':
			if identity[u'type'] == u'x-rss': # PyRSS
				_add_to_services_list(services_list, 'rss', component['jid'])


def add_component_unavailable(jid, services_list):
	'''Guess the service using the JIDs and update the set of servers
	services_list'''
	
	logging.debug('Guessing type of %s', jid)
	
	# Conference
	if jid.startswith((u'conference.', u'conf.', u'muc.', u'chat.', u'rooms.')):
		_add_to_services_list(services_list, 'muc', jid)
	elif jid.startswith(u'irc.'):
		_add_to_services_list(services_list, 'irc', jid)
	
	# Transports
	elif jid.startswith((u'aim.', u'aim-jab.')):
		_add_to_services_list(services_list, 'aim', jid)
	elif jid.startswith(u'aim-icq.'):
		_add_to_services_list(services_list, 'aim', jid)
		_add_to_services_list(services_list, 'icq', jid)
	elif jid.startswith((u'gg.', u'gadugadu.', u'gadu-gadu.')):
		_add_to_services_list(services_list, 'gadu-gadu', jid)
	elif jid.startswith(u'http-ws.'):
		_add_to_services_list(services_list, 'http-ws', jid)
	elif jid.startswith((u'icq.', u'icqt.', u'jit-icq.', u'icq-jab.', u'icq2')):
		_add_to_services_list(services_list, 'icq', jid)
	elif jid.startswith((u'msn.', u'msnt.', u'pymsnt.')):
		_add_to_services_list(services_list, 'msn', jid)
	elif jid.startswith(u'qq.'):
		_add_to_services_list(services_list, 'qq', jid)
	elif jid.startswith(u'sms.'):
		_add_to_services_list(services_list, 'sms', jid)
	elif jid.startswith(u'smtp.'):
		_add_to_services_list(services_list, 'smtp', jid)
	elif jid.startswith(u'tlen.'):
		_add_to_services_list(services_list, 'tlen', jid)
	elif jid.startswith(u'yahoo.'):
		_add_to_services_list(services_list, 'yahoo', jid)
	
	# Directories
	elif jid.startswith((u'jud.', u'vjud.', u'search.', u'users.')):
		_add_to_services_list(services_list, 'jud', jid)
	
	# PubSub
	elif jid.startswith(u'pubsub.'):
		_add_to_services_list(services_list, 'pubsub', jid)
	elif jid.startswith(u'pep.'):
		_add_to_services_list(services_list, 'pep', jid)
	
	# Presence
	elif jid.startswith((u'presence.', u'webpresence.')):
		_add_to_services_list(services_list, 'presence', jid)
	
	# Headline
	elif jid.startswith((u'newmail.', u'mail.', u'jmc.')):
		_add_to_services_list(services_list, 'newmail', jid)
	elif jid.startswith(u'rss.'):
		_add_to_services_list(services_list, 'rss', jid)
	elif jid.startswith(u'weather.'):
		_add_to_services_list(services_list, 'weather', jid)
	
	# Proxy
	elif jid.startswith((u'proxy.', u'proxy65')):
		_add_to_services_list(services_list, 'proxy', jid)



def get_item_info(dispatcher, component):
	'''Query the information about the item'''
	
	# Some components adresses ends in .localhost so the querys
	# will end on a 404 error
	# Then, we don't need to waste resources querying them
	if not component[u'jid'].endswith('.localhost'):
		try:
			if u'node' in component:
				logging.debug('Discovering component %s (node %s)',
				              component[u'jid'], component[u'node'])
				return features.discoverInfo(dispatcher, component[u'jid'],
				                             component[u'node'])
			else:
				logging.debug('Discovering component %s', component[u'jid'])
				return features.discoverInfo(dispatcher, component[u'jid'])
		except xml.parsers.expat.ExpatError:
			logging.warning('%s sent malformed XMPP', component[u'jid'],
			                exc_info=True)
			#return ([], [])
			#add_component_unavailable(component[u'jid'],
			                        #server[u'unavailableServices'])
			raise
			
	else:
		logging.debug('Ignoring %s', component[u'jid'])
		return  ([], [])


def get_items(dispatcher, component):
	'''Query the child items and nodes of component.
	Only returns items whose address it's equal or a subdomain of component'''
	
	try:
		if u'node' in component:
			items = features.discoverItems(dispatcher,
				                           component[u'jid'], component[u'node'])
		else:
			items = features.discoverItems(dispatcher,
			                               component[u'jid'])
	except xml.parsers.expat.ExpatError:
		logging.warning('%s sent malformed XMPP', component[u'jid'],
		                exc_info=True)
		#items = []
		raise
	
	# Process items
	
	for item in list(items):
		if not in_same_domain(component[u'jid'], item[u'jid']):
			items.remove(item)
	
	return items


def discover_item(dispatcher, component, server):
	'''Explore the component and its childs and 
	update the component list in server.
	Both, component and server, variables are modified.'''
	
	needs_to_query_items = False
	#cl.Process(1)
	
	try:
		component[u'info'] = get_item_info(dispatcher, component)
	except xml.parsers.expat.ExpatError:
		component[u'info'] = ([], [])
		add_component_unavailable(component[u'jid'], server[u'unavailableServices'])
		raise
	
	# Detect if it's a server or a branch (if it have child items)
	
	if (  (u'http://jabber.org/protocol/disco#info' in component[u'info'][1]) |
	      (u'http://jabber.org/protocol/disco' in component[u'info'][1])  ):
		needs_to_query_items = False
		add_component_available(component, server[u'availableServices'])
		for identity in component[u'info'][0]:
			if ( (identity['category'] == u'server') | (
			        (identity['category'] == u'hierarchy') &
			        (identity['type'] == u'branch')
			   ) ):
				needs_to_query_items = True
	
	elif u'jabber:iq:agents' in component[u'info'][1]:
		#Fake identities. But we aren't really sure that it's a server?
		component[u'info'] = ( ({u'category': u'server', u'type': u'im'}),
		                     component[u'info'][1] )
		needs_to_query_items = True
	
	elif u'jabber:iq:browse' in component[u'info'][1]: #Not sure if it's really used
		# Adapt the information
		# Process items
		component[u'items'] = []
		for item in component[u'info'][0]:
			if in_same_domain(component[u'jid'], item[u'jid']):
				component[u'items'].append(discover_item(dispatcher, item, server))
		
		needs_to_query_items = False # We already have the items
		#Fake identities. But we aren't really sure that it's a server?
		component[u'info'] = ( ({u'category': u'server', u'type': u'im'}),
		                     component[u'info'][1] )
	
	elif (component[u'info'] == ([], [])):
		# We have to guess what feature is using the JID
		add_component_unavailable(component[u'jid'], server[u'unavailableServices'])
	
	else:
		if u'availableServices' in component:
			# It's a server. It probably uses jabber:iq:browse
			# Adapt the information
			# Process items
			component[u'items'] = []
			for item in component[u'info'][0]:
				if in_same_domain(component[u'jid'], item[u'jid']):
					component[u'items'].append(discover_item(dispatcher, item,
					                                       server))
			
			needs_to_query_items = False # We already have the items
			#Fake identities. But we aren't really sure that it's a server?
			component[u'info'] = ( ({u'category': u'server', u'type': u'im'}),
			                    component[u'info'][1] )
		else:
			#try:
			add_component_available(component, server[u'availableServices'])
			#except:
				#add_component_unavailable(component[u'jid'],
				                        #server[u'unavailableServices'])
	
	# If it's a server or a branch node, get the child items
	
	if needs_to_query_items:
		try:
			component[u'items'] = get_items(dispatcher, component)
		except xml.parsers.expat.ExpatError:
			component[u'items'] = []
			raise
		
		for item in list(component[u'items']):
			if (component[u'jid'] != item[u'jid']):
				item = discover_item(dispatcher, item, server)
			elif u'node' in component:
				if (  (component[u'jid'] == item[u'jid']) &
					  (component[u'node'] != item[u'node'])  ):
					item = discover_item(dispatcher, item, server)
	
	return component


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
		                 u'availableServices': {}, 
	                     u'unavailableServices': {} })

#servers=[{u'jid': u'jabberes.org', u'availableServices': {}, u'unavailableServices': {}}, {u'jid': u'jab.undernet.cz', u'availableServices': {}, u'unavailableServices': {}}, {u'jid': u'12jabber.com', u'availableServices': {}, u'unavailableServices': {}}, {u'jid': u'allchitchat.com', u'availableServices': {}, u'unavailableServices': {}}]
#servers=[{u'jid': u'jabber.dk', u'availableServices': {}, u'unavailableServices': {}}, {u'jid': u'amessage.be', u'availableServices': {}, u'unavailableServices': {}}]
#servers=[
    #{u'jid': u'jabberes.org', u'availableServices': {}, u'unavailableServices': {}},
    #{u'jid': u'jabber.dk', u'availableServices': {}, u'unavailableServices': {}},
    #{u'jid': u'jabber-hispano.org', u'availableServices': {}, u'unavailableServices': {}}
#]

#servers=[]

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

#f = open('servers.dump', 'wb')
#pickle.dump(servers, f)

#f = open('servers.dump', 'rb')
#servers = pickle.load(f)

#f.close()


logging.info('Updating Database')

db = MySQLdb.Connection( user=DBUSER, passwd=DBPASSWORD, host=DBHOST,
                         db=DBDATABASE )

db.autocommit(True)

# Check service types


known_types = [ 'muc', 'irc', 'aim', 'gadu-gadu', 'http-ws', 'icq', 'msn', 'qq',
                'sms', 'smtp', 'tlen', 'yahoo', 'jud', 'pubsub', 'pep',
                'presence', 'newmail', 'rss', 'weather', 'proxy' ]


cursor = db.cursor(MySQLdb.cursors.DictCursor)
cursor.execute("""SELECT `type` FROM `pybot_service_types`""")
for row in cursor.fetchall():
	if row['type'] not in known_types:
		logging.info('Deleting service type %s', row['type'])
		cursor.execute("""DELETE FROM pybot_service_types
		                    WHERE type = %s """, (row['type'],))
	else:
		known_types.remove(row['type'])

for t in known_types:
	logging.debug('Add new service type %s', t)
	cursor.execute("""INSERT INTO pybot_service_types SET type = %s""", (t,))


# Save the servers and services

for server in servers:
	
	# Add server
	
	if server[u'info'] != ([], []): # Online server
		logging.debug('Add online server %s', server[u'jid'])
		cursor.execute("""INSERT INTO pybot_servers 
		                    SET jid = %s, times_offline = %s
		                    ON DUPLICATE KEY UPDATE times_offline = %s""",
		               (server[u'jid'], 0, 0))
		
		#Add services
		
		logging.debug('Delete components of %s server', server[u'jid'])
		cursor.execute("""DELETE FROM pybot_components
		                    WHERE server_jid = %s""", (server[u'jid'],) )
		
		for service in server[u'availableServices']:
			for component in server[u'availableServices'][service]:
				logging.debug( 'Add available %s component %s of %s server',
				               service, component, server[u'jid'])
				cursor.execute("""INSERT INTO  pybot_components
				                    SET jid = %s, server_jid = %s,
				                        type = %s, available = %s
				                    ON DUPLICATE KEY UPDATE available = %s""",
								(component, server[u'jid'], service, True, True))
		
		for service in server[u'unavailableServices']:
			for component in server[u'unavailableServices'][service]:
				logging.debug( 'Add unavailable %s component %s of %s server',
				               service, component, server[u'jid'])
				cursor.execute("""INSERT INTO pybot_components
				                    SET jid = %s, server_jid = %s,
				                        type = %s, available = %s
				                    ON DUPLICATE KEY UPDATE available = %s""",
				                (component, server[u'jid'], service, False, False))
	
	else:                           # Offline server
		logging.debug('Add offline server %s', server[u'jid'])
		cursor.execute("""INSERT INTO pybot_servers
		                    SET `jid` = %s, times_offline = %s
		                    ON DUPLICATE KEY UPDATE 
		                      times_offline = times_offline + %s""",
		                (server[u'jid'], 1, 1))


# Clean the servers table
cursor.execute("""SELECT jid FROM pybot_servers""")
for row in cursor.fetchall():
	exists = False
	for server in servers:
		if row[u'jid'] == server['jid']:
			exists = True
			break
		
	if not exists:
		logging.debug('Delete old server %s', row['jid'])
		cursor.execute("""DELETE FROM pybot_servers WHERE jid = %s""",
		                (row['jid'],))

cursor.close()

logging.info('Database updated')
