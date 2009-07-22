
# $Id$

#
# Under GNU General Public License
#
# Author:   noalwin
# Email:    lambda512@gmail.com
# JabberID: lambda512@jabberes.com
#

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


#def _add_identities(doc, element, server_component):
	#"""Add XEP-0030-like identities to the element"""
	#for identity in server_component[u'info'][0]:
		#identity_element = doc.createElement("identity")
		#identity_element.setAttribute("category", identity[u'category'])
		#identity_element.setAttribute("type", identity[u'type'])
		#if u'name' in identity:
			#identity_element.setAttribute("name", identity[u'name'])
		#element.appendChild(identity_element)


#def _add_features(doc, element, server_component):
	#"""Add XEP-0030-like features to the element"""
	#for feature in server_component[u'info'][1]:
		#feature_element = doc.createElement("feature")
		#feature_element.setAttribute("var", feature)
		#element.appendChild(feature_element)


#def _add_identities_and_features(doc, element, server_component):
	#"""Add XEP-0030-like identities and features to the element"""
	#_add_identities(doc, element, server_component)
	#_add_features(doc, element, server_component)


def generate(directory, servers, service_types, minimun_uptime=0, compress=False):
	"""Generate several XML files with the information stored in servers.
	It will generate one fine per type with only the available elements"""
	
	if minimun_uptime > 0:
		# Filter by uptime
		_servers = {}
		_servers.update([(k, v) for k, v in servers.iteritems() if float(v['times_queried_online'])/v['times_queried'] > minimun_uptime])
		servers = _servers
	
	logging.info('Generating XML files in "%s"', directory)
	impl = getDOMImplementation()
	
	# Create the filtered documents
	docs = {}
	for service_type in service_types:
		docs[service_type] = impl.createDocument(None, 'services', None)
	
	for key, server in sorted(servers.iteritems()):
		# Add only the requested types
		for service_type in service_types:
			doc = docs[service_type]
			if service_type in server['available_services']:
				# Only available services
				for component in server['available_services'][service_type]:
					iq_element = doc.createElement("iq")
					iq_element.setAttribute("from", component[u'jid'])
					query_element = doc.createElement("query")
					if u'node' in component:
						query_element.setAttribute("node", component[u'node'])
					identity_element = doc.createElement("identity")
					identity_element.setAttribute("category", service_type[0])
					# Sander asked to display conference:text instead conference:x-muc
					if not service_type[1] == 'x-muc':
						identity_element.setAttribute("type", service_type[1])
					else:
						identity_element.setAttribute("type", 'text')
					query_element.appendChild(identity_element)
					#component_element.setAttribute("available", "no")
					iq_element.appendChild(query_element)
					doc.documentElement.appendChild(iq_element)
	
	for service_type in service_types:
		filename = ("%s_%s.xml" % (service_type[0], service_type[1])).encode("utf-8").replace('/','_')
		filename = os.path.join(directory, filename)
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
		
