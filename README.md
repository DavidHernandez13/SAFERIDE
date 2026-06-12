# SAFERIDE - Sistema Inteligente de Seguridad para Ciclistas

## Integrantes del equipo

* Aguilar Figueroa José Miguel
* Liceaga Hernández Ángel Baruc
* Ibarra Muñoz José Francisco
* Zacarias Hernández Angel David

---

## Información general

**Institución:** Tecnológico Nacional de México - Campus León
**Carrera:** Ingeniería en Sistemas Computacionales
**Materia:** Sistemas Programables
**Docente:** Verónica Tapia
**Periodo:** Enero - Junio 2026

---

# Objetivo del proyecto

SafeRide es un sistema inteligente diseñado para incrementar la seguridad de los ciclistas mediante el uso de sensores, visión artificial y comunicación en tiempo real.

El proyecto integra un ESP32 como controlador principal y una ESP32-CAM para el monitoreo visual del entorno, permitiendo detectar accidentes, condiciones de baja iluminación y posibles distracciones del usuario. Toda la información es enviada mediante MQTT y almacenada en Firebase Realtime Database para su visualización en un dashboard web.

---

# Tecnologías utilizadas

* ESP32
* ESP32-CAM
* Arduino IDE
* Firebase Realtime Database
* Mosquitto MQTT
* Python
* TensorFlow / MobileNetV2
* HTML
* CSS
* JavaScript

---

# Componentes del sistema

| Componente                 | Descripción                                 |
| -------------------------- | ------------------------------------------- |
| ESP32                      | Controlador principal del casco inteligente |
| ESP32-CAM                  | Captura y transmisión de imágenes           |
| MPU6050                    | Detección de impactos y aceleraciones       |
| GPS NEO-6M                 | Obtención de coordenadas geográficas        |
| Sensor LDR                 | Medición del nivel de iluminación           |
| LED                        | Indicador visual de baja iluminación        |
| Buzzer                     | Generación de alertas sonoras               |
| Pantalla OLED              | Visualización del estado del sistema        |
| Firebase Realtime Database | Almacenamiento de información en la nube    |
| Mosquitto MQTT             | Comunicación entre dispositivos             |

---

# Arquitectura del sistema

```
                    Dashboard Web
                          │
                          │
             Firebase Realtime Database
                          │
                          │
                Python Bridge / Backend
                          │
                          │
               Broker MQTT (Mosquitto)
                  ┌────────┴────────┐
                  │                 │
                  │                 │
            ESP32 Principal     ESP32-CAM
                  │                 │
      MPU6050 - GPS - LDR - OLED    Cámara
                  │                 │
                  └────── Inteligencia Artificial ──────┘
```

---

# Estructura del repositorio

```
SAFERIDE/
│
├── HAL/
│   ├── ESP32/
│   ├── ESP32-CAM/
│   └── Firebase/
│
├── Servidor/
│   └── Mosquitto/
│
├── Interfaz/
│
└── README.md
```

---

# Funcionalidades implementadas

## ESP32 Principal

* Conexión a red WiFi.
* Comunicación mediante MQTT.
* Lectura del acelerómetro y giroscopio MPU6050.
* Obtención de coordenadas GPS.
* Detección de baja iluminación mediante LDR.
* Activación de LED y buzzer.
* Visualización de información en pantalla OLED.
* Envío periódico de datos hacia Firebase.

## ESP32-CAM

* Captura automática de imágenes.
* Streaming de video mediante HTTP (MJPEG).
* Envío de imágenes utilizando MQTT.
* Recepción de alertas remotas.
* Activación del buzzer.

## Inteligencia Artificial

* Procesamiento de imágenes.
* Detección de objetos de distracción.
* Generación de alertas mediante MQTT.

## Dashboard Web

* Visualización del video en tiempo real.
* Monitoreo de ubicación GPS.
* Estado del ciclista.
* Nivel de iluminación.
* Historial de eventos.
* Consulta de alertas registradas.

---

# Instalación de dependencias

## Dependencias de Python

Instalar todas las dependencias necesarias mediante:

```bash
pip install -r requirements.txt
```

El archivo `requirements.txt` debe incluir las librerías utilizadas por el proyecto.

## Librerías para ESP32

* WiFi.h
* TinyGPSPlus.h
* PubSubClient.h
* Wire.h
* Adafruit_GFX.h
* Adafruit_SSD1306.h
* MPU6050.h

## Librerías para ESP32-CAM

* esp_camera.h
* WiFi.h
* PubSubClient.h
* WebServer.h

---

# Configuración de Mosquitto

Para iniciar el broker MQTT en Windows ejecutar:

```cmd
"C:\Program Files\mosquitto\mosquitto.exe" -c "C:\Program Files\mosquitto\mosquitto.conf" -v
```

Puerto utilizado:

```
1883
```

La dirección IP del broker deberá configurarse dentro de los dispositivos ESP32 según la red local utilizada.

---

# Ejecución del sistema

1. Iniciar el servicio Mosquitto.
2. Programar el ESP32 principal.
3. Programar la ESP32-CAM mediante Arduino IDE.
4. Configurar las credenciales locales de Firebase.
5. Ejecutar el módulo Bridge y el procesamiento de Inteligencia Artificial.
6. Abrir el Dashboard Web desde un navegador.
7. Verificar la comunicación entre MQTT, Firebase y los dispositivos.

---

# Firebase Realtime Database

La base de datos almacena información relacionada con:

* Estado del sistema.
* Estado del ciclista.
* Coordenadas GPS.
* Información de sensores.
* Historial de eventos.
* Alertas generadas por el sistema.

La estructura general utilizada es:

```
estado
estado_ciclista
logs
sensores
ubicacion
```

---

# Seguridad

Por motivos de seguridad, las credenciales del proyecto (`credentials.json`) y cualquier archivo que contenga claves privadas o información sensible no se incluyen en este repositorio.

Cada desarrollador deberá configurar sus propias credenciales para establecer la conexión con Firebase y los demás servicios utilizados por el proyecto.

---

# Repositorio

https://github.com/DavidHernandez13/SAFERIDE

---

# Licencia

Este proyecto fue desarrollado con fines académicos para la asignatura de Sistemas Programables del Tecnológico Nacional de México - Campus León durante el periodo Enero - Junio 2026.
Fecha de entrega

11 de Junio de 2026

SAFERIDE © 2026
