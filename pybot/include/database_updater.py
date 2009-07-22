

# $Id$

#
# Under GNU General Public License
#
# Author:   Cesar Alcalde
# Email:    lambda512@gmail.com
# JabberID: lambda512@jabberes.com
#


# TODO: Check for SQL injections


import logging
import MySQLdb


def update_database(db_user, db_password, db_host, db_database, servers):
	
	logging.info('Updating Database')
	
	db = MySQLdb.Connection( user=db_user, passwd=db_password, host=db_host,
	                         db=db_database, use_unicode=True, charset='utf8',
	                         init_command='SET NAMES utf8' )
	
	#db.autocommit(True)
	
	# Check service types
	
	service_types = set()
	for server in servers.itervalues():
		service_types.update(server['available_services'].keys())
		service_types.update(server['unavailable_services'].keys())
	
	if (None, None) in service_types:
		service_types.remove((None, None))
		service_types.update(('', ''))
	
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("""SELECT `category`, `type` FROM `pybot_service_types`""")
	for row in cursor.fetchall():
		service_category = row['category'].decode('utf-8')
		service_type = row['type'].decode('utf-8')
		
		if (service_category, service_type) not in service_types:
			logging.debug('Deleting service type %s', service_type)
			
			cursor.execute( """DELETE FROM pybot_service_types
			                     WHERE category = %s AND type = %s """,
			                (service_category, service_type) )
		else:
			service_types.remove((service_category, service_type))
	
	for service_category, service_type in service_types:
		logging.debug('Add new service type %s', service_type)
		
		cursor.execute( """INSERT INTO pybot_service_types
		                     SET category = %s, type = %s""",
		                (service_category, service_type) )
	
	
	# Save the servers and services
	
	for server in servers.itervalues():
		
		offline_since = None if server['offline_since'] is None else server['offline_since'].strftime('%Y-%m-%d %H:%M:%S')
		
		# Add server
		logging.debug('Add server %s', server[u'jid'])
		cursor.execute( """INSERT INTO pybot_servers 
		                    SET jid = %s, offline_since = %s,
		                    times_queried_online = %s, times_queried = %s
		                    ON DUPLICATE KEY UPDATE offline_since = %s,
		                    times_queried_online = %s, times_queried = %s""",
		                ( server[u'jid'], offline_since, 
		                  server['times_queried_online'], server['times_queried'],
		                  offline_since, server['times_queried_online'],
		                  server['times_queried'] ) )
		
		# If it's offline the information will remain correct
		if server['offline_since'] is None: # Online server
			#logging.debug('Add online server %s', server[u'jid'])
			#cursor.execute("""INSERT INTO pybot_servers 
			                    #SET jid = %s, times_offline = %s
			                    #ON DUPLICATE KEY UPDATE times_offline = %s""",
			               #(server[u'jid'], 0, 0))
			
			#Add services
			
			logging.debug('Delete components of %s server', server[u'jid'])
			cursor.execute( """DELETE FROM pybot_components
			                     WHERE server_jid = %s""", (server[u'jid'],) )
			
			for service_type in server[u'available_services']:
				for component in server[u'available_services'][service_type]:
					logging.debug( 'Add available %s-%s component %s of %s server',
					               service_type[0], service_type[1], component[u'jid'],
					               server[u'jid'] )
					cursor.execute( """INSERT INTO  pybot_components
					                     SET jid = %s, node = %s, server_jid = %s,
					                       category = %s, type = %s, available = %s
					                     ON DUPLICATE KEY UPDATE available = %s""",
					                (component[u'jid'],
					                 component[u'node'] if 'node' in component else None,
					                 server[u'jid'], service_type[0], service_type[1],
					                 True, True) )
			
			for service_type in server[u'unavailable_services']:
				for component in server[u'unavailable_services'][service_type]:
					logging.debug( 'Add unavailable %s-%s component %s of %s server',
					               service_type[0], service_type[1], component[u'jid'],
					               server[u'jid'])
					cursor.execute( """INSERT INTO pybot_components
					                    SET jid = %s, node = %s, server_jid = %s,
					                      category = %s, type = %s, available = %s
					                    ON DUPLICATE KEY UPDATE available = %s""",
					                (component[u'jid'],
					                 component[u'node'] if 'node' in component else None,
					                 server[u'jid'], service_type[0], service_type[1],
					                 False, False) )
		
		#else:                           # Offline server
			#logging.debug('Add offline server %s', server[u'jid'])
			#cursor.execute("""INSERT INTO pybot_servers
			                    #SET `jid` = %s, times_offline = %s
			                    #ON DUPLICATE KEY UPDATE 
			                      #times_offline = times_offline + %s""",
			                #(server[u'jid'], 1, 1))
	
	
	# Clean the servers table
	cursor.execute("""SELECT jid FROM pybot_servers""")
	for row in cursor.fetchall():
		exists = False
		#for server in servers:
			#if row[u'jid'] == server['jid']:
				#exists = True
				#break
		# Servers are indexed by JID
		if row[u'jid'].decode('utf-8') in servers:
			exists = True
			break
			
		if not exists:
			logging.debug('Delete old server %s', row['jid'])
			cursor.execute("""DELETE FROM pybot_servers WHERE jid = %s""",
			                (row['jid'].decode('utf-8'),))
	
	cursor.close()
	
	logging.debug('Commit changes to database')
	db.commit()
	
	logging.info('Database updated')
