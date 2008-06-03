
#$Id$

import logging
import os.path
import shutil
from xml.dom.minidom import getDOMImplementation

def generate(filename, servers, service_types=None, only_available_components=False, minimun_uptime=None):
	"""Generate a XML file with the information stored in servers"""
	
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
	
	f = open(tmpfilename, 'w')
	doc.writexml(f)
	f.close()
	
	logging.info('XML file "%s" generated, moving to %s', tmpfilename, filename)
	
	shutil.move(tmpfilename, filename)



def generate_all(directory, filename_prefix, servers, service_types=None, only_available_components=False, minimun_uptime=None):
	
	extension = '.xml'
	
	# The unfiltered xml file
	generate( os.path.join(directory, filename_prefix+extension), servers,
	          only_available_components=False, minimun_uptime=None )
	
	# Generate individual filtered files by type
	for service_type in service_types:
		generate( os.path.join(directory, filename_prefix+'-'+service_type+extension),
		          servers, service_types=(service_type,),
		          only_available_components=only_available_components,
		          minimun_uptime=minimun_uptime )
	