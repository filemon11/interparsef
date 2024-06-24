from abc import ABC, abstractmethod

from representations import Representation, Token, Candidate, Constituent
from containers import Container, Buffer, Stack, RepSet, SingleElement, IntBuffer, Counter, RepresentationHolder

from typing import Iterable, TypeVar, TypeVarTuple, Mapping, Set, FrozenSet, Generic, TypedDict, Dict, Tuple, Any

T = TypeVar('T', bound = Representation)
C = TypeVar('C', bound = Container)
Cs = TypeVarTuple('Cs')

class Configuration(tuple[*Cs]):

    def __new__ (cls, *containers : *Cs) -> "Configuration":
        return super(Configuration, cls).__new__(cls, containers) # type: ignore
    
    def __init__(self, *containers : *Cs) -> None:
        """TODO"""
        pass
    
    @property
    def scope(self) -> Tuple[Tuple[Tuple[int, ...], ...], ...]:
        return tuple(container.scope for container in self if isinstance(container, RepresentationHolder))
    
    def format(self : tuple[*Cs], token_info : Mapping[int, str] | None = None, padding : int = 10,
               show_name : bool = True, delimiter : str = " || ") -> str:
        return delimiter.join([container.format(token_info, padding, show_name) for container in self]) # type: ignore
    
    def __str__(self) -> str:
        return self.format(padding = 0, show_name = False)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.format(padding = 0, show_name = True)})"

class StackBufferConfiguration(Configuration[Stack[T], Buffer[T]]):
    def __init__(self, tokens : Iterable[Token]) -> None:
        self.buffer : Buffer = Buffer(tokens)
        self.stack : Stack[T] = Stack([])
    
    def format(self, token_info : Mapping[int, str] | None = None, padding : int = 10,
               show_name : bool = False, delimiter : str = " || ") -> str:
        return super().format(token_info, padding,
                              show_name = show_name,
                              delimiter = delimiter)
    
class SetConfiguration(Configuration[IntBuffer, SingleElement[Candidate], 
                                     RepSet[Candidate], RepSet[Constituent],
                                     Counter]):
    def __init__(self, buffer : IntBuffer, focus : SingleElement[Candidate], 
                 repset : RepSet[Candidate], labelled : RepSet[Constituent], step : Counter = Counter(0)) -> None:
        super().__init__(buffer, focus, repset, labelled, step)
        self.buffer : IntBuffer = self[0]
        self.focus : SingleElement[Candidate] = self[1]
        self.repset : RepSet[Candidate] = self[2]
        self.labelled : RepSet[Constituent] = self[3]
        self.step : Counter = self[4]
    
    def format(self, token_info : Mapping[int, str] | None = None, padding : int = 10,
               show_name : bool = False, delimiter : str = " || ") -> str:
        return f"{delimiter.join([
                                self.repset.format(token_info, -padding, show_name), 
                                self.focus.format(token_info, show_name = show_name),
                                self.buffer.format(token_info, show_name),
                                self.labelled.format(token_info, padding, show_name)
                                ])} : {self.step.format(show_name = show_name)}"
    
def init_SetConfiguration(num_tokens : int) -> SetConfiguration:
    buffer : IntBuffer = IntBuffer(num_tokens, name = "Buffer")
    focus : SingleElement[Candidate] = SingleElement(name = "Focus")
    repset : RepSet[Candidate] = RepSet(name = "Candidates")
    labelled : RepSet[Constituent] = RepSet(name = "Constituents")
    step : Counter = Counter(name = "Step")
    return SetConfiguration(buffer, focus, repset, labelled, step)