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
	
		$this->logged = False;
		$this->jab = &$jab;
		$this->servers = &$servers;
//  		$this->servers = array("jab.undernet.cz","jabber.od.ua","jabber.te.ua","jabberlive.orgg","dimaz.homelinux.org");
// 		$this->servers = array("swissjabber.ch");
		foreach($this->servers as $srv) echo "\"$srv\",";
// 		$this->servers = array(/*"swissjabber.ch"*//*,*//*"swissjabber.de","swissjabber.eu","swissjabber.li","swissjabber.org","syndicon.de","szsport.org","tidesofwar.net",*//*"tigase.org"*//*,"tiggerswelt.net","tlug.up.ac.za","tronet.ru","tuff.org.uk","uaznia.net","ubuntu-jabber.de","ubuntu-jabber.net","udaff.com","udias.com","unilans.net","unstable.nl","verdammung.org","vilinkup.com","vke.ru","vodka-pomme.net","volgograd.ru","wankoo.org","www.wigiwigi.com","x23.eu","xabber.de","xim.ca","xmpp-im.net","xmpp.at",*//*"xmpp.be","xmpp.de","xmpp.dk","xmpp.eu","xmpp.mdve.net","xmpp.nl","xmpp.org.ru","xmpp.us","xmpp.vayusphere.com",*//*"xmpp.ws","xmppnet.de","zweilicht.org"*/"allchitchat.com","jab.undernet.cz");
// 		$this->servers = array("im.drazzib.com");
// 		print_r($this->servers);
// 		echo count($this->servers)."\n";
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
// 		$this->discover_servers_services();
		$this->servers_services = array();
		
		//All services
// 		$this->jab->services = array();
		
		// What services has been processed?
		$this->services_being_procesed = array();
		
		//We store the thierarchy parents[$parent]=array($son1, $son2)
		$this->parents = array();
		
		foreach($this->servers as $server){
// 			$this->services_being_procesed[$server] = True;
			$this->servers_services[$server] = False;
		}
		
		reset($this->servers);
		$this->logged = True;
//  			echo " Disco of server ".current($this->servers)." start at ". date(DATE_RFC850)."\n";
			$this->discover_services(current($this->servers));

	}
	
/* @annotation: no usada */
	/*function discover_servers_services() {
	
		$this->servers_services = array();
		
		//All services
		$this->jab->services = array();
		
		// What services has been processed?
		$this->services_being_procesed = array();
		
		//We store the thierarchy parents[$parent]=array($son1, $son2)
		$this->parents = array();
		
		//Get the servers list from http://www.jabber.org/servers.xml
		
		/*
		<query x=mlns='http://jabber.org/protocol/disco#items'>
			<item jid='12jabber.com'/>
			<item jid='12jabber.net'/>
			..........
		</query>
		*/
/*		
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
		
		foreach($this->servers as $server){
			sleep(1);
			echo " Disco of server ".$server." start at ". date(DATE_RFC850)."\n";
			$this->discover_services($server);
		}
		
	}*/
	
	function discover_services($server=JABBER_SERVER) {
		
//  		echo "Discovering server $server\n";
		//current($this->servers) = $server;
		
// 		echo "Disco ".current($this->servers)."(".key($this->servers)."), ".$this->servers[count($this->servers)-1]."\n";
		
// 		$this->servers_services[$server] = False;
		$this->services_being_procesed[$server]['service'] = True;
		$this->jab->get_info($server,NULL);
		
	}
	
	function serviceProcesed($server,$node=NULL){
// 		echo "unset $server,$node\n";
		if($node){
			unset($this->services_being_procesed[$server]['nodes'][$node]);
			if(!isset($this->services_being_procesed[$server]['service'])){
				unset($this->services_being_procesed[$server]);
			}
		}else{
			unset($this->services_being_procesed[$server]['service']);
			if(count($this->services_being_procesed[$server]['nodes']) == 0){
				unset($this->services_being_procesed[$server]);
			}
		}
	}
	
	
	function inSameServer($server, $service){
		//skip nodes from other servers
		preg_match('/([^.]+\.)?(?=[^.]+\.[^.]+)((([^.]+)\.)([^.]+)$)/',$server,$server_match);
		preg_match('/([^.]+\.)?(?=[^.]+\.[^.]+)((([^.]+)\.)([^.]+)$)/',$service,$service_match);
// 		echo "---------\n";
// 		print_r($server_match);
// 		print_r($service_match);
		if((!isset($service_match[4])) || ($service_match[5] == 'localhost')){
			//Not a valid domain
			return True;
		}else if(
			($server_match[4]=='com') || ($server_match[4]=='net') || ($server_match[4]=='org') || ($server_match[4]=='co') || ($server_match[4]=='gov') || ($server_match[4]=='edu')
		){
			//country code second-level domain
			return ($server_match[0] == $service_match[0]);
		}else{
			return ($server_match[2] == $service_match[2]);
		}
	}
	
	function handleBrowseResult($server,$services){
		$this->parents[$server] = array();
// 		echo "Translate Browse into Discovery on server $server\n";
// 		var_dump($this->jab->services);
// 		var_dump($services);
		$this->jab->services[$server]['identities'][] = array(
			'category' => 'server',
			'type' => 'im'
		);
		$this->parents[$server][] = $server;
		foreach($services as $jid){
			// Make the type an Service Discovery identity
			
			//skip nodes from other servers
// 			preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$server,$server_match);
// 			preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$jid,$service_match);
// 			
// 			if(($server_match[3]=='com')||($server_match[3]=='net')||($server_match[3]=='org')||($server_match[3]=='co')||($server_match[3]=='gov')||($server_match[3]=='edu')){
// 				//country code second-level domain
// 				$server_domain = $server_match[0];
// 				$service_domain = $service_match[0];
// 			}else{
// 				$server_domain = $server_match[2];
// 				$service_domain = $service_match[2];
// 			}
// 			
// 			if($server_domain != $service_domain) {
// 				echo "[SERVICES] Skipped ".$service_jid." child of ".$jid."\n";
// 				continue;
// 			}
			if(!$this->inSameServer($server,$jid)) {
// 				echo "[SERVICES] Skipped ".$service_jid." child of ".$jid."\n";
				continue;
			}
			
			$service = $this->jab->services[$jid];
			if(isset($category)) unset($category);
			if(isset($type)) unset($type);
			if(isset($features)) unset($features);
// 			switch($service['category']){
// 				case 'conference':
					switch($service['type']){
						case 'public':
							$category = "conference";
							$type = "text";
							$features = array("http://jabber.org/protocol/muc");
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
			if(isset($features)){
				$this->jab->services[$jid]['features'] = $features;
			}
			$this->parents[$server][] = $jid;
// 			echo "$jid $category $type\n";
		} //foreach services
		
		$this->serviceProcesed($server);
		if((count($this->services_being_procesed) == 0) && (current($this->servers) === False)){
			$this->processServerServices();
		}
	}
	
/* @annotation: handleServicesDiscovered > Idea, procesar todo a cañon, segun llegan resultados, mirar s el padre es un servidor, si lo es, añadir los jids como sus hijos, tambien se puede mirar si el padre enta en algun servidor y añadirlo */
	function handleServicesDiscovered($services_discovered,$nodes_discovered,$parent,$parentNode=NULL) {
// 		print_r($this->jab->services);
// 		echo " handleServicesDiscovered of $parent\n";
// 		foreach($services_discovered as $srv){
// 			echo "  Discovered service $srv\n";
// 		}
// 		foreach($nodes_discovered as $nod){
// 			echo "  Discoverered node $nod\n";
// 		}
		
// 		$is_branch = False;
// 		foreach($this->jab->services[$parent]['identities'] as $identity) {
// 			if((($identity['category']=='hierarchy') && ($identity['type']=='branch')) || (($identity['category']=='server') && ($identity['type']=='im'))) {
// 				$is_branch = True;
// 				break;
// 			}
// 		}
// 		if($is_branch){
// 			if($parent!=NULL){
// 				$this->services_procesed[$parent] = True;
// 			}
// 		}
// 		print_r($this->services_being_procesed);			
		foreach(array_keys($nodes_discovered) as $key) {
// 			//skip nodes from other servers
// 			preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$parent,$server_match);
// 			preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$nodes_discovered[$key],$service_match);
// 			
// 			if(($server_match[3]=='com')||($server_match[3]=='net')||($server_match[3]=='org')||($server_match[3]=='co')||($server_match[3]=='gov')||($server_match[3]=='edu')){
// 				//country code second-level domain
// 				$server_domain = $server_match[0];
// 				$service_domain = $service_match[0];
// 			}else{
// 				$server_domain = $server_match[2];
// 				$service_domain = $service_match[2];
// 			}
// 			
// 			if($server_domain != $service_domain) {
// 				echo "[SERVICES] Skipped node ".$services_discovered[$key]." child of ".$parent."\n";
// 				unset($nodes_discovered[$key]);
// 			}
			if(!$this->inSameServer($parent,$nodes_discovered[$key])) {
// 				echo "[SERVICES] Skipped node ".$services_discovered[$key]." child of ".$parent."\n";
				unset($nodes_discovered[$key]);
			}
		}
		
		foreach(array_keys($services_discovered) as $key) {
// 			//skip services from other servers
// 			preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$parent,$server_match);
// 			preg_match('/([^.]+\.)?(([^.]+)\.[^.]+$)/',$services_discovered[$key],$service_match);
// 			
// 			if(($server_match[3]=='com')||($server_match[3]=='net')||($server_match[3]=='org')||($server_match[3]=='co')||($server_match[3]=='gov')||($server_match[3]=='edu')){
// 				//country code second-level domain
// 				$server_domain = $server_match[0];
// 				$service_domain = $service_match[0];
// 			}else{
// 				$server_domain = $server_match[2];
// 				$service_domain = $service_match[2];
// 			}
// 			
// 			if($server_domain != $service_domain) {
// 				echo "[SERVICES] Skipped ".$services_discovered[$key]." child of ".$parent."\n";
// 				unset($services_discovered[$key]);
// 			}
			if(!$this->inSameServer($parent,$services_discovered[$key])) {
// 				echo "[SERVICES] Skipped ".$services_discovered[$key]." child of ".$parent."\n";
				unset($services_discovered[$key]);
			}
		}
		
// 		print_r($nodes_discovered);
// 		print_r($services_discovered);
			
		if((count($nodes_discovered)>0)||(count($services_discovered)>0)) {
		
			foreach($nodes_discovered as $node => $jid) {
				
				if(!in_array($jid,$this->parents[$parent])) $this->parents[$parent][] = $jid;
			
//  				echo "    Discover childs of $node\n";
				if($jid != $parent){
					$this->services_being_procesed[$jid]['nodes'][$node] = True;
					if($parent!=NULL){
						$this->serviceProcesed($parent,$parentNode);
// 					}else{
// 						echo "NO1 $jid\n";
					}
				}
				$this->jab->node_discovery($jid,$node);
			}
			foreach($services_discovered as $jid) {
				
				if(!(preg_match('/^echo\./',$jid))) {
					if(!in_array($jid,$this->parents[$parent])) $this->parents[$parent][] = $jid;
					if((!isset($this->jab->services[$jid]['identities'])) || (count($this->jab->services[$jid]['identities']) == 0)) {
// 						unset($this->services_being_procesed[$jid]);
						$this->services_being_procesed[$jid]['service'] = True;
						if($parent!=NULL){
							$this->serviceProcesed($parent,$parentNode);
// 						}else{
// 							echo "NO2 $jid\n";
						}
// 	 					echo "    Get info of $jid < $parent\n";//sleep(1);
// 	 					echo "------------------------------------------\n";
// 	 					var_dump($this->parents);
// 						echo "Ask info of $jid\n";
						$this->jab->get_info($jid);
					}else{
						//We came here by other way (i.e. jabber.linuxlovers.at is procesed before linuxlovers.at but they have the same services)
						if(!in_array($jid,$this->parents[$parent])) $this->parents[$parent][] = $jid;
						$allchilds_procesed = True;
						foreach($services_discovered as $service){
							if(($this->services_being_procesed[$service]['service']) || (!isset($this->jab->services[$service]))){
								$allchilds_procesed = False;
								break;
							}
						}
						if($allchilds_procesed){
							$this->serviceProcesed($parent,$parentNode);
// 						}else{
// 							echo "No3 $parent\n";
						}
					}
				}
			}
/* @annotation: DONE handleServicesDiscovered > para saber si al encontrar un nodo vacio, este es el servidor y, procesa servicios */
		}else{// if(in_array($parent,$this->servers)) {
			//If there are no services
// 			if(count($this->services_procesed) > 0){
			if($parent!=NULL){
				$this->serviceProcesed($parent,$parentNode);
			}
			if((count($this->services_being_procesed) == 0) && (current($this->servers) === False)){
				// We got the info of all services
				$this->processServerServices();
			}
		}
	}
	
	function handleServiceInfo($service,$node=NULL) {
// 		print_r($this->jab->services);
// 		echo "  Info from $service $node\n";
		
// 		print_r($this->jab->services[$service]);
// 		if($service != NULL){
		$is_branch = False;
		
		if((in_array($service,$this->servers)) && (!isset($this->parents[$service]))) $this->parents[$service][] = $service;
		
		if($node){
			if(isset($this->jab->services[$service]['nodes'][$node]['identities'])){
				$identities = $this->jab->services[$service]['nodes'][$node]['identities'];
			}
		}else{
			if(isset($this->jab->services[$service]['identities'])){
				$identities = $this->jab->services[$service]['identities'];
			}
		}
		
		if(isset($identities)){
			foreach($identities as $identity) {
// 				echo "   cat ".$identity['category']." type ".$identity['type']."\n";
				if((($identity['category']=='hierarchy') && ($identity['type']=='branch')) || 
					((($identity['category']=='server') && ($identity['type']=='im'))/* && (!in_array($service,$this->servers))*/) || 
					(($identity['category']=='services') && ($identity['type']=='jabber')) //Jabberd14
				) {
					$is_branch = True;
					break;
				}
			}
		}
		
		if($node){
			if($is_branch){
				//Y si es vacio?
// 				echo "    $service : $node is branch\n";//print_r($this->services_procesed);
				if($this->services_being_procesed[$service]['nodes'][$node]){
					if(!isset($this->parents[$service])) $this->parents[$service] = array();
// 					echo "     discovery $service\n";
					$this->jab->node_discovery($service,$node);
				}
			}else{
	// 			echo "    $service is not branch\n";
				$this->serviceProcesed($service,$node);
			}
		}else{
			if($is_branch){
				//Y si es vacio?
// 				echo "    $service is branch\n";//print_r($this->services_procesed);
				if($this->services_being_procesed[$service]['service']){
					if(!isset($this->parents[$service])) $this->parents[$service] = array();
// 					echo "     discovery $service\n";
					$this->jab->discovery($service);
				}
			}else{
	// 			echo "    $service is not branch\n";
				$this->serviceProcesed($service,$node);
			}
		}
// 		}
		
		//http://www.xmpp.org/registrar/disco-categories.html
// 		print_r($this->services_procesed);
// 		echo "info".$service."\n";
// 		echo $service."->".$this->services[$service]["category"]."\n";
		if((count($this->services_being_procesed) == 0) && (current($this->servers) === False)){
			// We got the info of all services
			$this->processServerServices();
		}
	}
	/*nousada*/
	function getParentServer($son){
		//Find the server
		/*	We assume that every son can only have ONE parent
			this asumption is "guaranteed" by the implementation
			by ignoring his non-natural parents
			(e.g. if jabber.example.com that has a child service.foo.com jabber.example.com is an unnatural parent)*/
		if(in_array($son,$this->servers)){
// 			echo "     Parents: $son is a server\n";
			return $son;
		}else{
			foreach(array_keys($this->parents) as $potentialparent){
// 				echo "      Potential: $potentialparent\n";
// 				print_r($this->parents[$potentialparent]);
// 				echo "          ------------------------------\n";
				if(in_array($son,$this->parents[$potentialparent])){
					//We found his parent
					if(in_array($potentialparent,$this->servers)){
// 						echo "     Parents: $son <- $potentialparent\n";
						return $potentialparent;
					}else{
// 						echo "     Parents: $son <- $potentialparent\n";
						return getParentServer($potentialparent);
					}
				}
			}
		}
	}
	
	function getChildrens($server){
		$childrens = array();
		if(isset($this->parents[$server])){
			foreach($this->parents[$server] as $service){
// 				echo "$server -> $service\n";
				$childrens[] = $service;
				if((isset($this->parents[$service])) && (!in_array($service,$this->servers))){
					$childrens = array_merge($childrens,$this->getChildrens($service));
				}
			}
		}
// 		echo "return\n";
// 		print_r($childrens);
		return $childrens;
	}
	
/* @annotation: [DONE?]REWORKprocessServerServices > se usa para iterar entre servidores, no hara falta */
	// The discovery of a server has ended, continue with next
	function processServerServices() {
// 		echo "  Server ".current($this->servers)." procesed: ".count($this->jab->services)."services ".gettype($this->jab->services)."\n";
// 		echo "Procesing services\n";
/* @annotation: HACER EN EL OTRO SENTIDO, desde el servidor sacar hijos */
// 		foreach($this->parents as $parent => $sons){
// 			foreach($sons as $son){
// // 			echo "------------------------------\n";
// 				$server = $this->getParentServer($parent);
// 				echo "Adding service $son of $parent to server $server\n";
// 				$this->servers_services[$server][$son] = $this->jab->services[$son];
// 			}
// 		}
		foreach($this->servers as $server){
			$services = $this->getChildrens($server);
// 			echo "get\n";
// 			print_r($services);
			foreach($services as $service){
				
// 				echo "Adding service $service of  to server $server\n";
				$this->servers_services[$server][$service] = $this->jab->services[$service];
			}
		}
// 		$this->servers_services[current($this->servers)] = $this->jab->services;
//  			echo " Disco of server ".current($this->servers)." ended at ". date(DATE_RFC850)."\n";
// 		if(next($this->servers)) {
//  			echo " Disco of server ".current($this->servers)." start at ". date(DATE_RFC850)."\n";
// 			$this->discover_services(current($this->servers));
// 		}else{
//  			echo "Server querys ended\n";print_r($this->servers_services[$server]);print_r($parents);
			$this->jab->terminated = true;
// 			$this->jab->disconnect();
			$this->processServers();
// 		}
	}
	
	function processOfflineServer($server) {
// 		echo "Server $server offline\n";
// 		$this->jab->services = False;
		unset($this->services_being_procesed[$server]);
		if((count($this->services_being_procesed) == 0) && (current($this->servers) === False)){
			$this->processServerServices();
		}
	}
	
	// The discovery has ended, show results
	function processServers() {
		
// 		echo "\n\n\n------------------------PARENTS-------------\n\n\n";
// 		print_r($this->parents);
// 		echo "\n\n\n----------------------services---------------\n\n\n";
// 		print_r($this->jab->services);
// 		echo "\n\n\n------------------------servers_services-------------\n\n\n";
// 		print_r($this->servers_services);
// 		var_dump($this->jab->services);
// 		echo "\n\n\n-------------------------------------\n\n\n";
// 		var_dump($this->servers_services);
		// 		print_r($this->services_procesed);
// 		print_r($this->servers_services);
		foreach($this->servers_services as $server => $services) {
			echo "Server: $server\n";
			if(!is_array($services)){
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
					
					if(isset($service['nodes'])){
						foreach($service['nodes'] as $name => $node){
							if(count($node['identities'])>0) {
								foreach($node['identities'] as $identity) {
									//http://www.xmpp.org/registrar/disco-categories.html
									echo "    $jid:$name -> category:".$identity['category'].' type:'.$identity['type'].' name:'.$identity['name']."\n";
								}
							}else{
								//Try to guess
								/*preg_match('/^[^.]+/',$jid,$match);echo '   '.$jid."\n";
								switch($match[0]){
								case 'aim':
								
								case 'msn':
								}*/
								echo "    $jid:$name\n";
							}
						}
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
		if($this->logged){
// 			$num_querys = 0;
// 			foreach($this->services_procesed as $service => $processed){
// 				if((!in_array($service,$this->servers)) && ($processed === False)){
// 					$num_querys++;
// // 					echo ">$service\n";
// 				}
// 			}
// 			echo count($this->services_being_procesed). " < ".MAX_SIMULTANEOUS_QUERYS."\n";
			if(count($this->services_being_procesed) < MAX_SIMULTANEOUS_QUERYS ){/*+ (count($this->servers) - key($this->servers))*/
				//Wait to not saturate the server
				if(next($this->servers)){
//  					echo " Disco of server ".current($this->servers)." start at ". date(DATE_RFC850)."\n";
					$this->discover_services(current($this->servers));
// 				}else{
// 					echo "No more servers".current($this->servers)."(".key($this->servers)."), ".$this->servers[count($this->servers)-1]."\n";
				}
//  			}else{
//  				echo " Deferryng next server disco\n";
//  				print_r($this->services_being_procesed);
			}
			
			
			$this->jab->discard_old_querys();
		
		}
		
// 		if(!isset($this->hearbeats)) $this->hearbeats=1000;
// 		$this->hearbeats+=1;
// 		if(($this->hearbeats%600)==0){
// 			print_r($this->jab->services);
// 			echo "\n\n\n-------------------------------------\n\n\n";
// 			print_r($this->services_being_procesed );
// 			foreach ($this->services_procesed as $service => $status)
// 				echo "$service status: ".($status?"":"NOT")." procesed\n";
// 		}
	}
	
/* @annotation: DONEhandleDiscardQuery > saber si el servidor es el que da problemas y marcarle offline */
	// called when a server takes too long answering a query
	function handleDiscardedQuery($id,$query) {
		if(isset($this->service_retrys[$query['to']])){
			$this->service_retrys[$query['to']] += 1;
		}else{
			$this->service_retrys[$query['to']] = 1;
		}
		//Retry the query? how many times? $this->service_retrys[$jid] += 1;
		
		if($this->services_being_procesed[$query['to']]){
			//If it has not been processed yet (this shouldn't happen if there aren't non-natural parents)
			if($this->service_retrys[$query['to']] <= RETRYS_IF_DISCARDED){
				//Retry query
// 				echo "Retry query to ".$query['to']."\n";
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
					if(in_array($query['to'],$this->servers)) {
						//Discard server
// 						echo "Discard the disco#info to server ".$query['to']."\n";
						$this->processOfflineServer($query['to']);
					}else{
						//Discard service
// 						echo "Discard the disco#info to service ".$query['to']."\n";
	// 					print_r($this->services_procesed);
						$this->handleServiceInfo($query['to']);
					}
				}else if(preg_match('/^discovery_[a-zA-Z0-9]{32}/',$id)) {
					if(in_array($query['to'],$this->servers)) {
// 						echo "Discard the disco#items to server ".$query['to']."\n";
						$this->processOfflineServer($query['to']);
					}else{
// 						echo "Discard the disco#items to service ".$query['to']."\n";
	// 					print_r($this->services_procesed);
						$this->handleServiceInfo($query['to']);
					}
				}else if(preg_match('/^discovery_[a-zA-Z0-9]{32}/',$id)) {
// 						echo "Discard the disco#items to service ".$query['to']." node ".$query['node']."\n";
	// 					print_r($this->services_procesed);
						$this->handleServiceInfo($query['to'],$query['node']);
				}else if(preg_match('/^browse_[a-zA-Z0-9]{32}/',$id)) {
					if(in_array($query['to'],$this->servers)) {
// 	 					echo "Discard the browse to server ".$query['to']."\n";
						$this->processOfflineServer($query['to']);
					}else{
// 						echo "Discard the browse to unknown item ".$query['to']."\n";
	// 					print_r($this->services_procesed);
	// 					$this->handleServiceInfo($query['to']);
					}
				}else{
// 					echo "Discard an unknown query to ".$query['to']." $id\n";
				}
			}
		}
	}
	
/* @annotation: DONE but needs REWORKhandleError saber si el servidor esta off o hay que browse */
	// called when an error is received from the Jabber server
	function handleError($code,$error,$xmlns,$packet) {
		$from = $packet['iq']['@']['from'];
// 		var_dump($packet);
		if(isset($packet['iq']['#']['query'][0]['@']['node'])){
			$node = $packet['iq']['#']['query'][0]['@']['node'];
		}else{
			$node = NULL;
		}
// 		echo "Error: $error ($code)".($xmlns?" in $xmlns":"noxmlns")." from $from $node id ".$packet['iq']['@']['id']."\n";
		if($xmlns == 'http://jabber.org/protocol/disco#info') {
			if(preg_match('/^get_info/',$packet['iq']['@']['id'])) {
				if(in_array($from,$this->servers) && (!isset($node))){
					if($code == 404){
						// The server is offline or don't supports Service discobery, try browse
// 						echo "Try jabber:iq:browse to ".$from."\n";
						$this->jab->browse($from);
					}else{
						// The server is offline
						$this->processOfflineServer($from);
					}
				}else{
					$this->handleServiceInfo($from,$node);
				}
			}
		}else if($xmlns == 'http://jabber.org/protocol/disco#items'){// && ($from == current($this->servers))) {
			//We couldn't discover the childs of a branch node => nothing to do
// 			echo "Couldn't discover childs of $from\n";
			//Ignore that is a branch
			if($node){
				if(isset($this->jab->services[$from]['nodes'][$node]['identities'])){
					$identities = $this->jab->services[$from]['nodes'][$node]['identities'];
				}
			}else{
				if(isset($this->jab->services[$from]['identities'])){
					$identities = $this->jab->services[$from]['identities'];
				}
			}
			if(isset($identities)){
				foreach($identities as $index => $identity){
					if((($identity['category']=='hierarchy') && ($identity['type']=='branch'))){
						unset($this->jab->services[$from]['identities'][$index]);
					}
				}
				//Reindex
				if($node){
					$this->jab->services[$from]['nodes'][$node]['identities'] = array_merge($this->jab->services[$from]['nodes'][$node]['identities']);
				}else{
					$this->jab->services[$from]['identities'] = array_merge($this->jab->services[$from]['identities']);
				}
			}else{
				if($node){
					$this->jab->services[$from]['nodes'][$node]['identities'] = array();
				}else{
					$this->jab->services[$from]['identities'] = array();
				}
			}
// 			$this->handleServicesDiscovered(array(),array(),$from);
			$this->handleServiceInfo($from,$node);
// 			if(count($this->services_procesed) <= 1){ //Itself
				// The server is offline
//  				echo "Server $from offline\n";
// 				$this->processOfflineServer($from);
// 			}else{
				//We couldn't discover the childs of a branch node
// 			}
			
		}else if($xmlns == 'jabber:iq:browse'){// && ($from == current($this->servers))) {
			// The server is probably offline
//  			echo "Server $from offline\n";;
			$this->processOfflineServer($from);
			
		}else if(!$xmlns){
			//Some servers give errors without the xmlns, so try to guess
			
			if(in_array($from,$this->servers)){
// 				if(count($this->services_procesed) <= 1){
					// Can't access to server
					$this->processOfflineServer($from);
// 				}
			}else if(preg_match('/^get_info/',$packet['iq']['@']['id'])) {
				// Maybe it's a service
				$this->handleServiceInfo($from,$node);
			}
			
		}
	}
}

?>
