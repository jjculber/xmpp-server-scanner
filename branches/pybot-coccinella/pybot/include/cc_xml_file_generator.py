
#$Id$

"""XML generator in the coccinella requested format

<?xml version="1.0" ?>
<servers>
<iq from='icq.jabber.cd.chalmers.se'><query><identity category='gateway' type='icq' name='ICQ Transport'/></query></iq>
<iq from='icq.jaim.at'><query><identity category='gateway' type='icq' name='ICQ Transport'/></query></iq>
...
</servers>
"""

import gzip
import logging
import os.path
import shutil
import sys
from xml.dom.minidom import getDOMImplementation


def _add_identities(doc, element, server_component):
	"""Add XEP-0030-like identities to the element"""
	for identity in server_component[u'info'][0]:
		identity_element = doc.createElement("identity")
		identity_element.setAttribute("category", identity[u'category'])
		identity_element.setAttribute("type", identity[u'type'])
		if u'name' in identity:
			identity_element.setAttribute("name", identity[u'name'])
		element.appendChild(identity_element)


def _add_features(doc, element, server_component):
	"""Add XEP-0030-like features to the element"""
	for feature in server_component[u'info'][1]:
		feature_element = doc.createElement("feature")
		feature_element.setAttribute("var", feature)
		element.appendChild(feature_element)


def _add_identities_and_features(doc, element, server_component):
	"""Add XEP-0030-like identities and features to the element"""
	_add_identities(doc, element, server_component)
	_add_features(doc, element, server_component)


def _guess_and_add_identity(doc, element, service_type):
	"""Guess the identity and add it.
	Assume that two categories don't have the same type"""
	
	# Convert the non standard types used by the script
	if service_type == 'muc':
		service_type = 'text'
	if service_type == 'jud':
		service_type = 'user'
	if service_type == 'proxy':
		service_type = 'bytestreams'
	
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
		logging.warning("Can't guess the identity of the type: %s", service_type)
		return
	
	identity_element.setAttribute("type", service_type)
	element.appendChild(identity_element)


def generate(directory, servers, service_types, minimun_uptime=None, compress=False):
	"""Generate several XML files with the information stored in servers.
	It will generate one fine per type with only the available elements"""
	
	#if service_types is not None:
		##Filter by service type
		#_servers = {}
		#if only_available_components:
			#_servers.update([(k,v) for k,v in servers.iteritems() if len(set(service_types) & set(v['available_services'].keys())) > 0])
		#else:
			#_servers.update([(k,v) for k,v in servers.iteritems() if len(set(service_types) & set(v['available_services'].keys() + v['unavailable_services'].keys())) > 0])
		#servers = _servers
	
	if minimun_uptime is not None:
		# Filter by uptime
		_servers = {}
		_servers.update([(k, v) for k, v in servers.iteritems() if float(v['times_queried_online'])/v['times_queried'] > minimun_uptime])
		servers = _servers
	
	#tmpfilename = filename + '.tmp'
	logging.info('Generating XML files in "%s"', directory)
	impl = getDOMImplementation()
	#unfiltered_doc = impl.createDocument(None, 'servers', None)
	
	# Create the filtered documents
	docs = {}
	for service_type in service_types:
		docs[service_type] = impl.createDocument(None, 'services', None)
	
	#servers_element = doc.documentElement
	
	for key, server in sorted(servers.iteritems()):
		#server_element = doc.createElement("server")
		#server_element.setAttribute("jid", server[u'jid'])
		
		##if (  len(server['available_services']) == 0 and
		      ##len(server['unavailable_services']) == 0 and
		      ##len(server[u'info'][0]) == 0 and
		      ##len(server[u'info'][1]) == 0  ):
			##server_element.setAttribute("available", "no")
		##else:
			##server_element.setAttribute("available", "yes")
		
		#if server['offline_since'] is None:
			#server_element.setAttribute("offline", "no")
		#else:
			#server_element.setAttribute("offline", "yes")
		
		
			
		## Add all services
		#if u'items' in server:
			#for item in server[u'items']:
				## Add only available components here
				#if u'info' in item and (len(item[u'info'][0]) != 0 or len(item[u'info'][1]) != 0 ):
					#component_element = doc.createElement("component")
					#component_element.setAttribute("jid", item[u'jid'])
					#_add_identities(doc, component_element, item)
					##component_element.setAttribute("available", "yes")
					#server_element.appendChild(component_element)
		if service_types is not None:
			# Add only the requested types
			for service_type in service_types:
				doc = docs[service_type]
				if service_type in server['available_services']:
					# Only available services
					for component in server['available_services'][service_type]:
						iq_element = doc.createElement("iq")
						iq_element.setAttribute("from", component)
						query_element = doc.createElement("query")
						_guess_and_add_identity(doc, query_element, service_type)
						#component_element.setAttribute("available", "no")
						iq_element.appendChild(query_element)
						doc.documentElement.appendChild(iq_element)
						
		
		#servers_element.appendChild(server_element)
	
	#f = open(tmpfilename, 'w+')
	##doc.writexml(f)
	#f.write(doc.toprettyxml().encode("utf-8"))
	
	
	#if compress:
		#tmpgzfilename = "%s.gz.tmp" % filename
		#logging.info( 'Creating a compressed version of file "%s"', tmpfilename )
		#gzf = gzip.open(tmpgzfilename, "wb")
		#gzf.write(doc.toprettyxml().encode("utf-8"))
		#gzf.close()
		#shutil.move(tmpgzfilename, filename+'.gz')
	
	#f.close()
	
	#logging.info('XML file "%s" generated, moving to %s', tmpfilename, filename)
	
	#shutil.move(tmpfilename, filename)
	
	for service_type in service_types:
		filename = "%s.xml" % os.path.join(directory, service_type)
		tmpfilename = "%s.tmp" % filename
		
		try:
			f = open(tmpfilename, 'w+')
			#doc.writexml(f)
			f.write(docs[service_type].toprettyxml().encode("utf-8"))
			f.close()
			shutil.move(tmpfilename, filename)
		except IOError:
			logging.error( 'Error generating %s and moving it to %s',
			               tmpfilename, filename, exc_info=sys.exc_info() )
			
		
		if compress:
			tmpgzfilename = "%s.gz.tmp" % filename
			try:
				gzf = gzip.open(tmpgzfilename, "wb")
				gzf.write(docs[service_type].toprettyxml().encode("utf-8"))
				gzf.close()
				shutil.move(tmpgzfilename, filename+'.gz')
			except IOError:
				logging.error( 'Error generating %s and moving it to %s',
				               tmpgzfilename, filename+'.gz', exc_info=sys.exc_info() )
			else:
				logging.info( 'XML compresed file %s generated, moving to %s',
				              tmpgzfilename, filename+'.gz' )
		
