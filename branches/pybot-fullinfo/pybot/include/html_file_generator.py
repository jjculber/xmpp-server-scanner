
# $id$

# TODO: Add sorting support

import logging

ROWS_BETWEEN_TITLES = 10

def _get_table_header(types, sortby=None):
	header = "\t<tr class=\"table_header\">"
	header += "<th class='name"
	if sortby is None or sortby == 'name':
		header += " sortedby"
	header += "'><a href='?order=name'>Name</a></th>"
	for service_type in types:
		header += "<th class='"+service_type
		if sortby == service_type:
			header += " sortedby"
		header += "'><a href='?order="+service_type+"'>"+service_type+"</a></th>"
	#header += "<th class='times_offline"
	#if sortby is 'times_offline':
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


def generate(filename, servers, types, sortby=None, compress=False):
	"""Generate a html file with the servers information.
	Don't display times_offline, to avoid a database access."""
	
	logging.info('Writing HTML file: %s',filename)
	
	if sortby is None:
		sortby = 'name'
	
	f = open(filename, "w")
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
			tr.table_header th.name, td.name{
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
	
	table_header = _get_table_header(types, sortby)
	
	row_number = 0
	
	for server in servers:
		if row_number % ROWS_BETWEEN_TITLES == 0:
			f.write(table_header+"\n")
		
		tr = "\t<tr class='"
		if server == {u'info': ([], []), u'unavailable_services': {}, u'jid': server[u'jid'], u'available_services': {}}:
			tr += 'offline'
		elif row_number % 2 == 1:
			tr += 'odd'
		else:
			tr += 'even'
		
		tr += "'>"
		
		
		f.write(tr+"\n")
		
		cell = "\t\t<td class='name"
		if sortby == 'name':
			cell += " sortedby"
		cell += "'><a name='"+server[u'jid']+"'>"+server[u'jid']+"</a></td>"
		f.write(cell+"\n")
		
		for service_type in types:
			
			if (  service_type not in server['available_services'] and 
				  service_type not in server['unavailable_services']  ):
				cell = "\t\t<td class='feature no " + service_type
				if sortby == service_type:
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
				
				if sortby == service_type:
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
		#if sortby == 'times_offline':
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
	
	logging.info('HTML file Generated')
