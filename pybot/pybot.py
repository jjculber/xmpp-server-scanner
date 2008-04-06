#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-

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
import urllib
import re
import MYSQLdb


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
	

def disco(service):
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
	
	if (u'http://jabber.org/protocol/disco#info' in service[u'info'][1]) | (u'http://jabber.org/protocol/disco' in service[u'info'][1]):
		isParent=False
		for identity in service[u'info'][0]:
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
			
	elif u'jabber:iq:browse' in service[u'info'][1]:
		# Adapt the information
		# Process items
		service[u'items']=[]
		for item in service[u'info'][0]:
			if inSameDomain(service[u'jid'], item[u'jid']):
				service[u'items'].append(disco(item))
		
		isParent=False # We already have the items
		#Fake identities. But we aren't really sure that it's a server?
		service[u'info']=(({u'category': u'server', u'type': u'im'}),service[u'info'][1])
		
		
		
		
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
					item=disco(item)
				elif u'node' in service.keys():
					if (service[u'jid'] == item[u'jid']) & (service[u'node'] != item[u'node']):
						item=disco(item)
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
		servers.append({u'jid': item.getAttr("jid")})


print servers


# Connect to server

cl=Client(jabberserver, debug=[])
if not cl.connect(secure=0):
	raise IOError('Can not connect to server.')

if not cl.auth(jabberuser, jabberpassword, jabberresource):
	raise IOError('Can not auth with server.')

cl.sendInitPresence()

cl.Process(1)
#servers=[{u'jid': u'jabberes.org'}]
#servers=[{u'jid': u'jabberfr.org'}]
#servers=[{u'jid': u'2on.net'}]
#servers=[{u'jid': u'brauchen.info'},{u'jid': u'egbers.info'}]
#servers=[{u'jid': u'jab.undernet.cz'}]
#servers=[{u'jid': u'12jabber.com'}]
#servers=[{u'jid': u'jabber.org.ar'}]
#servers=[{u'jid': u'startcom.org'}]
#servers=[{u'jid': u'jabber.com.ar'}]

#try:
mijid='noalwin@jabberes.org'
mijid='kaos@nexus.2mydns.net/nexus'
cl.send(Message(mijid,'\n\n\t\tStarting\n\n ','chat'))

for server in servers:
	#server[u'jid']
	#server[u'jid'].encode()
	cl.send(Message(mijid,'Begin Disco '+server[u'jid'],'chat'))
	print "\ndisco: "+server[u'jid']+"\n"
	#cl.Process(1)
	#try:
	disco(server)
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
cl.send(Message(mijid,'\n\n\t\tEnding\n\n ','chat'))
cl.Process(10)

for server in servers:
	showNode(server)
	
	
#print servers

cl.Process(1)
#cl.send(Message('lambda512@jabberes.org','Test message'))
cl.Process(1)
cl.disconnect()


	



