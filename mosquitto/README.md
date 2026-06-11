# Configuración de Mosquitto

Para iniciar el broker MQTT en Windows ejecutar:

```cmd
"C:\Program Files\mosquitto\mosquitto.exe" -c "C:\Program Files\mosquitto\mosquitto.conf" -v
```

Puerto utilizado:

```
1883
```

El ESP32-CAM debe apuntar a la IP del servidor MQTT:

```
172.20.10.14
```
