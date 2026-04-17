#include <Wire.h>
#include <MPU6050.h>

MPU6050 mpu;

float axBias = 0;
float ayBias = 0;
float azBias = 0;

// filtered angles
float pitchFiltered = 0.0;
float rollFiltered  = 0.0;

// tuning
const float alpha = 0.18;      // lower = more stable, higher = faster
const float deadband = 0.35;   // degrees; ignores tiny vibration/noise

void calibrateAccel() {
  Serial.println("Calibrating... keep still");

  const int samples = 800;

  long axSum = 0;
  long aySum = 0;
  long azSum = 0;

  for (int i = 0; i < samples; i++) {
    int16_t ax, ay, az, gx, gy, gz;
    mpu.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);

    axSum += ax;
    aySum += ay;
    azSum += az;

    delay(2);
  }

  axBias = axSum / (float)samples;
  ayBias = aySum / (float)samples;
  azBias = (azSum / (float)samples) - 16384;

  Serial.println("Calibration complete");
}

float applyDeadband(float value, float threshold) {
  if (fabs(value) < threshold) return 0.0;
  return value;
}

void setup() {
  Serial.begin(921600);

  Wire.begin(8, 9);
  Wire.setClock(400000);

  mpu.initialize();

  if (!mpu.testConnection()) {
    Serial.println("MPU connection failed");
    while (1);
  }

  calibrateAccel();
}

void loop() {
  int16_t axRaw, ayRaw, azRaw, gx, gy, gz;
  mpu.getMotion6(&axRaw, &ayRaw, &azRaw, &gx, &gy, &gz);

  float ax = (axRaw - axBias) / 16384.0;
  float ay = (ayRaw - ayBias) / 16384.0;
  float az = (azRaw - azBias) / 16384.0;

  float pitch = atan2(ax, sqrt(ay * ay + az * az)) * 180.0 / PI;

  // roll inverted here
  float roll = -atan2(ay, sqrt(ax * ax + az * az)) * 180.0 / PI;

  // deadband to suppress tiny vibrations
  pitch = applyDeadband(pitch, deadband);
  roll  = applyDeadband(roll, deadband);

  // low-pass filter for stability
  pitchFiltered = alpha * pitch + (1.0 - alpha) * pitchFiltered;
  rollFiltered  = alpha * roll  + (1.0 - alpha) * rollFiltered;

  Serial.print(pitchFiltered, 3);
  Serial.print(",");
  Serial.println(rollFiltered, 3);

  delay(15);
}