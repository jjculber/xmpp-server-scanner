<?php

$servers = array();

function getServers($xml_file){
	global $servers;
	
	function handleStartElement($parser,$element,$attrs){
		global $servers;
		if($element=="ITEM"){
			$servers[] = $attrs['JID'];
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



//$serverlist = new serverList();
print_r(getServers("http://www.jabber.org/servers.xml"));