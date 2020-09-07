
from .abstractgraphic import AbstractGraphic

class TextGraphic(AbstractGraphic):

    def __init__(self, position, text, font, fontColor, antialias):

        super().__init__(position)
        
        self._text = text
        self._font = font
        self._fontColor = fontColor
        self._antialias = antialias

    def getText(self):
        """Returns the current text of the textbox"""
        return self._text

    def setText(self, text):
        """Sets the text of a textbox"""
        self._text = text
        self.updateGraphic()

    def getFont(self):
        """Returns the current font of the textbox"""
        return self._font

    def setFont(self, font):
        """Sets the font of the textbox"""
        self._font = font
        self.updateGraphic()

    def getFontColor(self):
        """Returns the current font color of the textbox"""
        return self._fontColor

    def setFontColor(self, fontColor):
        """Sets the font color of the textbox"""
        self._fontColor = fontColor
        self.updateGraphic()

    def getAntiAlias(self):
        """Returns true if antialiasing is on otherwise false"""
        return self._antialias

    def setAntiAlias(self, antialias):
        """Set antialiasing"""
        self._antialias = antialias
        self.updateGraphic()
        
