
import pygame
from polybius.graphics.basics.drawable import Drawable

class AbstractGraphic(Drawable):

    def __init__(self, position):

        super().__init__("", position, worldBound=False)
        self._keepCenter = False

    def center(self, surface=None, cen_point=(1/2,1/2), multisprite=False):

        # Get the fractional coordinates to center around
        cen_x, cen_y = cen_point

        # Determine the dimensions of the surface
        if surface == None: #include normal pygame surfaces here as well
            surface = pygame.display.get_surface()
        
        surf_x = surface.get_width()
        surf_y = surface.get_height()

        # Get half the dimensions of the graphic
        x = self.getWidth() // 2
        y = self.getHeight() // 2

        # Calculate the new x and y position
        if cen_x != None:
            x_pos = int(surf_x * cen_x) - x
        else:
          x_pos = self.getX()
        if cen_y != None:
            y_pos = int(surf_y * cen_y) - y
        else:
            y_pos = self.getY()

        # Handle the offset caused by a multisprite setup
        if multisprite:
            if cen_x!=None: x_pos += surface.getX()
            if cen_y!=None: y_pos += surface.getY()
                    
        self.setPosition((x_pos, y_pos))

    def keepCentered(self, surface=None, cen_point=(1/2,1/2), multisprite=False):
        self._centeringData = (surface, cen_point, multisprite)
        self._keepCenter = True
        self.center(*self._centeringData)

    def turnCenteringOff(self):
        self._keepCenter = False

    def shiftRGBValues(self, color, amount):
        """Shift a tuple of rgb values by a tuple of amounts"""
        assert len(color) == 3
        assert len(amount) == 3
        r,g,b = color
        i,j,k = amount
        return (max(0,min(r+i,255)),
                max(0,min(g+j,255)),
                max(0,min(b+k,255)))

    def updateCentering(self):
        if self._keepCenter:
            self.center(*self._centeringData)

    def updateGraphic(self):
        """A default method for updating a graphic"""

        # Draw the base layer (what will become the border)
        surfBack = pygame.Surface((self._width, self._height))
        surfBack.fill(self._borderColor)

        # Draw the primary surface
        surf = pygame.Surface((self._width-(self._borderWidth*2),
                               self._height-(self._borderWidth*2)))
        
        # Apply the background color or make transparent
        if self._backgroundColor == None:
            surf.fill((1,1,1))
            surfBack.set_colorkey((1,1,1))
        else:
            surf.fill(self._backgroundColor)

        # Add widgets to the primary surface according to kind
        self.internalUpdate(surf)

        # Draw the primary surface onto the base layer
        surfBack.blit(surf, (self._borderWidth, self._borderWidth))

        # Set the image to the created surface
        self._image = surfBack

        # Update the centering on the graphic
        self.updateCentering()

    def internalUpdate(self, surf):
        """A placeholder method that can be replaced in child classes"""
        pass
        
        
