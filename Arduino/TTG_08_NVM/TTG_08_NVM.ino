#include "EmonLib.h"
EnergyMonitor emon1;                      // Create an instance


// Variables for measurements
double ACV;
double Irms;
double Power;
double Energy = 0.0;
double totalEnergy = 0.0;
double kWh = 0.0;

unsigned long START_TIME = 0;
unsigned long LAST_MEASURE_TIME = 0;
const unsigned long MEASURE_INTERVAL = 1000; // 10 seconds

// Simulated date and time variables
int year = 2024;
int month = 10;
int day = 30;
int hours = 12;
int minutes = 0;
int seconds = 0;

void setup() {
  Serial.begin(9600);
  /*
    // Wait until the Python script sends a signal
  while (!Serial.available()) {
    ; // Do nothing until a signal is received
  delay(1000);
  }
  */
  

  // Print headers for easy parsing in Python
  Serial.println("Date, Irms, Energy_Usage, kWh");

  // Initialize the EnergyMonitor library
  emon1.current(A0, 20.85);        // Current: input pin, calibration.
  emon1.voltage(A2, 171.36, 1.7);  // Voltage: input pin, calibration, phase shift

  START_TIME = millis();
  LAST_MEASURE_TIME = millis();
}

void loop() {
  unsigned long currentTime = millis();

  // Take measurements every 10 seconds
  if (currentTime - LAST_MEASURE_TIME >= MEASURE_INTERVAL) {
    emon1.calcVI(1480, 2000);      // Calculate all. No.of half wavelengths (crossings), timeout

    // Calculate Irms and power
    Irms = emon1.calcIrms(1480);
    ACV = 127.0;                    // Assuming constant AC voltage of 127V
    Power = Irms * ACV;             // Power in watts
    
    // Calculate energy in watt-seconds for the 10-second interval
    Energy = Power * (MEASURE_INTERVAL / 1000.0);   // Convert milliseconds to seconds
    totalEnergy += Energy;                          // Accumulate total energy in watt-seconds

    // Calculate kWh from total energy (in watt-seconds)
    kWh = totalEnergy / 3600000.0;  // Convert watt-seconds to kWh

    // Print data in CSV format for Python parsing
    printData();

    // Update the last measure time
    LAST_MEASURE_TIME = currentTime;
  }
}

void printData() {
  // Simulate incrementing time (1 measurement every 10 seconds)
  seconds += 10;  // Increment seconds by the measurement interval

  // Adjust minutes and hours based on seconds overflow
  if (seconds >= 60) {
    seconds -= 60;
    minutes++;
  }
  if (minutes >= 60) {
    minutes -= 60;
    hours++;
  }
  if (hours >= 24) {
    hours -= 24;
    day++;
  }

  // Simulate month-end and year-end logic (basic example)
  int daysInMonth[] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  if (month == 2 && ((year % 4 == 0 && year % 100 != 0) || (year % 400 == 0))) {
    daysInMonth[1] = 29;  // Leap year adjustment
  }

  // Check for month overflow
  if (day > daysInMonth[month - 1]) {
    day = 1;
    month++;
  }

  // Check for year overflow
  if (month > 12) {
    month = 1;
    year++;
  }

  // Format date and time string
  char dateBuffer[20];
  sprintf(dateBuffer, "%04d-%02d-%02d %02d:%02d:%02d", year, month, day, hours, minutes, seconds);

  // Print the data row with date and time
  Serial.print(dateBuffer);
  Serial.print(", ");
  Serial.print(Irms);
  Serial.print(", ");
  Serial.print(Energy);
  Serial.print(", ");
  Serial.println(kWh);
}
