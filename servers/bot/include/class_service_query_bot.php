<?php
/* Copyright 2007, noalwin <lambda512@gmail.com> <xmpp:lambda512@jabberes.org>
 * Based on
 * Jabber Class Example
 * Copyright 2002-2005, Steve Blinch
 * http://code.blitzaffe.com
 * ============================================================================
 *
 * LICENSE
 *
 * class_Jabber.php - Jabber Client Library (service discovery extension)
 * Copyright 2007, noalwin
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
 */
 

// This class query server by server to get their services


class service_query_bot {
	
	function service_query_bot(&$jab,&$servers) {
	
		$this->jab = &$jab;
		$this->servers = &$servers;
//  		$this->servers = array("jab.undernet.cz","jabber.od.ua","jabber.te.ua","jabberlive.orgg","dimaz.homelinux.org");
		/*echo "Created!\n";*/
	}
	
	// called when a connection to the Jabber server is established
	function handleConnected() {
		/*echo "Connected!\n";*/
		
		// now that we're connected, tell the Jabber class to login
		$this->jab->login(JABBER_USERNAME,JABBER_PASSWORD,JABBER_RESOURCE);
	}
	
	// called after a login to indicate the the login was successful
	function handleAuthenticated() {
		/*echo "Authenticated!\n";*/
		$this->discover_servers_services();
	}
	function discover_servers_services() {
	
		$this->servers_services = array();
		
		//Get the servers list from http://www.jabber.org/servers.xml
		
		/*
		<query x=mlns='http://jabber.org/protocol/disco#items'>
			<item jid='12jabber.com'/>
			<item jid='12jabber.net'/>
			..........
		</query>
		*/
		
// 		$server_list = new XMLReader();
// 		if(!$server_list->open(XML_SERVER_LIST)) die("Can\'t retrieve the XML server list ".XML_SERVER_LIST);
// // 		if(!$server_list->isValid()) die("The XML server list is NOT valid ".XML_SERVER_LIST);
// 		$this->servers = array();
// 		
// 		while($server_list->read()) {
// 			if(($server_list->nodeType == XMLReader::ELEMENT) && ($server_list->localName == "item")) {
// 				do {
// 					$this->servers[] = strtolower($server_list->getAttribute('jid'));
// 				}while($server_list->next('item'));
// 			}
// 		}
// 		
// 		
// 		
// 		$server_list->close();

// 		print_r($this->servers);
		
		reset($this->servers);
		
 		echo " Disco of server ".current($this->servers)." start at ". date(DATE_RFC850)."\n";
		$this->discover_services(current($this->servers));
		
	}
	
	function discover_services($server=JABBER_SERVER) {
		
//  		echo "Discovering server $server\n";
		//current($this->servers) = $server;
		
		//Server services
		$this->jab->services = array();
		
		// are we get info of that services?
		$this->services_procesed = array();
		
		$this->services_procesed[$server] = False;
		$this->jab->get_info($server,NULL);
		
	}
	
	
	function handleBrowseResult($server){
// 		echo "Translate Browse into Discovery on server $server\n";
		//var_dump($this->jab->services);
		foreach($this->jab->services as $jid => $service){
			// Make the type an Service Discovery identity
			
// 			switch($service['category']){
// 				case 'conference':
					switch($service['type']){
						case 'public':
							$category = "conference";
							$type = "text";
							break;
						case 'irc':
							$category = "conference";
							$type = "irc";
							break;
// 					}
// 					break;
					
// 				case 'service':
// 					switch($service['type']){
						case 'aim':
						case 'icq':
						case 'msn':
						case 'sms':
						case 'smtp':
						case 'yahoo':
							$category = "gateway";
							$type = $service['type'];
							break;
						case 'irc':
							$category = "conference";
							$type = "irc";
							break;
						case 'jud':
							$category = "directory";
							$type = "user";
							break;
// 					}
// 					break;
					
			}
			
			if((isset($category)) && (isset($type))){
				$this->jab->services[$jid]['identities'][] = array(
					'category' => $category,
					'type' => $type
				);
			}
		}
		$this->services_procesed[$server] = True;
		$this->processServerServices();
	}
	
/* @annotation: handleServicesDiscovered > Idea, procesar todo a cañon, segun llegan resultados, mirar s el padre es un servidor, si lo es, añadir los jids como sus hijos, tambien se puede mirar si el padre enta en algun servidor y añadirlo */
	function handleServicesDiscovered($services_discovered,$nodes_discovered,$parent) {

//  		echo " handleServicesDiscovered\n";
//  		foreach($services_discovered as $srv){
//  			echo "  Discovered service $srv\n";
//  		}
//  		foreach($nodes_discovered as $nod){
//  			echo "  Discoverered node $nod\n";
//  		}
		
		$is_branch = False;
		foreach($this->jab->services[$parent]['identities'] as $identity) {
			if((($identity['category']=='hierarchy') && ($identity['type']=='branch')) || (($identity['category']=='server') && ($identity['type']=='im'))) {
				$is_branch = True;
				break;
			}
		}
		if($is_branch){
			if($parent!=NULL){
				$this->services_procesed[$parent] = True;
			}
		}
		
		if((count($nodes_discovered)>0)||(count($services_discovered)>0)) {
			foreach($nodes_discovered as $node => $jid) {
//  				echo "    Discover childs of $node\n";
				$this->jab->node_discovery($jid,$node);
			}
			foreach($services_discovered as $jid) {
				if(!(preg_match('/^echo\./',$jid))) {
					$this->services_procesed[$jid] = False;
//  					echo "    Get info of $jid\n";//sleep(1);
					$this->jab->get_info($jid);
				}
			}
/* @annotation: handleServiceDiscovered > para saber si al encontrar un nodo vacio, este es el servidor y, procesa servicios */
		}else if($parent == current($this->servers)) {
			//If there are no services
			if(!in_array(False, $this->services_procesed, True)){
				// We got the info of all services
				$this->processServerServices();
			}
		}
	}
	
	function handleServiceInfo($service) {
//  		echo "  Info from $service\n";
		
// 		if($service != NULL){
		$is_branch = False;
		
		if(isset($this->jab->services[$service]['identities'])){
			foreach($this->jab->services[$service]['identities'] as $identity) {
// 				echo "   cat ".$identity['category']." type ".$identity['type']."\n";
				if((($identity['category']=='hierarchy') && ($identity['type']=='branch')) || (($identity['category']=='server') && ($identity['type']=='im'))) {
					$is_branch = True;
					break;
				}
			}
		}
		
		if($is_branch){
			//Y si es vacio?
			$this->jab->discovery($service);
		}else{
			$this->services_procesed[$service] = True;
		}
// 		}
		
		//http://www.xmpp.org/registrar/disco-categories.html
		print_r($this->services_procesed);
// 		echo "info".$service."\n";
		if(!in_array(False, $this->services_procesed, True)){
			// We got the info of all services
			$this->processServerServices();
		}
		//echo $service."->".$this->services[$service]["category"]."\n";
	}
	
/* @annotation: processServerServices > se usa para iterar entre servidores, no hara falta */
	// The discovery of a server has ended, continue with next
	function processServerServices() {
// 		echo "  Server ".current($this->servers)." procesed: ".count($this->jab->services)."services ".gettype($this->jab->services)."\n";
		$this->servers_services[current($this->servers)] = $this->jab->services;
 			echo " Disco of server ".current($this->servers)." ended at ". date(DATE_RFC850)."\n";
		if(next($this->servers)) {
 			echo " Disco of server ".current($this->servers)." start at ". date(DATE_RFC850)."\n";
			$this->discover_services(current($this->servers));
		}else{
 			echo "Server querys ended\n";
			$this->jab->terminated = true;
// 			$this->jab->disconnect();
			$this->processServers();
		}
	}
	
	function processOfflineServer($server) {
//  		echo "Server $server offline\n";
		$this->jab->services = False;
		$this->processServerServices();
	}
	
	// The discovery has ended, show results
	function processServers() {
		
		// 		print_r($this->services_procesed);
		foreach($this->servers_services as $server => $services) {
			echo "Server: $server\n";
			if(!(is_array($services))){
				echo " is offline\n";
			}else{
				foreach($services as $jid => $service){
					if(count($service['identities'])>0) {
						foreach($service['identities'] as $identity) {
							//http://www.xmpp.org/registrar/disco-categories.html
							echo '    '.$jid.'-> category:'.$identity['category'].' type:'.$identity['type'].' name:'.$identity['name']."\n";
						}
					}else{
						//Try to guess
						/*preg_match('/^[^.]+/',$jid,$match);echo '   '.$jid."\n";
						switch($match[0]){
						case 'aim':
						
						case 'msn':
						}*/
						echo "    $jid\n";
					}
				}
			}
		}
	}
	
	// called after a login to indicate that the login was NOT successful
	function handleAuthFailure($code,$error) {
		//echo "Authentication failure: $error ($code)\n";
		
		// set terminated to TRUE in the Jabber class to tell it to exit
		$this->jab->terminated = true;
	}
	
	// called periodically by the Jabber class to allow us to do our own
	// processing
 	function handleHeartbeat() {
//  		//echo "Heartbeat!\n";
		$this->jab->discard_old_querys();
	}
	
/* @annotation: handleDiscardQuery > saber si el servidor es el que da problemas y marcarle offline */
	// called when a server takes too long answering a query
	function handleDiscardedQuery($id,$query) {
		if(isset($this->service_retrys[$query['to']])){
			$this->service_retrys[$query['to']] += 1;
		}else{
			$this->service_retrys[$query['to']] = 1;
		}
		//Retry the query? how many times? $this->service_retrys[$jid] += 1;
		
		if($this->service_retrys[$query['to']] <= RETRYS_IF_DISCARDED){
			//Retry query
//  			echo "Retry query to ".$query['to']."\n";
			if(preg_match('/^get_info_[a-zA-Z0-9]{32}/',$id)){
				$this->jab->get_info($query['to']);
			}else if(preg_match('/^discovery_[a-zA-Z0-9]{32}/',$id)) {
				$this->jab->discovery($query['to']);
			}else if(preg_match('/^node_discovery_[a-zA-Z0-9]{32}/',$id)) {
				$this->jab->node_discovery($query['to'],$query['node']);
			}else if(preg_match('/^browse_[a-zA-Z0-9]{32}/',$id)) {
				$this->jab->browse($query['to']);
			}
		}else{
			//Discard the item
			if(preg_match('/^get_info_[a-zA-Z0-9]{32}/',$id)){
				if($query['to'] == current($this->servers)) {
					//Discard server
//  					echo "Discard the disco#info to server ".$query['to']."\n";
					$this->processOfflineServer($query['to']);
				}else{
					//Discard service
//  					echo "Discard the disco#info to service ".$query['to']."\n";
// 					print_r($this->services_procesed);
					$this->handleServiceInfo($query['to']);
				}
			}else if((preg_match('/^discovery_[a-zA-Z0-9]{32}/',$id)) || (preg_match('/^node_discovery_[a-zA-Z0-9]{32}/',$id))) {
				if($query['to'] == current($this->servers)) {
//  					echo "Discard the disco#items to server ".$query['to']."\n";
					$this->processOfflineServer($query['to']);
				}else{
//  					echo "Discard the disco#items to service ".$query['to']."\n";
// 					print_r($this->services_procesed);
					$this->handleServiceInfo($query['to']);
				}
			}else if(preg_match('/^browse_[a-zA-Z0-9]{32}/',$id)) {
				if($query['to'] == current($this->servers)) {
//  					echo "Discard the browse to server ".$query['to']."\n";
					$this->processOfflineServer($query['to']);
				}else{
//  					echo "Discard the browse to unknown item ".$query['to']."\n";
// 					print_r($this->services_procesed);
// 					$this->handleServiceInfo($query['to']);
				}
			}else{
//  				echo "Discard an unknown query to ".$query['to']." $id\n";
			}
		}
	}
	
/* @annotation: handleError saber si el servidor esta off o hay que browse */
	// called when an error is received from the Jabber server
	function handleError($code,$error,$xmlns,$packet) {
		$from = $packet['iq']['@']['from'];
//  		echo "Error: $error ($code)".($xmlns?" in $xmlns":"noxmlns")." from $from id ".$packet['iq']['@']['id']."\n";
		if($xmlns == 'http://jabber.org/protocol/disco#info') {
			
			if(preg_match('/^get_info/',$packet['iq']['@']['id'])) {
				if($from == current($this->servers)){
					if($code == 404){
						// The server is offline or don't supports Service discobery, try browse
// 						echo "Try jabber:iq:browse to ".$from."\n";
						$this->jab->browse($from);
					}else{
						// The server is offline
						$this->processOfflineServer($from);
					}
				}else{
					$this->handleServiceInfo($from);
				}
			}
			
		}else if(($xmlns == 'http://jabber.org/protocol/disco#items') && ($from == current($this->servers))) {
			
			if(count($this->services_procesed) <= 1){ //Itself
				// The server is offline
//  				echo "Server $from offline\n";
				$this->processOfflineServer($from);
			}else{
				//We couldn't discover the childs of a branch node
			}
			
		}else if(($xmlns == 'jabber:iq:browse') && ($from == current($this->servers))) {
			// The server is probably offline
//  			echo "Server $from offline\n";;
			$this->processOfflineServer($from);
			
		}else if(!$xmlns){
			//Some servers give errors without the xmlns, so try to guess
			
			if($from == current($this->servers)){
				if(count($this->services_procesed) <= 1){
					// Can't access to server
					$this->processOfflineServer($from);
				}
			}else if(preg_match('/^get_info/',$packet['iq']['@']['id'])) {
				// Maybe it's a service
				$this->handleServiceInfo($from);
			}
			
		}
	}
}

?>
