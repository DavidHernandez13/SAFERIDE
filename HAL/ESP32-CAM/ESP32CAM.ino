Cámara:
#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <WebServer.h>

// ========== CONFIGURACIÓN ==========
const char* ssid = "David";
const char* password = "Hola1234";
const char* mqtt_server = "172.20.10.14";

// ========== OBJETOS ==========
WiFiClient espClient;
PubSubClient client(espClient);
WebServer server(80);

#define BUZZER_PIN 14

// ========== PINES ESP32-CAM ==========
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM      0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM        5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ========== VARIABLES ==========
bool streamActive = false;

// ========== CALLBACK MQTT ==========
void callback(char* topic, byte* payload, unsigned int length) {
  if (payload[0] == '1') {
    digitalWrite(BUZZER_PIN, HIGH);
    delay(2000);
    digitalWrite(BUZZER_PIN, LOW);
  }
}

// ========== SERVIR STREAM MJPEG ==========
void handleStream() {
  WiFiClient clientStream = server.client();
  
  clientStream.println("HTTP/1.1 200 OK");
  clientStream.println("Content-Type: multipart/x-mixed-replace; boundary=frame");
  clientStream.println("Connection: close");
  clientStream.println();
  
  while (clientStream.connected()) {
    camera_fb_t *fb = esp_camera_fb_get();
    if (fb) {
      clientStream.print("--frame\r\n");
      clientStream.print("Content-Type: image/jpeg\r\n");
      clientStream.print("Content-Length: ");
      clientStream.print(fb->len);
      clientStream.print("\r\n\r\n");
      clientStream.write(fb->buf, fb->len);
      clientStream.print("\r\n");
      esp_camera_fb_return(fb);
    }
    delay(50);
  }
}

void handleRoot() {
  String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'>";
  html += "<title>SafeRide CAM</title>";
  html += "<style>body{margin:0;background:#000;}img{width:100%;height:auto;}</style>";
  html += "</head><body>";
  html += "<img src='/stream' />";
  html += "</body></html>";
  server.send(200, "text/html", html);
}

void handleStatus() {
  String json = "{\"status\":\"ok\",\"ip\":\"" + WiFi.localIP().toString() + "\"}";
  server.send(200, "application/json", json);
}

// ========== SETUP ==========
void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("\n=== SAFERIDE ESP32-CAM ===");
  
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
  
  // Configurar cámara
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_QVGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;
  
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Error cámara: 0x%x\n", err);
    return;
  }
  Serial.println(" CAMARA OK");
  
  // WiFi
  WiFi.begin(ssid, password);
  Serial.print("📡 Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\n WiFi conectado!");
  Serial.print(" IP: ");
  Serial.println(WiFi.localIP());
  
  // Servidor HTTP
  server.on("/", handleRoot);
  server.on("/stream", handleStream);
  server.on("/status", handleStatus);
  server.begin();
  Serial.println(" Servidor HTTP iniciado");
  Serial.print(" Video: http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream");
  
  // MQTT
  client.setServer(mqtt_server, 1883);
  client.setBufferSize(20480);
  client.setCallback(callback);
  
  Serial.print("📡 Conectando a MQTT");
  while (!client.connected()) {
    if (client.connect("ESP32CAM_SafeRide")) {
      Serial.println("  Conectado!");
      client.subscribe("saferide/alarma");
    } else {
      Serial.print(".");
      delay(1000);
    }
  }
  
  Serial.println("==================================");
  Serial.println(" SAFERIDE ESP32-CAM LISTA");
  Serial.print(" PRUEBA: Abre http://");
  Serial.print(WiFi.localIP());
  Serial.println("/stream en tu navegador");
  Serial.println("==================================");
}

// ========== LOOP ==========
void loop() {
  client.loop();
  server.handleClient();
  
  // Enviar foto por MQTT
  static unsigned long lastCapture = 0;
  if (millis() - lastCapture > 2500) {
    lastCapture = millis();
    
    camera_fb_t *fb = esp_camera_fb_get();
    if (fb) {
      if (client.publish("saferide/monitoreo", fb->buf, fb->len)) {
        Serial.printf("📸 Foto enviada: %d bytes\n", fb->len);
      }
      esp_camera_fb_return(fb);
    }
  }
  
  delay(10);
}
