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
	
	$fields = array('name' => 'Name', 'has_muc' => 'MUC', 'has_irc' => 'IRC', 'has_aim' => 'AIM', 'has_gg' => 'GG',/* 'has_httpws' => 'http-ws',*/ 'has_icq' => 'ICQ', 'has_msn' => 'MSN',/* 'has_qq' => 'QQ',*/ 'has_sms' => 'SMS', 'has_smtp' => 'SMTP', 'has_tlen' => 'TLEN', 'has_yahoo' => 'Yahoo', 'has_jud' => 'JUD', 'has_pubsub' => 'PubSub', 'has_pep' => 'PEP', 'has_presence' => 'WebPresence', 'has_newmail' => 'NewMail', 'has_rss' => 'RSS', 'has_weather' => 'Weather', 'has_proxy' => 'Transfer Proxy', 'times_offline' => 'Times Offline');
	
	
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
				background: #DAF2DA;
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
				<?php 
// 					switch($OS){
// // 						case 'WINDOWS':
// // 							echo 'font-family: Webdings;';
// // 							break;
// // 						case 'LINUX':
// // 							echo 'font-family: "DejaVu Sans";';
// // 							break;
// // 						case 'MACOSX':
// // 							echo 'font-family: Webdings;';
// // 							break;
// 						default:
// 							echo "height: 26px;";
// // 							echo 'font-family: webdings;';
// 							break;
// 					}
				?>
			}
			td.no{
				color: #E90900;/*firebrick;*/
			}
			td.yes{
				color: #00DA00;/*green;*/
			}
		</style>
	</head>
	<body>
		<div id="container">
			<div id="header">
				<div id="title"><h2>Jabber/<abbr title="eXtensible Messaging and Presence Protocol">XMPP</abbr> Server List</h2></div>
				<div class="note">If the service Jabber ID is from a domain different that the server, it will be ignored</div></div>
			<?php
				
				$query = "SELECT * FROM ".MYSQL_TABLE." ";
				foreach($_GET as $parameter => $value){
					if((isset($fields[$parameter])) && (($value === "False") || ($value === "True"))){
						if($where_condition == ""){
							$query .= "WHERE ";
						}else{
							$query .= "AND ";
						}
						$query .= "$parameter=$value ";
					}
				}
				
				if(isset($fields[$_GET['sort']])){
					$query .= "ORDER BY ".$_GET['sort']." ";
					if($_GET['order'] === "desc"){
						$query .= "DESC ";
					}else{
						$query .= "ASC ";
					}
					$query .= ", name ASC ";
				}else{
					$query .= " ORDER BY name ASC";
				}
				
				$query = $db->real_escape_string($query);
				if(($result = $db->query($query)) === False) die('MySQL Error: '.$db->error());
				
				echo "<table>\n";
// 				echo "\t<tr class=\"table_header\">\n";
// 				foreach($fields as $field => $field_name) echo "\t\t<th class=\"$field\">$field_name</th>\n";
// 				echo "\t</tr>\n";
				$row = $result->fetch_assoc();
				
				
				$row_number = 0;
				while(!is_null($row)){
// 					if($row['times_offline']<TIMES_OFFLINE_ALLOWED){
						if($row_number%ROWS_BETWEEN_TITLES==0){
							echo "\t<tr class=\"table_header\">\n";
							foreach($fields as $field => $field_name){
// 								switch($field){
// 									case 'name':
// 										echo "\t\t<th class=\"name\">".$field_name."</th>\n";
// 										break;
// 									case 'times_offline':
// 										echo "\t\t<th class=\"times_offline\">".$field_name."</th>\n";
// 										break;	
// 									default:
// 										echo "<th>".$field_name."</th>";
// 								}
								echo "<th class=\"$field_name".(($_GET['sort']==$field)?" sortedby":((!isset($_GET['sort']) && ('name'==$field))?" sortedby":""))."\"><a href=\"?sort=$field&amp;order=".((($_GET['order']==="desc")&&($_GET['sort']==$field))||(($field=='name')&&(!(($_GET['sort']==$field)&&($_GET['order']=='asc'))))?"asc":"desc")."\">".$field_name."</a></th>\n";
							}
							echo "\t</tr>\n";
						}
// 						echo "<tr class='".(($row_number%2)==1?"odd":"even")."'>";
						if($row['times_offline']>TIMES_OFFLINE_ALLOWED){
							$class = "offline";
						}else{
							if(($row_number%2)==1){
								$class = "odd";
							}else{
								$class = "even";
							}
						}
						echo "\t<tr class='$class'>\n";
						foreach($fields as $field => $field_name){
								switch($field){
									case 'name':
										echo "\t\t<td class=\"name\"><a name=\"".htmlspecialchars($row[$field])."\"></a>".htmlspecialchars($row[$field])."</td>\n";
										break;
									case 'times_offline':
										echo "\t\t<td class=\"times_offline\">".htmlspecialchars($row[$field])."</td>\n";
										break;	
									default:
// 										echo "\t\t<td>".($row[$field]?"<img src=\"images/button_ok.png\" width=\"22\" height=\"22\" title=\"Yes\" alt=\"Yes\" />":"<img src=\"images/button_cancel.png\" width=\"22\" height=\"22\" title=\"No\" alt=\"No\" />")."</td>\n";
										if($row[$field]){
											echo "\t\t<td class=\"feature yes ".$field."\">";
// 											switch($OS){
// 												case 'WINDOWS':
// 													echo 'a';
// 													break;
// 												case 'LINUX':
// 													echo '✔';
// 													break;
// 												case 'MACOSX':
// 													echo 'a';
// 													break;
// 												default:
// 													echo "<img src=\"images/button_ok.png\" width=\"22\" height=\"22\" title=\"Yes\" alt=\"Yes\" />";
// 													break;
// 											}
											switch($field){
												case 'has_muc':
													echo "<img src=\"images/irc_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_irc':
													echo "<img src=\"images/irc_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_aim':
													echo "<img src=\"images/aim_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_gg':
													echo "<img src=\"images/gadu_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_icq':
													echo "<img src=\"images/icq_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_msn':
													echo "<img src=\"images/msn_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_sms':
													echo "<img src=\"images/sms.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_yahoo':
													echo "<img src=\"images/yahoo_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_jud':
													echo "<img src=\"images/directory.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_newmail':
													echo "<img src=\"images/email.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_rss':
													echo "<img src=\"images/feed-icon-16x16.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
												case 'has_weather':
													echo "<img src=\"images/weather.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
// 												case 'has_msn':
// 													echo "<img src=\"images/msn_protocol.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
// 													break;
												default:
													echo "<img src=\"images/button_ok.png\" width=\"16\" height=\"16\" title=\"Yes\" alt=\"Yes\" />";
													break;
											}
											echo "</td>\n";
										}else{
											echo "\t\t<td class=\"feature no ".$field."\">";
// 											switch($OS){
// 												case 'WINDOWS':
// 													echo 'r';
// 													break;
// 												case 'LINUX':
// 													echo '✘';
// 													break;
// 												case 'MACOSX':
// 													echo 'r';
// 													break;
// 												default:
// 													echo "<img src=\"images/button_cancel.png\" width=\"22\" height=\"22\" title=\"No\" alt=\"No\" />";
// 													break;
// 											}
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
						echo "<th class=\"$field_name".(($_GET['sort']==$field)?" sortedby":"")."\"><a href=\"?sort=$field&amp;order=".((($_GET['order']==="desc")&&($_GET['sort']==$field))&&($_GET['sort']==$field)?"asc":"desc")."\">".$field_name."</a></th>\n";
					}
					echo "\t</tr>\n";
				}
				echo "</table>";
				$result->free_result();
				
			?>
		</div>
	</body>
</html>
<?php
	$db->close();
?>