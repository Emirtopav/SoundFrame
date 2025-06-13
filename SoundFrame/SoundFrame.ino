#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>  

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET    -1
#define NUM_BANDS     32
#define SMOOTHING_FACTOR 0.3


Adafruit_SH1106G display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);  // Düzeltilmiş sınıf ismi

float band_values[NUM_BANDS] = {0};
float smoothed_values[NUM_BANDS] = {0};

void setup() {
  Wire.begin(22,19);
  Serial.begin(115200);

  if (!display.begin(0x3C, true)) {  
    Serial.println(F("SH1106 allocation failed"));
    for (;;);
  }
  display.clearDisplay();
  display.display();
}

void loop() {
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    parseData(data);
    smoothData();
    drawBars();
  }
}

void parseData(String data) {
  int index = 0;
  int start = 0;
  int end = data.indexOf(',');

  while (end != -1 && index < NUM_BANDS) {
    band_values[index] = data.substring(start, end).toFloat();
    start = end + 1;
    end = data.indexOf(',', start);
    index++;
  }
  // Son değeri alma
  if (index < NUM_BANDS) {
    band_values[index] = data.substring(start).toFloat();
  }
}

void smoothData() {
  for (int i = 0; i < NUM_BANDS; i++) {
    smoothed_values[i] = 
      smoothed_values[i] * (1 - SMOOTHING_FACTOR) + 
      band_values[i] * SMOOTHING_FACTOR;
  }
}

void drawBars() {
  display.clearDisplay();

  int barWidth = SCREEN_WIDTH / NUM_BANDS;
  for (int i = 0; i < NUM_BANDS; i++) {
    // Değerleri ekran yüksekliğine uygun şekilde sınırla
    int barHeight = constrain(smoothed_values[i], 0, SCREEN_HEIGHT);
    display.fillRect(
      i * barWidth,             
      SCREEN_HEIGHT - barHeight, 
      barWidth - 1,            
      barHeight,                
      SH110X_WHITE             
    );
  }
  display.display();
}