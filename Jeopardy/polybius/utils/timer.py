class Timer:

    def __init__(self, initialTime):

        # Assert that the initialTime is an int or a function
        assert type(initialTime) in (int, float) or callable(initialTime)

        # If initialTime is a function, assert that it returns an int
        assert not callable(initialTime) or type(initialTime()) in (int, float)

        self._initialTime = initialTime
            
        self.resetTimer()

    def resetTimer(self):
        if type(self._initialTime) in [int, float]:
            self._timer = self._initialTime
        if callable(self._initialTime):
            self._timer = self._initialTime()

    def update(self, ticks, func):
        self._timer -= ticks
        if self._timer <= 0:
            func()
            self.resetTimer()
