#include <heltec.h>

// For a connection via I2C using the Arduino Wire include:
#include <Wire.h>               
#include "HT_SSD1306Wire.h"
#include <lora/LoRa.h>
#include <errno.h>

static SSD1306Wire  display(0x3c, 500000, SDA_OLED, SCL_OLED, GEOMETRY_128_64, RST_OLED); // addr , freq , i2c group , resolution , rst
LoRaClass lora_instance;
int LoRa_status = 10;

void setup() {
  
  Serial.begin(115200);
  Serial.println();
  Serial.println();
  VextON();
  delay(100);

  // Initialising the UI will init the display too.
  display.init();
  
  LoRa_status = lora_instance.begin(915E6, true); 
  
  // Optional: Print status to Serial for debugging
}


void VextON(void)
{
  pinMode(Vext,OUTPUT);
  digitalWrite(Vext, LOW);
}

void VextOFF(void) //Vext default OFF
{
  pinMode(Vext,OUTPUT);
  digitalWrite(Vext, HIGH);
}

void loop() {
  
  // clear the display
  display.clear();
  // draw the current demo method
  if (LoRa_status != 0) {
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.setFont(ArialMT_Plain_10);
    display.drawString(0,0,String(LoRa_status));
  } else {
    display.setTextAlignment(TEXT_ALIGN_LEFT);
    display.setFont(ArialMT_Plain_10);
    display.drawString(0,0,String(LoRa_status));
  }
  // write the buffer to the display
  display.display();

  
  delay(5000);
  Serial.println(LoRa_status);
} 