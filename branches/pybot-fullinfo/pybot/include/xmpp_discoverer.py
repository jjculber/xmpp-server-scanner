
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
# TODO: Simplify _discover_item()


import logging
import re
import xml


from xmpp import Client, features



URLREGEXP = re.compile(
	r'(?P<fullsubdomain>' +
		r'(?:(?P<subdomain>\w+)\.(?=\w+\.\w))?' +
		r'(?P<fulldomain>'+
			r'(?:(?P<domain>\w+)\.)?(?P<tld>\w+)$' +
	   r')' +
	r')'
	)


def _in_same_domain(parent, child):
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


def _add_component_available(component, services_list):
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


def _add_component_unavailable(jid, services_list):
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



def _get_item_info(dispatcher, component):
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
			                        #server[u'unavailable_services'])
			raise
			
	else:
		logging.debug('Ignoring %s', component[u'jid'])
		return  ([], [])


def _get_items(dispatcher, component):
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
		if not _in_same_domain(component[u'jid'], item[u'jid']):
			items.remove(item)
	
	return items


def _discover_item(dispatcher, component, server):
	'''Explore the component and its childs and 
	update the component list in server.
	Both, component and server, variables are modified.'''
	
	needs_to_query_items = False
	#cl.Process(1)
	
	try:
		component[u'info'] = _get_item_info(dispatcher, component)
	except xml.parsers.expat.ExpatError:
		component[u'info'] = ([], [])
		_add_component_unavailable(component[u'jid'], server[u'unavailable_services'])
		raise
	
	# Detect if it's a server or a branch (if it have child items)
	
	if (  (u'http://jabber.org/protocol/disco#info' in component[u'info'][1]) |
	      (u'http://jabber.org/protocol/disco' in component[u'info'][1])  ):
		needs_to_query_items = False
		_add_component_available(component, server[u'available_services'])
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
			if _in_same_domain(component[u'jid'], item[u'jid']):
				component[u'items'].append(_discover_item(dispatcher, item, server))
		
		needs_to_query_items = False # We already have the items
		#Fake identities. But we aren't really sure that it's a server?
		component[u'info'] = ( ({u'category': u'server', u'type': u'im'}),
		                     component[u'info'][1] )
	
	elif (component[u'info'] == ([], [])):
		# We have to guess what feature is using the JID
		_add_component_unavailable(component[u'jid'], server[u'unavailable_services'])
	
	else:
		if u'available_services' in component:
			# It's a server. It probably uses jabber:iq:browse
			# Adapt the information
			# Process items
			component[u'items'] = []
			for item in component[u'info'][0]:
				if _in_same_domain(component[u'jid'], item[u'jid']):
					component[u'items'].append(_discover_item(dispatcher, item,
					                                          server))
			
			needs_to_query_items = False # We already have the items
			#Fake identities. But we aren't really sure that it's a server?
			component[u'info'] = ( ({u'category': u'server', u'type': u'im'}),
			                       component[u'info'][1] )
		else:
			#try:
			_add_component_available(component, server[u'available_services'])
			#except:
				#add_component_unavailable(component[u'jid'],
				                        #server[u'unavailable_services'])
	
	# If it's a server or a branch node, get the child items
	
	if needs_to_query_items:
		try:
			component[u'items'] = _get_items(dispatcher, component)
		except xml.parsers.expat.ExpatError:
			component[u'items'] = []
			raise
		
		for item in list(component[u'items']):
			if (component[u'jid'] != item[u'jid']):
				item = _discover_item(dispatcher, item, server)
			elif u'node' in component:
				if (  (component[u'jid'] == item[u'jid']) &
					  (component[u'node'] != item[u'node'])  ):
					item = _discover_item(dispatcher, item, server)
	
	return component


def _show_node(node, indent=0):
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
			_show_node(item, indent+4)
	

def discover_servers(jabber_user, jabber_password, jabber_resource, jabber_server, server_list):

	servers = []
	
	for jid in server_list:
		servers.append({ u'jid': jid,
		                 u'available_services': {}, 
		                 u'unavailable_services': {} })


	# Connect to server
	
	cl = Client(jabber_server, debug=[])
	if not cl.connect(secure=0):
		raise IOError('Can not connect to server.')
	if not cl.auth(jabber_user, jabber_password, jabber_resource):
		raise IOError('Can not auth with server.')
	
	cl.sendInitPresence()
	cl.Process(1)
	
	logging.info('Begin discovery')
	
	for server in servers:
		try:
			_discover_item(cl.Dispatcher, server, server)
		
		except xml.parsers.expat.ExpatError: # Restart the client
			#cl.disconnect()
			logging.warning('Aborting discovery of %s server. ' +
			                'Restarting the client.', server[u'jid'])
			cl = Client(jabber_server, debug=[])
			if not cl.connect(secure=0):
				raise IOError('Can not connect to server.')
			if not cl.auth(jabber_user, jabber_password, jabber_resource):
				raise IOError('Can not auth with server.')
			cl.sendInitPresence()
			cl.Process(1)
	
	cl.Process(10)
	#for server in servers:
	#	show_node(server)
	cl.disconnect()
	
	logging.info('Discovery Finished')
	
	return servers
