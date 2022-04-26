void setup() {
  Serial.begin(9600);
  pinMode(A6, INPUT);
}
void loop() {
  float input = analogRead(A6);
  //Serial.write(input);
  input  = input / 1023;
  Serial.println(input);
}
