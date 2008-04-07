#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

# 
# Under GNU General Public License
# 
# TODO: Si falla un query, reintentar?


#jabberuser="my_user"
#jabberpassword="password"
#jabberresource="pybot"
#jabberserver="jabberes.org"

jabberuser="my_user"
jabberpassword="my_user"
jabberresource="pybot"
jabberserver="xmpp.example.net"

dbuser="user"
dbpassword="my_user"
dbhost="xmpp.example.net"
dbdatabase=""
dbtable=""

useurl=False
servers_url="http://www.jabber.org/basicservers.xml"
servers_file="servers.xml"


#from xmpp import *
from xmpp import Client, features, simplexml
from xmpp.protocol import Message
import MySQLdb
import urllib
import re
from sets import Set


urlRegExp = re.compile(r'(?P<fullsubdomain>(?:(?P<subdomain>\w+)\.(?=\w+\.\w))?(?P<fulldomain>(?:(?P<domain>\w+)\.)?(?P<tld>\w+)$))')
#, 'subdomain.domain.tld').groups() 
#re.search('/(([^.]+\.)?(?=[^.]+\.[^.]+)((([^.]+)\.)([^.]+)$))/')


def inSameDomain(parent, child):
	
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
		return parentMatch.group('fullsubdomain') == childMatch.group('fullsubdomain')
	else:
		# It's a usual domain name, check until the second level
		return parentMatch.group('fulldomain') == childMatch.group('fulldomain')
	

# Process Identities and update the set of server components
def addFeature(identity, components):
	if identity[u'category'] == u'conference':
		if identity[u'type'] == u'text':
			#if u'http://jabber.org/protocol/muc' in service[u'info'][1]:
				components.add('muc')
		elif identity[u'type'] == u'irc':
			components.add('irc')
		
	if identity[u'category'] == u'gateway':
		if identity[u'type'] == u'aim':
			components.add('aim')
		elif identity[u'type'] == u'gadu-gadu':
			components.add('gadu-gadu')
		elif identity[u'type'] == u'http-ws':
			components.add('http-ws')
		elif identity[u'type'] == u'icq':
			components.add('icq')
		elif identity[u'type'] == u'msn':
			components.add('msn')
		elif identity[u'type'] == u'qq':
			components.add('qq')
		elif identity[u'type'] == u'sms':
			components.add('sms')
		elif identity[u'type'] == u'smtp':
			components.add('smtp')
		elif identity[u'type'] == u'tlen':
			components.add('tlen')
		elif identity[u'type'] == u'yahoo':
			components.add('yahoo')
		
	if identity[u'category'] == u'directory':
		if identity[u'type'] == u'user':
			components.add('jud')
		
	if identity[u'category'] == u'pubsub':
		if identity[u'type'] == u'service': # XEP
			components.add('pubsub')
		elif identity[u'type'] == u'generic': # ejabberd 1.1.3
			components.add('pubsub')
		elif identity[u'type'] == u'pep':
			components.add('pep')
		
	if identity[u'category'] == u'component':
		if identity[u'type'] == u'presence':
			components.add('presence')
		
	if identity[u'category'] == u'headline':
		if identity[u'type'] == u'newmail':
			components.add('newmail')
		elif identity[u'type'] == u'rss':
			components.add('rss')
		elif identity[u'type'] == u'weather':
			components.add('weather')
		
	if identity[u'category'] == u'proxy':
		if identity[u'type'] == u'bytestreams':
			components.add('proxy')
		
	# Non standard components
	
	if identity[u'category'] == u'agent': 
		if identity[u'type'] == u'weather':
			components.add('weather')
		
	if identity[u'category'] == u'x-service':
		if identity[u'type'] == u'x-rss': # PyRSS
			components.add('rss')
		
	
# Guess the feature using the JIDs and update the set of server components
def guessFeature(jid, components):
	
	# Conference
	if jid.startswith((u'conference.', u'conf.', u'muc.', u'chat.', u'rooms.')):
		components.add('muc')
	elif jid.startswith(u'irc.'):
		components.add('irc')
	
	# Transports
	elif jid.startswith((u'aim.', u'aim-jab.')):
		components.add('aim')
	elif jid.startswith(u'aim-icq.'):
		components.add('aim')
		components.add('icq')
	elif jid.startswith((u'gg.', u'gadugadu.', u'gadu-gadu.')):
		components.add('gg')
	elif jid.startswith(u'http-ws.'):
		components.add('http-ws')
	elif jid.startswith((u'icq.', u'icqt.', u'jit-icq.', u'icq-jab.', u'icq2')):
		components.add('icq')
	elif jid.startswith((u'msn.', u'msnt.', u'pymsnt.')):
		components.add('msn')
	elif jid.startswith(u'qq.'):
		components.add('qq')
	elif jid.startswith(u'sms.'):
		components.add('sms')
	elif jid.startswith(u'smtp.'):
		components.add('smtp')
	elif jid.startswith(u'tlen.'):
		components.add('tlen')
	elif jid.startswith(u'yahoo.'):
		components.add('yahoo')
	
	# Directories
	elif jid.startswith((u'jud.', u'vjud.', u'search.', u'users.')):
		components.add('jud')
	
	# PubSub
	elif jid.startswith(u'pubsub.'):
		components.add('pubsub')
	elif jid.startswith(u'pep.'):
		components.add('pep')
	
	# Presence
	elif jid.startswith((u'presence.', u'webpresence.')):
		components.add('presence')
	
	# Headline
	elif jid.startswith((u'newmail.', u'mail.', u'jmc.')):
		components.add('newmail')
	elif jid.startswith(u'rss.'):
		components.add('rss')
	elif jid.startswith(u'weather.'):
		components.add('weather')
	
	# Proxy
	elif jid.startswith((u'proxy.', u'proxy65')):
		components.add('proxy')
	
	


def disco(service, server):
	isParent=False
	#cl.Process(1)
	try:
		print 'DISCO' + service[u'jid'] + service[u'node']
	except KeyError:
		print 'DISCO' + service[u'jid']
	
	#Process Info
	try:
		service[u'info'] = features.discoverInfo(cl.Dispatcher, service[u'jid'], service[u'node'])
	except KeyError:
		service[u'info'] = features.discoverInfo(cl.Dispatcher, service[u'jid'])
	
	
	print service
	
	
	if (u'http://jabber.org/protocol/disco#info' in service[u'info'][1]) | (u'http://jabber.org/protocol/disco' in service[u'info'][1]):
		isParent=False
		for identity in service[u'info'][0]:
			print "ADD "+service[u'jid']+" to "+server[u'jid']+" features"
			addFeature(identity, server[u'features'])
			
			if (identity['category'] == u'server') | ((identity['category'] == u'hierarchy') & (identity['type'] == u'branch')):
				isParent=True
				print service[u'jid'] + ' is a parent'
			
	elif u'jabber:iq:agents' in service[u'info'][1]:
		#Fake identities. But we aren't really sure that it's a server?
		service[u'info']=(({u'category': u'server', u'type': u'im'}),service[u'info'][1])
		if u'node' in service.keys():
			service[u'items'] = features.discoverItems(cl.Dispatcher, service[u'jid'], service[u'node'])
		else:
			service[u'items'] = features.discoverItems(cl.Dispatcher, service[u'jid'])
			
	elif u'jabber:iq:browse' in service[u'info'][1]: #Not sure if it's really used
		# Adapt the information
		# Process items
		service[u'items']=[]
		for item in service[u'info'][0]:
			if inSameDomain(service[u'jid'], item[u'jid']):
				service[u'items'].append(disco(item, server))
		
		isParent=False # We already have the items
		#Fake identities. But we aren't really sure that it's a server?
		service[u'info']=(({u'category': u'server', u'type': u'im'}),service[u'info'][1])
	elif (len(service[u'info'][0]) == 0) & (len(service[u'info'][1]) == 0):
		# We have to guess what feature is using the JID
		guessFeature(service[u'jid'], server[u'features'])
	else:
		if u'features' in service.keys():
			# It's a server. It probably uses jabber:iq:browse
			# Adapt the information
			# Process items
			service[u'items']=[]
			for item in service[u'info'][0]:
				if inSameDomain(service[u'jid'], item[u'jid']):
					service[u'items'].append(disco(item, server))
			
			isParent=False # We already have the items
			#Fake identities. But we aren't really sure that it's a server?
			service[u'info']=(({u'category': u'server', u'type': u'im'}),service[u'info'][1])
		else:
			try:
				for identity in service[u'info'][0]:
					print "ADD "+service[u'jid']+" to "+server[u'jid']+" features"
					addFeature(identity, server[u'features'])
			except:
				guessFeature(service[u'jid'], server[u'features'])
		
	
	
	
	# Process Items
	if isParent:
		if u'node' in service.keys():
			service[u'items'] = features.discoverItems(cl.Dispatcher, service[u'jid'], service[u'node'])
		else:
			service[u'items'] = features.discoverItems(cl.Dispatcher, service[u'jid'])
		
		#print service
		for item in list(service[u'items']):
			if inSameDomain(service[u'jid'], item[u'jid']):
				if (service[u'jid'] != item[u'jid']):
					item=disco(item, server)
				elif u'node' in service.keys():
					if (service[u'jid'] == item[u'jid']) & (service[u'node'] != item[u'node']):
						item=disco(item, server)
			else:
				service[u'items'].remove(item)
		
	return service

def showNode(node, indent=0):
	print node;
	for n in range(0,indent+1): print ' ',
	print 'JID:     ' + node[u'jid']
	try:
		for n in range(0,indent+1): print ' ',
		print 'node:     ' + node[u'node']
	except:
		pass
	
	
	if u'info' in node.keys():
		for identity in node[u'info'][0]:
			for n in range(0,indent+1): print ' ',
			print 'INFO: id: ' + str(identity)
		for feature in node[u'info'][1]:
			for n in range(0,indent+1): print ' ',
			print 'INFO: ft: ' + str(feature)
	
	if u'items' in node.keys():
		for item in node[u'items']:
			showNode(item, indent+4)
	


# Get server list

#lista de diccionarios
# jid
# info
# items (que seria otra lista de diccionarios)

if useurl:
	f = urllib.urlopen(servers_url)
else:
	f = open(servers_file, 'r')

xml = f.read()
f.close()

node = simplexml.XML2Node(xml)

#items = node.getChildren()
items = node.getTags(name="item")

servers = []

for item in items:
	if {u'jid': item.getAttr("jid")} not in servers:
		servers.append({u'jid': item.getAttr("jid"), u'features': Set()})


print servers


# Connect to server

cl=Client(jabberserver, debug=[])
if not cl.connect(secure=0):
	raise IOError('Can not connect to server.')

if not cl.auth(jabberuser, jabberpassword, jabberresource):
	raise IOError('Can not auth with server.')

cl.sendInitPresence()

cl.Process(1)
#servers=[{u'jid': u'jabberes.org', u'features': Set()}]
#servers=[{u'jid': u'jabberfr.org', u'features': Set()}]
#servers=[{u'jid': u'2on.net', u'features': Set()}]
#servers=[{u'jid': u'brauchen.info'},{u'jid': u'egbers.info'}]
#servers=[{u'jid': u'jab.undernet.cz', u'features': Set()}]
#servers=[{u'jid': u'12jabber.com', u'features': Set()}]
#servers=[{u'jid': u'jabber.org.ar'}]
#servers=[{u'jid': u'startcom.org'}]
#servers=[{u'jid': u'jabber.com.ar'}]
#servers=[{u'jid': u'jabberes.org', u'features': Set()}, {u'jid': u'jab.undernet.cz', u'features': Set()}, {u'jid': u'12jabber.com', u'features': Set()}]

#try:
mijid='noalwin@jabberes.org'
mijid='kaos@nexus.2mydns.net/nexus'
#cl.send(Message(mijid,'\n\n\t\tStarting\n\n ','chat'))

for server in servers:
	#server[u'jid']
	#server[u'jid'].encode()
	#cl.send(Message(mijid,'Begin Disco '+server[u'jid'],'chat'))
	#print "\ndisco: "+server[u'jid']+"\n"
	#cl.Process(1)
	#try:
	disco(server, server)
	#except:
		#print '\n\n>>>>>>>>>>>>>>>>>>>>>>>\n'
		#print '\n\nFALLO en el disco de '+server[u'jid']+' \n'
		#print '\n<<<<<<<<<<<<<<<<<<<<<<<\n\n'
		#print "Unexpected error:", sys.exc_info()[0]
		#raise
	#finally:
		#cl.send(Message('noalwin@jabberes.org','End Disco '+server[u'jid'],'chat'))
#except:
	#print '\n\n>>>>>>>>>>>>>>>>>>>>>>>\n'
	#print '\n\nFALLO Esta es la lista \n'
	#print '\n<<<<<<<<<<<<<<<<<<<<<<<\n\n'
	#cl.Process(10)
	#for server in servers:
		#showNode(server)
	
	#server[u'info'] = features.discoverInfo(cl.Dispatcher, server[u'jid'].encode())
	#server[u'items'] = features.discoverItems(cl.Dispatcher, server[u'jid'].encode())
	
cl.Process(1)
#cl.send(Message(mijid,'\n\n\t\tEnding\n\n ','chat'))
cl.Process(10)

#for server in servers:
#	showNode(server)
	
	
#print servers

cl.Process(1)
#cl.send(Message('lambda512@jabberes.org','Test message'))
cl.Process(1)
cl.disconnect()

print "\n\n\n"
for server in servers:
	print
	print server[u'jid']
	print server[u'features']
	



