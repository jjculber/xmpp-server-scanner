

# $id$

#
# Under GNU General Public License
#
# Author:   noalwin
# Email:    lambda512@gmail.com
# JabberID: lambda512@jabberes.com
#


# TODO: Check for SQL injections


import logging
import MySQLdb


def update_database(db_user, db_password, db_host, db_database, servers):
	
	logging.info('Updating Database')
	
	db = MySQLdb.Connection( user=db_user, passwd=db_password, host=db_host,
	                         db=db_database )
	
	db.autocommit(True)
	
	# Check service types
	
	service_types = set()
	for server in servers:
		service_types.update(server['available_services'].keys())
		service_types.update(server['unavailable_services'].keys())
	
	cursor = db.cursor(MySQLdb.cursors.DictCursor)
	cursor.execute("""SELECT `type` FROM `pybot_service_types`""")
	for row in cursor.fetchall():
		if row['type'] not in service_types:
			logging.info('Deleting service type %s', row['type'])
			cursor.execute( """DELETE FROM pybot_service_types
			                     WHERE type = %s """, (row['type'],) )
		else:
			service_types.remove(row['type'])
	
	for service_type in service_types:
		logging.debug('Add new service type %s', service_type)
		cursor.execute( """INSERT INTO pybot_service_types SET type = %s""",
		                (service_type,) )
	
	
	# Save the servers and services
	
	for server in servers:
		
		# Add server
		
		if server[u'info'] != ([], []): # Online server
			logging.debug('Add online server %s', server[u'jid'])
			cursor.execute("""INSERT INTO pybot_servers 
								SET jid = %s, times_offline = %s
								ON DUPLICATE KEY UPDATE times_offline = %s""",
						(server[u'jid'], 0, 0))
			
			#Add services
			
			logging.debug('Delete components of %s server', server[u'jid'])
			cursor.execute("""DELETE FROM pybot_components
								WHERE server_jid = %s""", (server[u'jid'],) )
			
			for service in server[u'available_services']:
				for component in server[u'available_services'][service]:
					logging.debug( 'Add available %s component %s of %s server',
								service, component, server[u'jid'])
					cursor.execute("""INSERT INTO  pybot_components
										SET jid = %s, server_jid = %s,
											type = %s, available = %s
										ON DUPLICATE KEY UPDATE available = %s""",
									(component, server[u'jid'], service, True, True))
			
			for service in server[u'unavailable_services']:
				for component in server[u'unavailable_services'][service]:
					logging.debug( 'Add unavailable %s component %s of %s server',
								service, component, server[u'jid'])
					cursor.execute("""INSERT INTO pybot_components
										SET jid = %s, server_jid = %s,
											type = %s, available = %s
										ON DUPLICATE KEY UPDATE available = %s""",
									(component, server[u'jid'], service, False, False))
		
		else:                           # Offline server
			logging.debug('Add offline server %s', server[u'jid'])
			cursor.execute("""INSERT INTO pybot_servers
			                    SET `jid` = %s, times_offline = %s
			                    ON DUPLICATE KEY UPDATE 
			                      times_offline = times_offline + %s""",
			                (server[u'jid'], 1, 1))
	
	
	# Clean the servers table
	cursor.execute("""SELECT jid FROM pybot_servers""")
	for row in cursor.fetchall():
		exists = False
		for server in servers:
			if row[u'jid'] == server['jid']:
				exists = True
				break
			
		if not exists:
			logging.debug('Delete old server %s', row['jid'])
			cursor.execute("""DELETE FROM pybot_servers WHERE jid = %s""",
			                (row['jid'],))
	
	cursor.close()
	
	logging.info('Database updated')
