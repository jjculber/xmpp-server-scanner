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

//
// define('XML_SERVER_LIST','http://www.jabber.org/servers.xml');
//define('TIMES_OFFLINE_ALLOWED',5);
// define('MYSQL_TABLE','servers');

require_once("class_service_query_bot.php");
class update_mysql_service_list_bot extends service_query_bot {

	function update_mysql_service_list_bot(&$jab,&$db,&$servers) {
		
		$this->db = &$db;
		
		if(!$this->db->ping()) die("The MySQL conection has failed");
		
		$this->jab = &$jab;
		$this->servers = &$servers;
	}
	
	function processServers() {
		
		foreach($this->servers_services as $server => $services) {
			
			$has_muc = 0;
			$has_irc = 0;
			$has_aim = 0;
			$has_gg = 0;
			$has_httpws = 0;
			$has_icq = 0;
			$has_msn = 0;
			$has_qq = 0;
			$has_sms = 0;
			$has_smtp = 0;
			$has_tlen = 0;
			$has_yahoo = 0;
			$has_jud = 0;
			$has_pubsub = 0;
			$has_pep = 0;
			$has_presence = 0;
			$has_newmail = 0;
			$has_rss = 0;
			$has_weather = 0;
			$has_proxy = 0;
			$is_offline  = 0;
			
			if(!(is_array($services))){
				$is_offline = True;
				
				//Insert or update the server
				$query = "INSERT ".MYSQL_TABLE." SET ".
					"name = '".$this->db->real_escape_string($server)."', ".
					"has_muc = $has_muc, ".
					"has_irc = $has_irc, ".
					"has_aim = $has_aim, ".
					"has_gg = $has_gg, ".
					"has_httpws = $has_httpws, ".
					"has_icq = $has_icq, ".
					"has_msn = $has_msn, ".
					"has_qq = $has_qq, ".
					"has_sms = $has_sms, ".
					"has_smtp = $has_smtp, ".
					"has_tlen = $has_tlen, ".
					"has_yahoo = $has_yahoo, ".
					"has_jud = $has_jud, ".
					"has_pubsub = $has_pubsub, ".
					"has_pep = $has_pep, ".
					"has_presence = $has_presence, ".
					"has_newmail = $has_newmail, ".
					"has_rss = $has_rss, ".
					"has_weather = $has_weather, ".
					"has_proxy = $has_proxy, ".
					"times_offline = ".($is_offline?"1":"0").
					" ON DUPLICATE KEY UPDATE ".
					"times_offline = ".($is_offline?"times_offline + 1":"0")." ";
// 				echo $query."\n\n";
				
				if(($this->db->query($query)) === False) die("MySQL Error:".$this->db->error." on query ".$query);
				
			}else{
				//http://www.xmpp.org/registrar/disco-categories.html
				foreach($services as $jid => $service){
					if(count($service['identities'])>0) {
						$identities = $service['identities'];
						if(isset($service['nodes'])){
							foreach($service['nodes'] as $node => $node_service){
								$identities = array_merge($identities,$node_service['identities']);
							}
						}
						$features = $service['features'];
						if(isset($service['nodes'])){
							foreach($service['nodes'] as $node => $node_service){
								$features = array_merge($features,$node_service['features']);
							}
						}
						foreach($identities as $identity) {
							
							switch($identity['category']){
							
								case 'conference':
									switch($identity['type']){
										case 'text': 
											//This don't neccesary mean that it's a MUC, some transports also use it, maybe we should add feature dettection
											if(in_array('http://jabber.org/protocol/muc',$features)){
												$has_muc = 255;
											}
											break;
										case 'irc': 
											$has_irc = 255;
											break;
									}
									break;
									
								case 'gateway':
									switch($identity['type']){
										case 'aim': 
											$has_aim = 255;
											break;
										case 'gadu-gadu': 
											$has_gg = 255;
											break;
										case 'http-ws': 
											$has_httpws = 255;
											break;
										case 'icq': 
											$has_icq = 255;
											break;
										case 'msn': 
											$has_msn = 255;
											break;
										case 'qq': 
											$has_qq = 255;
											break;
										case 'sms': 
											$has_sms = 255;
											break;
										case 'smtp': 
											$has_smtp = 255;
											break;
										case 'tlen': 
											$has_tlen = 255;
											break;
										case 'yahoo': 
											$has_yahoo = 255;
											break;
									}
									
									break;
									
								case 'directory':
									switch($identity['type']){
										case 'user': 
											$has_jud = 255;
											break;
									}
									
									break;
									
								case 'pubsub':
									switch($identity['type']){
										case 'service': //XEP
										case 'generic': //ejabberd 1.1.3
											$has_pubsub = 255;
											break;
										case 'pep': 
											$has_pep = 255;
											break;
									}
									
									break;
									
								case 'component':
									switch($identity['type']){
										case 'presence': 
											$has_presence = 255;
											break;
									}
									
									break;
									
								case 'headline':
									switch($identity['type']){
										case 'newmail': 
											$has_newmail = 255;
											break;
										case 'rss': 
											$has_rss = 255;
											break;
										case 'weather': 
											$has_weather = 255;
											break;
									}
									
									break;
									
								case 'proxy':
									switch($identity['type']){
										case 'bytestreams': 
											$has_proxy = 255;
											break;
									}
									
									break;
									
								/* NON STANDARD */
									
								case 'agent':
									switch($identity['type']){
										case 'weather': 
											$has_weather = 255;
											break;
									}
									
									break;
									
									
								case 'x-service':
									switch($identity['type']){
										case 'x-rss': //PyRSS
											$has_rss = 255;
											break;
									}
									
									break;
									
							} // switch category
						} //foreach identity
					}else{
						//There is no finfo about the service (maybe a 404 error while exploring) so we try to guess using the JID
						// TODO: use regular expresions instead cases
						preg_match('/^[^.]+/',$jid,$match);
						switch($match[0]){
							case 'conference':
							case 'conf':
							case 'muc':
							case 'chat':
							case 'rooms':
								$has_muc = 1;
								break;
							case 'irc':
								$has_irc = 1;
								break;
							case 'aim':
							case 'aim-icq':
							case 'aim-jab':
								$has_aim = 1;
								break;
							case 'gg':
							case 'gadugadu':
							case 'gadu-gadu':
								$has_gg = 1;
								break;
							case 'http-ws':
								$has_httpws = 1;
							case 'icq':
							case 'icqt':
							case 'aim-icq':
							case 'jit-icq':
							case 'icq-jab':
							case 'icq2':
								$has_icq = 1;
								break;
							case 'msn':
							case 'msnt':
							case 'pymsnt':
								$has_msn = 1;
								break;
							case 'qq':
								$has_qq = 1;
								break;
							case 'sms':
								$has_sms = 1;
								break;
							case 'smtp':
								$has_smtp = 1;
								break;
							case 'tlen':
								$has_tlen = 1;
								break;
							case 'yahoo':
								$has_yahoo = 1;
								break;
							case 'jud':
							case 'vjud':
							case 'search':
							case 'users':
								$has_jud = 1;
								break;
							case 'pubsub':
								$has_pubsub = 1;
								break;
							case 'pep':
								$has_pep = 1;
								break;
							case 'presence':
							case 'webpresence':
								$has_presence = 1;
								break;
							case 'newmail':
							case 'mail':
							case 'jmc': //JabberMailComponent
								$has_newmail = 1;
								break;
							case 'rss':
								$has_rss = 1;
								break;
							case 'weather':
								$has_weather = 1;
								break;
							case 'proxy':
							case 'proxy65':
								$has_proxy = 1;
								break;
							default:
								//Try to guess using the name
// 								if($service['name']){
// 									switch($service['name']){}
// 								}
// 								echo "Unknown service $jid ".$service['name']."\n";
						}
					}
				}
				
				//Insert or update the server
				$query = "INSERT ".MYSQL_TABLE." SET ".
					"name = '".$this->db->real_escape_string($server)."', ".
					"has_muc = $has_muc, ".
					"has_irc = $has_irc, ".
					"has_aim = $has_aim, ".
					"has_gg = $has_gg, ".
					"has_httpws = $has_httpws, ".
					"has_icq = $has_icq, ".
					"has_msn = $has_msn, ".
					"has_qq = $has_qq, ".
					"has_sms = $has_sms, ".
					"has_smtp = $has_smtp, ".
					"has_tlen = $has_tlen, ".
					"has_yahoo = $has_yahoo, ".
					"has_jud = $has_jud, ".
					"has_pubsub = $has_pubsub, ".
					"has_pep = $has_pep, ".
					"has_presence = $has_presence, ".
					"has_newmail = $has_newmail, ".
					"has_rss = $has_rss, ".
					"has_weather = $has_weather, ".
					"has_proxy = $has_proxy, ".
					"times_offline = ".($is_offline?"1":"0").
					" ON DUPLICATE KEY UPDATE ".
					"name = '".$this->db->real_escape_string($server)."', ".
					"has_muc = $has_muc, ".
					"has_irc = $has_irc, ".
					"has_aim = $has_aim, ".
					"has_gg = $has_gg, ".
					"has_httpws = $has_httpws, ".
					"has_icq = $has_icq, ".
					"has_msn = $has_msn, ".
					"has_qq = $has_qq, ".
					"has_sms = $has_sms, ".
					"has_smtp = $has_smtp, ".
					"has_tlen = $has_tlen, ".
					"has_yahoo = $has_yahoo, ".
					"has_jud = $has_jud, ".
					"has_pubsub = $has_pubsub, ".
					"has_pep = $has_pep, ".
					"has_presence = $has_presence, ".
					"has_newmail = $has_newmail, ".
					"has_rss = $has_rss, ".
					"has_weather = $has_weather, ".
					"has_proxy = $has_proxy, ".
					"times_offline = ".($is_offline?"times_offline + 1":"0")." ";
				
// 				echo "$query\n\n";
				if(($this->db->query($query)) === False) die("MySQL Error:".$this->db->error." on query ".$query);
			}//else (is online)
			
		}//foreach servers=>services
		
		//Delete servers that aren't in the list
		$servers = array_keys($this->servers_services);
		if(($result = $this->db->query("SELECT name FROM ".MYSQL_TABLE)) === False ) die("MySQL Error:".$this->db->error);
		
		$row = $result->fetch_assoc();
		while(!is_null($row)){
			if(!in_array($row['name'],$servers)){
				$query = "DELETE FROM ".MYSQL_TABLE." WHERE name='".$this->db->real_escape_string($row['name'])."'";
//  				echo "Delete '".$row['name']."'\n";
				if(($this->db->query($query)) === False) die("MySQL Error:".$this->db->error." on query ".$query);
				
			}
			$row = $result->fetch_assoc();
		}
		$result->free_result();
		
	}
}
	
?>
