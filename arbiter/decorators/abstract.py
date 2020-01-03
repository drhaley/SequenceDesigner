#Arbiter is built with the decorator pattern.  Wrap new tests around the base class

import abc

class AbstractArbiterDecorator(abc.ABC):

    @abc.abstractmethod
    def _check_single_condition(self, sequence):
        """
        returns True if sequence is to be 'accepted'

        has access to self._oracle, self._collection, self._threshold, etc.
        """
        pass




    ################################
    # the following are not abstract methods
    # and should not be overridden without calling back to them through super()
    ################################

    def __init__(self, parent):
        self._parent = parent

    @property
    def _oracle(self):
        return self._parent._oracle

    @property
    def _collection(self):
        return self._parent._collection

    def consider(self, sequence):
        this_condition_result = self._check_single_condition(sequence)
        if this_condition_result == True:
            return self._parent.consider(sequence)  #passthrough
        elif this_condition_result == False:
            return False
        else:
            raise AssertionError(f"received non-Bool from arbiter check condition: {this_condition_result}")
