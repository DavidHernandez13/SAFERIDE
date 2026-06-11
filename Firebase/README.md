# Firebase - SafeRide

## Descripción

Esta carpeta contiene la configuración y documentación relacionada con la integración de **Firebase Realtime Database** 
utilizada por el proyecto *SafeRide*.

Firebase es el encargado de almacenar y sincronizar en tiempo real la información enviada por el sistema, como el estado del ciclista,
sensores, ubicación GPS y registros de eventos.

---

## Estructura de la Base de Datos

La base de datos está organizada de la siguiente manera:

```text
/
├── estado
│   └── online
│
├── estado_ciclista
│   ├── accidente
│   └── baja_iluminacion
│
├── logs
│   └── eventos
│
├── sensores
│   └── LDR
│       ├── porcentaje
│       └── raw
│
└── ubicacion
    ├── latitud
    └── longitud
```

Esta estructura puede ampliarse conforme se agreguen nuevos sensores o funcionalidades al sistema.

---

## Configuración

Para que la aplicación funcione correctamente es necesario configurar:

* Credenciales del proyecto Firebase.
* URL de la Realtime Database.
* Permisos y reglas de acceso.
* Configuración de conexión desde la aplicación o dispositivos ESP32.

---

## Credenciales

Por motivos de seguridad, **las credenciales originales del proyecto (`credentials.json`) no son las originales en este repositorio**.

GitHub detecta automáticamente este tipo de archivos cuando contienen claves privadas o información sensible, por lo que no es 
recomendable compartirlas públicamente.

Cada desarrollador deberá generar o utilizar sus propias credenciales desde la consola de Firebase y colocarlas localmente en su 
entorno de trabajo.

---


## Integración con MQTT

El sistema utiliza MQTT para la comunicación entre los dispositivos ESP32 y la aplicación.

Los mensajes enviados por MQTT son posteriormente procesados y almacenados o utilizados por Firebase según la lógica implementada en el sistema.

---

## Nota

La estructura mostrada en este repositorio corresponde únicamente a la organización del proyecto.

Los datos almacenados en la Realtime Database pueden cambiar dinámicamente durante la ejecución del sistema y no representan necesariamente el estado actual del proyecto.
