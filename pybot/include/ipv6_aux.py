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
# but since it would require to run in a IPv6-ready machine, this step will be skipped if IPv6 is not available

# DNS SRV resolver code taken from xmpppy

import logging
import socket
import sys

HAVE_IPv6 = socket.has_ipv6
if not HAVE_IPv6:
	logging.warning("There is no support for IPv6 in this machine. IPv6 connection test will be skipped.")

# determine which DNS resolution library is available
HAVE_DNSPYTHON = False
HAVE_PYDNS = False
try:
	import dns.resolver # http://dnspython.org/
	import dns.exception
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


def get_server_host_port(host, use_srv=True):
	"""Get the host and port where the server is running. By default, use DNS SRV for that."""
	port = 5222
	# SRV resolver
	if use_srv and (HAVE_DNSPYTHON or HAVE_PYDNS):
		possible_queries = ['_xmpp-client._tcp.' + host]

		for query in possible_queries:
			try:
				if HAVE_DNSPYTHON:
					try:
						answers = [x for x in dns.resolver.query(query, 'SRV')]
					except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
						logging.debug('%s has no SRV records, using "%s:5222"' % (host, host))
						break
					except dns.exception.Timeout:
						logging.debug('A timeout occurred while looking up %s. Their DNS settings may be bad configured.' % query)
						break
					else:
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
	# end of SRV resolver
	return host, port


def resolve_ipv6(host):
	"""Get the IPv6 address of the host"""
	try:
		if HAVE_DNSPYTHON:
			try:
				answers = [x for x in dns.resolver.query(host, 'AAAA')]
			except dns.resolver.NoAnswer:
				return None
			except dns.resolver.NXDOMAIN:
				logging.info('%s domain doesn\'t seems to exist' % host)
				return None
			except dns.exception.Timeout:
				logging.debug('A timeout occurred while looking up %s. Their DNS settings may be bad configured.' % host)
				return None
			if answers:
				ipv6 = str(answers[0].address)
		elif HAVE_PYDNS:
			# ensure we haven't cached an old configuration
			DNS.ParseResolvConf()
			response = DNS.Request().req(host, qtype='AAAA')
			answers = response.answers
			raise NotImplementedError('PyDNS has no support for IPv6 yet.')
			if len(answers) > 0:
				# ignore the priority and weight for now
				_, _, port, ipv6 = answers[0]['data']
				del _
				port = int(port)
	except:
		#TODO: use self.DEBUG()
		logging.error('An error occurred while looking up %s' % host, exc_info=sys.exc_info())
		return None
	else:
		return ipv6

def is_ipv6_ready(server):
	"""Check if the server is IPv6-ready.
	In order to test it, we look for his IPv6 address
		If it doesn't have one, it is not IPv6-ready.
		If it have one and our machine is IPv6-ready, then try to stablish a connection.
		If it have one and our machine is not IPv6-ready, then trust the DNS record and believe that is IPv6-ready."""
	
	global HAVE_IPv6
	host, port = get_server_host_port(server)
	ipv6 = resolve_ipv6(host)
	
	if ipv6 is None:
		return False # There is no DNS record
	
	if not HAVE_IPv6:
		return True # We can't test the connection, so we trust the DNS record
	
	logging.debug("Trying to connect using IPv6 to %s: host %s, IPv6 %s, port %d." % (server, host, ipv6, port))
	try:
		#In Python 2.6 and later
		#s = socket.create_connection((ipv6, port))
		s = None
		for res in socket.getaddrinfo(server[0], int(server[1]), socket.AF_UNSPEC, socket.SOCK_STREAM):
			af, socktype, proto, canonname, sa = res
			try:
				s = socket.socket(af, socktype, proto)
			except socket.error, msg:
				s = None
				continue
			try:
				s.connect(sa)
			except socket.error, msg:
				s.close()
				s = None
				continue
			break
		if s is None:
			raise socket.error, "Can't open the socket"
		
		s.close()
	except socket.error, err:
		if err.errno == 97: # errno.EAFNOSUPPORT ([Errno 97] Address family not supported by protocol)
			HAVE_IPv6 = False
			logging.warning("There is no support for IPv6 in this machine: %s. IPv6 connection test will be skipped." % err)
			return True # We can't test the connection, so we trust the DNS record
		elif err.errno == 111: # errno.ECONNREFUSED ([Errno 111] Connection refused)
			# The server implementation doesn't have IPv6 support
			logging.debug("The server implementation of %s doesn't seems to have IPv6 support: %s." % (host, err))
			return False
		elif err.errno == 113: # errno.EHOSTUNREACH ([Errno 113] No route to host)
			# The server is unreachable
			logging.debug("The server %s is unreachable: %s." % (host, err))
			return False
		elif err.errno == 110: # errno.ETIMEDOUT ([Errno 110] Connection timed out)
			# Server offline?
			logging.debug("The server %s seems to be offline: %s." % (host, err))
			return True # We can't test the connection, so we trust the DNS record
		else:
			# Unknown error
			logging.warning("Connection attempt to %s (host %s, ip %s, port %d) failed while trying to test its IPv6-readyness. The error was: %s." % (server, host, ipv6, port, err), exc_info=sys.exc_info())
			return False
	else:
		return True
	
