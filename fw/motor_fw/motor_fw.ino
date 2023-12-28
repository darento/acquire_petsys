/*
FIRMWARE DE CONTROL DE AUTOMATISMO MOTORES PASO A PASO
AUTORA: CELIA VALLADARES DE FRANCISCO y DAVID SANCHEZ GONZALO
INSTITUTO DE IMAGEN MOLECULAR i3M
CSIC - UPV

Programa adaptado para el uso de Ramps 1.4 y drivers DRV8825/A4988

 * Declaración de bibliotecas
 * Definición de los pines de E/S
 * Definición de los 5 motores paso a paso, en configuración de uso con driver
 * Declaración de variables globales a usar en setup y loop
 * 

Estos son los pines para una Arduino MEGA 2560 y una Ramp 1.4 
#define X_STEP_PIN      54
#define X_DIR_PIN       55
#define X_ENABLE_PIN    38
#define X_MIN_PIN       2 //sensor de FC 1
#define X_MAX_PIN       3 //sensor de FC 2

#define Y_STEP_PIN      60
#define Y_DIR_PIN       61
#define Y_ENABLE_PIN    56
#define Y_MIN_PIN       14
#define Y_MAX_PIN       15

#define Z_STEP_PIN      46
#define Z_DIR_PIN       48
#define Z_ENABLE_PIN    62
#define Z_MIN_PIN       18
#define Z_MAX_PIN       19

#define E_STEP_PIN      26
#define E_DIR_PIN       28
#define E_ENABLE_PIN    24


#define Q_STEP_PIN      36
#define Q_DIR_PIN       34
#define Q_ENABLE_PIN    30


#define LED_PIN         13
#define FAN_PIN         9
#define TRIGGER         45
*/

//Los siguientes pines estan adaptados a una Arduino UNO r3 y una
//CNC shield V3

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
#define VUELTAS         200
//#define TRIGGERDELAY    1000


#define MAX_MOTORES 3

int numMotoresActivos = MAX_MOTORES;

AccelStepper X=AccelStepper(motorInterfaceType,X_STEP_PIN,X_DIR_PIN);
AccelStepper Y=AccelStepper(motorInterfaceType,Y_STEP_PIN,Y_DIR_PIN);
AccelStepper Z=AccelStepper(motorInterfaceType,Z_STEP_PIN,Z_DIR_PIN);
AccelStepper E=AccelStepper(motorInterfaceType,E_STEP_PIN,E_DIR_PIN);
AccelStepper Q=AccelStepper(motorInterfaceType,Q_STEP_PIN,Q_DIR_PIN);

void setupMotor(AccelStepper& motor, int stepPin, int dirPin, int enablePin) {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(enablePin, OUTPUT);
  digitalWrite(enablePin, LOW);
  motor.setMaxSpeed(200);
  motor.setSpeed(200);
  motor.setAcceleration(50);
}

void setup() {
  pinMode(LED_PIN  , OUTPUT);

  setupMotor(X, X_STEP_PIN, X_DIR_PIN, X_ENABLE_PIN);
  setupMotor(Y, Y_STEP_PIN, Y_DIR_PIN, Y_ENABLE_PIN);
  setupMotor(Z, Z_STEP_PIN, Z_DIR_PIN, Z_ENABLE_PIN);

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

void moveMotor(int motor, int dir, long distance) {
  if (motor == 1) {
    X.move(dir * distance);
  } else if (motor == 2) {
    Y.move(dir * distance);
  } else if (motor == 3) {
    Z.move(dir * distance);
  }
  int contador = 0; // Inicializar contador
  while (X.distanceToGo() != 0 || Y.distanceToGo() != 0 || Z.distanceToGo() != 0) {
    contador++; // Incrementar contador en cada iteración del bucle
    if (motor == 1) X.run();
    if (motor == 2) Y.run();
    if (motor == 3) Z.run();
  }
  Serial.println("F");
}

void stopMotor(int motor) {
  if (motor == 1) {
    X.stop();
    while(X.isRunning()) {
      X.run();
    }
  } else if (motor == 2) {
    Y.stop();
    while(Y.isRunning()) {
      Y.run();
    }
  } else if (motor == 3) {
    Z.stop();
    while(Z.isRunning()) {
      Z.run();
    }
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
    stopMotor(motorNum);
  } else if (action == "MOVE"){
    processMoveCommand(command, motorNum, firstCommaIndex);
  } else if (action == "LED"){
    pingLED();
  }
}

void processMoveCommand(String command, int motorNum, int firstCommaIndex) {
  int secondCommaIndex = command.indexOf(',', firstCommaIndex + 1);
  int thirdCommaIndex = command.indexOf(',', secondCommaIndex + 1);
  int dir = command.substring(secondCommaIndex + 1, thirdCommaIndex).toInt();
  long distance = command.substring(thirdCommaIndex + 1).toInt();
  if (motorNum > 0 && motorNum <= numMotoresActivos) {
    moveMotor(motorNum, dir, distance);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}
