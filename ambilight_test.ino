#include <FastLED.h>

#define LED_PIN     10
#define NUM_LEDS    144
int DIVIDE = 64;
#define FADE_INTERVAL 1000 // Time in milliseconds to wait before starting the fade
#define FADE_RATE    0.99  // Fade rate

CRGB leds[NUM_LEDS];
uint8_t LEDColour[3][144];

unsigned long lastUpdateTime = 0; // Initialize the last update time
unsigned long lastFadeTime = 0;    // Time tracking for fade steps

void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  FastLED.addLeds<WS2812, LED_PIN, GRB>(leds, NUM_LEDS);

  for (int i = 0; i < NUM_LEDS; i++) {
    leds[i] = CRGB(0, 0, 0);
  }
  FastLED.show();
  lastUpdateTime = millis(); // Initialize the last update time
  lastFadeTime = millis(); // Initialize the fade time
}

int LEDNum = 0;

void loop() {
  unsigned long currentTime = millis();
  
  // Check for serial data
  if (Serial.available() >= 3) {
    int r = Serial.read();
    int g = Serial.read();
    int b = Serial.read();

    if (r == 255 && g == 255 && b == 255) {
      LEDNum = 0; // Reset LED position
      while (Serial.available() == 0) { // Wait for brightness byte
        delay(1);
      }
      DIVIDE = Serial.read();
      lastUpdateTime = millis(); // Reset the last update time
    } else {
      LEDColour[0][LEDNum] = r / DIVIDE;
      LEDColour[1][LEDNum] = g / DIVIDE;
      LEDColour[2][LEDNum] = b / DIVIDE;
      leds[LEDNum] = CRGB(LEDColour[0][LEDNum], LEDColour[1][LEDNum], LEDColour[2][LEDNum]);
      LEDNum++;
      if (LEDNum >= NUM_LEDS) {
        LEDNum = 0;
        FastLED.show();
      }
      lastUpdateTime = millis(); // Reset the last update time
    }
  }

  // Check for fade-out condition
  if (currentTime - lastUpdateTime > FADE_INTERVAL) {
    // Non-blocking fade out
    if (currentTime - lastFadeTime > 50) { // Adjust the delay for smoother fading
      for (int i = 0; i < NUM_LEDS; i++) {
        LEDColour[0][i] *= FADE_RATE;
        LEDColour[1][i] *= FADE_RATE;
        LEDColour[2][i] *= FADE_RATE;
        leds[i] = CRGB(LEDColour[0][i], LEDColour[1][i], LEDColour[2][i]);
      }
      FastLED.show();
      lastFadeTime = currentTime; // Update last fade time
    }
  } else {
    lastFadeTime = currentTime; // Reset fade time if data is received
  }
}
