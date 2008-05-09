<?php
// 	require_once("bot/config.php");
require_once("bot/include/class_database.php");
define('ROWS_BETWEEN_TITLES',10);
// 	define("MYSQL_SERVER","localhost");
// 	define("MYSQL_USERNAME","user");
// 	define("MYSQL_PASSWORD","password");
// 	define("MYSQL_DB","server_list");
// 	define("MYSQL_TABLE","servers");
// 	define('TIMES_OFFLINE_ALLOWED',5);
	
// If a server has been offline more, we hide or mark it on the list
define('TIMES_OFFLINE_ALLOWED',5);

define("MYSQL_SERVER","localhost");
define("MYSQL_USERNAME","user");
define("MYSQL_PASSWORD","sql_password");
define("MYSQL_DB","server_list");


function write_table_header($types){
	echo "\t<tr class=\"table_header\">";
	echo "<th class='name".(((!$_GET['order'])||($_GET['order']=='name'))?" sortedby":"")."'>";
	echo "<a href='?order=name'>Name</a>";
	echo "</th>";
	foreach($types as $type){
		echo "<th class='$type".(($_GET['order']==$type)?" sortedby":"")."'>";
		echo "<a href='?order=$type'>$type</a>";
		echo "</th>";
// 								echo "<th class=\"$field_name".(($_GET['sort']==$field)?" sortedby":((!isset($_GET['sort']) && ('name'==$field))?" sortedby":""))."\"><a href=\"?sort=$field&amp;order=".((($_GET['order']==="desc")&&($_GET['sort']==$field))||(($field=='name')&&(!(($_GET['sort']==$field)&&($_GET['order']=='asc'))))?"asc":"desc")."\">".$field_name."</a></th>\n";
	}
	echo "<th class='times_offline'>Times Offline</th>";
	echo "</tr>\n";
}


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
	
	if((strstr($_SERVER['HTTP_USER_AGENT'],'Windows')) && (!strstr($_SERVER['HTTP_USER_AGENT'],'Gecko'))){
		$OS = 'WINDOWS';
	}else if(strstr($_SERVER['HTTP_USER_AGENT'],'Linux')){
		$OS = 'LINUX';
	}else if((strstr($_SERVER['HTTP_USER_AGENT'],'Macintosh')) || (strstr($_SERVER['HTTP_USER_AGENT'],'Mac OS X'))){
		$OS = 'MACOSX';
	}else{
		$OS = 'UNKNOWN';
	}
	
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
		<title>Jabber/XMPP Server List</title>
		<style type="text/css">
			body{
				font-family: sans-serif;
				font-size: 0.8em;
				}
			div#header{
				padding: 5px;
				margin:2px auto;
				}
			.note{
				padding: 5px;
				margin:2px auto;
				background: #FFC;
				}
			table{
				border-spacing: 0px;
				/*background: #C4DCFF;*/
				background: #EEE;
				width: 100%;
				}
			td, th{
				vertical-align: middle;
				text-align: center;
				padding: 0px 4px;
				}
			tr.table_header{
				background: #DFDFDF;
				}
			tr.table_header th{
				padding: 2px 4px;
				}
			tr.table_header th:hover{
				background: #EFEFEF;
				}
			tr.table_header th a{
				text-decoration: none;
				font-weight: normal;
				color: #0000AA;
				}
			tr.table_header th a:hover{
				text-decoration: underline;
				}
			tr.odd/* td*/{
				background:#EBF4FF;
				}
			tr.even/* td*/{
				background:#FFF;
				}
			tr.offline/* td*/{
				font-style: italic;
				background:#FFD4D4;
				}
			tr.table_header th.name, td.name{
				text-align: left;
				padding: 6px 4px;
				}
			tr.table_header th.sortedby{
				background: #CFCFCF;
				}
			tr.table_header th.sortedby a{
				font-weight: bolder;
				font-size: 1em;
/* 				background: #FAFAFA; */
				color: #0000FF;
				}
			th.times_offline,td.times_offline{
				/*display: none;*/
			}
			td.feature{
/* 				font-size: 2em; */
			}
			td.no{
				color: #E90900;/*firebrick;*/
			}
			.available{
				color: #00DA00;/*green;*/
			}
			.unavailable{
				color: #808080;/*grey;*/
			}
			tr.odd td.sortedby{
				background: #DCE5EF;
			}
			tr.even td.sortedby{
				background: #EFEFEF;
			}
			div.components span{
				display: block;
				font-size: 60%;
			}
		</style>
	</head>
	<body>
		<div id="container">
			<div id="header">
				<div id="title"><h2>Jabber/<abbr title="eXtensible Messaging and Presence Protocol">XMPP</abbr> Server List</h2></div>
				<div class="note">If the service Jabber ID is from a domain different that the server, it will be ignored.</div>
				<div class="note">Greyed icons mean that those services aren't accessible from external servers. Most times that indicates that they are only available for users of that server.</div>
			</div>
			<?php
				
				/* Query types
				 * They will be fetched in the order in wich pybot putted them there
				*/
				$query = "SELECT type FROM pybot_service_types";
				
				$query = $db->real_escape_string($query);
				if(($result = $db->query($query)) === False) die('MySQL Error: '.$db->error());
				
				$types_row = $result->fetch_assoc();
				
				$types = array();
				while(!is_null($types_row)){
					$types[] = $types_row['type'];
					$types_row = $result->fetch_assoc();
				}
				
				$result->free_result();
				
				//$types=array()
				
				$query = "SELECT ".
							"pybot_servers.jid AS server_jid, ".
							"pybot_servers.times_offline AS server_times_offline, ".
							"pybot_components.jid AS component_jid, ".
							"pybot_components.type AS component_type, ".
							"pybot_components.available AS component_available ".
						"FROM pybot_servers LEFT JOIN pybot_components ".
							"ON (pybot_servers.jid = pybot_components.server_jid) ".
						"ORDER BY ".
							"server_jid ASC, ".
							"component_type ASC, ".
							"component_available DESC, ".
							"component_jid ASC";
				
				if(($servers_result = $db->query($query)) === False) die('MySQL Error: '.$db->error());
				
				$server_row = $servers_result->fetch_assoc();
				
				echo "<table>\n";
				$row_number = 0;
				while(!is_null($server_row)){
					
					$server_data = array();
					$server_data['jid'] = $server_row['server_jid'];
					$server_data['times_offline'] = $server_row['server_times_offline'];
					$server_data['services'] = array();
					
					if(!is_null($server_row['component_jid'])){
						while((!is_null($server_row)) && ($server_data['jid'] == $server_row['server_jid'])){
							$server_data['services'][$server_row['component_type']][] = array(
								'jid' => $server_row['component_jid'],
								'available' => (boolean) $server_row['component_available']
							);
							$server_data['components'][$server_row['component_type']][] = $server_row['component_jid'];
							$server_row = $servers_result->fetch_assoc();
						}
					}else{
						$server_row = $servers_result->fetch_assoc();
					}
					
// 					if($servers_data['times_offline']<TIMES_OFFLINE_ALLOWED){
						if($row_number%ROWS_BETWEEN_TITLES == 0){
							write_table_header($types);
						}
						
// 						echo "<tr class='".(($row_number%2)==1?"odd":"even")."'>";
						if($server_data['times_offline']>TIMES_OFFLINE_ALLOWED){
							$class = "offline";
						}else{
							if(($row_number%2)==1){
								$class = "odd";
							}else{
								$class = "even";
							}
						}
						echo "\t<tr class='$class'>\n";
						
						
						echo "\t\t<td class='name".(((!$_GET['order'])||($_GET['order']=='name'))?" sortedby":"")."'>";
						echo "<a name='".htmlspecialchars($server_data['jid'])."'>".htmlspecialchars($server_data['jid'])."</a>";
						echo "</td>\n";
						foreach($types as $type){
							
							
							if(!array_key_exists($type, $server_data['services'])){
								// The server doesn't provide this service
								echo "\t\t<td class='feature no ".$type.(($_GET['order']==$type)?" sortedby":"")."'>";
								echo "</td>\n";
							}else{
							
								if($server_data['services'][$type][0]['available']){
									echo "\t\t<td class='feature yes available ".$type.(($_GET['order']==$type)?" sortedby":"")."'>";
									switch($type){
										case 'muc':
											echo "<img src=\"images/irc_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'irc':
											echo "<img src=\"images/irc_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'aim':
											echo "<img src=\"images/aim_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'gg':
											echo "<img src=\"images/gadu_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'icq':
											echo "<img src=\"images/icq_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'msn':
											echo "<img src=\"images/msn_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'sms':
											echo "<img src=\"images/sms.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'yahoo':
											echo "<img src=\"images/yahoo_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'jud':
											echo "<img src=\"images/directory.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'newmail':
											echo "<img src=\"images/email.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'rss':
											echo "<img src=\"images/feed-icon-16x16.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'weather':
											echo "<img src=\"images/weather.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										default:
											echo "<img src=\"images/button_ok.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
									}
									//echo "</td>\n";
								}else{
									// Unavailable service
									// i.e. error 404 due a bad DNS configuration)
									echo "\t\t<td class='feature yes unavailable ".$type.(($_GET['order']==$type)?" sortedby":"")."'>";
									switch($type){
										case 'muc':
											echo "<img src=\"images/irc_protocol-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'irc':
											echo "<img src=\"images/irc_protocol-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'aim':
											echo "<img src=\"images/aim_protocol-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'gg':
											echo "<img src=\"images/gadu_protocol-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'icq':
											echo "<img src=\"images/icq_protocol-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'msn':
											echo "<img src=\"images/msn_protocol-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'sms':
											echo "<img src=\"images/sms-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'yahoo':
											echo "<img src=\"images/yahoo_protocol-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'jud':
											echo "<img src=\"images/directory-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'newmail':
											echo "<img src=\"images/email-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'rss':
											echo "<img src=\"images/feed-icon-16x16-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										case 'weather':
											echo "<img src=\"images/weather-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
										default:
											echo "<img src=\"images/button_ok-grey.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
											break;
									}
									//echo "</td>\n";
								} // if service available
								
							// Print components
								echo "\n";
								echo "\t\t\t<div class='components'>";
								foreach($server_data['services'][$type] as $component){
									if($component['available']){
										echo "<span class='available'>".$component['jid']."</span>";
									}else{
										echo "<span class='unavailable'>".$component['jid']."</span>";
									}
								}
								echo "</div>";
								echo "</td>\n";
							} // if service provided
							
						} // foreach type
						echo "\t\t<td class=\"times_offline\">".$server_data['times_offline']."</td>\n";
						
						
						echo "\t</tr>\n";
						$row_number++;
// 					} // if times_offline < TIMES_OFFLINE_ALLOWED
					
				} // foreach server
				
				// The last header
				if($row_number%ROWS_BETWEEN_TITLES!=1){
					write_table_header($types);
				}
				
				echo "</table>";
				
				$servers_result->free_result();
			?>
		</div>
	</body>
</html>
<?php
	$db->close();
?>