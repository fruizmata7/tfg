README.txt
TFG FERNANDO RUIZ MATALLANOS.
" Diseño de sistema embarcado de monitorización de vehículos basado en ordenadores monoplaca "

Para que este trabajo se ejecute de manera correcta, es necesario que se sigan los siguientes pasos en la RPi en la que se ejecutará el sistema. Para empezar, es necesario descargar este código y todas las librerías necesarias para ejecutarlo. La manera de colocar correcta y jerárquicamente el código es la siguiente:

- En la ruta /etc/ de la RPi, el fichero rc.local debe ser el encargado de mandar la orden de ejecutar el script de Python, por lo que deberá tener los permisos necesarios para poder ejecutar este archivo. Las instrucciones se encuentran en el apartado de configuración del capítulo 4.

- Posteriormente, en la ruta /home/pi/ crearemos la carpeta raíz del trabajo y la llamaremos tfg. Desde aquí gestionaremos todo el proyecto. Esta carpeta consta de:
    · Una subcarpeta llamada static con otro directorio dentro llamado images que contiene todas las imágenes añadidas (/home/pi/static/images/).
    · Una subcarpeta llamada templates con todas las plantillas (HTML) que se muestran por pantalla mediante llamadas desde Python. Aquí encontramos agua.html, ajustes.html, alarmas.html, gps.html, home_tfg_fer_desktop.html, home_tfg_fer_mobile.html, info_caravan.html, luces.html y temperatura.html (/home/pi/templates/).
    · Un fichero llamado start.sh que es el encargado de ejecutar el script que inicia nuestro script de python.
    · Un fichero llamado startvpn.sh que es el encargado de ejecutar el script que inicia nuestra VPN.
    · Un fichero llamado telegram_bot.txt del cual se estraerán los datos necesarios para el correcto funcionamiento de la API de Telegram (Chat ID y Bot Token).
    · Un fichero llamado data.json en el cual se guardan las direcciones IP de los relés y del sistema.
    · Un fichero llamado msgs.log donde se guardan los mensajes que salen por pantalla en el terminal durante la ejecución.
    · Un fichero llamado alarmamsg.txt donde se guardan los mensajes de alarma que se reciben a través de Telegram durante la ejecución.
    · El código ejecutable de Python que gestiona todo lo demás llamado flask_raspberry_chopped.py.

- Una vez se han descargado y ordenado todos estos archivos en la RPi, se puede ejecutar el código simplemente accediendo a la ruta /home/pi/tfg y ejecutando el comando:
$ python3 flask_raspberry_chopped.py

De esta manera, el programa enseñará los mensajes por el terminal además de guardarlos en msgs.log. Para que el código se cargue y ejecute de manera automática, en vez de ejecutarlo manualmente, simplemente reiniciaremos la RPi con el comando $ sudo reboot ( o $ sudo init 6).

Muchas gracias por su atención.
