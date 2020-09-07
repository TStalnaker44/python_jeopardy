"""
Author: Trevor Stalnaker, Justin Pusztay
File: fsm.py

A class that models a finite state machine
"""

class FSM():
    """
    Models a generalized finite state machine
    """

    def __init__(self, startState, states, transitions):
        self._state = startState
        self._startState = startState
        self._states = states
        self._transitions = transitions

    def changeState(self, action):
        """
        Changes the state based on the action
        """
        for rule in self._transitions:
            if rule.getStartState() == self._state and \
               rule.getAction() == action:
                self._state = rule.getEndState()
            
    def getCurrentState(self):
        """
        Returns the current state
        """
        return self._state

    def getStates(self):
        """
        Returns all the possible states.
        """
        return self._states

    def getTransitions(self):
        """
        Returns the transitions.
        """
        return self._transitions

    def backToStart(self):
        """
        Returns the FSM to the start state.
        """
        self._state = self._startState

class Rule():
    """
    Models a transition in a finite state machine
    """

    def __init__(self, state1, action, state2):
        self._startState = state1
        self._action = action
        self._endState = state2

    def getStartState(self):
        """
        Returns the start state.
        """
        return self._startState

    def getAction(self):
        """
        Returns the action
        """
        return self._action

    def getEndState(self):
        """
        Returns the end state
        """
        return self._endState

    def __repr__(self):
        """
        Returns a reprsentation of the rule.
        """
        return "(" + str(self._startState) + "," + str(self._symbol) + \
               "," + str(self._endState) + ")"

