#!/bin/sh
cd /clientes/jabberes/servers/bot
wget -qN http://www.jabber.org/servers.xml
time php /clientes/jabberes/servers/bot/update_mysql_service_list_bot.php | tee /clientes/jabberes/servers/bot/log 
