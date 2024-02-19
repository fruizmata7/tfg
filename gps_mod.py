import gps

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

if __name__ == "__main__":
    latitud, longitud = obtener_coordenadas_gps()
    print(f"Coordenadas GPS - Latitud: {latitud}, Longitud: {longitud}")
