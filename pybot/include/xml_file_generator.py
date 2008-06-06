
#$Id$

import codecs
import logging
import os.path
import shutil
from xml.dom.minidom import getDOMImplementation


def _add_identities_and_features(doc, element, server_component):
	"""Add XEP-0030-like identities and features to the element"""
	for identity in server_component[u'info'][0]:
		identity_element = doc.createElement("identity")
		identity_element.setAttribute("category", identity[u'category'])
		identity_element.setAttribute("type", identity[u'type'])
		if u'name' in identity:
			identity_element.setAttribute("name", identity[u'name'])
		element.appendChild(identity_element)
	
	for feature in server_component[u'info'][1]:
		feature_element = doc.createElement("feature")
		feature_element.setAttribute("var", feature)
		element.appendChild(feature_element)


def _guess_and_add_identity(doc, element, service_type):
	"""Guess the identity and add it"""
	
	# MUC rooms uses the non-standard type 'muc' in this script
	if service_type == 'muc':
		service_type = 'text'
	
	identity_element = doc.createElement("identity")
	
	if service_type in ("admin", "anonymous", "registered"):
		identity_element.setAttribute("category", "account")
	elif service_type in ("cert", "generic", "ldap", "ntlm", "pam", "radius"):
		identity_element.setAttribute("category", "auth")
	elif service_type in ("command-list", "command-node", "rpc", "soap", "translation"):
		identity_element.setAttribute("category", "automation")
	elif service_type in ("bot", "console", "handheld", "pc", "phone", "web"):
		identity_element.setAttribute("category", "client")
	elif service_type in ("whiteboard",):
		identity_element.setAttribute("category", "collaboration")
	elif service_type in ("archive", "c2s", "generic", "load", "log",
		                  "presence", "router", "s2s", "sm", "stats"):
		identity_element.setAttribute("category", "component")
	elif service_type in ("irc", "text"):
		identity_element.setAttribute("category", "conference")
	elif service_type in ("chatroom", "group", "user", "waitinglist"):
		identity_element.setAttribute("category", "directory")
	elif service_type in ("aim", "gadu-gadu", "http-ws", "icq", "msn", "qq",
		                  "sms", "smtp", "tlen", "xfire", "yahoo"):
		identity_element.setAttribute("category", "gateway")
	elif service_type in ("newmail", "rss", "weather"):
		identity_element.setAttribute("category", "headline")
	elif service_type in ("branch""leaf"):
		identity_element.setAttribute("category", "hierarchy")
	elif service_type in ("bytestreams",):
		identity_element.setAttribute("category", "proxy")
	elif service_type in ("collection", "leaf", "pep", "service"):
		identity_element.setAttribute("category", "pubsub")
	elif service_type in ("im",):
		identity_element.setAttribute("category", "server")
	elif service_type in ("berkeley", "file", "generic", "ldap", "mysql",
		                  "oracle", "postgres"):
		identity_element.setAttribute("category", "store")
	else: # Don't do anything
		return
	
	identity_element.setAttribute("type", service_type)
	element.appendChild(identity_element)


def generate(filename, servers, service_types=None, full_info=False, only_available_components=False, minimun_uptime=None):
	"""Generate a XML file with the information stored in servers.
	If service_types is True, service_types will be ignored"""
	
	if service_types is not None:
		#Filter by service type
		_servers = {}
		if only_available_components:
			_servers.update([(k,v) for k,v in servers.iteritems() if len(set(service_types) & set(v['available_services'].keys())) > 0])
		else:
			_servers.update([(k,v) for k,v in servers.iteritems() if len(set(service_types) & set(v['available_services'].keys() + v['unavailable_services'].keys())) > 0])
		servers = _servers
	
	if minimun_uptime is not None:
		# Filter by uptime
		_servers = {}
		_servers.update([(k,v) for k,v in servers.iteritems() if float(v['times_queried_online'])/v['times_queried'] > minimun_uptime])
		servers = _servers
	
	tmpfilename = filename + '.tmp'
	logging.info('Generating XML file "%s"', tmpfilename)
	impl = getDOMImplementation()
	doc = impl.createDocument(None, 'servers', None)
	servers_element = doc.documentElement
	
	for key, server in sorted(servers.iteritems()):
		server_element = doc.createElement("server")
		server_element.setAttribute("jid", server[u'jid'])
		
		#if (  len(server['available_services']) == 0 and
		      #len(server['unavailable_services']) == 0 and
		      #len(server[u'info'][0]) == 0 and
		      #len(server[u'info'][1]) == 0  ):
			#server_element.setAttribute("available", "no")
		#else:
			#server_element.setAttribute("available", "yes")
		
		if server['offline_since'] is None:
			server_element.setAttribute("offline", "no")
		else:
			server_element.setAttribute("offline", "yes")
		
		if full_info:
			
			# Add available
			if u'items' in server:
				for item in server[u'items']:
					# Add only available components here
					if u'info' in item and (len(item[u'info'][0]) != 0 or len(item[u'info'][1]) != 0 ):
						component_element = doc.createElement("component")
						component_element.setAttribute("jid", item[u'jid'])
						_add_identities_and_features(doc, component_element, item)
						component_element.setAttribute("available", "yes")
						server_element.appendChild(component_element)
			
			# Add unavailable
			if not only_available_components:
				for service_type in server[u'unavailable_services']:
					for component in server['unavailable_services'][service_type]:
						component_element = doc.createElement("component")
						component_element.setAttribute("jid", component)
						_guess_and_add_identity(doc, component_element, service_type)
						component_element.setAttribute("available", "no")
						server_element.appendChild(component_element)
		else:
			if service_types is None:
				service_types = server['available_services'].keys()
				if only_available_components is False:
					service_types.extend(server['unavailable_services'].keys())
			
			for service_type in service_types:
				if service_type in server['available_services']:
					for component in server['available_services'][service_type]:
						component_element = doc.createElement("component")
						component_element.setAttribute("jid", component)
						component_element.setAttribute("type", service_type)
						component_element.setAttribute("available", "yes")
						server_element.appendChild(component_element)
				if only_available_components is False:
					if service_type in server['unavailable_services']:
						for component in server['unavailable_services'][service_type]:
							component_element = doc.createElement("component")
							component_element.setAttribute("jid", component)
							component_element.setAttribute("type", service_type)
							component_element.setAttribute("available", "no")
							server_element.appendChild(component_element)
		
		servers_element.appendChild(server_element)
	
	f = codecs.open(tmpfilename, 'w', 'utf_8')
	#doc.writexml(f)
	f.write(doc.toprettyxml())
	f.close()
	
	logging.info('XML file "%s" generated, moving to %s', tmpfilename, filename)
	
	shutil.move(tmpfilename, filename)



def generate_all(directory, filename_prefix, servers, service_types=None, only_available_components=False, minimun_uptime=None):
	
	extension = '.xml'
	
	# The unfiltered xml file with disco#info information
	generate( os.path.join(directory, filename_prefix+'_disco'+extension), servers,
	          full_info=True, only_available_components=False, minimun_uptime=None )
	
	# The unfiltered simplified xml file
	generate( os.path.join(directory, filename_prefix+extension), servers,
	          full_info=False, only_available_components=False, minimun_uptime=None )
	
	
	# Generate individual filtered files by type
	for service_type in service_types:
		generate( os.path.join(directory, filename_prefix+'-'+service_type+extension),
		          servers, full_info=False, service_types=(service_type,),
		          only_available_components=only_available_components,
		          minimun_uptime=minimun_uptime )
	