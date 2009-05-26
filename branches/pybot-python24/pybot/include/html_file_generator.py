
# $Id$

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


from ConfigParser import SafeConfigParser
from datetime import datetime
from glob import glob
import gzip
import logging
from os.path import abspath, dirname, basename, join
import shutil
import sys

ROWS_BETWEEN_TITLES = 10

# Take a look to the XMPP Registrar to see the component's category:type
# http://www.xmpp.org/registrar/disco-categories.html
COLUMNS_DESCRIPTION = {
  'server': 'Server',
  # Pure MUC components are marked as x-muc by the xmpp_discoverer
  ('conference', 'x-muc'): {'title': 'MUC', 'description': 'MultiUser Chat'},
  ('conference', 'irc'): {'title': 'IRC', 'description': 'Internet Relay Chat Gateway'},
  ('gateway', 'aim'): {'title': 'AIM', 'description': 'AIM Gateway'},
  ('gateway', 'gadu-gadu'): {'title': 'GG', 'description': 'Gadu Gadu gateway'},
  ('gateway', 'gtalk'): {'title': 'GTalk', 'description': 'Google Talk gateway'},
  ('gateway', 'http-ws'): {'title': 'WS', 'description': 'HTTP Web Services'},
  ('gateway', 'icq'): {'title': 'ICQ', 'description': 'ICQ gateway'},
  ('gateway', 'msn'): {'title': 'MSN', 'description': 'MSN gateway'},
  ('gateway', 'qq'): {'title': 'QQ', 'description': 'QQ gateway'},
  ('gateway', 'sms'): {'title': 'SMS', 'description': 'Short Message Service gateway'},
  ('gateway', 'smtp'): {'title': 'email', 'description': 'SMTP gateway'},
  ('gateway', 'tlen'): {'title': 'TLEN', 'description': 'TLEN gateway'},
  ('gateway', 'xmpp'): {'title': 'XMPP', 'description': 'Jabber/XMPP gateway'},
  ('gateway', 'yahoo'): {'title': 'Y!', 'description': 'Yahoo! gateway'},
  ('directory', 'user'): {'title': 'User Directory'},
  ('pubsub', 'service'): {'title': 'PubSub', 'description': 'Publish-Subscribe'},
  ('pubsub', 'pep'): {'title': 'PEP', 'description': 'Personal Eventing Protocol'},
  ('component', 'presence'): {'title': 'Web Presence'},
  ('store', 'file'): {'title': 'File Storage'},
  ('headline', 'newmail'): {'title': 'Mail Alerts'},
  ('headline', 'rss'): {'title': 'RSS', 'description': 'RSS notifications'},
  ('headline', 'weather'): {'title': 'Weather'},
  ('proxy', 'bytestreams'): {'title': 'Proxy', 'description': 'File transfer proxy'},
  'offline_since': {'title': 'Offline since'},
  'times_online': {'title': '% Uptime'}
}


# Load the configuration
SCRIPT_DIR = abspath(dirname(sys.argv[0]))
cfg = SafeConfigParser()
cfg.readfp(open(join(SCRIPT_DIR, 'config.cfg')))
OUTPUT_DIRECTORY      = cfg.get("Output configuration", "OUTPUT_DIRECTORY")
SHRINK_SERVERNAMES    = cfg.getboolean("Output configuration", "HTML_SHRINK_SERVERNAMES")
SHRINK_SERVERNAMES_TO = cfg.getint("Output configuration", "HTML_SHRINK_SERVERNAMES_TO")

def _get_filename(directory, filename_prefix, by=None, extension='.html'):
	if by is None:
		return join(directory, filename_prefix+extension)
	elif isinstance(by, tuple) and len(by)==2:
		return join(directory, filename_prefix+'_by_'+by[0]+'_'+by[1]+extension)
	else:
		return join(directory, filename_prefix+'_by_'+by+extension)


def _count_components(server, service_type=None, availability='both'):
	"""Count server components.
	If the same component provides two or more services, it's counted both times
	Components can be restricted to be from service_type type only.
	Components can be restricted using their availability.
	Availability values: ('available', 'unavailable', 'both')."""
	
	if service_type is None:
		num = 0
		
		if availability == 'available' or availability == 'both':
			for service_type in server['available_services']:
				num += len(server['available_services'][service_type])
		if availability == 'unavailable' or availability == 'both':
			for service_type in server['unavailable_services']:
				num += len(server['unavailable_services'][service_type])
		return num
	else:
		if availability == 'available':
			if service_type in server['available_services']:
				return len(server['available_services'][service_type])
			else:
				return 0
		if availability == 'unavailable':
			if service_type in server['unavailable_services']:
				return len(server['unavailable_services'][service_type])
			else:
				return 0
		if availability == 'both':
			num = 0
			if service_type in server['available_services']:
				num += len(server['available_services'][service_type])
			if service_type in server['unavailable_services']:
				num += len(server['unavailable_services'][service_type])
			return num


def _get_table_header(types, sort_by=None, sort_links=None):
	header = "\t<tr class='table_header'>"
	
	text = ('server' in COLUMNS_DESCRIPTION) and COLUMNS_DESCRIPTION['server'] or 'Server'
	
	link = "<a href='%s'>%s</a>" % (
	         _get_filename( sort_links['directory'], sort_links['filename_prefix']),
	         text)
	header += ( "<th class='server'>%s</th>" % (
	                 (sort_links is not None) and link or text ) )
	
	columns = list(types)
	columns.extend(['offline_since', 'times_online'])
	for column_id in columns:
		
		if column_id in COLUMNS_DESCRIPTION:
			text = COLUMNS_DESCRIPTION[column_id]['title']
		else:
			if column_id in types:
				text = column_id[1]
			else:
				text = column_id
		
		link = "<a href='%s'%s>%s</a>" % (
			        _get_filename( sort_links['directory'], sort_links['filename_prefix'], column_id ),
			        ('description' in COLUMNS_DESCRIPTION[column_id]) and (" title='%s'" % COLUMNS_DESCRIPTION[column_id]['description']) or '',
			        text )
		th_class = (column_id in types) and ("%s_%s" % (column_id[0], column_id[1])) or column_id
		header += "<th class='%s'>%s</th>" % ( th_class, (sort_links is not None) and link or text )
	
	header += "</tr>\n"
	
	return header

FILES = [basename(f) for f in glob(join(OUTPUT_DIRECTORY, 'images', '*.png'))]
def _get_image_filename(service_type, available):
	
	if not isinstance(service_type, tuple):
		raise Exception('Wrong service type')
	
	if available:
		filename = "%s_%s.png" % (service_type[0], service_type[1])
	else:
		filename = "%s_%s-grey.png" % (service_type[0], service_type[1])
	
	if filename in FILES:
		return 'images/%s' % filename
	else:
		if available:
			return 'images/yes.png'
		else:
			return 'images/yes-grey.png'
	


ROWS = None

def get_rows(servers, types):
	"""Generate the HTML code for the table rows (without the <tr> element!)
	Use singleton to generate them only once"""
	
	global ROWS
	
	if ROWS is not None:
		return ROWS
	
	ROWS = {}
	
	component_jid = lambda component: component.get('jid')
	
	for server_key, server in servers.iteritems():
		
		if SHRINK_SERVERNAMES and len(server[u'jid']) > SHRINK_SERVERNAMES_TO:
			server_text = "<div class='tooltip_container'>%s...<div class='tooltip'><span>%s</span></div></div>" % (
			           server[u'jid'][:SHRINK_SERVERNAMES_TO-3], server[u'jid'] )
		else:
			server_text = server[u'jid']
		
		row = ( "<td class='server'><a name='%s'>%s</a></td>" %
		                                    (server[u'jid'], server_text) )
		
		for service_type in types:
			
			if (  service_type not in server['available_services'] and 
				  service_type not in server['unavailable_services']  ):
				row += """<td class='feature no %s_%s'></td>""" % (
				                            service_type[0], service_type[1])
			else:
				if service_type in server['available_services']:
					service_available = True
				else:
					service_available = False
				
				row += """<td class='feature yes %s %s_%s'>""" % (
				           service_available and 'available' or 'unavailable',
				           service_type[0], service_type[1] )
				
				row += "<div class='tooltip_container'>"
				row += ("""<img src='%s' width='16' height='16' alt='Yes' />""" %
				           _get_image_filename(service_type, service_available))
				
				row += "<div class='tooltip'>"
				if service_type in server['available_services']:
					for component in sorted( server['available_services'][service_type],
					                         key=component_jid ):
						row += """<span class='available'>%s</span>""" % (
						  ('node' in component) and ("%s (%s)" % (component[u'jid'], component[u'node'])) or component[u'jid'] )
				if service_type in server['unavailable_services']:
					for component in sorted( server['unavailable_services'][service_type],
					        key=component_jid ):
						row += """<span class='unavailable'>%s</span>""" % (
						  ('node' in component) and ("%s (%s)" % (component[u'jid'], component[u'node'])) or component[u'jid'] )
				row += "</div></div></td>"
				
			
		row += "<td class='offline_since'>%s</td><td class='times_online'>%d/%d (%d%%)</td>" % (
		        (server['offline_since'] is not None)  and server['offline_since'].strftime('%d-%B-%Y %H:%M UTC') or '',
		        server['times_queried_online'], server['times_queried'],
		        int(100*server['times_queried_online']/server['times_queried']) )
		
		ROWS[server_key] = row
	
	return ROWS
	


def generate( filename, servers, types, sort_by=None, sort_links=None,
              minimun_uptime=0, compress=False ):
	"""Generate a html file with the servers information.
	Don't display times_offline, to avoid a database access.
	If sort_links is not None, it will be a dictionary with the following keys:
	'directory' and 'filename_prefix'. They will be used to build the links in the header table."""
	
	if minimun_uptime > 0:
		# Filter by uptime
		_servers = {}
		_servers.update([(k,v) for k,v in servers.iteritems() if float(v['times_queried_online'])/v['times_queried'] > minimun_uptime])
		servers = _servers
	
	
	tmpfilename = "%s.tmp" % filename
	
	logging.info('Writing HTML file  temporary "%s" ordered by %s', tmpfilename, sort_by)
	
	# Get the table rows in HTML (without <tr> element)
	rows = get_rows(servers, types)
	
	
	# Sort servers by columns
	server_keys = servers.keys()
	
	if sort_by is None:
		# Assume that the servers are sorted by name
		sort_by = 'server'
		server_keys.sort()
	elif sort_by is 'server':
		# If it's a explicit request, then sort
		server_keys.sort()
	elif sort_by is 'offline_since':
		
		# None is earlier than any date, so use current date
		now = datetime.utcnow()
		date = lambda key: (servers[key]['offline_since'] is not None) and servers[key]['offline_since'] or now
		server_keys.sort()
		server_keys.sort(key=date)
	elif sort_by is 'times_online':
		
		times = lambda key: float(servers[key]['times_queried_online'])/servers[key]['times_queried']
		server_keys.sort()
		server_keys.sort(key=times, reverse=True)
	else:
		# Sort servers
		
		num_available_components = (
		    lambda key: _count_components( servers[key], service_type=sort_by,
		                                   availability='available') )
		num_unavailable_components = (
		    lambda key: _count_components( servers[key], service_type=sort_by,
		                                   availability='unavailable') )
		
		# Stable sort
		server_keys.sort()
		server_keys.sort(key=num_unavailable_components, reverse=True)
		server_keys.sort(key=num_available_components, reverse=True)
	
	
	f = open(tmpfilename, "w+")
	
	f.write(
"""<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
		<title>Jabber/XMPP Server List</title>
		<style type="text/css">
			body{
				font-family: verdana, tahoma, sans-serif;
				font-size: 0.8em;
				background: #FFF;
				}
			div#header{
				padding: 5px;
				margin:2px auto;
				}
			h1, h2, h3, h4, h5{
				text-shadow: 0.1em 0.1em #AAA;
				font-weight: bold;
			}
			h1{
				font-size: 3em;
			}
			h2{
				font-size: 2.5em;
			}
			h3{
				font-size: 2em;
			}
			h4{
				font-size: 1.6em;
			}
			h5{
				font-size: 1.4em;
			}
			h6{
				font-size: 1.2em;
			}
			.note{
				padding: 5px;
				margin:2px auto;
				background: #FFC;
				}
			.footer{
				color: gray;
				font-size: 0.8em;
				text-align: center;
				margin: 5px;
				}
			table{
				border-collapse: collapse;
				border-spacing: 0px;
				/*background: #C4DCFF;*/
				background: #EEE;
				width: 100%;
				font-size: 0.85em;
				}
			td, th{
				vertical-align: middle;
				text-align: center;
				padding: 2px 2px;
				}
			tr.table_header{
				background: #DFDFDF;
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
			tr.odd{
				background:#EBF4FF;
				}
			tr.even{
				background:#FFF;
				}
			tr.offline{
				font-style: italic;
				background:#FFD4D4;
				}
			th.server, td.server{
				text-align: left;
				padding: 2px;
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
				color: #0A0;/*green;*/
			}
			.unavailable{
				color: #808080;/*gray;*/
			}
"""
	)
	
	# Apply a different style to sorted columns
	sort_class = isinstance(sort_by, tuple) and "%s_%s" % sort_by or sort_by
	f.write(
"""
			tr.table_header th.%s{
				background: #CFCFCF;
				}
			tr.table_header th.%s a{
				font-weight: bolder;
				font-size: 1em;
/* 				background: #FAFAFA; */
				color: #0000FF;
				}
			tr.odd td.%s{
				background: #DCE5EF;
			}
			tr.even td.%s{
				background: #EFEFEF;
			}
			tr.offline td.%s{
				font-style: italic;
				background:#FFD4D4;
				}""" % (sort_class, sort_class, sort_class, sort_class, sort_class)
	)
	
	f.write(
"""
			div.tooltip span{
				display: block;
				/*font-size: 0.7em;*/
				white-space: nowrap;
			}
			/*td div.tooltip{
				display: none;
			}
			td:hover div.tooltip{
				display: block;
			}*/
			div.tooltip_container{
				position: relative;
				display: inline;
			}
			div.tooltip{
				display: none;
				background: #FFC;
				z-index: 1;
			}
			th:hover div.tooltip, td:hover div.tooltip{
				display: block;
				margin: 0px auto;
				position: absolute;
				top: 15px;
				left: 15px;
				padding: 3px;
			}
			div.tooltip span{
			}
		</style>
	</head>
	<body>
		<div id='header'>
			<div id='title'><h2>Jabber/<abbr title="eXtensible Messaging and Presence Protocol">XMPP</abbr> Server List</h2></div>
			<h4>Notes:</h4>
			<div class='note'>If the service Jabber ID is from a different domain than the server, it will be ignored.</div>
			<div class='note'>Greyed icons mean that those services aren't accesible from external servers or that those gateways can't be used by users from another servers.</div>
		</div>
		<table>
"""
	)
	
	cols = "\t\t\t<col class='server' />"
	for service_type in types:
		cols += "<col class='%s_%s' />" % (service_type[0], service_type[1])
	cols += "<col class='offline_since' /><col class='times_online' />\n"
	
	f.write(cols)
	
	table_header = _get_table_header(types, sort_by, sort_links)
	row_number = 0
	
	for row_number, server_key in enumerate(server_keys):
		
		if row_number % ROWS_BETWEEN_TITLES == 0:
			f.write(table_header)
		
		offline = servers[server_key]['offline_since'] is not None
		
		f.write( ("<tr class='%s%s'>%s</tr>\n" %
		                     ( offline and 'offline ' or '',
		                       (row_number % 2 == 1) and 'odd' or 'even',
		                       rows[server_key] )) )
		
	if row_number % ROWS_BETWEEN_TITLES != 1:
		f.write(table_header)
	
	f.write("</table><div class='footer'>Page generated on %s</div></body></html>\n" %
	                    datetime.utcnow().strftime('%d-%B-%Y %H:%M UTC') )
	
	
	if compress:
		tmpgzfilename = "%s.gz.tmp" % filename
		logging.info( 'Creating a compressed version of file "%s"', tmpfilename )
		f.seek(0)
		gzf = gzip.open(tmpgzfilename, "wb")
		gzf.writelines(f.readlines())
		gzf.close()
		shutil.move(tmpgzfilename, filename+'.gz')
		
	f.close()
	
	shutil.move(tmpfilename, filename)
	
	if compress:
		logging.info('%s generated and compresed as %s.gz', filename, filename)
	else:
		logging.info('%s generated', filename)


def generate_all( directory, filename_prefix, servers, types, minimun_uptime=0,
                  compress=False ):
	'''Generate a set of HTML files sorted by different columns'''
	
	extension = '.html'
	
	sort_links = { 'directory': '.', 'filename_prefix': filename_prefix }
	
	# Name
	generate( _get_filename( directory, filename_prefix, extension=extension ),
	          servers, types, sort_links=sort_links, minimun_uptime=minimun_uptime,
              compress=compress )
	
	for service_type in types:
		generate( _get_filename( directory, filename_prefix, by=service_type,
		                         extension=extension ),
		          servers, types, sort_by=service_type, sort_links=sort_links,
		          minimun_uptime=minimun_uptime, compress=compress )
	
	generate( _get_filename( directory, filename_prefix, by='offline_since',
	                         extension=extension ),
	          servers, types, sort_by='offline_since', sort_links=sort_links,
	          minimun_uptime=minimun_uptime, compress=compress )
	generate( _get_filename( directory, filename_prefix, by='times_online',
	                         extension=extension ),
	          servers, types, sort_by='times_online', sort_links=sort_links,
	          minimun_uptime=minimun_uptime, compress=compress )