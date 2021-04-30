# Python Jeopardy
 A version of the classic Jeopardy game show programmed in python and pygame.  The game comes with thousands of preloaded questions from previous Jeopardy games, but also allows users to create their own custom games.
 
## Installation
* Install python on the target machine from [https://www.python.org/](https://www.python.org/)
* Install the pygame module
* Type the following into a terminal window:
```bash
pip install pygame
```
## Running the Program

* Navigate to the Jeopardy directory on your machine
* Open a terminal / CMD window, if you have not already done so
* Type the following to run the program 
```bash
py jeopardyGame.py
```

## Game Controls
* Press the ESCAPE key or press the X button to end the game
* Hit the M key to mute and unmute game audio
* Click on Question Tiles to select them
* The question timer will start automatically
* Press the SPACE BAR once the question is answered to advance to solution screen
* Note: The game will advance automatically when the timer runs out
* Press the SPACE BAR once more to advance from the Answer Screen back to the Game Board
* The game will automatically move between rounds (i.e. Jeopardy, Double Jeopardy, Final Jeopardy)
* Currently there is no functionality to keep track of scores
* This gives users more freedom in how they conduct and score the game

## Command Line Arguments
The user can provide four different arguments as described here:

```bash
py jeopardyGame.py --question <question file> --timer <answer time> --dims <window dimensions> --fullscreen
```

All of the arguments are optional, meaning you can choose which to include.

* Typing 'py jeopardyGame.py --help' will bring up documentation in the terminal
* Typing 'py jeopardyGame.py --controls' will bring up documentation on game controls

###The Arguments
* Question File:
    * This is the name of the CSV file that contains all of the questions and answers for the Jeopardy game
    * Do NOT include the .csv extension with the file name
    * The default is a random sampling of actual Jeopardy questions
    * See Using Custom Questions for more information
* Answer Time:
    * The amount of time in seconds that players iwll have to answer questions
    * Number must be a positive integer
    * The default is 30 seconds
* Fullscreen:
    * Boolean flag that determines if the game should be rendered in fullscreen
    * True = Fullscreen Mode
    * False = Windowed Mode
    * Default: True
* Window Dimensions:
    * The width and height of the desired screen in pixels
    * Entered as '(&lt;width&gt;,&lt;height&gt;)'
    * It is not recommended to change this parameter
    * The default is (1200, 800)

## Creating and Using Custom Questions
CSV files MUST have the following columns
* Show Number: show that the question aired in
* Air Date: date the question was originally asked (on TV)
* Round: Jeopardy, Double Jeopardy, or Final Jeopardy
* Category: The question category (i.e. World Geography)
* Value: Point value of question (i.e. 200, 400, 800, 1000)
* Question: The question text
* Answer: The answer to the question

When creating a custom CSV file, just type a lowercase 'x' for the Show Number, Air Date, and Value columns.  The point value of questions is randomly assigned by the game.  See the example CSV files for reference.

* Save your CSV file (make sure that it has a .csv extension).
* Place your new CSV file in the 'questions' folder
* Finally, include the file name of your CSV when you run the game

## License
[MIT](https://choosealicense.com/licenses/mit/)
