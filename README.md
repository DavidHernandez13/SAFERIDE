# SAFERIDE - Sistema Inteligente de Seguridad para Ciclistas
--------------------------------------------------------------
## Integrantes del equipo
- Aguilar Figueroa José Miguel
- Liceaga Hernández Angel Baruc
- Ibarra Muñoz Jose Francisco
- Zacarias Hernández Angel David
---
## Objetivo del programa
Desarrollar un sistema integral de seguridad para ciclistas urbanos mediante un casco inteligente equipado con sensores (MPU6050, GPS, LDR), actuadores (buzzer, Led) Pantalla OLED y una cámara con visión artificial (ESP32-CAM). El sistema detecta impactos, distracciones y baja iluminación, enviando alertas en tiempo real a un dashboard web a través de Firebase y MQTT.

---

## Componentes del proyecto

| Componente          | Función                                        |
|---------------------|------------------------------------------------|
| ESP32               | Microcontrolador principal del casco           |
| ESP32-CAM           | Captura de imágenes y visión en tiempo real    |
| MPU6050             | Detección de impactos y caídas                 |
| GPS NEO-6M          | Geolocalización en tiempo real                 |
| Sensor LDR          | Monitoreo de luz ambiental                     |
| LED                 | Indicador visual de poca luz                   |
| Buzzer Pasivo       | Alertas sonoras                                |
| Pantalla OLED 0.96" | Telemetría y estado del sistema                |
| Firebase Realtime Database | Almacenamiento en nube y sincronización |
| Mosquitto MQTT      | Comunicación entre componentes                 |

---

## Arquitectura del sistema
ESP32 Principal (Casco) ──(MQTT)──→ Broker Mosquitto ──(MQTT)──→ Python Bridge ──→ Firebase
│ │ │
│ │ ↓
│ │ Dashboard Web
│ │
ESP32-CAM ───────────────(MQTT)──────→┤
│ │
└──────────────(MQTT)──────────→ Python IA (Detección)
└──(MQTT)──→ Broker (alarma)


---

## Estructura de Firebase
{
  "estado": {
    "online": 1
  },
  "estado_ciclista": {
    "accidente": false,
    "distraccion": false,
    "baja_iluminacion": false
  },
  "ubicacion": {
    "Latitud": 21.109705,
    "Longitud": 101.627620
  },
  "sensores": {
    "LDR": {
      "raw": 1843,
      "porcentaje": 45
    }
  },
  "logs": {
    "eventos": {
      "-Nkf7gH3": {
        "tipo": "ACCIDENTE",
        "mensaje": "Impacto detectado",
        "timestamp": 1712345678
      }
    }
  }
}


Funcionalidades implementadas
ESP32 Principal (Casco)

Conexión WiFi y MQTT

Detección de impactos mediante MPU6050

Activación de buzzer y pantalla OLED al detectar impacto

Lectura de GPS y publicación de coordenadas

Detección de baja iluminación con LDR

Recepción de alertas de distracción por MQTT

Pantalla OLED con estado, coordenadas y alertas prioritarias

Envío periódico de telemetría cada 5 segundos

Procesamiento en paralelo con múltiples hilos

ESP32-CAM

Captura de imágenes cada 2.5 segundos

Envío de imágenes por MQTT

Servidor MJPEG para video en vivo

Python IA

Procesamiento de imágenes con MobileNetV2 (TensorFlow)

Detección de objetos como "cellular_telephone"

Publicación de alertas en tópico MQTT

Python Bridge

Suscripción a tópicos MQTT

Escritura en Firebase Realtime Database

Dashboard Web
Video en vivo de la ESP32-CAM

Monitoreo de GPS con enlace a Google Maps

Tarjetas de estado (Seguro, Distracción, Accidente, Baja iluminación)

Barra porcentual del nivel de luz

Historial de eventos con timestamps

Enlaces

Repositorio GitHub: https://github.com/DavidHernandez13/SAFERIDE

Firebase Console: https://sistemas-programables-71bb0-default-rtdb.firebaseio.com/

Fecha de entrega

11 de Junio de 2026

Instituto Tecnológico de León
Ingeniería en Sistemas Computacionales
Sistemas Programables
Docente: Verónica Tapia

SAFERIDE - Sistema Inteligente de Seguridad para Ciclistas
© 2026
