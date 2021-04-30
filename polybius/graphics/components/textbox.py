"""
Author: Trevor Stalnaker
File Name: textbox.py

A textbox class that inherits from the Drawable class
"""

from polybius.graphics.utils.textgraphic import TextGraphic

class TextBox(TextGraphic):

    def __init__(self, text, position, font, fontColor,
                 antialias=True, highlight=None):
        """
        Initializes a textbox object with text, position, font, and
        font color
        """
        super().__init__(position, text, font, fontColor, antialias)
        self._highlight = highlight
        self.updateGraphic()

    def getHighlightColor(self):
        """Returns the current highlight color"""
        return self._highlight

    def setHighlightColor(self, highlight):
        """Sets the current highlight color"""
        self._highlight = highlight
        self.updateTextBox()

    def updateGraphic(self):
        """Update the textbox after parameters have been changed"""
        self._image = self._font.render(self._text, self._antialias,
                                        self._fontColor, self._highlight)
        
        self.updateCentering()
