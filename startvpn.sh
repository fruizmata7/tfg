

while true
do 
   if ifconfig | grep 172.16.1.220
   then 
	: 
   else
	/usr/sbin/vpnc-disconnect
        /usr/sbin/vpnc 

   fi
   sleep 60
done   

