
#$Id$

"""XML generator"""

import gzip
import logging
import os.path
import shutil
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


def _get_fullinfo_component_element(doc, item):
	component_element = doc.createElement("component")
	component_element.setAttribute("jid", item[u'jid'])
	if u'node' in item:
		component_element.setAttribute("node", item[u'node'])
	_add_identities_and_features(doc, component_element, item)
	if item['available']:
		component_element.setAttribute("available", "yes")
	else:
		component_element.setAttribute("available", "no")
	
	return component_element


def _get_simple_component_element(doc, item, service_category, service_type):
	component_element = doc.createElement("component")
	component_element.setAttribute("jid", item[u'jid'])
	if u'node' in item:
		component_element.setAttribute("node", item[u'node'])
	component_element.setAttribute("category", service_category)
	component_element.setAttribute("type", service_type)
	if item['available']:
		component_element.setAttribute("available", "yes")
	else:
		component_element.setAttribute("available", "no")
	
	return component_element


def generate(filename, servers, service_types=None, full_info=False,
    only_available_components=False, minimun_uptime=None, compress=False):
	"""Generate a XML file with the information stored in servers.
	If full_info is True, service_types will be ignored"""
	
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
			
			if u'items' in server:
				for item in server[u'items']:
					if not only_available_components or item['available']:
						server_element.appendChild(_get_fullinfo_component_element(doc, item))
		
		else:
			if service_types is None:
				for service_type in server['available_services']:
					for component in server['available_services'][service_type]:
						server_element.appendChild(
						        _get_simple_component_element(doc, component,
						                service_type[0], service_type[1]))
				
				if only_available_components is False:
					for service_type in server['unavailable_services']:
						for component in server['unavailable_services'][service_type]:
							server_element.appendChild(
							        _get_simple_component_element(doc, component,
							                service_type[0], service_type[1]))
			
			else:
				for service_type in service_types:
					if service_type in server['available_services']:
						for component in server['available_services'][service_type]:
							server_element.appendChild(
							        _get_simple_component_element(doc, component,
							                service_type[0], service_type[1]))
					if only_available_components is False:
						if service_type in server['unavailable_services']:
							for component in server['unavailable_services'][service_type]:
								server_element.appendChild(
								        _get_simple_component_element(doc, component,
								                service_type[0], service_type[1]))
		
		servers_element.appendChild(server_element)
	
	f = open(tmpfilename, 'w+')
	#doc.writexml(f)
	f.write(doc.toprettyxml().encode("utf-8"))
	
	
	if compress:
		tmpgzfilename = "%s.gz.tmp" % filename
		logging.info( 'Creating a compressed version of file "%s"', tmpfilename )
		gzf = gzip.open(tmpgzfilename, "wb")
		gzf.write(doc.toprettyxml().encode("utf-8"))
		gzf.close()
		shutil.move(tmpgzfilename, filename+'.gz')
	
	f.close()
	
	logging.info('XML file "%s" generated, moving to %s', tmpfilename, filename)
	
	shutil.move(tmpfilename, filename)



def generate_all(directory, filename_prefix, servers, service_types=None,
                 only_available_components=False, minimun_uptime=None, compress=False):
	
	extension = '.xml'
	
	# The unfiltered xml file with disco#info information
	generate( os.path.join(directory, filename_prefix+'_disco'+extension), servers,
	          full_info=True, only_available_components=only_available_components,
	          minimun_uptime=minimun_uptime, compress=compress )
	
	# The unfiltered simplified xml file
	generate( os.path.join(directory, filename_prefix+extension), servers,
	          full_info=False, only_available_components=only_available_components,
	          minimun_uptime=minimun_uptime, compress=compress)
	
	
	# Generate individual filtered files by type
	for service_type in service_types:
		generate( os.path.join(directory, "%s-%s_%s%s" % (filename_prefix,
		                                                  service_type[0],
		                                                  service_type[1],
		                                                  extension),
		          servers, full_info=False, service_types=(service_type,),
		          only_available_components=only_available_components,
		          minimun_uptime=minimun_uptime, compress=compress) )
	