
import pygame
from .textbox import TextBox
from polybius.graphics.utils.textgraphic import TextGraphic

class MultiLineTextBox(TextGraphic):

    def __init__(self, text, position, font, fontColor, backgroundColor=None,
                 padding=(0,0), linespacing=0, antialias=True,
                 alignment="center"):

        if not alignment.lower() in ("left", "center", "right"):
            raise Exception("Invalid alignment type")

        super().__init__(position, text, font, fontColor, antialias)
        
        self._lines = text.split("\n")

        self._hpadding = padding[0]
        self._vpadding = padding[1]

        self._lineSpacing = linespacing
        self._alignment = alignment.lower()
        
        self._backgroundColor = backgroundColor

        self.updateGraphic()

    def setText(self, text):
        """Set the text"""
        self._text = text
        self._lines = text.split("\n")
        self.updateGraphic()

    def getLine(self, lineNumber):
        """Get the text from a line in the textbox"""
        if lineNumber - 1 >= len(self._lines):
            raise Exception("This textbox does not have " + \
                            str(lineNumber) + " lines")
        elif lineNumber - 1 < 0:
            raise Exception("Line numbers cannot be negative")
        else:
            return self._lines[lineNumber-1]

    def setLine(self, text, lineNumber):
        """Set a line of text in the textbox"""
        if lineNumber - 1 >= len(self._lines):
            raise Exception("This textbox does not have " + \
                            str(lineNumber) + " lines")
        elif lineNumber - 1 < 0:
            raise Exception("Line numbers cannot be negative")
        elif "\n" in text:
            raise Exception("Newline character cannot be in a single line of text")
        else:
            self._lines[lineNumber-1]=text
            self.updateGraphic()

    def appendLine(self, line):
        """Adds a line to the current text"""
        self._lines.append(text)
        self._text = "\n".join(self._lines)
        self.updateGraphic()

    def insertLine(self, line, index):
        """Insert a line at a given index"""
        self._lines[:index-1] + [line] +self._lines[index-1:]
        self._text = "\n".join(self._lines)
        self.updateGraphic()

    def getBackgroundColor(self):
        """Get the current background color"""
        return self._backgroundColor

    def setBackgroundColor(self, color):
        """Set the background color"""
        self._backgroundColor = color
        self.updateGraphic()

    def getPadding(self):
        """Return the padding around the parimeter"""
        return (self._hpadding, self._vpadding)

    def setPadding(self, padding):
        """Set the padding around the parimeter"""
        self._hpadding = padding[0]
        self._vpadding = padding[1]
        self.updateGraphic()

    def getLineSpacing(self):
        """Get the current pixel spacing between lines"""
        return self._lineSpacing

    def setLineSpacing(self, spacing):
        """Set the pixel spacing between lines"""
        self._lineSpacing = spacing
        self.updateGraphic()

    def getAlignment(self):
        """Get the current text alignment"""
        return self._alignment

    def setAlignment(self, alignment):
        """Set the text alignment"""
        if not alignment.lower() in ("left", "center", "right"):
            raise Exception("Invalid alignment type")
        else:
            self._alignment = alignment.lower()
        self.updateGraphic()

    def updateGraphic(self):
        """Update the textbox after parameters have been changed"""
        
        self._lineHeight = self._font.get_height() + self._lineSpacing
        
        self._width = TextBox(max(self._lines, key=len),
                              (0,0), self._font,
                              self._fontColor).getWidth() + \
                      (self._hpadding * 2)
        self._height = (self._lineHeight * len(self._lines)) + \
                       (self._vpadding * 2)
        
        lines = self._text.split("\n")
        surf = pygame.Surface((self._width+100, self._height))
        
        # Apply the background color or make transparent
        if self._backgroundColor == None:
            surf.fill((1,1,1))
            surf.set_colorkey((1,1,1))
        else:
            surf.fill(self._backgroundColor)
            
        p = (0,self._vpadding)
        for line in self._lines:
            t = TextBox(line, p, self._font, self._fontColor,
                        self._antialias)
            if self._alignment == "left":
                t.setPosition((self._hpadding, p[1]))
            elif self._alignment == "center":
                t.center(surf, (1/2, None))
            elif self._alignment == "right":
                t.setPosition((self._width-(t.getWidth()+self._hpadding//2),
                               p[1]))
            t.draw(surf)
            p = (0, p[1] + self._lineHeight)
        self._image = surf

        self.updateCentering()
