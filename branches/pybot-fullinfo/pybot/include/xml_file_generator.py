
#$Id$

import logging
from xml.dom.minidom import getDOMImplementation

def generate(filename, servers):
	"""Generate a XML file with the information stored in servers"""
	
	
	logging.info('Generating XML file "%s"', filename)
	impl = getDOMImplementation()
	doc = impl.createDocument(None, 'servers', None)
	servers_element = doc.documentElement
	
	for server in servers:
		server_element = doc.createElement("server")
		server_element.setAttribute("jid", server[u'jid'])
		
		service_types = server['available_services'].keys()
		service_types.extend(server['unavailable_services'].keys())
		
		for service_type in service_types:
			if service_type in server['available_services']:
				for component in server['available_services'][service_type]:
					component_element = doc.createElement("component")
					component_element.setAttribute("jid", component)
					component_element.setAttribute("type", service_type)
					component_element.setAttribute("available", "yes")
					server_element.appendChild(component_element)
			if service_type in server['unavailable_services']:
				for component in server['unavailable_services'][service_type]:
					component_element = doc.createElement("component")
					component_element.setAttribute("jid", component)
					component_element.setAttribute("type", service_type)
					component_element.setAttribute("available", "no")
					server_element.appendChild(component_element)
		
		servers_element.appendChild(server_element)
		
	f = open(filename, 'w')
	doc.writexml(f)
	f.close()
	
	logging.info('XML file "%s" generated', filename)
