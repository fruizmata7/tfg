# CODE FER #

#import sys
#import time

# CHECKPOINT BORRAR CUANDO FUNCIONE TERMOMETRO
import random

import requests
#import Adafruit_DHT
from time import sleep
import asyncio
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import telegram
#from flask import *
from flask import Flask, render_template, request

app = Flask(__name__)
bot = Bot(token="6184291140:AAEAFnh1Sp_UWsAELaEnSHQPsgchLloRrKQ")
dp = Dispatcher(bot)

# DHT22 sensor connected to GPIO 4 (BCM MODE)
#sensor1 = Adafruit_DHT.DHT22 
#sensor2 = Adafruit_DHT.DHT22 
#sensor3 = Adafruit_DHT.DHT22 

delta_temp = 0
contador = 0
pin1 = 4
pin2 = 5
pin3 = 14
print("[press ctrl+c to end the script]")  

# def my_ip():
#    global ip
#    while True:
#       try:
#          #ip = get('https://ip4.seeip.org').text
#          ip = '31.4.157.33'
#       except:
#          print("Algo fue mal.")
#    print("Todo OK.")

# MENSAJE TELEGRAM
def enviar_mensaje_telegram(mensaje, chat_id):
   asyncio.run(bot.send_message(chat_id=chat_id, text=mensaje))

# DEFINICION DE ALARMAS:
alarma_sonando = False

def activar_alarma():
   global alarma_sonando
   # Código para activar la alarma
   # # ...
   # # Después de activar la alarma, establece alarma_sonando en True
   alarma_sonando = True

def desactivar_alarma():
   global alarma_sonando
   # Código para desactivar la alarma
   # ...
   # Después de desactivar la alarma, establece alarma_sonando en False
	# Estado inicial de la alarma.
   alarma_sonando = False

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


# Definimos las rutas de la pagina secundaria de luces
@app.route('/luces/')
def luces():
   return render_template('luces.html')

# Definimos las rutas de la pagina secundaria de agua
@app.route('/agua/')
def agua():
   return render_template('agua.html')

# Definimos las rutas de la pagina secundaria de temperaturas
@app.route('/temperatura/')
def temperatura():
   #if contador < 5:
   contador = 4
   
   humidity1 = 1
   humidity2 = 2
   temperature1 = 0
   temperature2 = 2
   temperature3 = 35

   #humidity1, temperature1 = Adafruit_DHT.read_retry(sensor1, pin1)
   #humidity2, temperature2 = Adafruit_DHT.read_retry(sensor2, pin2)
   #temperature3 = Adafruit_DHT.read_retry(sensor3, pin3)


   if temperature1 != 'NULL':
      print("Failed to get reading. Try again! (temperature1).")
      temperature1 = 0
	  
   if temperature2 != 'NULL':
      print("Failed to get reading. Try again! (temperature2).")
      temperature2 = 0
	  
   if temperature3 != 'NULL':
      print("Failed to get reading. Try again! (temperature3).")
      temperature3 = 0
	  
   # CONECTAR TERMOMETROS

   # Empezar con el 1: Yellow/Blue/Green
   # Conectar en orden:

   # Conectar el 2: Grey/White/Black
   # Conectar en orden:

   # Conectar el 3: ___/___/___
   # Conectar en orden:
   temperature3 = random.randint(30, 45)
   temperature1 = 17
   
   # Configuramos la creacion de la variable de alarma.
   if temperature1 != 'NULL' or temperature3 != 'NULL':
      delta_temp = abs(temperature3 - temperature1)
      # Comprobamos que haga mucho calor, y tambien mucho frio.


   # Comprobamos alarma:
   if delta_temp  >= 20:
		# Condicion para encender la alarma.
      contador += 1
      activar_alarma()
   
   print("\n delta_temp {}.".format(delta_temp))
   print("\n contador {}.".format(contador))
   
   mensaje = "¡CUIDADO! La temperatura exterior es extrema. Hace {} grados.".format(temperature3)
   chat_id = "2114374143"  # Reemplaza con el ID del chat al que deseas enviar el mensaje

   if alarma_sonando:
      str(delta_temp)
      print("\n ALAMRMA con delta_temp {}.\n".format(delta_temp))
      if (delta_temp  >= 20) and ((contador % 5)==0):
         enviar_mensaje_telegram(mensaje, chat_id)
   desactivar_alarma()  # Desactivar la alarma
   
   return render_template('temperatura.html', tmp1=f"{temperature1:0.001f}", tmp2=f"{temperature2:0.001f}", tmp3=f"{temperature3:0.001f}", hmt1=f"{humidity1:0.0001f}", hmt2=f"{humidity2:0.0001f}")


# Definimos las rutas de la pagina secundaria de alarmas.
@app.route('/alarmas/')
def alarmas():
   return render_template('alarmas.html')

# Definimos las rutas de la pagina secundaria de ajustes.
@app.route('/ajustes/')
def ajustes():
   return render_template('ajustes.html')

# Definimos las rutas de la pagina secundaria de ajustes.
@app.route('/info_caravan/')
def info_caravan():
   return render_template('info_caravan.html')


# Inicializamos el servidor flask
if __name__ == '__main__':
   app.run(host='0.0.0.0', port=80, debug=True)

# APAGAR EL DEBUG DE app.run!!! debug=False

#Cambiar IP según uso: 172.20.10.12 // 127.0.0.1 // 0.0.0.0 // 192.168.137.77
# micasita´s IP: 172.16.1.210 -> broadcast micasita: 172.16.1.255
