<?php
/* This set of classes give a common interface for mysqli and mysql
 *
 * Copyright 2007, noalwin <lambda512@gmail.com> <xmpp:lambda512@jabberes.org>
 *
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
 */

abstract class abstractDatabase{
	
	public function __construct($host, $user, $password, $database){
		$this->connect($host, $user, $password, $database);
	}
	
	abstract function connect($host, $user, $password, $database);
	
	abstract function ping();
	
	abstract function error();
	
	abstract function query($query);
	
	abstract function real_escape_string($query);
	
	abstract function close();
	
}

abstract class abstractResult{
	
	abstract function fetch_assoc();
	
	abstract function free_result();
	
}

class mysqliDatabase extends abstractDatabase{
	
	private $db;
	
	public function __construct($host, $user, $password, $database){
		parent::__construct($host, $user, $password, $database);
	}
	
	public function connect($host, $user, $password, $database){
		$this->db = new mysqli($host, $user, $password, $database);
				
		/* check connection */
		if (mysqli_connect_errno()) {
			printf("Connect failed: %s\n", mysqli_connect_error());
			exit();
		}
		
		return $this->db;
	}
	
	public function ping(){
		return $this->db->ping();
	}
	
	public function error(){
		return $this->db->error;
	}
	
	public function query($query){
		$result = $this->db->query($query);
		if($result){
			return new mysqliResult($result);
		}else{
			return False;
		}
	}
	
	public function real_escape_string($query){
		return $this->db->real_escape_string($query);
	}
	
	public function close(){
		return $this->db->close();
	}
	
}

class mysqlDatabase extends abstractDatabase{
	
	private $db;
	
	public function __construct($host, $user, $password, $database){
		parent::__construct($host, $user, $password, $database);
	}
	
	public function connect($host, $user, $password, $database){
		
		$this->db = mysql_connect($host, $user, $password);
		
		/* check connection */
		if (mysql_errno()) {
			printf("Connect failed: %s\n", mysql_error());
			exit();
		}
		
		if(!mysql_select_db($database)) die('Could not select database');
		
		return $this->db;
	}
	
	public function ping(){
		return mysql_ping($this->db);
	}
	
	public function error(){
		return mysql_error($this->db);
	}
	
	public function query($query){
		$result = mysql_query($query,$this->db);
		if($result){
			return new mysqlResult($result);
		}else{
// 			die("MySQL Error: ".mysql_error($this->db));
			return False;
		}
	}
	
	public function real_escape_string($query){
		return mysql_real_escape_string($query,$this->db);
	}
	
	public function close(){
		return mysql_close($this->db);
	}
	
}


class mysqliResult extends abstractResult{
	
	private $result;
	
	public function __construct($result){
		$this->result = &$result;
	}
	
	public function fetch_assoc(){
		$row = $this->result->fetch_assoc();
		if($row){
			return $row;
		}else{
			return NULL;
		}
	}
	
	public function free_result(){
		return $this->result->free_result();
	}
	
}


class mysqlResult extends abstractResult{
	
	private $result;
	
	public function __construct($result){
		$this->result = &$result;
	}
	
	public function fetch_assoc(){
		$row = mysql_fetch_assoc($this->result);
		if($row){
			return $row;
		}else{
			return NULL;
		}
	}
	
	public function free_result(){
		return mysql_free_result($this->result);
	}
	
}

?>