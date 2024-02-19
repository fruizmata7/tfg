
# CODE FER #

import os
import glob
import json
import requests
import Adafruit_DHT
from time import sleep
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import telegram
import gps
from flask import Flask, render_template, request, jsonify, redirect
import math
import socket
import threading
import time
app = Flask(__name__)
bot = Bot(token="6184291140:AAEAFnh1Sp_UWsAELaEnSHQPsgchLloRrKQ")
# Secondaty bot = Bot(token="6261635132:AAGl4Cs9uclSPBtbBqvRr0xN288GpxB5S6w")
dp = Dispatcher(bot)

# DHT22 sensor connected to GPIO 4 (BCM MODE)
sensor = Adafruit_DHT.DHT22
delta_temp = 0
pin1 = 4
print("[press ctrl+c to end the script]")  

def obtener_ip_local():
    while True:
        try:
            # Crear un socket UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))  # Conectarse a un servidor externo arbitrario
            ip_local = sock.getsockname()[0]  # Obtener la dirección IP local
            sock.close()
            return ip_local
        except socket.error:
            continue

# MENSAJE TELEGRAM
def enviar_mensaje_telegram(mensaje, chat_id):
   asyncio.run(bot.send_message(chat_id=chat_id, text=mensaje))

# DEFINICION DE ALARMAS:
alarma_sonando = False

current_location = None  # Ubicación actual del coche
alarm_active = False  # Variable para controlar si la alarma está activada
last_alarm_time = 0  # Variable para registrar el tiempo de la última alarma

@app.route('/start-tracking')
def start_tracking():
    global current_location, alarm_active
    # Obtener la ubicación actual del coche (simulada)
    current_location = obtener_coordenadas_gps()  # Define la latitud y longitud del coche
    alarm_active = True  # Activar la alarma
    # Iniciar un hilo para verificar la alarma continuamente
    alarm_thread = threading.Thread(target=check_alarm)
    alarm_thread.start()
    return '', 204  

@app.route('/stop-tracking')
def stop_tracking():
    global alarm_active
    alarm_active = False  # Desactivo alamra
    return '', 204  # Respuesta vacía con código 204

    # Detengo el hilo de la alarma si está en ejecución
    for thread in threading.enumerate():
        if thread.name == 'alarm_thread':
            thread.join()  # Mato hilo


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

def check_alarm():
    global current_location, alarm_active
    if current_location:
        # Coordenadas del centro del radio de 500m
        center_lat, center_lon = current_location
        # Coordenadas de la ubicación actual del coche
        car_lat, car_lon = current_location
        # Calcular la distancia entre las coordenadas
        distance = calculate_distance(center_lat, center_lon, car_lat, car_lon)
        # Si la distancia es mayor a 500m y la alarma está activada, enviar una alerta
        if distance > 500 and alarm_active:
            enviar_mensaje_telegram("¡El coche ha salido del radio de 500m!",'5938316291')
            alarm_active = False
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


base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temperature_c = float(temp_string) / 1000.0
        return temperature_c

alarm_triggered = False
def read_temp_continuously(interval):
    global alarm_triggered  

    while True:
        temperature = read_temp()
        print("Temperature: {:.2f} °C".format(temperature))
        
        if temperature <= 23 and not alarm_triggered:
            alarm_message = "¡Alarma! La temperatura es de {:.2f} °C.".format(temperature)
            print(alarm_message)
            enviar_mensaje_telegram(alarm_message,'2114374143')
            #enviar_mensaje_telegram(alarm_message,'5938316291')
            alarm_triggered = True  #Active
            time.sleep(10)        
        if temperature >= 24 and alarm_triggered:
            alarm_triggered = False  # Reset
        
        time.sleep(interval)

# Intervalo de tiempo entre cada lectura de temperatura en segundos
interval_seconds = 30

temp_thread = threading.Thread(target=read_temp_continuously, args=(interval_seconds,))
temp_thread.daemon = True  # Hacer que el hilo sea un demonio para que se detenga cuando el programa principal termine
temp_thread.start()

# Definimos las rutas de homepage
@app.route('/')
def homepage():
   print('TODO OK. Bienvenido.')
   user_agent = request.headers.get('User-Agent')
   print(user_agent + ' .\n')
    
   if 'mobile' in user_agent.lower() or 'Mobile' in user_agent:
      # Redirigir a la página para dispositivos móviles
      return render_template('home_tfg_fer_mobile.html')
   else:
      # Redirigir a la página para ordenadores
      return render_template('home_tfg_fer_desktop.html')
# HOMEPAGE

@app.route('/reboot/')
def reboot_system():
   os.system('sudo reboot')



@app.route('/gps/')
def get_gps_data():
   latitud, longitud = obtener_coordenadas_gps()
   return render_template('gps.html', latitude=latitud, longitude=longitud)


@app.route('/luces/', methods = ['POST', 'GET'])
def luces():
   with open('data.json', 'r') as file:
        data = json.load(file)
   ip_dispositivo = data['data'][0]['relay'][0]['ip']
   channel = data['data'][0]['relay'][0]['channel']
   return redirect(f"http://{ip_dispositivo}")
# Definimos las rutas de la pagina secundaria de agua
@app.route('/agua/')
def agua():
   return render_template('agua.html')

# Definimos las rutas de la pagina secundaria de temperaturas
@app.route('/temperatura/')
def temperatura():
   humidity1, temperature1 = Adafruit_DHT.read_retry(sensor, pin1)
   #temperature3 = Adafruit_DHT.read_retry(sensor3, pin3)
   temperature3 = read_temp()
   if temperature1 is not None or humidity1 is not None or temperature3:

   # CONECTAR TERMOMETROS

   # Empezar con el 1: Yellow/Blue/Green
   # Conectar en orden:

   # Conectar el 2: Grey/White/Black
   # Conectar en orden:

   # Conectar el 3: ___/___/___
   # Conectar en orden:
   # random temp3

       return render_template('temperatura.html', tmp1=f"{temperature1:0.001f}", hmt1=f"{humidity1:0.0001f}",tmp3=f"{temperature3:0.0001f}")


# Definimos las rutas de la pagina secundaria de alarmas.
# Configuramos la creacion de la variable de alarma.
@app.route('/alarmas/')
def alarmas():
   if delta_temp  >= 20:
		# Condicion para encender la alarma.
      activar_alarma()

   activar_alarma()  # Activar la alarma
   if alarma_sonando:
      mensaje = "La temperatura exterior es extrema. ¡CUIDADO!"
      chat_id = "2114374143"  # Reemplaza con el ID del chat al que deseas enviar el mensaje
      enviar_mensaje_telegram(mensaje, chat_id)
   desactivar_alarma()  # Desactivar la alarma
   return render_template('alarmas.html')

# Definimos las rutas de la pagina secundaria de ajustes.
@app.route('/ajustes/')
def ajustes():
    if request.method == 'GET':
        # Cargar datos actuales del JSON
        with open('data.json', 'r') as file:
            data = json.load(file)
        return render_template('ajustes.html', data=data)
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
   local_IP = obtener_ip_local()
   app.run(host=local_IP, port=5000, debug=True)

# APAGAR EL DEBUG DE app.run!!! debug=False

#Cambiar IP según uso: 172.20.10.6 // 127.0.0.1 // 0.0.0.0 // 192.168.137.77
# micasita´s IP: 172.16.1.210 -> broadcast micasita: 172.16.1.255

