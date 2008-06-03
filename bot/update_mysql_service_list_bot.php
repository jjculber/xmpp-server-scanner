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
 *
 */
 
require_once("config.php");
/* We use config.php
// set your Jabber server hostname, username, and password here
define("JABBER_SERVER","example.org");
define("JABBER_USERNAME","user");
define("JABBER_PASSWORD","pass");
define("MYSQL_SERVER","localhost");
define("MYSQL_USERNAME","user");
define("MYSQL_PASSWORD","pass");
define("MYSQL_DB","server_list");

define("RUN_TIME",7200);	// set a maximum run time of 2 hours
define("CBK_FREQ",60);	// fire a callback event every minute
 */
if(!defined('XML_SERVER_LIST')) define('XML_SERVER_LIST','http://www.jabber.org/servers.xml');

require_once("include/class_database.php");

// include the bot class
require_once("include/class_update_mysql_service_list_bot.php");

// include the Jabber class
require_once("include/class_Jabber_services_Browser.php");


$servers = array();

function getServers($xml_file){
	global $servers;
	
	function handleStartElement($parser,$element,$attrs){
		global $servers;
		if($element=="ITEM"){
			$servers[] = strtolower($attrs['JID']);
		}
}
	if(!($stream = fopen($xml_file,"r"))) die("Can't load the server list");
	$xml_data = stream_get_contents($stream);
	fclose($stream);
	$parser = xml_parser_create();
	xml_set_element_handler($parser, "handleStartElement", False);
	if (!xml_parse($parser,$xml_data,True)) die("Can't parse the server list");
	xml_parser_free($parser);
	
	return array_unique($servers);
}

// create an instance of the Jabber class
//$jab = new Jabber_services_Browser(false);
$jab = new Jabber_services_Browser(true);

//$db = new mysqli ( MYSQL_SERVER, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB );
if(class_exists('mysqli')){
	$db = new mysqliDatabase ( MYSQL_SERVER, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB );
}else{
	$db = new mysqlDatabase ( MYSQL_SERVER, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB );
}

// create an instance of our event handler class
$test = new update_mysql_service_list_bot($jab,$db,getServers(XML_SERVER_LIST));



// set handlers for the events we wish to be notified about
$jab->set_handler("connected",$test,"handleConnected");
$jab->set_handler("authenticated",$test,"handleAuthenticated");
$jab->set_handler("authfailure",$test,"handleAuthFailure");
$jab->set_handler("services_discovered",$test,"handleServicesDiscovered");
$jab->set_handler("service_got_info",$test,"handleServiceInfo");
$jab->set_handler("browseresult",$test,"handleBrowseResult");
$jab->set_handler("heartbeat",$test,"handleHeartbeat");
$jab->set_handler("discardQuery",$test,"handleDiscardedQuery");
$jab->set_handler("error",$test,"handleError");

// connect to the Jabber server
if (!$jab->connect(JABBER_SERVER)) {
	die("Could not connect to the Jabber server!\n");
}
// now, tell the Jabber class to begin its execution loop
$jab->execute(CBK_FREQ,RUN_TIME);

// Note that we will not reach this point (and the execute() method will not
// return) until $jab->terminated is set to TRUE.  The execute() method simply
// loops, processing data from (and to) the Jabber server, and firing events
// (which are handled by our TestMessenger class) until we tell it to terminate.
//
// This event-based model will be familiar to programmers who have worked on
// desktop applications, particularly in Win32 environments.

/* close connection */
$db->close();
// disconnect from the Jabber server
$jab->disconnect();
?>