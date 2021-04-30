import pygame

class EventWrapper():
    """A wrapper class for pygame events"""

    def __init__(self, t, key, mods=[]):
        """Creates an event"""

        self._type = t
        self._key = key
        self._mods = mods

    def check(self, event):
        """Checks if the event has happened by comparing
        to an event from the event queue"""
        if event.type == self._type:
            if hasattr(event, 'button') and event.button==self._key:
                if all(pygame.key.get_mods() & mod for mod in self._mods):
                    return True
            elif hasattr(event, 'key') and event.key==self._key:
                if all(event.mod & mod for mod in self._mods):
                    return True
        return False

    def getType(self):
        return self._type

    def getKey(self):
        return self._key

    def getMods(self):
        return self._mods

    def __str__(self):
        return "Event type: " + str(self._type) + \
               "\nEvent key: " + str(self._key) + \
               "\nEvent mods: " + str(self._mods)
            
