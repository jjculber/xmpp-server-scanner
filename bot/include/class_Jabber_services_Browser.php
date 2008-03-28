<?php
/* Jabber Client Library (service discovery extension)
 * Version 0.8-noalwin
 * Copyright 2007, noalwin <lambda512@gmail.com> <xmpp:lambda512@jabberes.org>
 * Copyright 2002-2005, eSite Media Inc.
 * Portions Copyright 2002, Carlo Zottmann
 * http://www.centova.com
 * ============================================================================
 *
 * This file was contributed (in part or whole) by a third party, and is
 * released under the GNU LGPL.  Please see the CREDITS and LICENSE sections
 * below for details.
 * 
 *****************************************************************************
 *
 * DETAILS
 *
 * This is a class that extends Jabber client class implementation
 * from eSite Media Inc. It has been added Service Discovery support
 * and a mechanism to discard old querys (some servers don't answer
 * and we didn't get even a 404 error)
 * Please keep in mind that this class hasn't been heavily tested, nor has
 * been designed to give compatibility with the old class.
 *
 *
 *
 * LICENSE
 *
 * class_Jabber.php - Jabber Client Library (service discovery extension)
 * Copyright 2007, noalwin
 * Copyright (C) 2002-2005, eSite Media Inc.
 * Copyright (C) 2002, Carlo Zottmann
 *
 * This library is free software; you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as published by the
 * Free Software Foundation; either version 2.1 of the License, or (at your
 * option) any later version.
 * 
 * This library is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
 * for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with this library; if not, write to the Free Software Foundation,
 * Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 *
 *
 * JABBER is a registered trademark of Jabber Inc.
 *
 */

// include the Jabber class
require_once(dirname(__FILE__)."/jabberclass/class_Jabber.php");

// Version string
define("CLASS_JABBER_VERSION","0.8-noalwin");

// Default connection timeout
define("DEFAULT_CONNECT_TIMEOUT",15);

// Default iq query timeout
if (!defined("QUERY_TIMEOUT")) define("QUERY_TIMEOUT",90);// 90 seconds (some servers are very slow)

// Default Jabber resource
define("DEFAULT_RESOURCE","JabberClass-noalwin");

// Minimum/Maximum callback frequencies
define("MIN_CALLBACK_FREQ",1);	// more than once per second is dangerous
define("MAN_CALLBACK_FREQ",10); // less than once every 10 seconds will be very, very slow

// Make sure we have SHA1 support, one way or another, such that we can
// perform encrypted logins.
if (!function_exists('sha1')) {  // PHP v4.3.0+ supports sha1 internally

	if (function_exists('mhash')) { // is the Mhash extension installed?

		// implement the sha1() function using mhash
		function sha1($str) {
			return bin2hex(mhash(MHASH_SHA1, $str));
		}

	} else {

		// implement the sha1() function in native PHP using the SHA1Library class;
		// this is slow, but it's better than plaintext.
		require_once(dirname(__FILE__)."/jabberclass/class_SHA1Library.php");
	}
	
}

// Jabber communication class
class Jabber_services_Browser extends Jabber {
	var $_iq_version_name	= "class_Jabber.php - http://www.centova.com - Copyright 2003-2005, eSite Media Inc.";
	var $_iq_version_version= CLASS_JABBER_VERSION;
	//var	$_iq_version_os	= $_SERVER['SERVER_SOFTWARE'];
	var $_iq_querys= array();
	
	function connect($server_host,$server_port=5222,$connect_timeout=null,$alternate_ip=false) {
		
		if (is_null($connect_timeout)) $connect_timeout = DEFAULT_CONNECT_TIMEOUT;
		$connector = $this->_connector;
		
		$this->_connection = &new $connector();
		$this->_server_host = $server_host;
		$this->_server_port = $server_port;
		$this->_server_ip = $alternate_ip ? $alternate_ip : $server_host;
		$this->_connect_timeout = $connect_timeout;
		
		$this->roster = array();
		$this->services = array();
		
		$this->_is_win32 = (substr(strtolower(php_uname()),0,3)=="win");
		$this->_sleep_func = $this->_is_win32 ? "win32_sleep" : "posix_sleep";
		
		return $this->_connect_socket();
	}
	
	
	
	// browse the services (transports) available on the server
	function browse($server=JABBER_SERVER) {
		$browse_id = $this->_unique_id("browse");
		$this->_set_iq_handler("_on_browse_result",$browse_id,NULL,$server);
		
		return $this->_send_iq($server, 'get', $browse_id, "jabber:iq:browse");
	}
	
	
	
	// receives the results of a service browse query
	function _on_browse_result(&$packet) {
		$packet_type = $packet['iq']['@']['type'];
		$server = $packet['iq']['@']['from'];
		
//		$this->_log("BROWSE packet: ".var_export($packet,true));
		
		// did we get a result?  if so, process it, and remember the service list	
		if ($packet_type=="result") {
			
// 			$this->services = array();

			//$this->_log("SERVICES: ".print_r($packet,true));
			
			//$this->_log("\n\nSOFTWARE: ".$this->server_software." v".$this->server_version."\n\n");
			
			if ($packet['iq']['#']['service']) {
				// Jabberd uses the 'service' element
				$servicekey = $itemkey = 'service';
			} elseif ($packet['iq']['#']['item']) {
				// Older versions of Merak use 'item'
				$servicekey = $itemkey = 'item';
			} elseif ($packet['iq']['#']['query']) {
				// Newer versions of Merak use 'query'
				$servicekey = 'query';
				$itemkey = 'item';
			} else {
				// try to figure out what to use
				$k = array_keys($packet['iq']['#']);
				$servicekey = $k[0];
				if (!$servicekey) return;
			}
			// if the item key is incorrect, try to figure that out as well
			if ($packet['iq']['#'][$servicekey] && !$packet['iq']['#'][$servicekey][0]['#'][$itemkey]) {
				$k = array_keys($packet['iq']['#'][$servicekey][0]['#']);
				$itemkey = $k[0];
			}
			
			$number_of_services = count($packet['iq']['#'][$servicekey][0]['#'][$itemkey]);

			$services_updated = false;
			$services = array();
			for ($a = 0; $a < $number_of_services; $a++)
			{
				$svc = &$packet['iq']['#'][$servicekey][0]['#'][$itemkey][$a];

				$jid = strtolower($svc['@']['jid']);
				
/* @annotation: should be done in the bot? *//*
				//skip nodes from other servers
				preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$server,$server_match);
				preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$jid,$service_match);
				
				if(($server_match[3]=='com')||($server_match[3]=='net')||($server_match[3]=='org')||($server_match[3]=='co')||($server_match[3]=='gov')||($server_match[3]=='edu')){
					//country code second-level domain
					$server_domain = $server_match[0];
					$service_domain = $service_match[0];
				}else{
					$server_domain = $server_match[2];
					$service_domain = $service_match[2];
				}
				
				if($server_domain != $service_domain) {
					//$this->_log("[SERVICES] Skipped".$service_jid." child of ".$jid);
					continue;
				}*/
				
				$is_new = !isset($this->services[$jid]);
				$services[] = $jid;
				
				if(!$is_new){
					//skip already discovered nodes
					//$this->_log("[SERVICES] Skipped already discovered ".$jid." child of ".$server);
					continue;
				}
				
				$this->services[$jid] = array(	
					"type"			=> strtolower($svc['@']['type']),
// 					"category"			=> strtolower($svc['@']['category']),
					"status"		=> "Offline",
					"show"			=> "off",
					"name"			=> $svc['@']['name']
					);
				
				$number_of_namespaces = count($packet['iq']['#'][$servicekey][0]['#'][$itemkey][$a]['#']['ns']);
				for ($b = 0; $b < $number_of_namespaces; $b++) {
						$this->services[$jid]['namespaces'][$b] = $packet['iq']['#'][$servicekey][0]['#'][$itemkey][$a]['#']['ns'][$b]['#'];
				}

				if ($this->service_single_update) {
					$services_updated = true;
				} else {
					$this->_call_handler("serviceupdate",$jid,$is_new);
				}
			}
			
			if ($this->service_single_update && $services_updated) {
				$this->_call_handler("serviceupdate",NULL,$is_new);
			}
			
			$this->_log("Received service list");
			$this->_call_handler("browseresult",$server,$services);
			//$this->_log("Received service list: ".print_r($this->services,true));
		// choke on error
		} elseif ($packet_type=="error") {
			$this->_handle_iq_error($packet);
			
		// confusion sets in
		} else {
			$this->_log("Don't know what to do with jabber:iq:browse packet!");
		}
	}
	
	
	// Ask for information about an service
	function get_info($service) {
		$browse_id = $this->_unique_id("get_info");
		$this->_set_iq_handler("_on_get_info_result",$browse_id,NULL,$service);
		
		return $this->_send_iq($service, 'get', $browse_id, "http://jabber.org/protocol/disco#info");
	}
	
	// Process the information about an service
	function _on_get_info_result(&$packet) {
		$packet_type = $packet['iq']['@']['type'];
	
		//		$this->_log("BROWSE packet: ".var_export($packet,true));
	
		// did we get a result?  if so, process it, and remember the service list	
		if ($packet_type=="result") {
		
			//$this->_log("SERVICES: ".print_r($packet,true));
			
			//$this->_log("\n\nSOFTWARE: ".$this->server_software." v".$this->server_version."\n\n");
					
			$jid = $packet['iq']['@']['from'];
			
			if(isset($packet['iq']['#']['query'][0]['@']['node'])){
				$node = $packet['iq']['#']['query'][0]['@']['node'];
			}
			
			$number_of_identities = count($packet['iq']['#']['query'][0]['#']['identity']);
			
			for ($a = 0; $a < $number_of_identities; $a++)
			{
				$identity = &$packet['iq']['#']['query'][0]['#']['identity'][$a];
				
				if(isset($node)){
					$this->services[$jid]['nodes'][$node]["identities"][$a] = array(	
						"type"			=> $identity['@']['type'],
						"category"			=> $identity['@']['category']
						);
					if($identity['@']['name']){
						$this->services[$jid]['nodes'][$node]["identities"][$a]["name"] = $identity['@']['name'];
					}
						
				}else{
					$this->services[$jid]["identities"][$a] = array(	
						"type"			=> $identity['@']['type'],
						"category"			=> $identity['@']['category']
						);
					if($identity['@']['name']){
						$this->services[$jid]["identities"][$a]["name"] = $identity['@']['name'];
					}
				}
				if ($this->service_single_update) {
					$services_updated = true;
				} else {
					$this->_call_handler("serviceupdate",$jid,$is_new);
				}
			}
			
			$number_of_features = count($packet['iq']['#']['query'][0]['#']['feature']);
			
			for ($a = 0; $a < $number_of_features; $a++)
			{
				$feature = &$packet['iq']['#']['query'][0]['#']['feature'][$a];
				
				if(isset($node)){
					$this->services[$jid]['nodes'][$node]['features'][$a] = $feature['@']['var'];
						
				}else{
					$this->services[$jid]['features'][$a] = $feature['@']['var'];
				}
				if ($this->service_single_update) {
					$services_updated = true;
				} else {
					$this->_call_handler("serviceupdate",$jid,$is_new);
				}
			}
			
			if ($this->service_single_update && $services_updated) {
				$this->_call_handler("serviceupdate",NULL,$is_new);
			}

			$this->_call_handler("service_got_info",$jid,$node);
			$this->_log("Received info of ".$jid);
			//$this->_log("Received service list: ".print_r($this->services,true));
			// choke on error
		} elseif ($packet_type=="error") {
			//A lot of servers don't configure their DNS to point to services like transports, so they aren't accessible from oher servers using S2S
			
			$this->_handle_iq_error($packet);
		
		// confusion sets in
		} else {
			$this->_log("Don't know what to do with packet!");
		}
	}
	
	// Get the nodes childs of $parent
	function discovery($parent) {
		$discovery_id = $this->_unique_id("discovery");
		$this->_set_iq_handler("_on_discovery_result",$discovery_id,NULL,$parent);
		
		return $this->_send_iq($parent, 'get', $discovery_id, "http://jabber.org/protocol/disco#items");
	}
	
	// receives the results of a service discovery query
	function _on_discovery_result(&$packet) {
		$packet_type = $packet['iq']['@']['type'];
		
		//		$this->_log("BROWSE packet: ".var_export($packet,true));
		
		// did we get a result?  if so, process it, and remember the service list	
		if ($packet_type=="result") {
			//$this->services = array();
			
			$childs = array();
			$childs_nodes = array();
			
			//$this->_log("SERVICES: ".print_r($packet,true));
			
			//$this->_log("\n\nSOFTWARE: ".$this->server_software." v".$this->server_version."\n\n");
			
			$jid = &$packet['iq']['@']['from'];
			
			if(isset($packet['iq']['#']['query'][0]['@']['node'])){
				$jid_node = &$packet['iq']['#']['query'][0]['@']['node'];
			}else{
				$jid_node = NULL;
			}
			
			//$number_of_services = count($packet['iq']['#'][$servicekey][0]['#'][$itemkey]);
			if(isset($packet['iq']['#']['query'][0]['#']['item'])){
				$number_of_services = count($packet['iq']['#']['query'][0]['#']['item']);
			}else{
		 		$number_of_services = 0;
			}
		
			for ($a = 0; $a < $number_of_services; $a++)
			{
				$svc = &$packet['iq']['#']['query'][0]['#']['item'][$a];
				
				$service_jid = strtolower($svc['@']['jid']);
				
/* @annotation: should be done in the bot? *//*
			//skip nodes from other servers
				preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$jid,$server_match);
				preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$service_jid,$service_match);
				
				if(($server_match[3]=='com')||($server_match[3]=='net')||($server_match[3]=='org')||($server_match[3]=='co')||($server_match[3]=='gov')||($server_match[3]=='edu')){
					//country code second-level domain
					$server_domain = $server_match[0];
					$service_domain = $service_match[0];
				}else{
					$server_domain = $server_match[2];
					$service_domain = $service_match[2];
				}
				
				if($server_domain != $service_domain) {
					//$this->_log("[SERVICES] Skipped".$service_jid." child of ".$jid);
					continue;
				}*/
				
				if($svc['@']['node']){
					//It's a hierarchy node, not a service
// 					$is_new = False; //Don't add nodes to roster
					$node = $svc['@']['node'];
					$is_new = !isset($this->services[$service_jid]['nodes'][$node]); //Don't add nodes to roster
					$childs_nodes[$node] = $service_jid;
					
					if(!$is_new){
						//skip already discovered nodes
						//$this->_log("[SERVICES] Skipped already discovered ".$service_jid." child of ".$jid);
						continue;
					}
					
					$this->services[$service_jid]['nodes'][$node] = array(	
							"identities"			=> array(), //strtolower($svc['@']['type']),
							"features"			=> array(), //strtolower($svc['@']['type']),
							"status"		=> "Offline",
							"show"			=> "off",
							"name"			=> ($svc['@']['name']?$svc['@']['name']:$svc['@']['jid'])
						);
					
					if ($this->service_single_update) {
						$services_updated = true;
					} else {
						$this->_call_handler("serviceupdate",$service_jid,$is_new);
					}
					
				}else{
					//It's a service
					$is_new = !isset($this->services[$service_jid]);
					
					$childs[] = $service_jid;
					
// 				echo "preprocesar $service_jid $jid\n";
// 				if($service_jid=="aspsms.swissjabber.ch") print_r($this->services[$service_jid]);
					if(!$is_new){
						//skip already discovered nodes
						//$this->_log("[SERVICES] Skipped already discovered ".$service_jid." child of ".$jid);
						continue;
					}
// 					echo "procesar $service_jid $jid\n";
// 				if($service_jid=="aspsms.swissjabber.ch") print_r($this->services[$service_jid]);
					$this->services[$service_jid] = array(	
						"identities"			=> array(), //strtolower($svc['@']['type']),
						"features"			=> array(), //strtolower($svc['@']['type']),
						"status"		=> "Offline",
						"show"			=> "off",
						"name"			=> ($svc['@']['name']?$svc['@']['name']:$svc['@']['jid'])
					);
					
					if ($this->service_single_update) {
						$services_updated = true;
					} else {
						$this->_call_handler("serviceupdate",$service_jid,$is_new);
					}
// 					echo "procesado $service_jid $jid\n";
// 				if($service_jid=="aspsms.swissjabber.ch") print_r($this->services[$service_jid]);
// 					echo "----------------------\n";
				}
			}
				
			if ($this->service_single_update && $services_updated) {
				$this->_call_handler("serviceupdate",NULL,$is_new);
			}
			
			$this->_call_handler("services_discovered",$childs,$childs_nodes,$jid,$jid_node);
			$this->_log("Received service list");
			//$this->_log("Received service list: ".print_r($this->services,true));
			
			// choke on error
		} elseif ($packet_type=="error") {
			//A lot of servers don't configure their DNS to point to services like transports, so they aren't accessible from oher servers using S2S
			$this->_handle_iq_error($packet);
			
			// confusion sets in
		} else {
			$this->_log("Don't know what to do with packet!");
		}
	}
	
	// send a discovery query to a branch node
	function node_discovery($jid,$node) {
		
		$node_discovery_id = $this->_unique_id("node_discovery");
		$this->_set_iq_handler("_on_discovery_result",$node_discovery_id,NULL,$jid,$node);
		
		$xml = "<iq type='get' id='$node_discovery_id' to='$jid'>";
		$xml .= "<query xmlns='http://jabber.org/protocol/disco#items' node='$node' />";
		$xml .= "</iq>";
		return $this->_send($xml);
	}
	
	// ask for informacion about a branch node
	function node_get_info($jid,$node) {
		
		$node_get_info_id = $this->_unique_id("node_get_info");
		$this->_set_iq_handler("_on_get_info_result",$node_get_info_id,NULL,$service,$node);
		
		$xml = "<iq type='get' id='$node_discovery_id' to='$jid'>";
			$xml .= "<query xmlns='http://jabber.org/protocol/disco#info' node='$node' />";
			$xml .= "</iq>";
		
		return $this->_send($xml);
		
	}
	
	// Some servers/services doesn't answer anithing (we do not even get a 404 error)
	function discard_old_querys() {
		if(isset($this->_iq_querys)) {
			$time_now = time();
			foreach($this->_iq_querys as $id => $query) {
				if(($query['time'] + QUERY_TIMEOUT) < $time_now) {
					$this->_log("Discard query: ".$id);
// 					echo "Discard query: ".$id." ".$query['to']." ".($query['time'] + QUERY_TIMEOUT) ." ". $time_now."\n";
					$this->_unset_iq_handler($id);
					$this->_call_handler("discardQuery",$id,$query);
					unset($this->_iq_querys[$id]);
				}
			}
		}
	}
	
	// Sets a handler for a particular IQ packet ID (and optionally packet type).
	// Assumes that $method is the name of a method of $this
	function _set_iq_handler($method,$id,$type=NULL,$to=NULL,$node=NULL) {
		if (is_null($type)) $type = "_all";
		$this->_iq_querys[$id] = array( 'to' => $to, 'time' => time());
		if($node != NULL) {
			$this->_iq_querys[$id]['node'] = $node;
		}
		//print_r(array( 'id' => $id, 'to' => $to, 'time' => time()));
		$this->_iq_handlers[$id][$type] = array(&$this,$method);
	}
	
	// Unsets a handler for a particular IQ packet ID (and optionally packet type).
	function _unset_iq_handler($id,$type='_all') {
		unset($this->_iq_handlers[$id][$type]);
		unset($this->_iq_querys[$id]);
	}
	
	// handle IQ packets
	function _handle_iq(&$packet) {
		$iq_id = $packet['iq']['@']['id'];
		$iq_type = $packet['iq']['@']['type'];
		
		// see if we already have a handler setup for this ID number; the vast majority of IQ
		// packets are handled by their ID number, since they are usually in response to a
		// request we submitted
		if ($this->_iq_handlers[$iq_id]) {
			
			// OK, is there a handler for this specific packet type as well?
			if ($this->_iq_handlers[$iq_id][$iq_type]) {
				// yup - try  the handler for our packet type
				$iqt = $iq_type;
			} else {
				// nope - try the catch-all handler
				$iqt = "_all";
			} 
			
			$this->dlog("Handling $iq_id [$iqt]");
			$handler_method = $this->_iq_handlers[$iq_id][$iqt];
			$this->_unset_iq_handler($iq_id,$iqt);
			
			if ($handler_method) {
				call_user_func($handler_method,&$packet);
			} else {
				$this->_log("Don't know what to do with packet: ".$this->dump($packet));
			}
		} else {
			// this packet didn't have an ID number (or the ID number wasn't recognized), so
			// see if we can salvage it.
			switch($iq_type) {
			case "get":
				if (!$packet['iq']['#']['query']) return;
				
				$xmlns = $packet['iq']['#']['query'][0]['@']['xmlns'];
				switch($xmlns) {
					case "jabber:iq:version":
						// handle version inquiry/response
						$this->_handle_version_packet($packet);
						break;
					case "jabber:iq:time":
						// handle time inquiry/response
						$this->_handle_time_packet($packet);
						break;
					default:
						// unknown XML namespace; borkie borkie!
						break;
				}
				break;
			
			case "set": // handle <iq type="set"> packets
				if (!$packet['iq']['#']['query']) return;
					
					$xmlns = $packet['iq']['#']['query'][0]['@']['xmlns'];
				switch($xmlns) {
					case "jabber:iq:roster":
						$this->_on_roster_result($packet);
						break;
					default:
						// unknown XML namespace; borkie borkie!
						break;
				}
				break;
				
			default:
				// don't know what to do with other types of IQ packets!
				break;
				
			}
		}
	}
	
	function _receive() {
		unset($incoming);
		$packet_count = 0;
		
		$sleepfunc = $this->_sleep_func;
		
		$iterations = 0; 
		do {
			$line = $this->_connection->socket_read(16384);
			
			$incoming .= $line;
			
			//if the stanzas are complete It DOESN'T detects <iq attribute=">"/> but detects <iq >
			//echo $this->_is_valid_xml($incoming); it's a bad workarround 
			if ( preg_match_all("/<(message|iq|presence)([^>]*[^\/])?>/",$incoming,$null) == preg_match_all("/<\/(message|iq|presence)/",$incoming,$null) ){
				if (strlen($line)==0) break;
			}else{
				//	echo "$incoming\n";
				sleep(1);
			}
			$iterations++;
			
			$this->_log("line: $line");
		// the iteration limit is just a brake to prevent infinite loops if
		// something goes awry in socket_read()
		} while($iterations<100);
		
		$incoming = trim($incoming);
		
		if ($incoming != "") {
			//$this->_log("RECV: $incoming");
			
			$temp = $this->_split_incoming($incoming);
			
			$packet_count = count($temp);
			
			for ($a = 0; $a < $packet_count; $a++) {
				$this->_packet_queue[] = $this->xml->xmlize($temp[$a]);
				
				$this->_log("RECV: ".$temp[$a]);
				//.$this->_packet_queue[count($this->_packet_queue)-1]);
			}
		}
		
		return $packet_count;
	}
	
}

?>