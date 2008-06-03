<?php
	require_once("bot/config.php");
	require_once("bot/include/class_database.php");
	define('ROWS_BETWEEN_TITLES',10);
// 	define("MYSQL_SERVER","localhost");
// 	define("MYSQL_USERNAME","user");
// 	define("MYSQL_PASSWORD","password");
// 	define("MYSQL_DB","server_list");
// 	define("MYSQL_TABLE","servers");
// 	define('TIMES_OFFLINE_ALLOWED',5);
	
	$fields = array('name' => 'name', 'has_muc' => 'muc', 'has_irc' => 'irc', 'has_aim' => 'aim', 'has_gg' => 'gg', 'has_httpws' => 'http-ws', 'has_icq' => 'icq', 'has_msn' => 'msn', 'has_qq' => 'qq', 'has_sms' => 'sms', 'has_smtp' => 'smtp', 'has_tlen' => 'tlen', 'has_yahoo' => 'yahoo', 'has_jud' => 'jud', 'has_pubsub' => 'pubsub', 'has_pep' => 'pep', 'has_presence' => 'presence', 'has_newmail' => 'newmail', 'has_rss' => 'rss', 'has_weather' => 'weather', 'has_proxy' => 'proxy', 'times_offline' => 'times offline');
	
	
// 	$db = new mysqli ( MYSQL_SERVER, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB );
// 	
// 	/* check connection */
// 	if (mysqli_connect_errno()) {
// 		printf("Connect failed: %s\n", mysqli_connect_error());
// 		exit();
// 	}
		
	if(class_exists('mysqli')){
		$db = new mysqliDatabase ( MYSQL_SERVER, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB );
	}else{
		$db = new mysqlDatabase ( MYSQL_SERVER, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DB );
	}

	$query = "SELECT * FROM ".MYSQL_TABLE." ORDER BY name ASC";
	
	$query = $db->real_escape_string($query);
	if(($result = $db->query($query)) === False) die('MySQL Error: '.$db->error());
	
	$document = new DOMDocument('1.0','utf-8');
	$servers = $document->createElement('servers');
	$servers = $document->appendChild($servers);
	
	$row = $result->fetch_assoc();
	
	while(!is_null($row)){
// 					if($row['times_offline']<TIMES_OFFLINE_ALLOWED){
		$server = $document->createElement('server');
		$server->setAttribute('name',htmlspecialchars($row['name']));
		$server->setAttribute('times_offline',$row['times_offline']);
// 						echo "<tr class='".(($row_number%2)==1?"odd":"even")."'>";
		if($row['times_offline']>TIMES_OFFLINE_ALLOWED){
			$server->setAttribute('offline','True']);
		}else{
			$server->setAttribute('offline','False');
		}
		
		foreach($fields as $field => $field_name){
			switch($field){
				case 'name':
					break;
				case 'times_offline':
					break;	
				default:
					$server = $document->createElement('server');
					$server = $document->appendChild($server);
								//	echo "\t\t<td>".($row[$field]?"<img src=\"button_ok.png\" width=\"22\" height=\"22\" title=\"Yes\" alt=\"Yes\" />":"<img src=\"button_cancel.png\" width=\"22\" height=\"22\" title=\"No\" alt=\"No\" />")."</td>\n";
										if($row[$field]){
											echo "\t\t<td class=\"feature yes ".$field."\">";
											switch($OS){
												default:
													echo "<img src=\"button_ok.png\" width=\"22\" height=\"22\" title=\"Yes\" alt=\"Yes\" />";
													break;
											}
											echo "</td>\n";
										}else{
											echo "\t\t<td class=\"feature no ".$field."\">";
											switch($OS){

											}
											echo "</td>\n";
										}
								}
						}
						echo "\t</tr>\n";
						$row_number++;
// 					}
						$row = $result->fetch_assoc();
				}
				if($row_number%ROWS_BETWEEN_TITLES!=1){
					echo "\t<tr class=\"table_header\">\n";
					foreach($fields as $field_name){
						echo "<th class=\"$field_name\"><a href=\"?sort=$field&amp;order=".($_GET['order']==="desc"?"asc":"desc")."\">".$field_name."</a></th>\n";
					}
					echo "\t</tr>\n";
				}
				echo "</table>";
				$result->free_result();
					echo $document->saveXML();
	$db->close();
?>