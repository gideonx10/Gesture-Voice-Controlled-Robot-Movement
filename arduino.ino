#include <SoftwareSerial.h>

SoftwareSerial BT(10, 11); // RX | TX for Bluetooth module

#define IN1 6
#define IN2 7
#define IN3 8
#define IN4 9

void setup() {
    BT.begin(9600); // Start Bluetooth communication
    Serial.begin(9600); // For debugging
    
    pinMode(IN1, OUTPUT);
    pinMode(IN2, OUTPUT);
    pinMode(IN3, OUTPUT);
    pinMode(IN4, OUTPUT);
    
    stopMotors(); // Ensure motors are stopped at the start
}

void loop() {
    if (BT.available()) {
        char command = BT.read();
        Serial.print("Received: ");
        Serial.println(command); // Debugging

        if (command == 'W' || command == 'w') {
            forward();
        } 
        else if (command == 'S' || command == 's') {
            backward();
        } 
        else if (command == 'A' || command == 'a') {
            left();
        } 
        else if (command == 'D' || command == 'd') {
            right();
        } 
        else if (command == 'X' || command == 'x') {
            stopMotors();
        } 
        else {
            stopMotors(); // Unknown command safety
        }
    }
    // void loop() {
    // Serial.print("starting");
    // Serial.print(BT.available());
    // if (BT.available()) {
    //     char c = BT.read();
    //     Serial.print("Received: ");
    //     Serial.println(c); // See if anything is received
    // }
    // Serial.print("Ending");
// }

    delay(50); // Prevent command flooding
}

void forward() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    Serial.println("Moving Forward");
}

void backward() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    Serial.println("Moving Backward");
}

void left() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
    Serial.println("Turning Left");
}

void right() {
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
    Serial.println("Turning Right");
}

void stopMotors() {
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
    Serial.println("Stopped");
}