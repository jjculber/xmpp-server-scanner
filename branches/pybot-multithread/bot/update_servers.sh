#!/bin/sh
cd /clientes/jabberes/servers/bot
#Use local file until web file gets more complete
#wget -qN http://www.jabber.org/basicservers.xml -O servers.xml
time php /clientes/jabberes/servers/bot/update_mysql_service_list_bot.php | tee /clientes/jabberes/servers/bot/log 