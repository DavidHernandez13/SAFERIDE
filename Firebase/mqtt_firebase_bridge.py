# mqtt_bridge.py - Puente MQTT a Firebase
import paho.mqtt.client as mqtt
import firebase_admin
from firebase_admin import credentials, db
import json
import time

# Configuración
BROKER_IP = "172.20.10.14"  # IP de tu PC

# Inicializar Firebase
cred = credentials.Certificate('credenciales.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sistemas-programables-71bb0-default-rtdb.firebaseio.com/'
})
ref_root = db.reference()

def on_connect(client, userdata, flags, rc):
    print(f" Conectado a MQTT (código: {rc})")
    client.subscribe("saferide/telemetria")
    client.subscribe("saferide/alarma")
    ref_root.child('estado/online').set(1)
    print(" Suscrito a saferide/telemetria y saferide/alarma")

def on_message(client, userdata, msg):
    try:
        print(f"\n📨 Recibido: {msg.topic}")
        
        if msg.topic == "saferide/telemetria":
            datos = json.loads(msg.payload.decode('utf-8'))
            print(f"   Lat: {datos.get('latitud')}, Accidente: {datos.get('accidente')}")
            
            ref_root.child('ubicacion').update({
                'latitud': datos.get('latitud', 21.1166),
                'longitud': datos.get('longitud', -101.6502)
            })
            ref_root.child('estado_ciclista').update({
                'accidente': datos.get('accidente', False),
                'baja_iluminacion': datos.get('baja_iluminacion', False)
            })
            
            if datos.get('accidente'):
                ref_root.child('logs/eventos').push({
                    'tipo': 'ACCIDENTE',
                    'mensaje': f"Impacto en {datos.get('latitud')},{datos.get('longitud')}",
                    'timestamp': int(time.time() * 1000)
                })
                print("    ACCIDENTE EN FIREBASE!")
            
            print("    Firebase actualizado")
        
        elif msg.topic == "saferide/alarma":
            estado = msg.payload.decode('utf-8') == "1"
            ref_root.child('estado_ciclista/distraccion').set(estado)
            print(f"    Distracción: {estado}")
            print("    Firebase actualizado")
            
    except Exception as e:
        print(f"    Error: {e}")

print("="*50)
print("BRIDGE MQTT → FIREBASE")
print(f"Broker: {BROKER_IP}")
print("="*50)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_IP, 1883, 60)
client.loop_forever()
