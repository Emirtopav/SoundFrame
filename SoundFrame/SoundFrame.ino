
/*      _______.  ______    __    __  .__   __.  _______   _______ .______          ___      .___  ___.  _______       */
/*     /       | /  __  \  |  |  |  | |  \ |  | |       \ |   ____||   _  \        /   \     |   \/   | |   ____|      */
/*    |   (----`|  |  |  | |  |  |  | |   \|  | |  .--.  ||  |__   |  |_)  |      /  ^  \    |  \  /  | |  |__         */
/*     \   \    |  |  |  | |  |  |  | |  . `  | |  |  |  ||   __|  |      /      /  /_\  \   |  |\/|  | |   __|        */
/* .----)   |   |  `--'  | |  `--'  | |  |\   | |  '--'  ||  |     |  |\  \----./  _____  \  |  |  |  | |  |____       */
/* |_______/     \______/   \______/  |__| \__| |_______/ |__|     | _| `._____/__/     \__\ |__|  |__| |_______|      */
/*                                                                                                                     */
/* .______   ____    ____  _______ .___  ___.  __  .______     .___________.  ______   .______      ___   ____    ____ */
/* |   _  \  \   \  /   / |   ____||   \/   | |  | |   _  \    |           | /  __  \  |   _  \    /   \  \   \  /   / */
/* |  |_)  |  \   \/   /  |  |__   |  \  /  | |  | |  |_)  |   `---|  |----`|  |  |  | |  |_)  |  /  ^  \  \   \/   /  */
/* |   _  <    \_    _/   |   __|  |  |\/|  | |  | |      /        |  |     |  |  |  | |   ___/  /  /_\  \  \      /   */
/* |  |_)  |     |  |     |  |____ |  |  |  | |  | |  |\  \----.   |  |     |  `--'  | |  |     /  _____  \  \    /    */
/* |______/      |__|     |_______||__|  |__| |__| | _| `._____|   |__|      \______/  | _|    /__/     \__\  \__/     */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include "userConfig.h"
#include "bitmap.h"

#if defined(USE_SH1106)
  #include <Adafruit_SH110X.h>
  #define COLOR_WHITE SH110X_WHITE
  Adafruit_SH1106G display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
#elif defined(USE_SSD1306)
  #include <Adafruit_SSD1306.h>
  #define COLOR_WHITE WHITE
  Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);
#else
  #error "Lütfen userConfig.h içinde bir ekran tipi seçin!"
#endif

float band_values[NUM_BANDS] = {0};
float smoothed_values[NUM_BANDS] = {0};
bool connected = false;


/*      _______. _______ .___________. __    __  .______   */
/*     /       ||   ____||           ||  |  |  | |   _  \  */
/*    |   (----`|  |__   `---|  |----`|  |  |  | |  |_)  | */
/*     \   \    |   __|      |  |     |  |  |  | |   ___/  */
/* .----)   |   |  |____     |  |     |  `--'  | |  |      */
/* |_______/    |_______|    |__|      \______/  | _|      */
void setup() {
  Wire.begin(I2C_SDA, I2C_SCL);
  Serial.begin(115200);

  if (!display.begin(OLED_ADDRESS, true)) {
    Serial.println(F("Ekran başlatılamadı!"));
    for (;;);
  }

  display.clearDisplay();
  display.display();

  showBitmap(startLogo);
  delay(2000);
  showBitmap(waitLogo);
}//-----------End of VoidSetup---------//



/*  __        ______     ______   .______   */
/* |  |      /  __  \   /  __  \  |   _  \  */
/* |  |     |  |  |  | |  |  |  | |  |_)  | */
/* |  |     |  |  |  | |  |  |  | |   ___/  */
/* |  `----.|  `--'  | |  `--'  | |  |      */
/* |_______| \______/   \______/  | _|      */




void loop() {
  if (!connected) {
    if (Serial.available()) {
      connected = true;
      display.clearDisplay();
      display.display();
    } else {
      delay(100);
      return;
    }
  }

  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    parseData(data);
    smoothData();
    drawBars();
  }
}//------------End of VoidLoop------------//

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
    int barHeight = constrain(smoothed_values[i], 0, SCREEN_HEIGHT);
    display.fillRect(i * barWidth, SCREEN_HEIGHT - barHeight, barWidth - 1, barHeight, COLOR_WHITE);
  }
  display.display();
}

void showBitmap(const unsigned char *bitmap) {
  display.clearDisplay();
  display.drawBitmap(0, 0, bitmap, SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_WHITE);
  display.display();
}
