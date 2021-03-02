
File: Python Jeopardy
Author: Trevor Stalnaker

Preparing Your Machine to Run the Program:

	- Install python on the target machine from https://www.python.org/

	- Install the pygame module

		- Type 'pip install pygame' in the command line / terminal

		- You may need to provide a path to pip if it is not an environment variable 

Running the Program:

	- Start the game by navigating to the Jeopardy directory on your machine

	- Open a terminal / command line, if you have not already done so

	- Type 'py jeopardyGame.py' to run the program

Game Controls:

	- Press the ESCAPE key  or press the X to exit the game

	- Hit the M key to mute and unmute game audio

	- Click on Question Tiles to select them

		- The timer will begin automatically

	- Click the Space Bar when the question has been answered to advance
	    to the solution screen. 

		- The game will advance automatically when the timer runs out

	- Click the Space Bar once more to advance from the Answer Screen
            back to the Game Board

	- The game will automatically advance between rounds

	- There is no functionality to keep track of scores
		
		- This enables more freedom in play

Optional Command Line Arguments:

	- The user can provide three different arguments, described below:

		py jeopardyGame.py <question file> <answer time> <window dimensions>

	- The Arguments:

		- Question File:

			- This is the name of the CSV file that contains all of the questions
			  and answers for the Jeopardy Game

			- Do NOT include the .csv extension with the file name

			- The default is a random sampling of actual Jeopardy questions

			- See Using Custom Questions for more information

		- Answer Time:

			- The amount of time in seconds that players will have to 
			  answer questions

			- Number must be a positive integer

			- The default is 30 seconds

		- Full Screen
			
			- Boolean flag the determines if the game should be
			     rendered in full screen

			- True = Full Screen Mode; 
			  False = Windowed Mode		

			- Default: True	

		- Window Dimensions:

			- The width and height of the desired screen in pixels

			- Entered as '(<width>, <height>)'

			- It is not recommended to change this parameter

			- The default is (1200, 800)

Creating and Using Custom Questions:

	- CSV files MUST have the following columns

		- Show Number: show that the question aired in

		- Air Date: date the question was originally asked (on tv)

		- Round: Jeopardy, Double Jeopardy, or Final Jeopardy

		- Category: The question category (i.e. World Geography)

		- Value: Point value of question (i.e. 200, 400, 800, 2000)

		- Question: The question text

		- Answer: The answer to the question

	- When creating a custom CSV file, just type a lowercase 'x' for
	  the Show Number, Air Date, and Value columns

		- The value is randomly determined by the game

	- See the example CSV files for reference

	- Save your CSV file (make sure that it has a .csv extension)

	- Place your new CSV file in the 'questions' folder 

	- Finally, include the file name of your CSV when you run the game
