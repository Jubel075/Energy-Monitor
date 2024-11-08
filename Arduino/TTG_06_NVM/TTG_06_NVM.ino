#include <LiquidCrystal.h>

#include "EmonLib.h"                   // Include Emon Library
EnergyMonitor emon1;                   // Create an instance

const int rs = 2, en = 3, d4 = 4, d5 = 5, d6 = 6, d7 = 7;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

double ACV;
double Irms;
double Power;
double Energy;
unsigned long START_TIME    = 0;
unsigned long TIME          = 0;


void setup()
{  
  Serial.begin(9600);
  Serial.println("CLEARDATA");
  Serial.println("LABEL,Time,ACV,Irms,Power,Energy)");
  //lcd.begin(16, 2);
  Serial.println("ACV   Irms Power Energy");

  emon1.current(A0, 20.85);        // Current: input pin, calibration.
  emon1.voltage(A2, 171.36 , 1.7); // Voltage: input pin, calibration, phase_shift
  START_TIME=millis();
}

void loop()
{
  emon1.calcVI(1480,2000);         // Calculate all. No.of half wavelengths (crossings), time-out
/*
  
  emon1.serialprint();             // Print out all variables (realpower, apparent power, Vrms, Irms, power factor)
  
  float realPower       = emon1.realPower;        //extract Real Power into variable
  float apparentPower   = emon1.apparentPower;    //extract Apparent Power into variable
  float powerFActor     = emon1.powerFactor;      //extract Power Factor into Variable
  float supplyVoltage   = emon1.Vrms;             //extract Vrms into Variable
  float Irms            = emon1.Irms;             //extract Irms into Variable
*/
  Irms = emon1.calcIrms(1480);  // Calculate Irms only
  /*ACV  = emon1.Vrms ;
    if(ACV <= 7.2){
    }
  */

  ACV = 127.0;
  Power = Irms*ACV;
  Energy = Power*TIME;
 // do_serialprint();
  do_PLXprint();
  //do_lcdprint();
  delay(1000);
}

void do_serialprint()
{
  Serial.print(ACV,1);      Serial.print(" ");
  Serial.print(Irms,2);		  Serial.print(" ");
  Serial.print(Power,1);    Serial.print(" ");
  Serial.println(Energy,1);
}

void do_PLXprint(){
  TIME=(millis()-START_TIME)/1000;
  Serial.print("DATA,");
  Serial.print(TIME);
  Serial.print(","); 
  Serial.print(ACV);
  Serial.print(","); 
  Serial.print(Irms);
  Serial.print(","); 
  Serial.print(Power);
  Serial.print(","); 
  Serial.println(Energy);
}

void do_lcdprint()
{
  lcd.clear();
  lcd.setCursor(0, 0);   lcd.print("V:");   lcd.print(ACV,1);       // Line voltage
  lcd.setCursor(8, 0);   lcd.print("P:");   lcd.print(Power,1);     // Apparent power
  lcd.setCursor(0, 1);   lcd.print("I:");   lcd.print(Irms,2);      // Irms
  lcd.setCursor(8, 1);   lcd.print("E:");   lcd.print(Energy,1);    // Energy used     
}

