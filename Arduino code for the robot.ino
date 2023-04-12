// Matthew Uy
// Cube Solver: An Arduino Rubik's cube solving robot
// Video: https://www.youtube.com/watch?v=gy5B6neyWf8
// Instructable: http://www.instructables.com/id/Rubiks-Cube-Solver/

// There are 4 layers of movement functions:
// 1. servo movement - how many degrees to move each servo
// 2. servo actions - ex. pushing the cube, or rotating it
// 3. cube moves - also known as cube notation; combinations of servo actions to orient the cube, then turn it, then orient it back
// 4. cube algorithms - combinations of cube moves that perform a desired action to the cube
#include <SoftwareSerial.h>
#include <Servo.h>
#include <LiquidCrystal_I2C.h>

// servo objects
SoftwareSerial debug_serial(8,2); //RX, TX
LiquidCrystal_I2C lcd(0x27,20,4);  // set the LCD address to 0x27 for a 16 chars and 2 line display
Servo rotate_servo;
Servo push_servo;

int move_speed = 5;
int buffer_time = 75; // time between moves
int rotate_pos = 90;
int push_pos = 140;
int hold_progress = 3;
int offset_degrees = 10;
bool slow_push = false;
//int push_forward_pos =85;
int push_forward_pos =77;
int push_back_pos = 120;

//////// cube move variables:


////////// Servo movement function: ///////////
int move_servo(int start, int finish, int servo_pin)
{
	int pos;
	if (start - finish < 0)
	{
		for(pos = start; pos <= finish; pos += 1)
		{
			if (servo_pin == 6)
			{
				push_servo.write(pos);
				delay(move_speed);
			}
			else if (servo_pin == 9)
			{
				rotate_servo.write(pos);
				delay(move_speed);
			}
		}
	}
	else
	{
		for(pos = start; pos >= finish; pos -= 1)
		{
			if (servo_pin == 6)
			{
				push_servo.write(pos);
				delay(move_speed);
			}
			else if (servo_pin == 9)
			{
				rotate_servo.write(pos);
				delay(move_speed);
			}
		}
	}
	// use a swich case next time
	if (servo_pin == 9)
	{
		rotate_pos = pos;
	}
	if (servo_pin == 6)
	{
		push_pos = pos;
	}
	delay(buffer_time);
}
///////// Cube movement functions: ////////////
void push_cube(int num_of_pushes = 1)
{
	if (num_of_pushes == 1)
		{
			if (slow_push == false)
			{
				move_servo(push_pos, push_forward_pos, 6);
				delay(buffer_time+300);
				release_cube();
				delay(buffer_time+300);
			}
			else // on rotate one
			{
				move_servo(push_pos, push_forward_pos, 6);
				delay(buffer_time+300);
				release_cube();
				delay(buffer_time+300);
			}
		}
	else
	{
		while (num_of_pushes != 0)
		{
			if (slow_push == false)
			{
				move_servo(push_pos, push_forward_pos, 6);
				delay(buffer_time+250);
				move_servo(push_pos, push_back_pos, 6);
				delay(buffer_time+300);
				num_of_pushes--;
			}
			else // on rotate one
			{
				move_servo(push_pos, push_forward_pos, 6);
				delay(buffer_time+300);
				move_servo(push_pos, push_back_pos, 6);
				delay(buffer_time+300);
				num_of_pushes--;
			}	
		}
	release_cube();
	}
}
void hold_cube()
{
	move_servo(push_pos, 117, 6);
	hold_progress = 1;
}
void release_cube()
{
	move_servo(push_pos, 140, 6);
	hold_progress = 3;
}
void rotate_one()
{
	slow_push = true;
	int rotate_finish = 11;
	if (hold_progress == 1) // hold progress 1 = hold
    {
		// from rotate_two
		if (rotate_pos < 140)
		{
			// initial turn
			move_servo(rotate_pos, rotate_finish-11, 9);
			move_servo(rotate_pos, rotate_finish+10, 9);
			// release and turn some more
			release_cube();
			move_servo(rotate_pos, 101, 9);
			hold_cube();
			move_servo(rotate_pos, 82, 9);
			move_servo(rotate_pos, 92, 9); // prevent pulling
			release_cube();
			move_servo(rotate_pos, rotate_finish, 9);
		}

		// from rotate_three
		else if (rotate_pos > 140)
		{
			// initial turn
			move_servo(rotate_pos, rotate_finish-11, 9);
			move_servo(rotate_pos, rotate_finish+15, 9);
			// release and turn some more
			release_cube();
			move_servo(rotate_pos, 108, 9);
			hold_cube();
			move_servo(rotate_pos, 83, 9);
			move_servo(rotate_pos, 93, 9); // prevent pulling
			release_cube();
			move_servo(rotate_pos, rotate_finish, 9);
		}
		hold_progress = 2;
	}
	else if (hold_progress == 2) // hold progress 2 = release, but offset still there
	{
		hold_progress = 3;
		move_servo(rotate_pos, rotate_finish, 9);
	}
	else if (hold_progress == 3) // hold progress 3 = release, offsets reconciled
	{
		// do nothing
		move_servo(rotate_pos, rotate_finish, 9);
	}
}


void rotate_two()
{
	slow_push = false;
	int rotate_finish = 90;
	if (hold_progress == 1) // hold progress 1 = hold
	{
		// rotate from rotate_one
		if (rotate_pos < 50) 
		{
			// initial turn
			move_servo(rotate_pos, rotate_finish+10, 9);
			move_servo(rotate_pos, rotate_finish-5, 9);

			// release and turn some more
			
			release_cube();
			move_servo(rotate_pos, 0, 9);
			hold_cube();
			move_servo(rotate_pos, 18, 9);
			move_servo(rotate_pos, 8, 9); // prevent pulling
			release_cube();
			
			move_servo(rotate_pos, rotate_finish, 9);
		}
		// rotate from rotate_three
		else if (rotate_pos > 150) 
		{
			move_servo(rotate_pos, rotate_finish-12, 9);
			move_servo(rotate_pos, rotate_finish+4, 9);


			// release and turn some more
			release_cube();
			move_servo(rotate_pos, 180, 9);
			hold_cube();
			move_servo(rotate_pos, 170, 9);
			move_servo(rotate_pos, 178, 9); // prevent pulling
			release_cube();
			move_servo(rotate_pos, rotate_finish, 9);
		}
		hold_progress = 2;
	}
	else if (hold_progress == 2) // hold progress 2 = release, but offset still there
	{
		hold_progress = 3;
		move_servo(rotate_pos, rotate_finish, 9);
	}
	else if (hold_progress == 3) // hold progress 3 = release, offsets reconciled
	{
		// do nothing
		move_servo(rotate_pos, rotate_finish, 9);
	}
}


void rotate_three()
{
	slow_push = false;
	int rotate_finish = 180;
	if (hold_progress == 1) // hold progress 1 = hold
	{
		// from rotate_two
		if (rotate_pos > 40)
		{
			move_servo(rotate_pos, rotate_finish+5, 9);
			move_servo(rotate_pos, rotate_finish-10, 9); // prevent pulling

			// fix: cube not fully turned
			release_cube();
			move_servo(rotate_pos, 80, 9);
			hold_cube();
			move_servo(rotate_pos, 100, 9);
			move_servo(rotate_pos, 90, 9); // prevent pulling
			release_cube();
			move_servo(rotate_pos, rotate_finish, 9);
		}

		// from rotate_one
		if (rotate_pos < 40)
		{
			move_servo(rotate_pos, rotate_finish+5, 9);
			move_servo(rotate_pos, rotate_finish-20, 9); // prevent pulling

			// fix: cube not fully turned
			release_cube();
			move_servo(rotate_pos, 70, 9);
			hold_cube();
			move_servo(rotate_pos, 100, 9);
			move_servo(rotate_pos, 90, 9); // prevent pulling
			release_cube();
			move_servo(rotate_pos, rotate_finish, 9);
		}

		hold_progress = 2;
	}
	else if (hold_progress == 2) // hold progress 2 = release, but offset still there
	{
		hold_progress = 3;
		move_servo(rotate_pos, rotate_finish, 9);
	}
	else if (hold_progress == 3) // hold progress 3 = release, offsets reconciled
	{
		// do nothing
		move_servo(rotate_pos, rotate_finish, 9);
	}
}


//our code

int Perform_Move(String move,int num_of_moves)
{
  String delimiter = " "; // Change this to the desired delimiter
  int pos = move.indexOf(delimiter); // Find the first occurrence of the delimiter

  while (pos != -1) {
    String step = move.substring(0, pos); // Extract the token
    print_num_of_moves_lcd(num_of_moves--);
    handle_cube_movement(step);

    move = move.substring(pos + 1); // Remove the token from the input string
    pos = move.indexOf(delimiter); // Find the next occurrence of the delimiter
  }
  return num_of_moves;
}

void print_num_of_moves_lcd(int num_of_moves_left)
{
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print((String)num_of_moves_left+" moves left!");
}



bool read_solution(int num_of_moves)
{
  String solution;
  char character;
  debug_serial.println("read S1");
  while(!Serial.available()) 
  {
  }
  String line;
  debug_serial.println("read S2");
  line = Serial.readString();
  print_num_of_moves_lcd(num_of_moves);
  int i=0;
  while (line!= "end\n")
  {
    
    Serial.println(line);
    num_of_moves = Perform_Move(line,num_of_moves);
    line = Serial.readString();
    debug_serial.println("read S3");
  }
	delay(10);
	Serial.print("String Accepted: ");
	delay(10);
  return true;
}


void handle_cube_movement(String step){

      if (step=="s1"){
          rotate_one();
      }
      else if (step =="s2"){
        rotate_two();            
      }
      else if (step =="s3"){
        rotate_three();            
      }
      else if(step =="p1"){
        push_cube(1);            
      }
      else if (step =="p2"){
        push_cube(2);            
      }
      else if (step =="p3"){
        push_cube(3);            
      }
      else if (step =="h"){
        hold_cube();            
      }
      else if (step =="re"){
        release_cube();
      }  

}

void read_serial_line(String go_string)
{
  //noInterrupts();
  while (!Serial.available());
  String serial_string= Serial.readString();
  debug_serial.println("debug: "+serial_string);
  while (serial_string != go_string){//move to yellow
    while (!Serial.available());
    serial_string= Serial.readString();
    debug_serial.println("debug: "+serial_string);
  }
  //interrupts();
}

void scan_all_sides(){
  Serial.println("start scan");

  debug_serial.println("Start scanning");
  read_serial_line("Go");//move to yellow
  push_cube();
  Serial.println("finished");

  read_serial_line("Go2");//move to blue
  push_cube();
  Serial.println("finished");

  read_serial_line("Go3");//move to white 
  push_cube();
  Serial.println("finished");

  read_serial_line("Go4");//move to orange
  push_cube();
  rotate_one();
  Serial.println("finished");

  read_serial_line("Go5");//move to red
  rotate_three();
  Serial.println("finished");

  read_serial_line("Go6");//move to start
  rotate_two();      
  Serial.println("finished");
}

int read_num_of_moves()
  {
    while (!Serial.available())
    {}
    String num_of_moves = Serial.readString();
    Serial.println("recieved");
    int int_num_of_moves = num_of_moves.toInt();
    return(int_num_of_moves-2);
  }

void solve_done_lcd()
{
  String DoneString = "Done!!                ";

  const char* stars[8] = {"*              *",
                          "**            **",
                          " **          ** ",
                          "  **        **  ",
                          "   **      **   ",
                          "    **    **    ",
                          "     **  **     ",
                          "      ****      "
                    };

  
                  
  for (int i = 0 ; i < 2000 ; i++)
  {
      char movedChar = DoneString[0];
      DoneString = DoneString.substring(1) +movedChar;
      lcd.setCursor(0,0);
      lcd.print(DoneString);
      lcd.setCursor(0,1);
      lcd.print(stars[7-i%8]);
      delay(80);
  }
}


////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////// PROGRAM START ///////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////

void setup()
{
  lcd.init(); 
  pinMode(7, INPUT_PULLUP); //joystick pin is 7

  lcd.backlight();
  lcd.setCursor(2,0);
  lcd.print("Rubik's cube");
  lcd.setCursor(4,1);
  lcd.print("solver!");


	rotate_servo.attach(9);  // attaches the servo on pin 9 to the servo object
	push_servo.attach(6);  // attaches the servo on pin 6 to the servo object
	push_servo.write(push_pos);
	rotate_servo.write(rotate_pos);


	delay(1000);
	Serial.begin(9600);
  debug_serial.begin(9600);
  String line;
	while (! Serial); // Wait untilSerial is ready
  line = Serial.readStringUntil("\n");
  while (line!= "start\n")
    line = Serial.readStringUntil("\n");
  Serial.println("arduino is ready");
  
}

/////////////// Loop //////////////////
void loop()
{
  int value = digitalRead(7);	// read Button state [0,1]
  while (value == 1)
  {
    value = digitalRead(7);	// read Button state [0,1]
  }
  scan_all_sides();
  int num_of_moves =read_num_of_moves();
  bool is_solve_done=read_solution(num_of_moves);
  //bool is_solve_done=read_solution(6);
  if (is_solve_done){
    Serial.println("Done!");    
    solve_done_lcd();   
  }
	while(true){}
}
