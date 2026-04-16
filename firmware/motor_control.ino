#define IN1 5
#define IN2 6
#define IN3 7
#define IN4 8
#define ENA 9
#define ENB 10

void setup() {
  // MUST match the Pi's baud rate
  Serial.begin(115200); 
  
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT);
  pinMode(ENA, OUTPUT); pinMode(ENB, OUTPUT);
  
  // Safety: Start stopped
  stopMotors();
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    
    // Blink LED on pin 13 so you can see the command arriving
    digitalWrite(13, HIGH); 

    if (cmd == 'F') { // Forward
       digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
       digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
       analogWrite(ENA, 75); analogWrite(ENB, 75);
    } 
    else if (cmd == 'L') { // Left Turn
       digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH);
       digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
       analogWrite(ENA, 75); analogWrite(ENB, 75);
    }
    else if (cmd == 'R') { // Right Turn
       digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
       digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH);
       analogWrite(ENA, 75); analogWrite(ENB, 75);
    }
    else if (cmd == 'S') { // Stop
       stopMotors();
    }
    
    delay(10);
    digitalWrite(13, LOW);
  }
}

void stopMotors() {
  digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
  analogWrite(ENA, 0); analogWrite(ENB, 0);
}
