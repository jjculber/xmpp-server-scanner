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

	
	
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
	<head>
		<meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
		<title>Jabber/XMPP Server List</title>
		<style type="text/css">
			body{
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
				text-align: center;
				padding: 2px 4px;
				}
			tt.table_header{
				background: #EEE;
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
			th.name, td.name{
				text-align: left;
				}
			th.times_offline,td.times_offline{
				/*display: none;*/
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
								echo "<th class=\"$field_name\"><a href=\"?sort=$field&amp;order=".($_GET['order']==="desc"?"asc":"desc")."\">".$field_name."</a></th>\n";
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
										echo "\t\t<td class=\"name\">".$row[$field]."</td>\n";
										break;
									case 'times_offline':
										echo "\t\t<td class=\"times_offline\">".$row[$field]."</td>\n";
										break;	
									default:
										echo "\t\t<td>".($row[$field]?"<img src=\"button_ok.png\" width=\"22\" height=\"22\" title=\"Yes\" alt=\"Yes\" />":"<img src=\"button_cancel.png\" width=\"22\" height=\"22\" title=\"No\" alt=\"No\" />")."</td>\n";
								}
						}
						echo "\t</tr>\n";
						$row_number++;
// 					}
						$row = $result->fetch_assoc();
				}
				if($row_number%ROWS_BETWEEN_TITLES!=1){
					echo "\t<tr class=\"table_header\">\n";
					foreach($fields as $field_name) echo "\t\t<th>$field_name</th>\n";
					echo "\t</tr>\n";
					echo "</table>";
				}
				$result->free_result();
				
			?>
		</div>
	</body>
</html>
<?php
	$db->close();
?>