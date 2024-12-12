# CODE FER # 03/12/2024.
# /home/pi/TFG/final f_r_c.py - FINAL VERSION
import os
import glob
import json
import requests
import subprocess
from time import sleep
import asyncio
import math
import socket
import threading
import time
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import telegram
from flask import Flask, render_template, request, jsonify, redirect

try:
    import Adafruit_DHT
except ImportError as e:
    print("Error importing Adafruit_DHT library:")
    print(e)
    
try:
    import gps
except ImportError as e:
    print("Error importing gps library:")
    print(e)

app = Flask(__name__)

# DHT22 sensor connected to GPIO 4 (BCM MODE)
sensor = Adafruit_DHT.DHT22
delta_temp = 0.0
last_temp = 0.0
pin1 = 4
debug_rele_check = False
flag_reboot = False
flag_turnoff = False

# Leer configuración desde telegram_bot.txt
def read_config(file_path):
    config = {}
    try:
        # Comprobamos que la ruta es correcta
        with open(file_path, 'r') as file:
            for line in file:
                key, value = line.strip().split('=', 1)
                config[key] = value
    except FileNotFoundError:
        print(f"El archivo {file_path} no se encontró.")
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
    return config

config = read_config('telegram_bot.txt')

# Obtener el token del bot y el chat ID desde el archivo de configuración
bot_token = config.get('bot_token')
chat_id = config.get('chat_id')

# Inicializar el bot de Telegram
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

def clearmsg (file):  
    # Borra el contenido del fichero y deja solo las ultimas 3 lineas
    f = open(file,"r+") # Open for update AT THE BEGINNING, does not delete.
    d = f.readlines()
    if len(d) >= 4: start = len(d) - 4
    else: start = 0
    f.seek(0) 
    i=0
    for line in d: 
        if i >= start :
            f.write(line)
        i += 1 
    d= []
    f.truncate() 
    f.close() 
    return ('{} lineas borradas'.format(start))
    

def writemsg (text):
    try:
        f = open("alarmamsg.txt","a") # Open for update AT THE END, does not delete.
        f.write(text + " \n ")
        f.close()
    except Exception as e:
       print(e)
       print('Error escribiendo mensaje en archivo "alarmamsg.txt".')

# FUNCION MENSAJE DE TELEGRAM
def enviar_mensaje_telegram(chat_id, mensaje):
    try:
    # THREAD FUNCION MENSAJE DE TELEGRAM
    #    msg_interval_secs = 10
    #    msg_thread = threading.Thread(target=enviar_mensaje_telegram, args=(msg_interval_secs,))
    #    msg_thread.daemon = True  # Hilo demonio para que se detenga cuando el programa principal termine
    #    msg_thread.start()
        asyncio.run(bot.send_message(chat_id=chat_id, text=mensaje))
    except KeyboardInterrupt:
        print("Programa terminado por el usuario.")
    except Exception as e:
       print(e)
       print('Error enviando Telegram')

# Función para verificar credenciales y mandar notificación por Telegram
def init_correcto():
    global flag_turnoff, flag_reboot

    if flag_reboot:
        print('REINICIO COMPLETADO.')

    if bot_token and chat_id:
        try:
            print('Iniciando el sistema...')
            sleep(10)
            # Intentar enviar un mensaje para verificar el bot_token
            enviar_mensaje_telegram(chat_id, 'Chat ID y TOKEN correctos. Programa iniciado.')
            writemsg('Chat ID y TOKEN correctos. Programa iniciado.')
            print('Chat ID y TOKEN correctos.')
        except Exception as e:
            print('ERROR: No se ha podido enviar el mensaje de Telegram.')
            print('Chat ID y TOKEN correctos.')
            print(e)
    else:
        if not bot_token:
            print('ERROR: BOT TOKEN INCORRECTO.')
            print(e)
        if not chat_id:
            print('ERROR: Chat ID INCORRECTO.')
            print(e)

# Verificar credenciales y notificar al iniciar el programa
init_correcto()

print("[--- Press Ctrl + C to end the script ---]")

# Leer configuración desde data.json
def read_devices_config(file_path):
    try:
        with open(file_path, 'r') as file:
            config = json.load(file)
            return config.get('data', [])
    except FileNotFoundError:
        print(f"El archivo {file_path} no se encontró.")
        return []
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        return []

# Obtener la configuración de los dispositivos desde data.json
devices = read_devices_config('data.json')

# Inicializar la lista de dispositivos como "No conectado". Despues los conectados
# se actualizarán a True, el resto de dispositivos se mantendrán en False.
for device in devices:
    device["conectado"] = False
    device["retries"] = 0

# Definimos la funcion del relé
def rele_shelly (device, action):
    #print (device) #comentario de control
    json_datos = '{}'
    my_session = requests.session()
    if debug_rele_check:
        print ('rele_Shelly {} {}'.format(device, action))
    
    if (action == 'on') or (action == 'off'):
        url = 'http://{}/relay/0?turn={}'.format(device, action)
        if debug_rele_check:
            print(url)
        try:
            r = my_session.post(url, data = json_datos, timeout = 1)
            if debug_rele_check:
                print(r)
        except:
            print ('ERROR de conexion {} a {}'.format(action,device))
            return 'ERROR de conexion con Rele Shelly {}'.format(device)
        return (action)
    elif action == 'get':
        url = 'http://{}/relay/0'.format(device)
        if debug_rele_check:
            print(action)
            print(url)
        try:
            r = my_session.get(url, timeout = 1.5)
            if debug_rele_check:
                print (r)
                print ("***")
                print (r.text)
            r = json.loads(r.text)
            r = r['ison']
            if debug_rele_check:
                print ('Shelly {} = {}'.format(device, r))
            if r:
                return ('on')
            else:
                return ('off')
        except:
            print ('ERROR de conexion {} {}'.format(action, url))
            return 'ERROR de conexion'
    else:
        return 'ERROR parametro incorrecto Rele Shelly'

# Intento de obtener direccion IP local mediante DNS de Google
# def obtener_ip_local():
#     tries = 5
#     while tries > 0:
#         try:
#             # Crear un socket UDP
#             sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#             sock.connect(("8.8.8.8", 80))  # Conectarse a un servidor externo arbitrario
#             ip_local = sock.getsockname()[0]  # Obtener la dirección IP local
#             sock.close()
#             return ip_local
#         except Exception as e:
#             print(f"Error al obtener la IP local: {e}")
#             tries -= 1
#             time.sleep(1)
#             return '0.0.0.0'

# DEFINICION DE ALARMAS:
alarma_sonando = False
current_location = None  # Ubicación actual del coche
alarm_active = False  # Variable para controlar si la alarma está activada
last_alarm_time = 0  # Variable para registrar el tiempo de la última alarma


# Comienzo de localizacion
@app.route('/start-tracking')
def start_tracking():
    global current_location, alarm_active
    # Obtener la ubicación actual del coche (simulada)
    current_location = obtener_coordenadas_gps()  # Define la latitud y longitud del coche
    writecoord = str(current_location)
    alarm_active = True  # Activar la alarma
    print('Seguimiento activado en coordenadas:')
    print(current_location)
    try:
        f = open("location.txt","w") # Open for update AT THE END, does not delete.
        f.write(writecoord)
        f.close()
    except Exception as e:
       print(e)
       print('Error escribiendo mensaje en archivo "location.txt".')
    # Iniciar un hilo para verificar la alarma continuamente
    alarm_thread = threading.Thread(target=check_alarm)
    alarm_thread.start()
    return '', 204  

# Fin de localizacion
@app.route('/stop-tracking')
def stop_tracking():
    global alarm_active
    alarm_active = False  # Desactivo alamra
    try:
        f = open("location.txt","r+") # Open for update AT THE END, does not delete.
        f.seek(0)
        f.truncate()
        f.close()
    except Exception as e:
       print(e)
       print('Error desactivando localización en "location.txt".')
    return '', 204  # Respuesta vacía con código 204

    # Detengo el hilo de la alarma si está en ejecución
    for thread in threading.enumerate():
        if thread.name == 'alarm_thread':
            thread.join()  # Mato hilo


# Calcular distancia
def calculate_distance(lat1, lon1, lat2, lon2):
    # Convertir grados a radianes
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Radio de la tierra en metros
    R = 6371000

    # Diferencias de latitud y longitud
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Fórmula de Haversine
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Decisión de mensaje
def check_alarm():
    global current_location, alarm_active
    while True:
        archivoalarma = current_location
        try:
            with open("alarmamsg.txt", "r") as archivo_msg:
                archivoalarma = archivo_msg.read() # Aquí leo el archivo
        except Exception as e:
            print(e)
            print("Error leyendo fichero de mensajes de alarma.")

        if current_location:
            # Coordenadas del centro del radio de 500m
            center_lat, center_lon = current_location
            # Coordenadas de la ubicación actual del coche
            car_lat, car_lon = current_location
            # Calcular la distancia entre las coordenadas
            distance = calculate_distance(center_lat, center_lon, car_lat, car_lon)
            # Si la distancia es mayor a 500m y la alarma está activada, enviar una alerta
            if distance > 500 and alarm_active:
                current_location = archivoalarma
                enviar_mensaje_telegram(chat_id, "¡El vehículo ha salido del radio de 500 mtr!")
                writemsg("¡El vehículo ha salido del radio de 500 mtr!")
                alarm_active = False
        time.sleep(10)  # Espera 10 segundos antes de volver a comprobar

# Localizacion gps
def obtener_coordenadas_gps():
    sesion_gps = gps.gps(mode=gps.WATCH_ENABLE)
    try:
        while True:
            reporte = sesion_gps.next()
            if reporte['class'] == 'TPV':
                if hasattr(reporte, 'lat') and hasattr(reporte, 'lon'):
                    latitud = reporte.lat
                    longitud = reporte.lon
                    return latitud, longitud
    except KeyboardInterrupt:
        print("Programa terminado por el usuario.")
    finally:
        sesion_gps.close()


# PROCESAR TEMPERATURA
def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        try:
            temperature_c = float(temp_string) / 1000.0
            return temperature_c
        except ValueError:
            print("Error al convertir la temperatura a float.")
            # Aquí podríamos actuar ante un error de conversión de temperatura.
            return 0.0


# CONFIGURACION DE LA ALARMA DE TEMPERATURA
alarm_triggered = False
def read_temp_continuously(interval):
    global alarm_triggered
    global last_temp
    global alarma_sonando

    while True:
        # Lectura Sonda
        base_dir = '/sys/bus/w1/devices/'
        try:
            for device_folder in glob.glob(base_dir + '28*'):
                device_file = device_folder + '/w1_slave'
                temperature = read_temp(device_file)
                last_temp = temperature
        except Exception as e:
            print(e)
            print(device_folder)
            print ("Error obteniendo device_file.")
            device_file = ''
        print("Temperature (tmp3): {:.2f} °C".format(temperature))
        
        # Comprobación de alarma de temperatura
        try:
            if temperature <= 10 and not alarm_triggered:
                alarma_sonando = True
                alarm_message = "¡HACE FRÍO! La temperatura es de {:.2f} °C.".format(temperature)
                activar_alarma(alarm_message)
                alarm_triggered = True  #Active
                time.sleep(10)

            if temperature >= 30:
                alarma_sonando = True
                alarm_message = "Hace calor, la temperatura es de {:.2f} °C.".format(temperature)
                activar_alarma(alarm_message)
            else:
                alarm_triggered = False # Reset
                alarma_sonando = False # Reset
        except Exception as e:
            print(e)
        
        time.sleep(interval)


# Lectura de info del termómetro
def read_temp_raw(device_file):
    if os.path.exists(device_file):    
            # try
        f = open(device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    else:
        lines = ''

# Intervalo de tiempo entre cada lectura de temperatura en segundos
temp_interval_secs = 30

temp_thread = threading.Thread(target=read_temp_continuously, args=(temp_interval_secs,))
temp_thread.daemon = True  # Hilo demonio para que se detenga cuando el programa principal termine
temp_thread.start()

# Definimos las rutas de homepage
@app.route('/')
def homepage():
    global flag_reboot, flag_turnoff

    if flag_reboot == True:
        # CHECKPOINT
        os.system('sudo reboot')
        subprocess.run("sudo reboot", shell=True, check=True)
    
    if flag_turnoff == True:
        os.system('sudo shutdown -h now')
        subprocess.run("sudo shutdown -h now", shell=True, check=True)

    print('-------------------------------')
    print('TODO OK. Bienvenido a homepage.')
    print('-------------------------------')
    user_agent = request.headers.get('User-Agent')

    if 'mobile' in user_agent.lower() or 'Mobile' in user_agent:
        # Redirigir a la página para dispositivos móviles
        return render_template('home_tfg_fer_mobile.html')
    else:
        # Redirigir a la página para ordenadores
        return render_template('home_tfg_fer_desktop.html')
# HOMEPAGE

# Definimos la ruta para reiniciar el sistema - init 6
@app.route('/reboot/')
def reboot_system():
    global flag_reboot
    flag_reboot = True
    f = open('reboot', "w")
    f.write('REINICIADO')
    f.close()
    return redirect('/', code=302)
    
# Definimos la ruta para apagar el sistema - init 0
@app.route('/turnoff/')
def turnoff_system():
    global flag_turnoff
    flag_turnoff = True
    return redirect('/', code=302)
    
# Definimos la ruta de la página secundaria de gps
@app.route('/gps/')
def get_gps_data():
    latitud, longitud = obtener_coordenadas_gps()
    print('Latitud  / longitud actual: {},{}'.format(latitud, longitud))
    return render_template('gps.html', latitude=latitud, longitude=longitud)


# Definimos las rutas de la pagina secundaria de luz
@app.route('/luces/', methods = ['POST', 'GET'])
def luces():
    with open('data.json', 'r') as file:
        data = json.load(file)
    relays_info = []
    
    for relay in data['data'][0]['relay']:
        device = relay['ip']
        ifon = rele_shelly(device, 'get')
        if ifon == 'on':
            boton_rele = 'Apagar'
            status_rele = 'Encendido'
        elif ifon == 'off':
            boton_rele = 'Encender'
            status_rele = 'Apagado'
        else:
            boton_rele = '---'
            status_rele = 'Desconectado'
        
        relays_info.append({
            'id': relay['id'],
            'status_rele': status_rele,
            'boton_rele': boton_rele,
            'ip': relay['ip']
        })
    ip_system = data['data'][0]['system'][0]['ip']
    return render_template('luces.html', relays_info=relays_info, ip_system=ip_system)


# Definimos las rutas de la pagina que cambia el estado de las luces.
@app.route('/luces_toggel_button/', methods = ['POST', 'GET'])
def luces_toggel_button():
    # device = request.form
    for k, v in request.form.items(): # Como no saco los valores, saco las claves. (IP)
        device = k
        print ('Petición de {} .'.format(device))
        x = rele_shelly(device, 'get')
        if x == 'on':
            rele_shelly(device, 'off')
        else:
            rele_shelly(device, 'on')
    return redirect('/luces/', code=302)

# Definimos las rutas de la pagina que elimina los mensajes de alarma antiguos.
@app.route('/reloadalarmas/', methods = ['POST', 'GET'])
def reloadalarmas():
    clearmsg("alarmamsg.txt")
    return redirect('/alarmas/', code=302)

# Definimos las rutas de la pagina secundaria de agua
@app.route('/agua/')
def agua():
    return render_template('agua.html')

# Definimos las rutas de la pagina secundaria de temperaturas
@app.route('/temperatura/')
def temperatura():
    global last_temp
    global delta_temp
    humidity1, temperature1 = Adafruit_DHT.read_retry(sensor, pin1) # Obtencion dato termómetro
    temperature3 = last_temp # Obtencion dato sonda
    # print(temperature3)
    # print(temperature1)
    # print(humidity1)

    # Comprobación termómetro
    if temperature1 is None:
        if humidity1 is None:
            print("---- ERROR 1 ----")
            print("hmt1 no recargado / temp1 no recargado")
            enviar_mensaje_telegram(chat_id, "No se ha cargado htm1 ni tmp1 correctamente.")
            writemsg("No se ha cargado htm1 ni tmp1 correctamente.")
            temperature1 = float(0.0)
            humidity1 = float(0.0)
        else:
            print("---- ERROR 2 ----")
            print("tmp1 no recargado")
            enviar_mensaje_telegram(chat_id, "No se ha cargado tmp1 correctamente.")
            writemsg("No se ha cargado tmp1 correctamente.")
            temperature1 = 0.0
    else:
        if humidity1 is None:
            print("---- ERROR 3 ----")
            print("hmt1 no recargado")
            enviar_mensaje_telegram(chat_id, "No se ha cargado htm1 correctamente.")
            writemsg("No se ha cargado htm1 correctamente.")
            humidity1 = 0.0

    # Comprobación sonda
    if temperature3 is None:
        print("temp3 no recargado.")
        enviar_mensaje_telegram(chat_id, "Carga de temp3 incorrecta.")
        writemsg("Carga de temp3 incorrecta.")

    delta_temp = abs(temperature1 - temperature3)
    
    if delta_temp  >= 15:
    # Condicion para encender la alarma.
        print(delta_temp)
        alarma_sonando = True
        mensaje = "La temperatura exterior es extrema. ¡CUIDADO!."
        activar_alarma(mensaje)

    return render_template('temperatura.html', tmp1=f"{temperature1:0.02f}", hmt1=f"{humidity1:0.02f}",tmp3=f"{temperature3:0.02f}")



# Configuramos la creacion de la variable de alarma.
def activar_alarma(msg):  # Activar la alarma
    if alarma_sonando:
        enviar_mensaje_telegram(chat_id, msg)
        writemsg(msg)
#    desactivar_alarma()  # Desactivar la alarma


# Definimos las rutas de la pagina secundaria de alarmas.
@app.route('/alarmas/')
def alarmas():
    filecont = ""
    try:
        with open("alarmamsg.txt", "r") as archivo_msg:
            filecont = archivo_msg.read() # Aquí leo el archivo
        filecont = filecont.replace('\n', '<br>')
    except Exception as e:
        print(e)
        print("Error leyendo fichero de mensajes de alarma.")
        filecont = "No se ha podido leer el fichero de mesajes de alerta."
    return render_template('alarmas.html', filecont = filecont)

# Definimos las rutas de la pagina secundaria de ajustes.
@app.route('/ajustes/')
def ajustes():
    if request.method == 'GET':
        # Cargar datos actuales del JSON
        with open('data.json', 'r') as file:
            data = json.load(file)
        ip_dispositivo = data['data'][0]['relay'][0]['ip']
        return render_template('ajustes.html', data=data, ip_dispositivo=ip_dispositivo)
    elif request.method == 'POST':
        # Obtener datos del formulario
        ip_relay = request.form['ip_relay']
        ip_system = request.form['ip_system']
        # Actualizar datos en el JSON
        with open('data.json', 'r+') as file:
            data = json.load(file)
            data['data'][0]['relay'][0]['ip'] = ip_relay
            data['data'][0]['system'][0]['ip'] = ip_system
            file.seek(0)
            json.dump(data, file, indent=4)
            file.truncate()
        # Redirigir a la página de ajustes
        return redirect('/ajustes/')

# Definimos las rutas de la pagina secundaria de ajustes.
@app.route('/info_caravan/')
def info_caravan():
   return render_template('info_caravan.html')

# Inicializamos el servidor flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

# APAGAR EL DEBUG DE app.run!!! debug=False
# Cambiar IP según uso: 172.20.10.120 / Empezamos programa en 0.0.0.0 para evitar errores.

# FIN DEL CÓDIGO.
