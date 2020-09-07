"""
A Singleton Frame Manager class
Author: Liz Matthews, 9/20/2019
Author: Trevor Stalnaker

Provides on-demand loading of images for a pygame program.

"""

from pygame import image, Surface, Rect
from .abstractManager import AbstractManager
from pathlib import Path
import os



class FrameManager():
   """A singleton factory class to create and store frames on demand."""
   
   # The singleton instance variable
   _INSTANCE = None
   
   @classmethod
   def getInstance(cls):
      """Used to obtain the singleton instance"""
      if cls._INSTANCE == None:
         cls._INSTANCE = cls._FM()
      
      return cls._INSTANCE
   
   # Do not directly instantiate this class!
   class _FM(AbstractManager):
      """An internal FrameManager class to contain the actual code. Is a private class."""
      
      def __init__(self):
         self._surfaces = {}
         self._images = {}
         #self._image_folder = None

      def prepareImage(self, filePath, dimensions=(32,32), colorKey=False):
         """Prepare an image to be loaded later"""
         if not os.path.exists(filePath):
            raise Exception("The path " + filePath + " does not exist")
         else:
            fileName = Path(filePath).name
            self._images[fileName]={"frame_dimensions":dimensions, "color_key":colorKey,
                                    "path":filePath}
         
      def prepareImagesFromCSV(self, csv_path, folder_path=""):
         """Prepare a group of images from a csv file"""
         self.readFromCSV(csv_path, self._images, lower=False)
         for key in self._images.keys():
            path = os.path.join(folder_path, key)
            if not os.path.exists(path):
               raise Exception("The path " + path + " does not exist")
            else:
               self._images[key]["path"] = path
        
      def __getitem__(self, key):
         return self._surfaces[key]
   
      def __setitem__(self, key, item):
         self._surfaces[key] = item
      
      def getFrame(self, fileName, offset=None):
         """Returns the requested frame if possible"""

         # Check if the file name provided is a full path to a known image
         if fileName in [self._images[k]["path"] for k in self._images.keys()]:
            fileName = Path(fileName).name
            
         # Check if this is a novel image
         elif fileName not in self._images.keys():
            self.prepareImage(fileName)
            fileName = Path(fileName).name
            
         # If this frame has not already been loaded, load the image from memory
         if fileName not in self._surfaces.keys():
            
            self._loadImage(fileName, sheet=offset!=None)
         
         # If this is an image sheet, return the correctly offset sub surface
         if offset != None:
            return self[fileName][offset[1]][offset[0]]
         
         # Otherwise, return the sheet created
         return self[fileName]

      def _loadImage(self, fileName, sheet=False):
         """Loads an image and saves it to the internal surfaces dictionary"""

         colorKey = self._images[fileName]["color_key"]

         # Load the full image
         fullImage = image.load(self._images[fileName]["path"])
         fullImage = fullImage.convert()
         
         # If the image to be loaded is an image sheet, split it up based on the frame size
         if sheet:
               
            self[fileName] = []

            dimensions = self._images[fileName]["frame_dimensions"]
            sheetDimensions = fullImage.get_size()
            
            for y in range(0, sheetDimensions[1], dimensions[1]):
               self[fileName].append([])
               for x in range(0, sheetDimensions[0], dimensions[0]):
                  
                  frame = Surface(dimensions)    
                  frame.blit(fullImage, (0,0), Rect((x,y), dimensions))
                  
                  # If we need to set the color key
                  if colorKey:
                     frame.set_colorkey(frame.get_at((0,0)))
                  
                  self[fileName][-1].append(frame)
         else:
            
            self[fileName] = fullImage
               
            # If we need to set the color key
            if colorKey:
               self[fileName].set_colorkey(self[fileName].get_at((0,0)))

                     
# Set up an instance for others to import         
FRAMES = FrameManager.getInstance()
