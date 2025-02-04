//#include <Ultrasonic.h>
//Ultrasonic ultrasonic(8, 9);
int trigPin = 8;    // 超音波感測器 Trig 腳位
int echoPin = 9;    // 超音波感測器 Echo 腳位
const int slowPin = 6;
const int stopPin = 7;
const int redPin = 11;
const int greenPin = 12;
long duration, cm;
int stat, nstable=6, fstable=6;
bool ntimes=true, ftimes=true;
String data;

void setup() {
  Serial.begin (115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(12, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(7, OUTPUT);
  pinMode(6, OUTPUT);
  digitalWrite(redPin, HIGH);
  digitalWrite(slowPin, HIGH);
}

// 計算距離
void measureDistance() {
    digitalWrite(trigPin, LOW);
    delayMicroseconds(5);
    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigPin, LOW);
    duration = pulseIn(echoPin, HIGH);
    cm = (duration / 2) / 29.1;
}

// 控制燈號
void controlLED(){
  data = Serial.readStringUntil('\r');
  if (data=="g"){   //data>0 and data<6
    digitalWrite(stopPin, HIGH);
    digitalWrite(slowPin, LOW);
    delay(250);
    digitalWrite(redPin, LOW);
    digitalWrite(greenPin, HIGH);
  }
  if (data=="r"){
    digitalWrite(redPin, HIGH);
    digitalWrite(greenPin, LOW);
    delay(250);
    digitalWrite(stopPin, LOW);
    digitalWrite(slowPin, HIGH);
  }
}

void loop() {
//  distance = ultrasonic.read();
//  if (5<distance and distance<80) {
//    if (fstable>0){
//      fstable=fstable-1;
//      stat=0;
//      Serial.println(stat);
//      delay(10);
//    }else{
//      stat=1;
//      nstable=65535;
//      Serial.println(stat);
//    }
//  }else{
//    if (nstable>0){
//      nstable=nstable-1;
//      stat=1;
//      Serial.println(stat);
//      delay(10);
//    }else{
//      stat=0;
//      fstable=65535;
//      Serial.println(stat);
//    }
//  }
  unsigned long currentTime = millis();
  measureDistance();  // 計算距離
    if (cm > 0 && cm < 100) {
      if (fstable>0){
        fstable=fstable-1;
        stat=0;
      }else{
        stat=1;
        nstable=6;
        if (ntimes==true){
          Serial.println(stat);
          ntimes=false;
          ftimes=true;
        }
      }
    }else{
      if (nstable>0){
        nstable=nstable-1;
        stat=1;
      }else{
        stat=0;
        fstable=6;
        if (ftimes==true){
          Serial.println(stat);
          ftimes=false;
          ntimes=true;
        }
      }
    }
  if (Serial.available()>0){controlLED();}
  delay(100);
}
