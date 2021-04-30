from polybius.managers.abstractManager import AbstractManager

class UIManager():

    # The singleton instance variable
    _INSTANCE = None
   
    @classmethod
    def getInstance(cls):
        """Used to obtain the singleton instance"""
        if cls._INSTANCE == None:
            cls._INSTANCE = cls._UIM()
        return cls._INSTANCE

    class _UIM(AbstractManager):

        def __init__(self):
            self._menuButtons = {}
            
        def setResourcePath(self, path):
           self.readFromCSV(path,self._menuButtons,toLyst=[0], lower=False)
    
        def getControlsForMenu(self, menu):
            return self._menuButtons[menu]

USER_INTERFACE = UIManager.getInstance()

