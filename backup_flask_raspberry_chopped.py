# CODE FER #

#import sys
#import time
import Adafruit_DHT
from time import sleep

from flask import *
app = Flask(__name__)

# Init GPIO
#import RPi.GPIO as GPIO
#GPIO.setwarnings(False)
#GPIO.cleanup()
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.OUT) # PIN 4 -> 1WIRE OUTPUT

sensor = Adafruit_DHT.DHT22 


# DHT22 sensor connected to GPIO 4 (BCM MODE)
pin = 4
#print("[press ctrl+c to end the script]")  

# Definimos las rutas
@app.route('/')
def homepage():
   print('OK')
   return render_template('webfer.html')

# Definimos las rutas de la web corporativa del trabajo
@app.route('/tfg_fer/')
def tfg_fer():
   return render_template('tfg_fer.html')

# Definimos las rutas de la pagina secundaria de luces
@app.route('/luces/')
def luces():
   return render_template('luces.html')

# Definimos las rutas de la pagina secundaria de agua
@app.route('/agua/')
def agua():
   return render_template('agua.html')



# Definimos las rutas de la pagina de temperaturas
@app.route('/temperatura/')
def temperatura():
   
   humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
   #sleep(10) # segundos de refresco.

   #
   #try: # Main program loop

   #while True:
      #humidity, temperature = Adafruit_DHT.read_retry(sensor, pin) 
      #sleep(2.5) # segundos de refresco.

      #if humidity is not None and temperature is not None:
      # print("Temp = {0:0.1f} ºC Humidity = {1:0.1f} %" .format(temperature, humidity)) 

      #else:
      # print("Failed to get reading. Try again!")

   # Scavenging work after the end of the program 

#except KeyboardInterrupt:
#print("end")

   return render_template('temperatura.html', tmp=f"{temperature:0.001f}", hmt=f"{humidity:0.0001f}")


# Inicializamos el servidor flask
if __name__ == '__main__':
   app.run(host='192.168.137.208', port=5000, debug=True)
   #Cambiar IP según uso: 172.20.10.12 // 127.0.0.1 // 0.0.0.0 // 192.168.137.77
   # micasita´s IP: 172.16.1.210 -> broadcast micasita: 172.16.1.255
   # 


