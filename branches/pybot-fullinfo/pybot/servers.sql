



CREATE TABLE pybot_servers (
	jid VARCHAR(255) NOT NULL UNIQUE,
	offline_since DATETIME DEFAULT NULL,
	times_queried_online INT UNSIGNED NOT NULL,
	times_queried INT UNSIGNED NOT NULL,
	PRIMARY KEY (jid)
) ENGINE=InnoDB;


CREATE TABLE pybot_service_types (
	type VARCHAR(255) NOT NULL UNIQUE,
	PRIMARY KEY (type)
) ENGINE=InnoDB;


CREATE TABLE pybot_components (
	jid VARCHAR(255) NOT NULL,
	server_jid VARCHAR(255) NOT NULL,
	type VARCHAR(255) NOT NULL,
	available BOOLEAN NOT NULL,
	-- Add ther server_jid due the service.localhost components
	PRIMARY KEY (jid, server_jid),
	FOREIGN KEY (server_jid) REFERENCES pybot_servers (jid)
	    ON DELETE CASCADE ON UPDATE CASCADE,
	FOREIGN KEY (type) REFERENCES pybot_service_types (type)
	    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB;
