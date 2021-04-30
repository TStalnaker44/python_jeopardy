
import pygame
from polybius.graphics.utils.abstractgraphic import AbstractGraphic
from polybius.graphics.components.textinput import TextInput
from polybius.graphics.components.button import Button
from polybius.graphics.components.textbox import TextBox
from polybius.graphics.utils.mysurface import MySurface

class Incrementer(AbstractGraphic):

    def __init__(self, pos, buttonFont=None, valueFont=None, boxDims=(30,30),
                 buttonDims=(20,20), spacing=5, increments=[1,5,"all"],
                 padding=(0,0), backgroundColor=None, borderWidth=0,
                 borderColor=(0,0,0), maxValue=None, minValue=None,
                 defaultValue = None, activeTextInput=True, onlyIncrement=False,
                 onlyDecrement=False, buttonBorderWidth=4, buttonFontColor=(255,255,255),
                 buttonText=[], decrementColor=(255,0,0), incrementColor=(25,130,30),
                 valueBoxBorderWidth=2, valueBoxBackgroundColor=(255,255,255),
                 valueBoxBorderColor=(0,0,0), valueBoxAntialias=True, clearOnActive=False):

        AbstractGraphic.__init__(self, pos)

        if buttonFont == None:
            buttonFont = pygame.font.SysFont("Arial", 16)
        if valueFont == None:
            valueFont = pygame.font.SysFont("Arial", 16)
        self._buttonFont = buttonFont
        self._valueFont = valueFont

        self._borderColor = borderColor
        self._borderWidth = borderWidth
        self._backgroundColor = backgroundColor

        self._buttonBorderWidth = buttonBorderWidth
        self._buttonFontColor = buttonFontColor

        self._valueBoxBorderWidth = valueBoxBorderWidth
        self._valueBoxBackgroundColor = valueBoxBackgroundColor
        self._valueBoxBorderColor = borderColor
        self._valueBoxAntialias = valueBoxAntialias

        self._decrementColor = decrementColor
        self._incrementColor = incrementColor

        self._padding = padding
        self._buttonDims = buttonDims
        self._boxDims = boxDims
        self._spacing = spacing

        self._maxValue = maxValue
        self._minValue = minValue
        self._defaultValue = defaultValue

        self._activeTextInput = activeTextInput

        self._increments = increments
        self._onlyIncrement = onlyIncrement
        self._onlyDecrement = onlyDecrement

        self._clearOnActive = clearOnActive

        if "all" in increments and (maxValue == None or minValue == None):
            raise Exception("All can only be used if their are caps provided")

        self._buttonNum = 2 * len(increments)

        # Create the button text if it wasn't provided
        self._buttonText = buttonText
        if len(self._buttonText) == len(self._increments):
            self._buttonText += self._buttonText[::-1]
        if self._buttonText == []:
            temp = "<"*len(increments)
            for x in range(len(increments)):
                self._buttonText.append(temp)
                temp = temp[:len(temp)-1]
            temp = ""
            for x in range(len(increments)):
                temp += ">"
                self._buttonText.append(temp)
                
        self.updateDisplay()

        self._displayUpdated = False # Variable to prevent infinite recursion

    def updateDisplay(self):
        # Create the decrement buttons
        self._buttons = []
        button_y = 0 #Just a placeholder value (buttons are centered later)
        button_x = self.getX() + self._padding[0] + self._borderWidth

        if not self._onlyIncrement:
            for i, x in enumerate(self._increments[::-1]):
                buttonWidth = max(TextBox(self._buttonText[i], (0,0), self._buttonFont,
                                          (0,0,0)).getWidth() + \
                                  (2*self._buttonBorderWidth) + 6,
                                  self._buttonDims[0])

                # Create the button
                b = Button(self._buttonText[i], (button_x, button_y), self._buttonFont,
                           self._buttonFontColor, self._decrementColor,
                       self._buttonDims[1], buttonWidth, borderWidth=self._buttonBorderWidth,
                           borderColor=self.shiftRGBValues(self._decrementColor, (-30,-30,-30)))

                # Save the function and arguments for the button
                if x == "all":
                    func = self.setValue
                    arg = self._minValue
                else:
                    func = self.increment
                    arg = -1 * x

                # Add the button information to the list                  
                self._buttons.append((b, func, arg))

                # Update the position for the next button
                button_x += buttonWidth + self._spacing

        # Create the value box
        valueBox_x = button_x
        valueBox_y = self.getY() + self._padding[1] + self._borderWidth
        defaultText = "" if self._defaultValue == None else str(self._defaultValue)
        self._valueBox = TextInput((valueBox_x, valueBox_y), self._valueFont, self._boxDims,
                                   numerical=True, defaultText=defaultText,
                                   clearOnActive=self._clearOnActive, allowNegative=True,
                                   borderColor=self._valueBoxBorderColor,
                                   backgroundColor=self._valueBoxBackgroundColor,
                                   borderWidth=self._valueBoxBorderWidth,
                                   antialias = self._valueBoxAntialias)

        # Create the increment buttons
        button_y = 0 #Just a placeholder value (buttons are centered later)
        button_x = valueBox_x + self._valueBox.getWidth() + self._spacing
        if not self._onlyDecrement:
            for i, x in enumerate(self._increments):
                buttonWidth = max(TextBox(self._buttonText[i+len(self._increments)], (0,0),
                                          self._buttonFont, (0,0,0)).getWidth() + \
                                  (2*self._buttonBorderWidth) + 6,
                                  self._buttonDims[0])

                # Create the button
                b = Button(self._buttonText[i+len(self._increments)], (button_x, button_y),
                           self._buttonFont, self._buttonFontColor, self._incrementColor,
                       self._buttonDims[1], buttonWidth, borderWidth=self._buttonBorderWidth,
                           borderColor=self.shiftRGBValues(self._incrementColor, (-30,-30,-30)))

                # Save the function and arguments for the button
                if x == "all":
                    func = self.setValue
                    arg = self._maxValue
                else:
                    func = self.increment
                    arg = x

                # Add the button information to the list                  
                self._buttons.append((b, func, arg))

                # Update the position for the next button
                button_x += buttonWidth + self._spacing

        # Center the buttons around the text input
        for b in self._buttons:
            b[0].center(self._valueBox, (None,1/2), True)

        self._width = (sum([b[0].getWidth() for b in self._buttons])) + \
                      self._valueBox.getWidth() + \
                      (self._buttonNum * self._spacing) + (2 * self._padding[0]) + \
                      (2 * self._borderWidth)

        self._height = max(self._buttons[0][0].getHeight(), self._valueBox.getHeight()) + \
                       (2 * self._padding[1]) + (2 * self._borderWidth)

        self._background = pygame.Surface((self._width, self._height))

        self._displayUpdated = True
        self.updateGraphic()

    def increment(self, amount):
        currentVal = int(self._valueBox.getInput())
        newVal = min(self._maxValue, max(self._minValue, currentVal + amount))
        self._valueBox.setText(str(newVal))

    def setValue(self, value):
        value = min(self._maxValue, max(self._minValue, int(value)))
        self._valueBox.setText(str(value))

    def getValue(self):
        return self._valueBox.getInput()

    def draw(self, surface):
        super().draw(surface)
        self._valueBox.draw(surface)
        for b in self._buttons:
            b[0].draw(surface)

    def handleEvent(self, event):
        for b in self._buttons:
            b[0].handleEvent(event, b[1], [b[2]])
        if self._activeTextInput:
            self._valueBox.handleEvent(event, self._valueBox.getInput(),
                                       func=self.setValue)

    def center(self, surface=None, cen_point=(1/2,1/2), multisprite=False):
        super().center(surface, cen_point, multisprite)
        if not self._displayUpdated:
           self.updateDisplay()
        self._displayUpdated = False
            

        
