"""
    ============================================================
    SAFERIDE - ESP32 PRINCIPAL (CASCO INTELIGENTE)
    ============================================================
    
    DESCRIPCIÓN DEL SISTEMA:
    ---------------------------------
    Este código corre en el ESP32 montado dentro del casco. Es 
    el cerebro principal que procesa todos los sensores y 
    coordina las alertas.
    
    HARDWARE IMPLEMENTADO:
    ---------------------------------
    1. MPU6050 (Acelerómetro/Giroscopio):
       - Pines I2C: SCL=22, SDA=21
       - Detecta impactos mediante delta entre lecturas consecutivas
       - Umbral configurado: 10000 (ajustable según sensibilidad)
    
    2. GPS NEO-6M (Módulo de geolocalización):
       - UART2: TX=17, RX=16, Baudrate=9600
       - Librería: MicropyGPS para parseo de tramas NMEA
       - Envía coordenadas al dashboard en tiempo real
    
    3. OLED SSD1306 (Pantalla 128x64):
       - I2C1: SCL=26, SDA=27
       - Muestra: estado del sistema, coordenadas GPS, alertas
       - Interfaz amigable para el ciclista
    
    4. LDR (Sensor de luz):
       - Pin ADC: GPIO34
       - Detecta condiciones de poca luz (<2000)
       - Activa LED de advertencia automáticamente
    
    5. LED (Indicador visual):
       - Pin: GPIO25
       - Se enciende automáticamente en condiciones de oscuridad
    
    6. Buzzer Pasivo (Alerta sonora):
       - Pin PWM: GPIO15
       - Dos tonos: impacto (2000Hz) y distracción (1500Hz)
    
    CONEXIONES DE RED:
    ---------------------------------
    - WiFi: Conecta a hotspot "David" (contraseña: Hola1234)
    - MQTT Broker: IP 172.20.10.14, puerto 1883
    - Tópicos:
        * saferide/telemetria (envío de datos)
        * saferide/alarma (recepción de alertas IA)
    
    ARQUITECTURA DE HILOS (THREADS):
    ---------------------------------
    Se utilizan 6 hilos en paralelo para procesamiento simultáneo:
    
    Hilo 1 (leer_gps):         Lee y parsea datos GPS
    Hilo 2 (leer_mpu6050):     Monitorea impactos y activa buzzer
    Hilo 3 (leer_ldr):         Controla LED según luminosidad
    Hilo 4 (enviar_telemetria): Publica datos cada 5 segundos
    Hilo 5 (update_display):   Actualiza OLED cada 0.5 segundos
    Hilo 6 (mqtt_listener):    Escucha alertas de distracción
    
    FLUJO DE DATOS:
    ---------------------------------
    ESP32 (Casco) --(MQTT)--> Broker Mosquitto --(MQTT)--> Bridge Python
                                                                 |
                                                                 v
    ESP32-CAM --(MQTT)--> IA Python --(MQTT)--> Broker     Firebase DB
                                                              |
                                                              v
                                                          DASHBOARD WEB
    
    ALERTAS SOPORTADAS:
    ---------------------------------
    1. ACCIDENTE: 
       - Activación: Delta MPU6050 > UMBRAL_GOLPE (10000)
       - Acciones: Buzzer 2000Hz por 0.5s, pantalla "!! IMPACTO !!"
       
    2. DISTRACCIÓN:
       - Activación: MQTT recibe "1" del tópico saferide/alarma
       - Acciones: Buzzer 1500Hz (2 pitidos), pantalla "!DISTRACCION!"
       
    3. BAJA ILUMINACIÓN:
       - Activación: LDR < LDR_LIMITE (2000)
       - Acciones: LED encendido, pantalla muestra "Luz: ENC"
    
    INTEGRANTES DEL EQUIPO:
    ---------------------------------
    - Aguilar Figueroa Jose Miguel
    - Liceaga Hernández Ángel Baruc
    - Ibarra Muñoz Jose Francisco
    - Zacarias Hernández Angel David
    
    ---------------------------------
    Tecnológico Nacional de México - Campus León
    Ingeniería en Sistemas Computacionales
    Sistemas Programables - Docente: Verónica Tapia
    Enero - Junio 2026
    
    VERSIÓN: 2.0 
    ============================================================
"""
from machine import Pin, ADC, SoftI2C, PWM, UART
import mpu6050
import time
import ssd1306
from micropyGPS import MicropyGPS
import network
from umqtt.simple import MQTTClient
import _thread
import ujson

# ============================================================================
# 1. CONFIGURACIÓN DE RED
# ============================================================================

WIFI_SSID = "David"
WIFI_PASSWORD = "Hola1234"
MQTT_BROKER = "172.20.10.14"
MQTT_TOPIC_TELEMETRIA = "saferide/telemetria"
MQTT_TOPIC_ALARMA = "saferide/alarma"

# Variables globales
mqtt_client = None
alerta_distraccion = False
wifi_connected = False
mqtt_connected = False

# ============================================================================
# 2. CONFIGURACIÓN DE HARDWARE
# ============================================================================

print("\n=== SAFERIDE - INICIANDO ===\n")

# --- OLED (SCL=26, SDA=27) ---
try:
    i2c_oled = SoftI2C(scl=Pin(26), sda=Pin(27), freq=400000)
    oled = ssd1306.SSD1306_I2C(128, 64, i2c_oled)
    oled.fill(0)
    oled.text("SafeRide", 25, 20)
    oled.text("Cargando...", 22, 40)
    oled.show()
    print(" OLED inicializado")
except Exception as e:
    print(f" Error OLED: {e}")
    oled = None

# --- MPU6050 (SCL=22, SDA=21) ---
try:
    i2c_mpu = SoftI2C(scl=Pin(22), sda=Pin(21))
    sensor = mpu6050.accel(i2c_mpu)
    print(" MPU6050 inicializado")
except Exception as e:
    print(f" Error MPU6050: {e}")
    sensor = None

# --- GPS (UART2: TX=17, RX=16) 
uart_gps = UART(2, baudrate=9600, tx=17, rx=16)
gps = MicropyGPS()
print(" GPS inicializado")

# --- LDR (GPIO34) y LED (GPIO25) ---
ldr = ADC(Pin(34))
ldr.atten(ADC.ATTN_11DB)
led = Pin(25, Pin.OUT)
led.value(0)

# --- Buzzer (GPIO15) ---
buzzer = PWM(Pin(15))
buzzer.duty(0)

# Umbrales
LDR_LIMITE = 2000
UMBRAL_GOLPE = 10000

# Variables para MPU6050
x_ant, y_ant = 0, 0
ultimo_golpe = 0
golpe_activo = False

# Variables para GPS 
latitud = 0.0
longitud = 0.0
gps_fijado = False

# ============================================================================
# 3. FUNCIONES DE CONEXIÓN WiFi y MQTT
# ============================================================================

def conectar_wifi():
    global wifi_connected
    print("\n Conectando a WiFi...")
    
    try:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(False)
        time.sleep(0.5)
        wlan.active(True)
        time.sleep(0.5)
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        
        timeout = 20
        while timeout > 0:
            if wlan.isconnected():
                wifi_connected = True
                ip = wlan.ifconfig()[0]
                print(f" WiFi conectada! IP: {ip}")
                if oled:
                    oled.fill(0)
                    oled.text("WiFi OK", 35, 25)
                    oled.text(ip, 10, 40)
                    oled.show()
                    time.sleep(1)
                return True
            time.sleep(1)
            timeout -= 1
            print(f"   Esperando... {timeout}s")
        
        print(" Error: Timeout WiFi")
        return False
    except Exception as e:
        print(f" Error WiFi: {e}")
        return False

def mqtt_callback(topic, msg):
    global alerta_distraccion
    try:
        if topic == b'saferide/alarma':
            if msg == b'1':
                alerta_distraccion = True
                print("️ ¡ALERTA DE DISTRACCIÓN!")
                for _ in range(2):
                    buzzer.freq(1500)
                    buzzer.duty(256)
                    time.sleep(0.2)
                    buzzer.duty(0)
                    time.sleep(0.1)
                actualizar_pantalla()
            else:
                alerta_distraccion = False
                print(" Distracción terminada")
                actualizar_pantalla()
    except Exception as e:
        print(f"Error callback: {e}")

def conectar_mqtt():
    global mqtt_client, mqtt_connected
    if not wifi_connected:
        return False
    try:
        mqtt_client = MQTTClient("saferide_esp32", MQTT_BROKER)
        mqtt_client.set_callback(mqtt_callback)
        mqtt_client.connect()
        mqtt_client.subscribe(MQTT_TOPIC_ALARMA)
        mqtt_connected = True
        print(" MQTT conectado")
        if oled:
            oled.fill(0)
            oled.text("MQTT OK", 35, 25)
            oled.show()
            time.sleep(0.5)
        return True
    except Exception as e:
        print(f" Error MQTT: {e}")
        return False

def mqtt_listener_thread():
    global mqtt_client
    while True:
        try:
            if mqtt_client:
                mqtt_client.check_msg()
        except:
            pass
        time.sleep_ms(100)

def publicar_telemetria():
    global mqtt_client, mqtt_connected
    if not mqtt_connected or not mqtt_client:
        return
    try:
        valor_ldr = ldr.read()
        porcentaje_luz = int((valor_ldr / 4095) * 100)
        baja_luz = valor_ldr < LDR_LIMITE
        
        datos = {
            "latitud": latitud,
            "longitud": longitud,
            "accidente": golpe_activo,
            "baja_iluminacion": baja_luz,
            "ldr_porcentaje": porcentaje_luz,
            "timestamp": time.time()
        }
        mqtt_client.publish(MQTT_TOPIC_TELEMETRIA, ujson.dumps(datos))
        print(f"Telemetría enviada: Lat={latitud:.4f}")
    except Exception as e:
        print(f"Error publicar: {e}")

# ============================================================================
# 4. FUNCIONES DE LA PANTALLA OLED 
# ============================================================================

def actualizar_pantalla():
    if not oled:
        return
    try:
        oled.fill(0)
        oled.text("SafeRide", 0, 0)
        
        # Estado de luz
        if ldr.read() < LDR_LIMITE:
            oled.text("Luz: ENC", 0, 15)
        else:
            oled.text("Luz: OFF", 0, 15)
        
        # GPS 
        oled.text("Lat: {:.4f}".format(latitud), 0, 35)
        oled.text("Lon: {:.4f}".format(longitud), 0, 45)
        
        # Alertas
        if alerta_distraccion:
            oled.text("!DISTRACCION!", 0, 55)
        elif golpe_activo:
            oled.text("!! IMPACTO !!", 0, 55)
        
        # Indicadores de conexión
        if wifi_connected:
            oled.text("W", 120, 0)
        if mqtt_connected:
            oled.text("M", 120, 10)
        
        oled.show()
    except:
        pass

def mostrar_nivel_luz():
    if not oled:
        return
    try:
        valor = ldr.read()
        porcentaje = int((valor / 4095) * 100)
        oled.fill(0)
        oled.text("Nivel de Luz", 25, 10)
        oled.text(f"{porcentaje}%", 55, 30)
        oled.rect(10, 45, 108, 10, 1)
        ancho = int((porcentaje / 100) * 108)
        oled.fill_rect(10, 45, ancho, 10, 1)
        oled.show()
        time.sleep(2)
        actualizar_pantalla()
    except:
        pass

# ============================================================================
# 5. HILOS DE SENSORES 
# ============================================================================

def leer_gps():
    """Hilo para leer GPS - IGUAL que tu código funcional"""
    global latitud, longitud, gps_fijado
    while True:
        try:
            while uart_gps.any():
                data = uart_gps.read(1)
                if data:
                    gps.update(data.decode('utf-8'))
            
            # Actualizar coordenadas
            latitud = gps.latitude
            longitud = gps.longitude
            
            if latitud != 0 and longitud != 0:
                gps_fijado = True
                
        except Exception as e:
            pass
        time.sleep_ms(100)

def leer_mpu6050():
    global x_ant, y_ant, ultimo_golpe, golpe_activo
    if sensor is None:
        return
    while True:
        try:
            val = sensor.get_values()
            delta = abs(val['AcX'] - x_ant) + abs(val['AcY'] - y_ant)
            x_ant, y_ant = val['AcX'], val['AcY']
            
            if delta > UMBRAL_GOLPE and (time.time() - ultimo_golpe) > 2:
                ultimo_golpe = time.time()
                golpe_activo = True
                print(f" ¡IMPACTO! Delta: {delta}")
                
                buzzer.freq(2000)
                buzzer.duty(512)
                time.sleep(0.5)
                buzzer.duty(0)
                
                publicar_telemetria()
                actualizar_pantalla()
            
            if golpe_activo and (time.time() - ultimo_golpe) > 3:
                golpe_activo = False
                actualizar_pantalla()
        except:
            pass
        time.sleep_ms(50)

def leer_ldr():
    while True:
        try:
            if ldr.read() < LDR_LIMITE:
                led.value(0)
            else:
                led.value(1)
        except:
            pass
        time.sleep_ms(200)

def enviar_telemetria_periodica():
    while True:
        try:
            publicar_telemetria()
        except:
            pass
        time.sleep(5)

def update_display_loop():
    contador = 0
    while True:
        try:
            actualizar_pantalla()
            contador += 1
            if contador >= 20 and not golpe_activo and not alerta_distraccion:
                mostrar_nivel_luz()
                contador = 0
        except:
            pass
        time.sleep(0.5)

# ============================================================================
# 6. MAIN
# ============================================================================

def main():
    global wifi_connected, mqtt_connected
    
    print("\n" + "="*50)
    print("   SAFERIDE - SISTEMA DE SEGURIDAD")
    print("="*50)
    
    print("\n Conectando redes...")
    
    wifi_connected = conectar_wifi()
    
    if wifi_connected:
        mqtt_connected = conectar_mqtt()
    else:
        print(" Sin WiFi - Modo local")
    
    # Pitido de inicio
    try:
        buzzer.freq(1500)
        buzzer.duty(256)
        time.sleep(0.2)
        buzzer.duty(0)
    except:
        pass
    
    # Iniciar hilos
    print("\n Iniciando hilos...")
    _thread.start_new_thread(leer_gps, ())
    _thread.start_new_thread(leer_mpu6050, ())
    _thread.start_new_thread(leer_ldr, ())
    _thread.start_new_thread(enviar_telemetria_periodica, ())
    _thread.start_new_thread(update_display_loop, ())
    
    if mqtt_connected:
        _thread.start_new_thread(mqtt_listener_thread, ())
    
    print("\n" + "="*50)
    print("    SISTEMA OPERATIVO")
    print(f"    WiFi: {'Conectado' if wifi_connected else 'Local'}")
    print(f"    MQTT: {'Conectado' if mqtt_connected else 'No'}")
    print("    Esperando eventos...")
    print("="*50 + "\n")
    
    # Pantalla de inicio
    if oled:
        try:
            oled.fill(0)
            oled.text("SafeRide", 25, 20)
            oled.text("Sistema Listo!", 20, 40)
            oled.show()
            time.sleep(2)
            actualizar_pantalla()
        except:
            pass
    
    # Bucle principal
    while True:
        try:
            actualizar_pantalla()
            time.sleep(0.5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
