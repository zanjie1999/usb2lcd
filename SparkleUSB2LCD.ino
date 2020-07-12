//#define DEBUG
#include <TinyWireM.h>                  // I2C Master lib for ATTinys which use USI - comment this out to use with standard arduinos
#include <LiquidCrystal_I2C.h>          // for LCD w/ GPIO MODIFIED for the ATtiny85
#include <DigiUSB.h>

#define GPIO_ADDR     0x27             // (PCA8574A A0-A2 @5V) typ. A0-A3 Gnd 0x20 / 0x38 for A - 0x27 is the address of the Digispark LCD modules.

LiquidCrystal_I2C lcd(GPIO_ADDR, 16, 2); // set address & 16 chars / 2 lines
boolean backlight = 0;
boolean reverseBacklight = 1;

void led(int isOn) {
  if (isOn) {
    if (reverseBacklight) {
      lcd.noBacklight();
    } else {
      lcd.backlight();
    }
    backlight = 1;
  } else {
    if (reverseBacklight) {
      lcd.backlight();
    } else {
      lcd.noBacklight();
    }
    backlight = 0;
    
  }
}

void setup() {
  DigiUSB.begin();
  TinyWireM.begin();                    // initialize I2C lib - comment this out to use with standard arduinos
  lcd.init();                           // initialize the lcd
  led(0);
  lcd.print("Sparkle  USB2LCD");
  lcd.setCursor(0, 1);
  lcd.print("    cupinkie.com");
  lcd.setCursor(0, 0);
}


void loop() {
  int currentLine = 0;
  boolean clearOnNext = 0;
  boolean clearMsg = 1;
  // when there are no characters to read, or the character isn't a newline
  int lastRead;
  int lastRead2;
  boolean hasRead2 = 0;
  int num = 0;
  // overflow
  boolean ovf = 0;
  while (1) {
    if (DigiUSB.available()) {
      //something to read
      lastRead = DigiUSB.read();
      if (clearMsg) {
        lcd.print("                ");
        lcd.setCursor(4, 1);
        lcd.print("            ");
        lcd.setCursor(0, 0);
        clearMsg = 0;
        if (DigiUSB.available()) {
          lastRead2 = DigiUSB.read();
          hasRead2 = 1;
        }
      }
      if (lastRead == '\r') {
        currentLine = 0;
        lcd.setCursor(0, currentLine);
        clearOnNext = 0;
        num = 0;
      } else if (lastRead == '\n') {
        if (currentLine)
          currentLine = 0;
        else
          currentLine = 1;
        clearOnNext = 1;
        lcd.setCursor(0, currentLine);
        num = 0;
      } else if (lastRead == 172) { //not sign "¬" send it with the send program to toggle the backlight
        led(!backlight);
        DigiUSB.read(); //read to nothing to get rid of newline that should come after it
      } else {
        if (clearOnNext) {
          lcd.print("                "); //clear a single line
          if (ovf) {
            lcd.setCursor(0, !currentLine);
            lcd.print("                ");
            ovf = 0;
          }
          lcd.setCursor(0, currentLine);
          clearOnNext = 0;
          if (DigiUSB.available()) {
            lastRead2 = DigiUSB.read();
            hasRead2 = 1;
          }
        }
        num++;
        if (num > 16) {
          if (currentLine)
            currentLine = 0;
          else
            currentLine = 1;
          lcd.setCursor(0, currentLine);
          //          lcd.print("                ");
          //          lcd.setCursor(0, currentLine);
          num = 0;
          ovf = 1;
        }
        lcd.print(char(lastRead));
        if (hasRead2) {
          lcd.print(char(lastRead2));
          hasRead2 = 0;
        }
      }
    } else {
      if (digitalRead(1)) {
        DigiUSB.write(1);
      }
    }
    // refresh the usb port
    DigiUSB.refresh();
    //    delay(10);
  }
}
