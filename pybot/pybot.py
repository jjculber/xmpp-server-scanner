#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# 
# Under GNU General Public License
# 
# TODO: Si falla un query, reintentar?

# Multithread
# Testing
# Make the code more prettier, pylint
# Check for SQL injections



#jabberuser="my_user"
#jabberpassword="password"
#jabberresource="pybot"
#jabberserver="jabberes.org"

# Jabber account
jabberuser     = "xxxxxxx"
jabberpassword = "xxxxxxx"
jabberresource = "pybot"
jabberserver   = "xmpp.example.net"

# Database
dbuser         = "user"
dbpassword     = "sql_password"
dbhost         = "localhost"
dbdatabase     = "server_list"
dbtable        = "pyservers"

useurl         = False
servers_url    = "http://www.jabber.org/basicservers.xml"
servers_file   = "servers-fixed.xml"

logfile='out.log'

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

if logfile is None:
	logging.basicConfig(
		level=logging.DEBUG,
		format='%(asctime)s %(levelname)s %(message)s'
		)
else:
	logging.basicConfig(
		level=logging.DEBUG,
		format='%(asctime)s %(levelname)s %(message)s',
		filename=logfile,
		filemode='w'
		)



urlRegExp = re.compile(
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
	
	parentMatch = urlRegExp.search(parent)
	childMatch = urlRegExp.search(child)
	
	if childMatch.group('tld') == 'localhost':
		return True
	elif 'domain' not in childMatch.groupdict().keys():
		return True
	elif childMatch.group('domain') in ('com', 'net', 'org', 'co', 'gov', 'edu'):
		# It's a country code second level domain, until the third level
		return (parentMatch.group('fullsubdomain') == childMatch.group('fullsubdomain'))
	else:
		# It's a usual domain name, check until the second level
		return (parentMatch.group('fulldomain') == childMatch.group('fulldomain'))
	


def add_service_available(identities, serviceSet):
	'''Process identity and update the set of server serviceSet'''
	
	for identity in identities:
		if identity[u'category'] == u'conference':
			if identity[u'type'] == u'text':
				#if u'http://jabber.org/protocol/muc' in service[u'info'][1]:
					serviceSet.add('muc')
			elif identity[u'type'] == u'irc':
				serviceSet.add('irc')
			
		if identity[u'category'] == u'gateway':
			if identity[u'type'] == u'aim':
				serviceSet.add('aim')
			elif identity[u'type'] == u'gadu-gadu':
				serviceSet.add('gadu-gadu')
			elif identity[u'type'] == u'http-ws':
				serviceSet.add('http-ws')
			elif identity[u'type'] == u'icq':
				serviceSet.add('icq')
			elif identity[u'type'] == u'msn':
				serviceSet.add('msn')
			elif identity[u'type'] == u'qq':
				serviceSet.add('qq')
			elif identity[u'type'] == u'sms':
				serviceSet.add('sms')
			elif identity[u'type'] == u'smtp':
				serviceSet.add('smtp')
			elif identity[u'type'] == u'tlen':
				serviceSet.add('tlen')
			elif identity[u'type'] == u'yahoo':
				serviceSet.add('yahoo')
			
		if identity[u'category'] == u'directory':
			if identity[u'type'] == u'user':
				serviceSet.add('jud')
			
		if identity[u'category'] == u'pubsub':
			if identity[u'type'] == u'service': # XEP
				serviceSet.add('pubsub')
			elif identity[u'type'] == u'generic': # ejabberd 1.1.3
				serviceSet.add('pubsub')
			elif identity[u'type'] == u'pep':
				serviceSet.add('pep')
			
		if identity[u'category'] == u'component':
			if identity[u'type'] == u'presence':
				serviceSet.add('presence')
			
		if identity[u'category'] == u'headline':
			if identity[u'type'] == u'newmail':
				serviceSet.add('newmail')
			elif identity[u'type'] == u'rss':
				serviceSet.add('rss')
			elif identity[u'type'] == u'weather':
				serviceSet.add('weather')
			
		if identity[u'category'] == u'proxy':
			if identity[u'type'] == u'bytestreams':
				serviceSet.add('proxy')
			
		# Non standard serviceSet
		
		if identity[u'category'] == u'agent': 
			if identity[u'type'] == u'weather':
				serviceSet.add('weather')
			
		if identity[u'category'] == u'x-service':
			if identity[u'type'] == u'x-rss': # PyRSS
				serviceSet.add('rss')


def add_service_unavailable(jid, serviceSet):
	'''Guess the service using the JIDs and update the set of server serviceSet'''
	
	logging.debug('Guessing type of %s', jid)
	
	# Conference
	if jid.startswith((u'conference.', u'conf.', u'muc.', u'chat.', u'rooms.')):
		serviceSet.add('muc')
	elif jid.startswith(u'irc.'):
		serviceSet.add('irc')
	
	# Transports
	elif jid.startswith((u'aim.', u'aim-jab.')):
		serviceSet.add('aim')
	elif jid.startswith(u'aim-icq.'):
		serviceSet.add('aim')
		serviceSet.add('icq')
	elif jid.startswith((u'gg.', u'gadugadu.', u'gadu-gadu.')):
		serviceSet.add('gg')
	elif jid.startswith(u'http-ws.'):
		serviceSet.add('http-ws')
	elif jid.startswith((u'icq.', u'icqt.', u'jit-icq.', u'icq-jab.', u'icq2')):
		serviceSet.add('icq')
	elif jid.startswith((u'msn.', u'msnt.', u'pymsnt.')):
		serviceSet.add('msn')
	elif jid.startswith(u'qq.'):
		serviceSet.add('qq')
	elif jid.startswith(u'sms.'):
		serviceSet.add('sms')
	elif jid.startswith(u'smtp.'):
		serviceSet.add('smtp')
	elif jid.startswith(u'tlen.'):
		serviceSet.add('tlen')
	elif jid.startswith(u'yahoo.'):
		serviceSet.add('yahoo')
	
	# Directories
	elif jid.startswith((u'jud.', u'vjud.', u'search.', u'users.')):
		serviceSet.add('jud')
	
	# PubSub
	elif jid.startswith(u'pubsub.'):
		serviceSet.add('pubsub')
	elif jid.startswith(u'pep.'):
		serviceSet.add('pep')
	
	# Presence
	elif jid.startswith((u'presence.', u'webpresence.')):
		serviceSet.add('presence')
	
	# Headline
	elif jid.startswith((u'newmail.', u'mail.', u'jmc.')):
		serviceSet.add('newmail')
	elif jid.startswith(u'rss.'):
		serviceSet.add('rss')
	elif jid.startswith(u'weather.'):
		serviceSet.add('weather')
	
	# Proxy
	elif jid.startswith((u'proxy.', u'proxy65')):
		serviceSet.add('proxy')


def discover_item(dispatcher, service, server):
	isParent = False
	#cl.Process(1)
	
	#Process Info
	
	# Some components adresses ends in .localhost so the querys will end on a 404 error
	# Then, we don't need to waste resources querying them
	if not service[u'jid'].endswith('.localhost'):
		try:
			try:
				logging.debug('Discovering service %s (node %s)', service[u'jid'], service[u'node'])
				service[u'info'] = features.discoverInfo(dispatcher, service[u'jid'], service[u'node'])
			except KeyError:
				logging.debug('Discovering service %s', service[u'jid'])
				service[u'info'] = features.discoverInfo(dispatcher, service[u'jid'])
		except xml.parsers.expat.ExpatError:
			logging.warning('%s sent malformed XMPP', service[u'jid'], exc_info=True)
			service[u'info'] = ([], [])
			add_service_unavailable(service[u'jid'], server[u'unavailableServices'])
			raise
			
	else:
		logging.debug('Ignoring %s', service[u'jid'])
		service[u'info'] = ([], [])
	
	if (u'http://jabber.org/protocol/disco#info' in service[u'info'][1]) | (u'http://jabber.org/protocol/disco' in service[u'info'][1]):
		isParent = False
		add_service_available(service[u'info'][0], server[u'availableServices'])
		for identity in service[u'info'][0]:
			if (identity['category'] == u'server') | ((identity['category'] == u'hierarchy') & (identity['type'] == u'branch')):
				isParent = True
			
	elif u'jabber:iq:agents' in service[u'info'][1]:
		#Fake identities. But we aren't really sure that it's a server?
		service[u'info'] = (({u'category': u'server', u'type': u'im'}), service[u'info'][1])
		isParent = True
		
	elif u'jabber:iq:browse' in service[u'info'][1]: #Not sure if it's really used
		# Adapt the information
		# Process items
		service[u'items'] = []
		for item in service[u'info'][0]:
			if in_same_domain(service[u'jid'], item[u'jid']):
				service[u'items'].append(discover_item(dispatcher, item, server))
		
		isParent = False # We already have the items
		#Fake identities. But we aren't really sure that it's a server?
		service[u'info'] = (({u'category': u'server', u'type': u'im'}), service[u'info'][1])
	elif (len(service[u'info'][0]) == 0) & (len(service[u'info'][1]) == 0):
		# We have to guess what feature is using the JID
		add_service_unavailable(service[u'jid'], server[u'unavailableServices'])
	else:
		if u'availableServices' in service.keys():
			# It's a server. It probably uses jabber:iq:browse
			# Adapt the information
			# Process items
			service[u'items'] = []
			for item in service[u'info'][0]:
				if in_same_domain(service[u'jid'], item[u'jid']):
					service[u'items'].append(discover_item(dispatcher, item, server))
			
			isParent = False # We already have the items
			#Fake identities. But we aren't really sure that it's a server?
			service[u'info'] = (({u'category': u'server', u'type': u'im'}),service[u'info'][1])
		else:
			try:
				add_service_available(service[u'info'][0], server[u'availableServices'])
			except:
				add_service_unavailable(service[u'jid'], server[u'unavailableServices'])
	
	# Process Items
	if isParent:
		if u'node' in service.keys():
			service[u'items'] = features.discoverItems(dispatcher, service[u'jid'], service[u'node'])
		else:
			service[u'items'] = features.discoverItems(dispatcher, service[u'jid'])
		
		for item in list(service[u'items']):
			if in_same_domain(service[u'jid'], item[u'jid']):
				if (service[u'jid'] != item[u'jid']):
					item = discover_item(dispatcher, item, server)
				elif u'node' in service.keys():
					if (service[u'jid'] == item[u'jid']) & (service[u'node'] != item[u'node']):
						item = discover_item(dispatcher, item, server)
			else:
				service[u'items'].remove(item)
		
	return service


def showNode(node, indent=0):
	print node
	for n in range(0, indent+1): print ' ',
	print 'JID:     ' + node[u'jid']
	
	for n in range(0, indent+1): print ' ',
	print 'node:     ' + node[u'node']
	
	if u'info' in node.keys():
		for identity in node[u'info'][0]:
			for n in range(0, indent+1): print ' ',
			print 'INFO: id: ' + str(identity)
		for feature in node[u'info'][1]:
			for n in range(0, indent+1): print ' ',
			print 'INFO: ft: ' + str(feature)
	
	if u'items' in node.keys():
		for item in node[u'items']:
			showNode(item, indent+4)
	


# Get server list

if useurl:
	f = urllib.urlopen(servers_url)
else:
	f = open(servers_file, 'r')

xmldata = f.read()
f.close()

node = simplexml.XML2Node(xmldata)

#items = node.getChildren()
items = node.getTags(name="item")

servers = []

for item in items:
	if {u'jid': item.getAttr("jid")} not in servers:
		servers.append({u'jid': item.getAttr("jid"), u'availableServices': Set(), u'unavailableServices': Set()})

#servers=[{u'jid': u'jabberes.org', u'availableServices': Set(), u'unavailableServices': Set()}, {u'jid': u'jab.undernet.cz', u'availableServices': Set(), u'unavailableServices': Set()}, {u'jid': u'12jabber.com', u'availableServices': Set(), u'unavailableServices': Set()}, {u'jid': u'allchitchat.com', u'availableServices': Set(), u'unavailableServices': Set()}]
#servers=[{u'jid': u'jabber.dk', u'availableServices': Set(), u'unavailableServices': Set()}]



# Connect to server

cl=Client(jabberserver, debug=[])
if not cl.connect(secure=0):
	raise IOError('Can not connect to server.')
if not cl.auth(jabberuser, jabberpassword, jabberresource):
	raise IOError('Can not auth with server.')

cl.sendInitPresence()
cl.Process(1)

logging.info('Begin discovery')

for server in servers:
	try:
		discover_item(cl.Dispatcher, server, server)
	
	except xml.parsers.expat.ExpatError: # Restart the client
		#cl.disconnect()
		logging.warning('Aborting discovery of %s server. Restarting the client.', server[u'jid'])
		cl=Client(jabberserver, debug=[])
		if not cl.connect(secure=0):
			raise IOError('Can not connect to server.')
		if not cl.auth(jabberuser, jabberpassword, jabberresource):
			raise IOError('Can not auth with server.')
		cl.sendInitPresence()
		cl.Process(1)
	
cl.Process(10)
#for server in servers:
#	showNode(server)
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

db = MySQLdb.Connection(user = dbuser, passwd = dbpassword, host = dbhost, db = dbdatabase)

#f.close()

# feature: database field
dbfields = {
	u'muc': 'has_muc',
	u'irc': 'has_irc',
	u'aim': 'has_aim',
	u'gg': 'has_gg',
	u'http-ws': 'has_httpws',
	u'icq': 'has_icq',
	u'msn': 'has_msn',
	u'qq': 'has_qq',
	u'sms': 'has_sms',
	u'smtp': 'has_smtp',
	u'tlen': 'has_tlen',
	u'yahoo': 'has_yahoo',
	u'jud': 'has_jud',
	u'pubsub': u'has_pubsub',
	u'pep': 'has_pep',
	u'presence': 'has_presence',
	u'newmail': 'has_newmail',
	u'rss': 'has_rss',
	u'weather': 'has_weather',
	u'proxy': u'has_proxy'
}

# u'muc', u'irc', u'aim', u'gg', u'http-ws', u'icq', u'msn', u'qq', u'sms', u'smtp', u'tlen', u'yahoo', u'jud', u'pubsub', u'pep', u'presence', u'newmail', u'rss', u'weather', u'proxy'

for server in servers:
	if server[u'info'] != ([], []):
		
		query = "`name` = '"+server[u'jid']+"', "
		
		for service in dbfields.keys():
			if service in server[u'availableServices']:
				query += "`"+dbfields[service]+"` = 255, "
			elif service in server[u'unavailableServices']:
				query += "`"+dbfields[service]+"` = 1, "
			else:
				query += "`"+dbfields[service]+"` = 0, "
		
		query += "`times_offline` = 0"
			
		query = "INSERT "+dbtable+" SET "+query+" ON DUPLICATE KEY UPDATE "+query
		
	else:
		
		query = "`name` = '"+server[u'jid']+"', "
		for service in dbfields.keys():
			query += "`"+dbfields[service]+"` = 0, "
		query += "`times_offline` = `times_offline` + 1"
		
		query = "INSERT "+dbtable+" SET "+query+" ON DUPLICATE KEY UPDATE "+query
	
	logging.debug('Executing query: %s', query)
	db.query(query)

# Clean the table
c = db.cursor(MySQLdb.cursors.DictCursor)
c.execute("SELECT name FROM "+dbtable)
resulset = c.nextset()
while resulset is not None:
	exists = False
	for server in servers:
		if resulset[u'name'] == server['jid']:
			exists = True
			break
		
	if not exists:
		query = "DELETE FROM "+dbtable+" WHERE name = '"+resulset[u'name']+"'"
		logging.debug('Executing query: %s', query)
		db.execute(query)

c.close()

logging.info('Database updated')
