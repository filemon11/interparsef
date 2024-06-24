from representations import Representation, Token, Candidate, Constituent
from containers import Buffer, Stack, RepSet, SingleElement, IntBuffer
from configurations import Configuration, SetConfiguration

from typing import Iterable, TypeVar, Mapping, Set, FrozenSet, Generic, overload
from abstract_helpers import ABC, abstractmethod

T = TypeVar('T', bound = Configuration)

class Transition(ABC, Generic[T]):
    @abstractmethod
    def apply(self, configuration : T) -> T:
        ...

    @abstractmethod
    def check(self, configuration : T) -> bool:
        ...

    def __call__(self, configuration : T) -> T:
        return self.apply(configuration)
    
class SetTransition(Transition[SetConfiguration]):
    @abstractmethod
    def apply(self, configuration : SetConfiguration) -> SetConfiguration:
        ...

    @abstractmethod
    def check(self, configuration : SetConfiguration) -> bool:
        ...

class SetEven(SetTransition):
    def check(self, configuration : SetConfiguration) -> bool:
        if configuration.step % 2 == 0:
            return True
        else:
            return False

class SetOdd(SetTransition):
    def check(self, configuration : SetConfiguration) -> bool:
        if configuration.step % 2 == 0:
            return False
        else:
            return True

class SetShift(SetEven):

    def apply(self, configuration : SetConfiguration) -> SetConfiguration:
        new_buffer : IntBuffer
        new_focus : SingleElement[Candidate]
        new_set : RepSet[Candidate]

        new_item : Token
        shifted_element : Candidate | None

        new_buffer, new_item = configuration.buffer.next()
        new_focus, shifted_element = configuration.focus.replace(Candidate((new_item,)))

        if shifted_element is not None:
            new_set = configuration.repset.add(shifted_element)
            return SetConfiguration(new_buffer, new_focus, new_set, 
                                    configuration.labelled, configuration.step.increment())
        
        else:
            return SetConfiguration(new_buffer, new_focus, 
                                    configuration.repset, configuration.labelled,
                                    configuration.step.increment())
        
    def check(self, configuration : SetConfiguration) -> bool:
        return (not configuration.buffer.empty) and super().check(configuration)

class SetCombine(SetEven):
    def __init__(self, selected : Candidate):
        self.selected : Candidate = selected
    
    def apply(self, configuration : SetConfiguration) -> SetConfiguration:
        assert(configuration.focus.top)

        new_focus : SingleElement[Candidate]
        new_set : RepSet[Candidate]

        new_set = configuration.repset.remove(self.selected)

        new_focus = SingleElement(configuration.focus.top.merge(self.selected))

        return SetConfiguration(configuration.buffer, new_focus, new_set, 
                                configuration.labelled, configuration.step.increment())
    
    def check(self, configuration : SetConfiguration) -> bool:
        return (self.selected in configuration.repset) and super().check(configuration)
        
class SetLabel(SetOdd):
    def __init__(self, label : str):
        self.label : str = label
    
    def apply(self, configuration : SetConfiguration) -> SetConfiguration:
        assert(configuration.focus.top)

        constituent : Constituent = Constituent(configuration.focus.top, self.label)

        return SetConfiguration(configuration.buffer, configuration.focus, 
                                configuration.repset, configuration.labelled.add(constituent),
                                configuration.step.increment())

class SetNoLabel(SetOdd):
    "TODO"
    
    def apply(self, configuration : SetConfiguration) -> SetConfiguration:
        return SetConfiguration(configuration.buffer, configuration.focus, 
                                configuration.repset, configuration.labelled,
                                configuration.step.increment())

    def check(self, configuration : SetConfiguration) -> bool:
        return ((not configuration.repset.empty) 
                and (not configuration.buffer.empty) 
                and super().check(configuration))

A = TypeVar('A', bound = Transition)

class TransitionSet(ABC, Set[A]):
    @abstractmethod
    def generate(self, configuration : Configuration, labels : Iterable[str]) -> "TransitionSet":
        pass

    def checkall(self, configuration : Configuration) -> Set[A]:
        out_set : Set[A] = {transition for transition 
                                      in self if transition.check(configuration)}
        
        return out_set

class SetTransitionSet(TransitionSet[SetTransition]):
    @staticmethod
    def generate(configuration : Configuration, labels : Iterable[str]) -> "SetTransitionSet":
        assert(isinstance(configuration, SetConfiguration))
        transition_set : Set[SetTransition] = set((SetShift(), SetNoLabel()))

        for label in labels:
            transition_set.add(SetLabel(label))

        for candidate in configuration.repset:
            transition_set.add(SetCombine(candidate))
        
        return SetTransitionSet(transition_set)

    def __init__(self, transitions : Iterable[SetTransition]):
        super().__init__(transitions)
