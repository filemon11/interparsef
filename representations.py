from abc import ABC, abstractmethod, abstractproperty

from typing import Iterable, TypeVar, Mapping, FrozenSet, Generic

R = TypeVar('R', bound = "Representation")

class Representation(ABC):

    @abstractmethod
    def format(self, token_info : Mapping[int, str] | None) -> str:
        ...

    @abstractproperty
    def scope(self) -> tuple[int, ...]:
        ...

class Token(int, Representation):
    def __new__ (cls, index : int) -> "Token":
        return super(Token, cls).__new__(cls, index) # type: ignore
    
    def __init__(self, index : int) -> None:
        pass
    
    def format(self, token_info : None | Mapping[int, str] = None) -> str:
        if token_info is not None:
            return f"{self}:{token_info[self]}"
        else:
            return str(self)
    
    @property
    def scope(self) -> tuple[int]:
        return (self,)
        
class Candidate(FrozenSet[Token], Representation):
    def __new__ (cls, tokens : Iterable[Token]) -> "Candidate":
        return super(Candidate, cls).__new__(cls, tokens) # type: ignore
    
    def __init__(self, tokens : Iterable[Token]) -> None:
        """TODO"""
        pass

    def merge(self, token : "Candidate") -> "Candidate":
        return Candidate((*self, *token))
    
    @property
    def scope(self) -> tuple[int, ...]:
        return (min(self), max(self)) # TODO

    def __str__(self) -> str:
        return self.format()

    def __repr__(self) -> str:
        return self.format()
    
    def format(self, token_info : None | Mapping[int, str] = None) -> str:
        return f"{{{','.join([token.format(token_info) for token in self])}}}"
        
class Constituent(Candidate):
    def __new__ (cls, tokens : Iterable[Token], label : str) -> "Constituent":
        return super(Constituent, cls).__new__(cls, tokens) # type: ignore
    
    def __init__(self, tokens : Iterable[Token], label : str) -> None:
        """TODO"""
        self.label : str = label
    
    def format(self, token_info : None | Mapping[int, str] = None) -> str:
        return f"({self.label},{{{','.join([token.format(token_info) for token in self])}}})"


class Label(str, Representation):
    def __new__ (cls, label : str) -> "Label":
        return super(Label, cls).__new__(cls, label) # type: ignore
    
    def __init__(self, label : str) -> None:
        pass
    
    def format(self, *args: object, **kwargs: object) -> str:
        return str(self)
    
    @property
    def scope(self) -> tuple[int, ...]:
        return tuple()
    
class Node(Generic[R], "tuple[Node[R], ...]", Representation):
    def __new__ (cls, content : R, 
                 children : tuple[Node[R], ...] = tuple()) -> "Node":
        
        return super(Node, cls).__new__(cls, children) # type: ignore
    
    def __init__(self, content : R, 
                 children : tuple[Node[R], ...] = tuple()):
        self.content : R = content

    def format(self, token_info : None | Mapping[int, str] = None) -> str:
        return f"({self.content.format(token_info)} {' '.join(c.format(token_info) for c in self)})"
    
    @property
    def scope(self) -> tuple[int, ...]:
        if len(self) == 0:
            if isinstance(self.content, Token):
                return self.content.scope
            else:
                return tuple()
        elif len(self) == 1:
            return self[0].scope
        else:
            return self[0].scope + self[-1].scope