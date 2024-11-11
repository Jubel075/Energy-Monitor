#include "EmonLib.h"
EnergyMonitor emon1;                      // Create an instance


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
  Serial.println("ACV   Irms Power Energy");

  emon1.current(A0, 20.85);        // Current: input pin, calibration.
  emon1.voltage(A2, 171.36 , 1.7); // Voltage: input pin, calibration, phase_shift
  START_TIME=millis();
}

void loop()
{
  emon1.calcVI(1480,2000);         // Calculate all. No.of half wavelengths (crossings), time-out

  Irms = emon1.calcIrms(1480);     // Calculate Irms only
  ACV = 127.0;
  Power = Irms*ACV;
  Energy = Power*TIME;
  do_PLXprint();
  delay(1000);
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
