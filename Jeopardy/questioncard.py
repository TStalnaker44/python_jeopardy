
import pygame
from polybius.graphics import *

class QuestionCard(AbstractGraphic):

    def __init__(self, question):

        AbstractGraphic.__init__(self, (0,0))

        self._question = question

        self._width = 1200
        self._height = 700
        
        self._backgroundColor = (6, 12, 233)
        self._borderColor = (255, 255, 255)
        self._borderWidth = 2

        self._font = pygame.font.SysFont("futura bold", 64)
        self._fontColor = (255, 255, 255)

        self.updateGraphic()

    def internalUpdate(self, surf):
        """Update the button after parameters have been changed"""

        # Use the current background color
        surf.fill(self._backgroundColor)

        # Create and draw the internal textbox
        t = MultiLineTextBox(self._question, (0,0), self._font,
                    self._fontColor)
        t.center(surf)
        t.draw(surf)

    
