# -*- coding: utf-8 -*-
# $Id: pybot.py 434 2009-11-17 16:28:22Z lambda512 $

#
# Under GNU General Public License
#
# Author:   Cesar Alcalde
# Email:    lambda512@gmail.com
# JabberID: lambda512@jabberes.com
#

# The idea is to get the SRV record of the server (_xmpp-client._tcp.jabber.org -> hermes.jabber.org)
# If it fails, the server name (jabber.org) will be used
# Then, make an AAAA query to get the IPv6 ip, if there is one, mark as IPv6 ready
# Ideally it should be checked with a telnet-like connection to see if the server implementation is IPv6 ready
# but since it would require to run in a IPv6-ready machine, this won't be implemented
# TODO: Check if we are in a IPv6-ready machine and create a socket to test the connection

# DNS SRV resolver code taken from xmpppy

import logging
import sys

# determine which DNS resolution library is available
HAVE_DNSPYTHON = False
HAVE_PYDNS = False
try:
	import dns.resolver # http://dnspython.org/
	HAVE_DNSPYTHON = True
except ImportError:
	
	# pydns doesn't have IPv6 support, so we don't use it but we left the code just in case it gains support
	logging.warning("Could not load one of the supported DNS library (dnspython). IPv6 readiness can not be tested.\n", exc_info=sys.exc_info())
	raise
	
	try:
		import DNS # http://pydns.sf.net/
		HAVE_PYDNS = True
	except ImportError:
		#TODO: use self.DEBUG()
		logging.warning("Could not load one of the supported DNS libraries (dnspython or pydns). IPv6 readiness can not be tested.\n", exc_info=sys.exc_info())
		raise


def get_server_cname(server, use_srv=True):
	# SRV resolver
	if use_srv and (HAVE_DNSPYTHON or HAVE_PYDNS):
		host = server
		possible_queries = ['_xmpp-client._tcp.' + host]

		for query in possible_queries:
			try:
				if HAVE_DNSPYTHON:
					answers = [x for x in dns.resolver.query(query, 'SRV')]
					if answers:
						host = str(answers[0].target)
						port = int(answers[0].port)
						break
				elif HAVE_PYDNS:
					# ensure we haven't cached an old configuration
					DNS.ParseResolvConf()
					response = DNS.Request().req(query, qtype='SRV')
					answers = response.answers
					if len(answers) > 0:
						# ignore the priority and weight for now
						_, _, port, host = answers[0]['data']
						del _
						port = int(port)
						break
			except:
				#TODO: use self.DEBUG()
				logging.error('An error occurred while looking up %s' % query, exc_info=sys.exc_info())
		server = host
	# end of SRV resolver
	return server


def resolve_ipv6(cname):
	try:
		if HAVE_DNSPYTHON:
			try:
				answers = [x for x in dns.resolver.query(cname, 'AAAA')]
			except dns.resolver.NoAnswer:
				return None
			if answers:
				host = str(answers[0].address)
		elif HAVE_PYDNS:
			# ensure we haven't cached an old configuration
			DNS.ParseResolvConf()
			response = DNS.Request().req(cname, qtype='AAAA')
			answers = response.answers
			raise NotImplemented
			if len(answers) > 0:
				# ignore the priority and weight for now
				_, _, port, host = answers[0]['data']
				del _
				port = int(port)
	except:
		#TODO: use self.DEBUG()
		logging.error('An error occurred while looking up %s' % cname, exc_info=sys.exc_info())
		return None
	else:
		return host

def get_server_ipv6(server):
	return resolve_ipv6(get_server_cname(server))


def is_ipv6_ready(server):
	return resolve_ipv6(get_server_cname(server)) is not None
