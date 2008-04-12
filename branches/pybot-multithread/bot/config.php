<?php
// set your Jabber server hostname, username, and password here
// define("JABBER_SERVER","host.example.com");
// define("JABBER_USERNAME","xxx");
// define("JABBER_PASSWORD","passwd");
// define("JABBER_RESOURCE","servicebot2-nexus");

// set your Jabber server hostname, username, and password here
define("JABBER_SERVER","server12.example.com");
define("JABBER_USERNAME","a_user");
define("JABBER_PASSWORD","the_password");
define("JABBER_RESOURCE","servicebot-nexus");

define("RUN_TIME",14400);	// set a maximum run time of 4 hours (40 minutes should be sufficient)
define("CBK_FREQ",2);	// fire a callback event every second

// define('XML_SERVER_LIST','http://www.jabber.org/basicservers.xml');
define('XML_SERVER_LIST','servers.xml');
// If a server has been offline more, we hide or mark it on the list
define('TIMES_OFFLINE_ALLOWED',5);
//Maximun simultaneous querys, if it's big it can saturate the server obtaining errors 404
//We didn't start to discover another server if there are more querys
define("MAX_SIMULTANEOUS_QUERYS",10);

// Default iq query timeout
define("QUERY_TIMEOUT",60);// seconds (some servers are very slow)
// Times to retry a query that hasn't been answered in QUERY_TIMEOUT seconds
define('RETRYS_IF_DISCARDED',3);

// set your MySQL server hostname, username, ........ here
// define("MYSQL_SERVER","localhost");
// define("MYSQL_USERNAME","user");
// define("MYSQL_PASSWORD","sql_password");
// define("MYSQL_DB","server_list");
// define('MYSQL_TABLE','servers');

// set your MySQL server hostname, username, ........ here
define("MYSQL_SERVER","localhost");
define("MYSQL_USERNAME","dbuser");
define("MYSQL_PASSWORD","dbpassword");
define("MYSQL_DB","xmpp_servers");
define('MYSQL_TABLE','servers');

?>