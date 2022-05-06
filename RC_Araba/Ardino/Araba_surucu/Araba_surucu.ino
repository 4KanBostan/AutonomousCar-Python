//Siddharth Sharma tarafından paylaşılan kodlardır.

//Youtube de Self Driving RC Car olarak videosu paylaşılmıştır.

//Sadece küçük değişikler yapılarak çalışır hale getirildi.

//rc_driver.ino olarak paylaşılan açık kaynak koddur.

//Video açıklamalar kısmında kaynak kodlar linkine bakabilirsiniz:)

int forward_pin = 6;
int reverse_pin = 7;
int left_pin = 8;
int right_pin = 9;

int command = 0;

int on_time = 1;
int off_time = 99;

void setup() {
  pinMode(forward_pin, OUTPUT);
  pinMode(reverse_pin, OUTPUT);
  pinMode(left_pin, OUTPUT);
  pinMode(right_pin, OUTPUT);
  
  Serial.begin(115200);
}

void loop() {
  if (Serial.available() > 0)
  {
    command = Serial.read();
  }
  else
  {
    reset();
  }

   drive(command);
}

void reset()
{
  digitalWrite(forward_pin, HIGH);
  digitalWrite(reverse_pin, HIGH);
  digitalWrite(left_pin, HIGH);
  digitalWrite(right_pin, HIGH);
}

void forward(int complex)
{
  if(complex == 0)
  {
    digitalWrite(reverse_pin, HIGH);
    digitalWrite(left_pin, HIGH);
    digitalWrite(right_pin, HIGH);
  } 
  
  digitalWrite(forward_pin, LOW);
  delay(on_time);
}

void reverse(int complex)
{
  if(complex == 0)
  {
    digitalWrite(forward_pin, HIGH);
    digitalWrite(left_pin, HIGH);
    digitalWrite(right_pin, HIGH);
  } 
  
  digitalWrite(reverse_pin, LOW);
  delay(on_time);
}

void left()
{
  digitalWrite(forward_pin, HIGH);
  digitalWrite(reverse_pin, HIGH);
  digitalWrite(left_pin, LOW);
  digitalWrite(right_pin, HIGH);
  delay(on_time);
}

void right()
{
  digitalWrite(forward_pin, HIGH);
  digitalWrite(reverse_pin, HIGH);
  digitalWrite(left_pin, HIGH);
  digitalWrite(right_pin, LOW);
  delay(3);
}

void forward_right()
{
  digitalWrite(reverse_pin, HIGH);
  digitalWrite(left_pin, LOW);
  digitalWrite(right_pin, HIGH);
  forward(3);
}


void forward_left()
{
  digitalWrite(reverse_pin, HIGH);
  digitalWrite(right_pin, LOW);
  digitalWrite(left_pin, HIGH);
  forward(3);
}

void reverse_right()
{
  digitalWrite(forward_pin, HIGH);
  digitalWrite(left_pin, HIGH);
  digitalWrite(right_pin, LOW);
  reverse(1);
}

void reverse_left()
{
  digitalWrite(forward_pin, HIGH);
  digitalWrite(left_pin, LOW);
  digitalWrite(right_pin, HIGH);
  reverse(1);
}

void drive(int command)
{
  switch(command)
  {
    case 48: reset(); break;
    case 49: forward(0); break;
    case 50: reverse(0); break;
    case 51: right(); break;
    case 52: left(); break;
    case 53: forward_right(); break;
    case 54: forward_left(); break;
    case 55: reverse_right(); break;
    case 56: reverse_left(); break;
    default: break;
  }
}
