# Configuración de Mosquitto

## Objetivo

Mosquitto funciona como broker MQTT para la comunicación entre el ESP32, ESP32-CAM, los módulos de procesamiento y el dashboard del sistema SafeRide.

## Inicio del servicio

En Windows ejecutar:

```cmd
"C:\Program Files\mosquitto\mosquitto.exe" -c "C:\Program Files\mosquitto\mosquitto.conf" -v
```

## Puerto utilizado

```
1883
```

## Dirección del broker

La dirección IP deberá corresponder al equipo donde se encuentra ejecutándose Mosquitto.

Ejemplo:

```
172.20.10.14
```

## Función dentro del proyecto

- Recepción de telemetría del ESP32.
- Recepción de imágenes desde ESP32-CAM.
- Distribución de alertas de accidente y distracción.
- Comunicación con el módulo Bridge y la Inteligencia Artificial.
