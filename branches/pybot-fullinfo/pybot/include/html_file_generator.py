
# $id$

# TODO: Make the HTML and the CSS less verbose

"""This module generates html files from the data gathered by the xmpp_discoverer
	There are two functions generate() and generate_all()
	
	generate_all() just generates several html files sorted by columns
	
	The files are static and can be very verbose so, you might want
	to cache and compress them.
	
	You can use dynamic compression or static compression, the dynamic
	compression compreses the page on every request, the static one compress
	the page on the first request and stores it to serve it from that moment.
	
	Since the webpage content doesn't change, you might prefer static
	compression to lower the CPU load.
	
	Just in case your webserver doesn't support static compression, I have
	added the compress option. This option, generates gzipped files, so you can
	serve them specifing the enconding as gzip.
	
	Then you have to configure your server.
	
	
	
	On Apache, static compresion can be achieved combining mod_deflate and
	mod_cache. Or, if they aren't available, generating the gzipped page and
	configuring Apache like:
	
	AddEncoding x-gzip .gz
	<IfModule mod_rewrite.c>
		RewriteEngine On
		RewriteCond %{HTTP:Accept-Encoding} gzip
		RewriteCond %{REQUEST_FILENAME}.gz -f
		RewriteRule ^(.+).html$ $1.$2.gz [L]
	</IfModule>
	
	
	
	On lighttpd, static compression can be achieved using mod_compress or
	generating the gzipped page and configuring lighttpd like:
	
	# Assuming that the pages are on /servers/ and that the index is servers.html.gz
	url.rewrite-once = (
		"^/servers/$" => "/servers/servers.html.gz",
		"^/servers/([a-zA-Z\-_]+)\.html?$" => "/servers/$1.html.gz"
	)
	
	$HTTP["url"] =~ "^/servers/([a-zA-Z_\-]+)\.html(\.gz)?$" {
		compress.filetype          = () # Disable static compression of the already compressed pages
		setenv.add-response-header = ( "Content-Encoding" => "gzip" )
		mimetype.assign = ( ".html.gz" => "text/html" )
	}
	
	
	"""


import gzip
import logging
import os.path
import shutil

ROWS_BETWEEN_TITLES = 10


SERVICE_TYPE_DESCRIPTION = {
  'muc': 'MultiUser Chat',
  'irc': 'IRC',
  'aim': 'AIM',
  'gadu-gadu': 'Gadu Gadu',
  'http-ws': 'HTTP Web Services',
  'icq': 'ICQ',
  'msn': 'MSN',
  'qq': 'QQ',
  'sms': 'SMS',
  'smtp': 'e-mail',
  'tlen': 'TLEN',
  'yahoo': 'Yahoo!',
  'jud': 'User Directory',
  'pubsub': 'Publish-Subscribe',
  'pep': 'Personal Eventing Protocol',
  'presence': 'Web Presence',
  'file': 'File Storage',
  'newmail': 'New Mail Notifications',
  'rss': 'RSS',
  'weather': 'Weather',
  'proxy': 'Proxy for file transfers'
}


def _get_filename(directory, filename_prefix, service_type=None, extension='.html'):
	if service_type is None:
		return os.path.join(directory,filename_prefix+extension)
	else:
		return os.path.join(directory, filename_prefix+'_by_'+service_type+extension)

def _count_components(server, service_type=None, availability='both'):
	"""Count server components.
	If the same component provides two or more services, it's counted both times
	Components can be restricted to be from service_type type only.
	Components can be restricted using their availability.
	Availability values: ('available', 'unavailable', 'both')."""
	
	if service_type is None:
		num = 0
		
		if availability=='available' or availability=='both':
			for service_type in server['available_services']:
				num += len(server['available_services'][service_type])
		if availability=='unavailable' or availability=='both':
			for service_type in server['unavailable_services']:
				num += len(server['unavailable_services'][service_type])
		return num
	else:
		if availability=='available':
			if service_type in server['available_services']:
				return len(server['available_services'][service_type])
			else:
				return 0
		if availability=='unavailable':
			if service_type in server['unavailable_services']:
				return len(server['unavailable_services'][service_type])
			else:
				return 0
		if availability=='both':
			num = 0
			if service_type in server['available_services']:
				num += len(server['available_services'][service_type])
			if service_type in server['unavailable_services']:
				num += len(server['unavailable_services'][service_type])
			return num

def _get_table_header(types, sort_type=None, sort_links=None):
	header = "\t<tr class=\"table_header\">"
	
	header += "<th class='server"
	if sort_type is None or sort_type == 'server':
		header += " sortedby"
	header += "'>"
	if sort_links is None:
		header += "Server"
	else:
		header += "<a href='"
		#header += _get_filename( sort_links['directory'],
		                         #sort_links['filename_prefix'], 'server' )
		header += _get_filename( sort_links['directory'],
		                         sort_links['filename_prefix'] )
		header += "'>Server</a>"
	header += "</th>"
	
	for service_type in types:
		header += "<th class='"+service_type
		if sort_type == service_type:
			header += " sortedby"
		header += "'>"
		if sort_links is None:
			if service_type in SERVICE_TYPE_DESCRIPTION:
				header += SERVICE_TYPE_DESCRIPTION[service_type]
			else:
				header += service_type
		else:
			header += "<a href='"
			header += _get_filename( sort_links['directory'],
		                             sort_links['filename_prefix'],
			                         service_type )
			header += "'>"
			
			if service_type in SERVICE_TYPE_DESCRIPTION:
				header += SERVICE_TYPE_DESCRIPTION[service_type]
			else:
				header += service_type
			
			header += "</a>"
		
		header += "</th>"
	
	#header += "<th class='times_offline"
	#if sort_type is 'times_offline':
		#header += " sortedby"
	#header += "'>Times Offline</th>"
	
	header += "</tr>"
	
	return header

def _get_image_filename(service_type, available):
	filename = 'images/'
	
	if service_type in ['muc', 'irc']:
		filename += "irc_protocol"
	elif service_type == 'aim':
		filename += "aim_protocol"
	elif service_type == 'gadu-gadu':
		filename += "gadu_protocol"
	elif service_type == 'icq':
		filename += "icq_protocol"
	elif service_type == 'msn':
		filename += "msn_protocol"
	elif service_type == 'sms':
		filename += "sms"
	elif service_type == 'yahoo':
		filename += "yahoo_protocol"
	elif service_type == 'jud':
		filename += "directory"
	elif service_type == 'newmail':
		filename += "email"
	elif service_type == 'rss':
		filename += "feed-icon-16x16"
	elif service_type == 'weather':
		filename += "weather"
	else:
		filename += "button_ok"
	
	if not available:
		filename += "-grey"
	
	filename += '.png'
	
	return filename


def generate( filename, servers, types, sort_type=None, sort_links=None,
              compress=False ):
	"""Generate a html file with the servers information.
	Don't display times_offline, to avoid a database access.
	If sort_links is not None, it will be a dictionary with the following keys:
	'directory' and 'filename_prefix'. They will be used to build the links in the header table."""
	
	tmpfilename = filename + '.tmp'
	
	logging.info('Writing HTML file  temporary "%s" ordered by %s', tmpfilename, sort_type)
	
	if sort_type is None:
		# Assume that the servers are sorted by name
		sort_type = 'server'
	elif sort_type is 'server':
		# If it's a explicit request, then sort
		jid = lambda server: server[u'jid']
		# I prefer to not touch the original list
		servers = list(servers)
		servers.sort(key=jid)
	else:
		# Sort servers
		
		num_available_components = (
		    lambda server: _count_components( server,
		                                      service_type=sort_type,
		                                      availability='available') )
		num_unavailable_components = (
		    lambda server: _count_components( server,
		                                      service_type=sort_type,
		                                      availability='unavailable') )
		jid = lambda server: server[u'jid']
		
		# I prefer to not touch the original list
		servers = list(servers)
		
		# Stable sort
		servers.sort(key=jid)
		servers.sort(key=num_unavailable_components, reverse=True)
		servers.sort(key=num_available_components, reverse=True)
	
	f = open(tmpfilename, "w+")
	
	f.write(
"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
		<title>Jabber/XMPP Server List</title>
		<style type="text/css">
			body{
				font-family: sans-serif;
				font-size: 0.8em;
				}
			div#header{
				padding: 5px;
				margin:2px auto;
				}
			.note{
				padding: 5px;
				margin:2px auto;
				background: #FFC;
				}
			table{
				border-spacing: 0px;
				/*background: #C4DCFF;*/
				background: #EEE;
				width: 100%;
				}
			td, th{
				vertical-align: middle;
				text-align: center;
				padding: 0px 4px;
				}
			tr.table_header{
				background: #DFDFDF;
				}
			tr.table_header th{
				padding: 2px 4px;
				}
			tr.table_header th:hover{
				background: #EFEFEF;
				}
			tr.table_header th a{
				text-decoration: none;
				font-weight: normal;
				color: #0000AA;
				}
			tr.table_header th a:hover{
				text-decoration: underline;
				}
			tr.odd/* td*/{
				background:#EBF4FF;
				}
			tr.even/* td*/{
				background:#FFF;
				}
			tr.offline/* td*/{
				font-style: italic;
				background:#FFD4D4;
				}
			tr.table_header th.server, td.server{
				text-align: left;
				padding: 6px 4px;
				}
			tr.table_header th.sortedby{
				background: #CFCFCF;
				}
			tr.table_header th.sortedby a{
				font-weight: bolder;
				font-size: 1em;
/* 				background: #FAFAFA; */
				color: #0000FF;
				}
			th.times_offline,td.times_offline{
				/*display: none;*/
			}
			td.feature{
/* 				font-size: 2em; */
			}
			td.no{
				color: #E90900;/*firebrick;*/
			}
			.available{
				color: #00DA00;/*green;*/
			}
			.unavailable{
				color: #808080;/*grey;*/
			}
			tr.odd td.sortedby{
				background: #DCE5EF;
			}
			tr.even td.sortedby{
				background: #EFEFEF;
			}
			div.components span{
				display: block;
				font-size: 60%;
			}
			td div.components{
				display: none;
			}
			td:hover div.components{
				display: block;
			}
		</style>
	</head>
	<body>
		<div id="container">
			<div id="header">
				<div id="title"><h2>Jabber/<abbr title="eXtensible Messaging and Presence Protocol">XMPP</abbr> Server List</h2></div>
				<div class="note">If the service Jabber ID is from a domain different that the server, it will be ignored.</div>
				<div class="note">Greyed icons mean that those services aren't accessible from external servers. Most times that indicates that they are only available for users of that server.</div>
			</div>
			<table>
"""
	)
	
	cols = "\t\t\t<col class=\"server\" />"
	for service_type in types:
		cols += "<col class=\"" + service_type + "\" />"
	#cols += "<col class=\"times_offline\" />"
	
	f.write(cols+"\n")
	
	table_header = _get_table_header(types, sort_type, sort_links)
	
	row_number = 0
	
	for server in servers:
		
		if row_number % ROWS_BETWEEN_TITLES == 0:
			f.write(table_header+"\n")
		
		tr = "\t<tr class='"
		if (  len(server['available_services']) == 0 and
		      len(server['unavailable_services']) == 0 and
		      len(server[u'info'][0]) == 0 and
		      len(server[u'info'][1]) == 0  ):
			tr += 'offline'
		elif row_number % 2 == 1:
			tr += 'odd'
		else:
			tr += 'even'
		
		tr += "'>"
		
		
		f.write(tr+"\n")
		
		cell = "\t\t<td class='server"
		if sort_type == 'server':
			cell += " sortedby"
		cell += "'><a name='"+server[u'jid']+"'>"+server[u'jid']+"</a></td>"
		f.write(cell+"\n")
		
		for service_type in types:
			
			if (  service_type not in server['available_services'] and 
				  service_type not in server['unavailable_services']  ):
				cell = "\t\t<td class='feature no " + service_type
				if sort_type == service_type:
					cell += " sortedby"
				cell += "'></td>"
			else:
				cell = "\t\t<td class='feature yes"
				
				if service_type in server['available_services']:
					service_available = True
					cell += " available"
				else:
					service_available = False
					cell += " unavailable"
				
				cell += " " + service_type
				
				if sort_type == service_type:
					cell += " sortedby"
				
				cell += "'>"
				
				cell += "<img src=\""
				cell += _get_image_filename(service_type, service_available)
				cell += "\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />" + "\n"
				
				cell += "\t\t\t<div class='components'>"
				if service_type in server['available_services']:
					for component in sorted(server['available_services'][service_type]):
						cell += "<span class='available'>"+component+"</span>"
				if service_type in server['unavailable_services']:
					for component in sorted(server['unavailable_services'][service_type]):
						cell += "<span class='unavailable'>"+component+"</span>"
				cell += "</div></td>"
				
			f.write(cell+"\n")
		
		#FIX: don't display times_offline this way
		#TODO: display it (needs a access to the DB) or mark the tr as offline?
		#cell = "\t\t<td class=\"times_offline"
		#if sort_type == 'times_offline':
			#cell += " sortedby"
		#cell += "\">4</td>"
		#f.write(cell+"\n")
		
		f.write("</tr>"+"\n")
		
		row_number += 1
	
	if row_number % ROWS_BETWEEN_TITLES != 1:
		f.write(table_header+"\n")
	
	f.write(
"""			</table>
		</div>
	</body>
</html>
"""
	)
	
	
	if compress:
		tmpgzfilename = filename + '.gz.tmp'
		logging.info( 'Creating a compressed version of file "%s"', tmpfilename )
		f.seek(0)
		gzf = gzip.open(tmpgzfilename, "wb")
		gzf.writelines(f.readlines())
		gzf.close()
		shutil.move(tmpgzfilename, filename+'.gz')
		
	
	f.close()
	
	shutil.move(tmpfilename, filename)
	
	if compress:
		logging.info('%s generated and compresed as %s', filename, filename+'.gz')
	else:
		logging.info('%s generated', filename)


def generate_all(directory, filename_prefix, servers, types, compress=False):
	'''Generate a set of HTML files sorted by different columns'''
	
	extension = '.html'
	
	sort_links = { 'directory': '.', 'filename_prefix': filename_prefix }
	
	# Name
	generate( _get_filename( directory, filename_prefix, extension=extension ),
	          servers, types, sort_links=sort_links, compress=compress )
	#generate( _get_filename( directory, filename_prefix, service_type='server',
	                         #extension=extension ),
	          #servers, types, sort_type='server', sort_links=sort_links,
	          #compress=compress )
	
	for service_type in types:
		generate( _get_filename( directory, filename_prefix,
		                         service_type=service_type, extension=extension ),
		          servers, types, sort_type=service_type, sort_links=sort_links,
		          compress=compress )

