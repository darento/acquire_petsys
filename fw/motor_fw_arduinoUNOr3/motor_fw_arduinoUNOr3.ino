/*
FIRMWARE DE CONTROL DE AUTOMATISMO MOTORES PASO A PASO
AUTORA: CELIA VALLADARES DE FRANCISCO y DAVID SANCHEZ GONZALO
INSTITUTO DE IMAGEN MOLECULAR i3M
CSIC - UPV

//Los siguientes pines estan adaptados a una Arduino UNO r3 y una
//CNC shield V3.0 con drivers DRV8825/A4988

// TODO
// - 
*/
#include <AccelStepper.h>

#define X_STEP_PIN      2
#define X_DIR_PIN       5
#define X_ENABLE_PIN    8
#define X_MIN_PIN       9
#define X_MAX_PIN       10

#define Y_STEP_PIN      3
#define Y_DIR_PIN       6
#define Y_ENABLE_PIN    8
#define Y_MIN_PIN       11
#define Y_MAX_PIN       12

#define Z_STEP_PIN      4
#define Z_DIR_PIN       7
#define Z_ENABLE_PIN    8
#define Z_MIN_PIN       A0
#define Z_MAX_PIN       A1

#define E_STEP_PIN      12
#define E_DIR_PIN       13
#define E_ENABLE_PIN    8

#define Q_STEP_PIN      36
#define Q_DIR_PIN       34
#define Q_ENABLE_PIN    30

#define LED_PIN         13

#define motorInterfaceType 1 //Debe ser 1 si se usan drivers
#define MAX_MOTORES 3

int numMotoresActivos = MAX_MOTORES;

AccelStepper X=AccelStepper(motorInterfaceType,X_STEP_PIN,X_DIR_PIN);
AccelStepper Y=AccelStepper(motorInterfaceType,Y_STEP_PIN,Y_DIR_PIN);
AccelStepper Z=AccelStepper(motorInterfaceType,Z_STEP_PIN,Z_DIR_PIN);
AccelStepper E=AccelStepper(motorInterfaceType,E_STEP_PIN,E_DIR_PIN);
AccelStepper Q=AccelStepper(motorInterfaceType,Q_STEP_PIN,Q_DIR_PIN);

void setupMotor(AccelStepper& motor, int stepPin, int dirPin, int enablePin, int minPin, int maxPin) {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  pinMode(minPin, INPUT_PULLUP);
  pinMode(maxPin, INPUT_PULLUP);
  digitalWrite(enablePin, LOW);
  motor.setMaxSpeed(200);
  motor.setSpeed(200);
  motor.setAcceleration(50);
}

void setMotorParameter(String command, int motor, int firstCommaIndex, void (*setFunc)(AccelStepper&, int)) {
  int secondCommaIndex = command.indexOf(',', firstCommaIndex + 1);
  int value = command.substring(secondCommaIndex + 1).toInt();
  if (motor == 1) setFunc(X, value);
  if (motor == 2) setFunc(Y, value);
  if (motor == 3) setFunc(Z, value);
  Serial.println("F");
}

void setMotorMaxSpeed(String command, int motor, int firstCommaIndex) {
  setMotorParameter(command, motor, firstCommaIndex, [](AccelStepper& motor, int maxSpeed) { motor.setMaxSpeed(maxSpeed); });
}

void setMotorSpeed(String command, int motor, int firstCommaIndex) {
  setMotorParameter(command, motor, firstCommaIndex, [](AccelStepper& motor, int speed) { motor.setSpeed(speed); });
}

void setMotorAcceleration(String command, int motor, int firstCommaIndex) {
  setMotorParameter(command, motor, firstCommaIndex, [](AccelStepper& motor, int acceleration) { motor.setAcceleration(acceleration); });
}

void setup() {
  pinMode(LED_PIN  , OUTPUT);

  setupMotor(X, X_STEP_PIN, X_DIR_PIN, X_ENABLE_PIN, X_MIN_PIN, X_MAX_PIN);
  setupMotor(Y, Y_STEP_PIN, Y_DIR_PIN, Y_ENABLE_PIN, Y_MIN_PIN, Y_MAX_PIN);
  setupMotor(Z, Z_STEP_PIN, Z_DIR_PIN, Z_ENABLE_PIN, Z_MIN_PIN, Z_MAX_PIN);

  Serial.begin(9600);
  delay(1000);
  Serial.print("<>");
}

void connectionMotor() {
  String info = "MOTORUP\n";
  Serial.println(info);
  Serial.println("F");
}

void pingLED(){
  digitalWrite(LED_PIN, HIGH);
  delay(5000);
  digitalWrite(LED_PIN, LOW);
  delay(100);
  Serial.println("F");
}

void setNumMotores(int num) {
  numMotoresActivos = max(1, min(num, MAX_MOTORES));
  Serial.println("F");
}

void processMoveCommand(String command, int motorNum, int firstCommaIndex, bool isAbsolute) {
  int secondCommaIndex = command.indexOf(',', firstCommaIndex + 1);
  int thirdCommaIndex = command.indexOf(',', secondCommaIndex + 1);
  int dir = isAbsolute ? 0 : command.substring(secondCommaIndex + 1, thirdCommaIndex).toInt();
  long distance = command.substring(isAbsolute ? secondCommaIndex + 1 : thirdCommaIndex + 1).toInt();
  if (motorNum > 0 && motorNum <= numMotoresActivos) {
    moveMotor(motorNum, dir, distance, isAbsolute);
  }
}

void moveMotor(int motor, int dir, long distance, bool isAbsolute) {
  if (motor == 1) {
    if (isAbsolute) {
      X.moveTo(distance);
    } else {
      X.move(dir * distance);
    }
  } else if (motor == 2) {
    if (isAbsolute) {
      Y.moveTo(distance);
    } else {
      Y.move(dir * distance);
    }
  } else if (motor == 3) {
    if (isAbsolute) {
      Z.moveTo(distance);
    } else {
      Z.move(dir * distance);
    }
  }

  while (X.distanceToGo() != 0 || Y.distanceToGo() != 0 || Z.distanceToGo() != 0) {
    if (isAbsolute) {
      dir = (distance > (motor == 1 ? X.currentPosition() : motor == 2 ? Y.currentPosition() : Z.currentPosition())) ? 1 : -1;
    }
    checkEndstopsAndStopMotors(motor, dir);
    if (motor == 1) X.run();
    if (motor == 2) Y.run();
    if (motor == 3) Z.run();
  }
  Serial.println("F");
}

void checkEndstopAndStopMotor(int motor, int dir, int minPin, int maxPin, bool& endstopHit, AccelStepper& stepper) {
  if (digitalRead(minPin) == LOW || digitalRead(maxPin) == LOW) {
    if (!endstopHit) {
      stopMotor(motor, true);
      stepper.move(-dir * 100); // Move a small amount in the opposite direction
      endstopHit = true;
    }
  } else {
    endstopHit = false;
  }
}

void checkEndstopsAndStopMotors(int motor, int dir) {
  static bool endstopHitX = false;
  static bool endstopHitY = false;
  static bool endstopHitZ = false;

  if (motor == 1) {
    checkEndstopAndStopMotor(motor, dir, X_MIN_PIN, X_MAX_PIN, endstopHitX, X);
  } else if (motor == 2) {
    checkEndstopAndStopMotor(motor, dir, Y_MIN_PIN, Y_MAX_PIN, endstopHitY, Y);
  } else if (motor == 3) {
    checkEndstopAndStopMotor(motor, dir, Z_MIN_PIN, Z_MAX_PIN, endstopHitZ, Z);
  }
}

void stopMotor(int motor, bool fromEndStop) {
  if (motor == 1) {
    X.setCurrentPosition(X.currentPosition());
  } else if (motor == 2) {
    Y.setCurrentPosition(Y.currentPosition());
  } else if (motor == 3) {
    Z.setCurrentPosition(Z.currentPosition());
  }
  if (!fromEndStop){
    Serial.println("F");
  }  
}

void setCurrentPositionToZero(int motorNum) {
  if (motorNum == 1) {
    X.setCurrentPosition(0);
  } else if (motorNum == 2) {
    Y.setCurrentPosition(0);
  } else if (motorNum == 3) {
    Z.setCurrentPosition(0);
  }
  Serial.println("F");
}

void processCommand(String command) {
  command.trim();
  int firstCommaIndex = command.indexOf(',');
  String action = command.substring(0, firstCommaIndex);
  int motorNum = command.substring(firstCommaIndex+1).toInt();

  if (action == "CON"){
    connectionMotor();
  } else if (action == "SETMOTORS") {
    setNumMotores(motorNum); // In this case, motorNum corresponds to the number of motors to set 
  } else if (action == "STOP") {
    stopMotor(motorNum, false);
  } else if (action == "MOVE") {  // Unused for now, prefer to use MOVETO
    processMoveCommand(command, motorNum, firstCommaIndex, false);
  } else if (action == "MOVETO") {
    processMoveCommand(command, motorNum, firstCommaIndex, true);
  } else if (action == "SET_ZERO") {
    setCurrentPositionToZero(motorNum);
  } else if (action == "SET_MAX_SPEED"){
    setMotorMaxSpeed(command, motorNum, firstCommaIndex);
  } else if (action == "SET_SPEED"){
    setMotorSpeed(command, motorNum, firstCommaIndex);
  } else if (action == "SET_ACCEL"){
    setMotorAcceleration(command, motorNum, firstCommaIndex);
  } else if (action == "LED") {
    pingLED();
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}
