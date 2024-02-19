# -*- coding: utf-8 -*-

def get_temp_sens():
        tfile = open("/sys/bus/w1/devices/28-00000560a4e2/w1_slave")
        text = tfile.read()
        tfile.close()
        secondline = text.split("\n")[1]
        temperaturedata = secondline.split(" ")[9]
        temperature = float(temperaturedata[2:])
        temperature = temperature / 1000
        return float(temperature)

mensaje = str(get_temp_sens()) + " ºC"

print(mensaje)
