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
			
			$has_muc = False;
			$has_irc = False;
			$has_aim = False;
			$has_gg = False;
			$has_httpws = False;
			$has_icq = False;
			$has_msn = False;
			$has_qq = False;
			$has_sms = False;
			$has_smtp = False;
			$has_tlen = False;
			$has_yahoo = False;
			$has_jud = False;
			$has_pubsub = False;
			$has_pep = False;
			$has_presence = False;
			$has_newmail = False;
			$has_rss = False;
			$has_weather = False;
			$has_proxy = False;
			$is_offline  = False;
			
			if(!(is_array($services))){
				$is_offline = True;
				
				//Insert or update the server
				$query = "INSERT ".MYSQL_TABLE." SET ".
					"name = '".$this->db->real_escape_string($server)."', ".
					"has_muc = ".($has_muc?"True":"False").", ".
					"has_irc = ".($has_irc?"True":"False").", ".
					"has_aim = ".($has_aim?"True":"False").", ".
					"has_gg = ".($has_gg?"True":"False").", ".
					"has_httpws = ".($has_httpws?"True":"False").", ".
					"has_icq = ".($has_icq?"True":"False").", ".
					"has_msn = ".($has_msn?"True":"False").", ".
					"has_qq = ".($has_qq?"True":"False").", ".
					"has_sms = ".($has_sms?"True":"False").", ".
					"has_smtp = ".($has_smtp?"True":"False").", ".
					"has_tlen = ".($has_tlen?"True":"False").", ".
					"has_yahoo = ".($has_yahoo?"True":"False").", ".
					"has_jud = ".($has_jud?"True":"False").", ".
					"has_pubsub = ".($has_pubsub?"True":"False").", ".
					"has_pep = ".($has_pep?"True":"False").", ".
					"has_presence = ".($has_presence?"True":"False").", ".
					"has_newmail = ".($has_newmail?"True":"False").", ".
					"has_rss = ".($has_rss?"True":"False").", ".
					"has_weather = ".($has_weather?"True":"False").", ".
					"has_proxy = ".($has_proxy?"True":"False").", ".
					"times_offline = ".($is_offline?"1":"0").
					" ON DUPLICATE KEY UPDATE ".
					"times_offline = ".($is_offline?"times_offline + 1":"0")." ";
// 				echo $query."\n\n";
				
				if(($this->db->query($query)) === False) die("MySQL Error:".$this->db->error." on query ".$query);
				
			}else{
				//http://www.xmpp.org/registrar/disco-categories.html
				foreach($services as $jid => $service){
					if(count($service['identities'])>0) {
						foreach($service['identities'] as $identity) {
							
							switch($identity['category']){
							
								case 'conference':
									switch($identity['type']){
										case 'text': 
											$has_muc = True;
											break;
										case 'irc': 
											$has_irc = True;
											break;
									}
									break;
									
								case 'gateway':
									switch($identity['type']){
										case 'aim': 
											$has_aim = True;
											break;
										case 'gadu-gadu': 
											$has_gg = True;
											break;
										case 'http-ws': 
											$has_httpws = True;
											break;
										case 'icq': 
											$has_icq = True;
											break;
										case 'msn': 
											$has_msn = True;
											break;
										case 'qq': 
											$has_qq = True;
											break;
										case 'sms': 
											$has_sms = True;
											break;
										case 'smtp': 
											$has_smtp = True;
											break;
										case 'tlen': 
											$has_tlen = True;
											break;
										case 'yahoo': 
											$has_yahoo = True;
											break;
									}
									
									break;
									
								case 'directory':
									switch($identity['type']){
										case 'user': 
											$has_jud = True;
											break;
									}
									
									break;
									
								case 'pubsub':
									switch($identity['type']){
										case 'service': //XEP
										case 'generic': //ejabberd 1.1.3
											$has_pubsub = True;
											break;
										case 'pep': 
											$has_pep = True;
											break;
									}
									
									break;
									
								case 'component':
									switch($identity['type']){
										case 'presence': 
											$has_presence = True;
											break;
									}
									
									break;
									
								case 'headline':
									switch($identity['type']){
										case 'newmail': 
											$has_newmail = True;
											break;
										case 'rss': 
											$has_rss = True;
											break;
										case 'weather': 
											$has_weather = True;
											break;
									}
									
									break;
									
								case 'proxy':
									switch($identity['type']){
										case 'bytestreams': 
											$has_proxy = True;
											break;
									}
									
									break;
							} // switch category
						} //foreach service
					}else{
						//There is no finfo about the service (maybe a 404 error while exploring) so we try to guess using the JID
						preg_match('/^[^.]+/',$jid,$match);
						switch($match[0]){
							case 'conference':
							case 'conf':
							case 'muc':
							case 'chat':
								$has_muc = True;
								break;
							case 'irc':
								$has_irc = True;
								break;
							case 'aim':
								$has_aim = True;
								break;
							case 'gg':
							case 'gadugadu':
							case 'gadu-gadu':
								$has_gg = True;
								break;
							case 'http-ws':
								$has_httpws = True;
							case 'icq':
								$has_icq = True;
								break;
							case 'msn':
								$has_msn = True;
								break;
							case 'qq':
								$has_qq = True;
								break;
							case 'sms':
								$has_sms = True;
								break;
							case 'smtp':
								$has_smtp = True;
								break;
							case 'tlen':
								$has_tlen = True;
								break;
							case 'yahoo':
								$has_yahoo = True;
								break;
							case 'jud':
							case 'vjud':
							case 'search':
							case 'users':
								$has_jud = True;
								break;
							case 'pubsub':
								$has_pubsub = True;
								break;
							case 'pep':
								$has_pep = True;
								break;
							case 'presence':
							case 'webpresence':
								$has_presence = True;
								break;
							case 'newmail':
								$has_newmail = True;
								break;
							case 'rss':
								$has_rss = True;
								break;
							case 'weather':
								$has_weather = True;
								break;
							case 'proxy':
								$has_proxy = True;
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
					"has_muc = ".($has_muc?"True":"False").", ".
					"has_irc = ".($has_irc?"True":"False").", ".
					"has_aim = ".($has_aim?"True":"False").", ".
					"has_gg = ".($has_gg?"True":"False").", ".
					"has_httpws = ".($has_httpws?"True":"False").", ".
					"has_icq = ".($has_icq?"True":"False").", ".
					"has_msn = ".($has_msn?"True":"False").", ".
					"has_qq = ".($has_qq?"True":"False").", ".
					"has_sms = ".($has_sms?"True":"False").", ".
					"has_smtp = ".($has_smtp?"True":"False").", ".
					"has_tlen = ".($has_tlen?"True":"False").", ".
					"has_yahoo = ".($has_yahoo?"True":"False").", ".
					"has_jud = ".($has_jud?"True":"False").", ".
					"has_pubsub = ".($has_pubsub?"True":"False").", ".
					"has_pep = ".($has_pep?"True":"False").", ".
					"has_presence = ".($has_presence?"True":"False").", ".
					"has_newmail = ".($has_newmail?"True":"False").", ".
					"has_rss = ".($has_rss?"True":"False").", ".
					"has_weather = ".($has_weather?"True":"False").", ".
					"has_proxy = ".($has_proxy?"True":"False").", ".
					"times_offline = ".($is_offline?"1":"0").
					" ON DUPLICATE KEY UPDATE ".
					"name = '".$this->db->real_escape_string($server)."', ".
					"has_muc = ".($has_muc?"True":"False").", ".
					"has_irc = ".($has_irc?"True":"False").", ".
					"has_aim = ".($has_aim?"True":"False").", ".
					"has_gg = ".($has_gg?"True":"False").", ".
					"has_httpws = ".($has_httpws?"True":"False").", ".
					"has_icq = ".($has_icq?"True":"False").", ".
					"has_msn = ".($has_msn?"True":"False").", ".
					"has_qq = ".($has_qq?"True":"False").", ".
					"has_sms = ".($has_sms?"True":"False").", ".
					"has_smtp = ".($has_smtp?"True":"False").", ".
					"has_tlen = ".($has_tlen?"True":"False").", ".
					"has_yahoo = ".($has_yahoo?"True":"False").", ".
					"has_jud = ".($has_jud?"True":"False").", ".
					"has_pubsub = ".($has_pubsub?"True":"False").", ".
					"has_pep = ".($has_pep?"True":"False").", ".
					"has_presence = ".($has_presence?"True":"False").", ".
					"has_newmail = ".($has_newmail?"True":"False").", ".
					"has_rss = ".($has_rss?"True":"False").", ".
					"has_weather = ".($has_weather?"True":"False").", ".
					"has_proxy = ".($has_proxy?"True":"False").", ".
					"times_offline = ".($is_offline?"times_offline + 1":"0")." ";
				
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
					
				if(($this->db->query($query)) === False) die("MySQL Error:".$this->db->error." on query ".$query);
				
			}
			$row = $result->fetch_assoc();
		}
		$result->free_result();
		
	}
}
	
?>