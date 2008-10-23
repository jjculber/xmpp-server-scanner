
#$Id$

import logging
import shutil
from xml.dom.minidom import getDOMImplementation

def generate(filename, servers, minimun_uptime=0):
	"""Generate a XML file with the information stored in servers"""
	
	if minimun_uptime > 0:
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
			
		service_types = set(server['available_services'].keys())
		service_types.update(server['unavailable_services'].keys())
		
		for service_type in service_types:
			if service_type in server['available_services']:
				for component in server['available_services'][service_type]:
					component_element = doc.createElement("component")
					component_element.setAttribute("jid", component[u'jid'])
					if 'node' in component:
						component_element.setAttribute("node", component[u'node'])
					component_element.setAttribute("category", service_type[0])
					component_element.setAttribute("type", service_type[1])
					component_element.setAttribute("available", "yes")
					server_element.appendChild(component_element)
			if service_type in server['unavailable_services']:
				for component in server['unavailable_services'][service_type]:
					component_element = doc.createElement("component")
					component_element.setAttribute("jid", component[u'jid'])
					if 'node' in component:
						component_element.setAttribute("node", component[u'node'])
					component_element.setAttribute("category", service_type[0])
					component_element.setAttribute("type", service_type[1])
					component_element.setAttribute("available", "no")
					server_element.appendChild(component_element)
	
		servers_element.appendChild(server_element)
	
	f = open(tmpfilename, 'w')
	f.write(doc.toprettyxml().encode("utf-8"))
	f.close()
	
	logging.info('XML file "%s" generated, moving to %s', tmpfilename, filename)
	
	shutil.move(tmpfilename, filename)
