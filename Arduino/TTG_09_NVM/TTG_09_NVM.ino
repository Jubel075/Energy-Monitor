#include "EmonLib.h"  // Include EmonLib
#include <Wire.h>     // Include Wire library for I2C
#include "RTClib.h"   // Include RTClib for RTC

EnergyMonitor emon1;      // Create an instance of EnergyMonitor
RTC_DS3231 rtc;           // Create an instance of the RTC module

// Variables for measurements
double ACV;
double Irms;
double Power;
double Energy = 0.0;
double totalEnergy = 0.0;
double kWh = 0.0;

// Variables for time tracking
DateTime lastMeasureTime;           // Stores the time of the last measurement
const int MEASURE_INTERVAL = 10;    // Interval in seconds

void setup() {
  Serial.begin(9600);

  // Initialize RTC
  if (!rtc.begin()) {
    Serial.println("RTC not found!");
    while (1);
  }

  // Set the initial time (if needed)
  rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));

  // Wait until the Python script sends a signal
  while (!Serial.available()) {
    delay(100);
  }

  // Print headers for easy parsing in Python
  Serial.println("Date, Irms, Energy_Usage, kWh");

  // Initialize the EnergyMonitor library
  emon1.current(A0, 20.85);        // Current: input pin, calibration.
  emon1.voltage(A2, 171.36, 1.7);  // Voltage: input pin, calibration, phase shift

  // Initialize the last measurement time to the current time
  lastMeasureTime = rtc.now();
}

void loop() {
  // Get the current time from the RTC
  DateTime currentTime = rtc.now();

  // Calculate the elapsed time in seconds
  long elapsedTime = currentTime.unixtime() - lastMeasureTime.unixtime();

  // Check if the interval has passed
  if (elapsedTime >= MEASURE_INTERVAL) {
    emon1.calcVI(1480, 2000);      // Calculate all. No.of half wavelengths (crossings), timeout

    // Calculate Irms and power
    Irms = emon1.calcIrms(1480);
    ACV = 127.0;                    // Assuming constant AC voltage of 127V
    Power = Irms * ACV;             // Power in watts

    // Calculate energy in watt-seconds for the interval
    Energy = Power * elapsedTime;   // Use elapsed time in seconds
    totalEnergy += Energy;          // Accumulate total energy in watt-seconds

    // Calculate kWh from total energy (in watt-seconds)
    kWh = totalEnergy / 3600000.0;  // Convert watt-seconds to kWh

    // Print data in CSV format for Python parsing
    printData(currentTime);

    // Update the last measurement time
    lastMeasureTime = currentTime;
  }
}

void printData(DateTime currentTime) {
  // Format date and time string
  char dateBuffer[20];
  sprintf(dateBuffer, "%04d-%02d-%02d %02d:%02d:%02d", 
          currentTime.year(), currentTime.month(), currentTime.day(),
          currentTime.hour(), currentTime.minute(), currentTime.second());

  // Print the data row with date and time
  Serial.print(dateBuffer);
  Serial.print(", ");
  Serial.print(Irms);
  Serial.print(", ");
  Serial.print(Energy);
  Serial.print(", ");
  Serial.println(kWh);
}