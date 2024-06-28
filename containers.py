from representations import Representation, Token

from typing import List, TypeVar, Generic, Iterable, FrozenSet, Mapping, Sequence
from abc import ABC, abstractmethod, abstractproperty

A = TypeVar('A')
T = TypeVar('T', bound = Representation)

class Container(ABC, Generic[A]):
    _name : str | None

    @classmethod
    def adjust(cls, sequence : str, padding : int) -> str:
        if padding >= 0:
            return sequence.ljust(padding)
        else:
            return sequence.rjust(-padding)

    def format(self, token_info : Mapping[int, str] | None = None, padding : int = 0, show_name : bool = True) -> str:
        sequence : str
        if show_name:
            sequence = f"{self.name}({self._format(token_info)})"
        else:
            sequence = self._format(token_info)
        return self.adjust(sequence, padding)

    @abstractmethod
    def _format(self, token_info : Mapping[int, str] | None) -> str:
        ...  

    def __str__(self) -> str:
        return self.format(show_name = True)
    
    def __repr__(self) -> str:
        if self._name is not None:
            return f"{self.__class__.__name__}({self.format(show_name = False)}, name={self.name})"
        else:
            return f"{self.__class__.__name__}({self.format(show_name = False)})"

    @property
    def name(self) -> str:
        if self._name is not None:
            return self._name
        else:
            return self.__class__.__name__

class Counter(Container[int], int):
    """TODO
    WARNING: Does not implement dunder methods
    """
    def __new__(cls, value : int = 0, name : str | None = None) -> "Counter":
        return super(Counter, cls).__new__(cls, value)
        
    def __init__(self, value : int = 0, name : str | None = None) -> None:
        """TODO"""
        self._name = name

    def _format(self, token_info : Mapping[int, str] | None = None) -> str:
        return str(self.__int__())
    
    def increment(self, value : int = 1) -> "Counter":
        return Counter(self + value)

class RepresentationHolder(Container[T]):
    @abstractmethod
    def some(self) -> T | None:
        ...

    @abstractproperty
    def empty(self) -> bool:
        ...

    @abstractproperty
    def scope(self) -> tuple[tuple[int, ...], ...]:
        ...

class OrderedRepresentationHolder(RepresentationHolder[T], Sequence):
    _scope_size : int

    @abstractproperty
    def top(self) -> T | None:
        ...

    def some(self) -> T | None:
        return self.top

    @property
    def scope(self) -> tuple[tuple[int, ...], ...]:
        num_retrieve : int = min(self._scope_size, len(self))
        num_padding : int = self._scope_size - num_retrieve

        scope : tuple[tuple[int, ...], ...] = tuple(rpr.scope for rpr in self[-num_retrieve:])

        return scope + tuple(num_padding * ((-1,),)) 

class Stack(tuple[T], OrderedRepresentationHolder[T]):
    """TODO
    """
    def __new__ (cls, content : Iterable[T] | None = None, scope_size : int = 2, name : str | None = None) -> "Stack":
        if content is None:
            return super(Stack, cls).__new__(cls, []) # type: ignore
        else:
            return super(Stack, cls).__new__(cls, content) # type: ignore
        
    def __init__(self, content : Iterable[T] | None = None, scope_size : int = 2, name : str | None = None) -> None:
        """TODO"""
        self._name = name
        self._scope_size : int = scope_size

    def push(self, item : T) -> "Stack[T]":
        "TODO"
        return(Stack((*self, item)))
    
    def pop(self) -> tuple["Stack[T]", T]:
        "TODO"
        return Stack(self[:-1]), self[-1]
    
    @property
    def empty(self) -> bool:
        return len(self) == 0
    
    @property
    def top(self) -> T:
        return self[-1]

    def _format(self, token_info : Mapping[int, str] | None = None) -> str:
        return ", ".join((item.format(token_info) for item in self))

class Buffer(tuple[T], OrderedRepresentationHolder[T]):
    """TODO"""
    def __new__ (cls, content : Iterable[T] | None = None,
                 _curr_idx : int = 0, 
                 scope_size : int = 1, 
                 name : str | None = None) -> "Buffer":
        if content is None:
            return super(Buffer, cls).__new__(cls, []) # type: ignore
        else:
            return super(Buffer, cls).__new__(cls, content) # type: ignore
    
    def __init__(self, content : Iterable[T] | None = None,
                 _curr_idx : int = 0, 
                 scope_size : int = 2, 
                 name : str | None = None) -> None:
        self._curr_idx : int = _curr_idx
        self._name = name
        self._scope_size : int = scope_size


    def next(self) -> tuple["Buffer[T]", T]:
        new_buffer : Buffer = Buffer(self, self._curr_idx + 1)
        return new_buffer, self[self._curr_idx]
    
    @property
    def empty(self) -> bool:
        return len(self) == 0
    
    @property
    def top(self) -> T:
        return self[-1]
    
    def _format(self, token_info : Mapping[int, str] | None = None) -> str:
        return ", ".join((item.format(token_info) for item in self[self._curr_idx:]))
    
class IntBuffer(Buffer[Token]):
    """TODO"""
    def __new__ (cls, max_idx : int,
                 start_idx : int = 0, 
                 scope_size : int = 2, 
                 name : str | None = None) -> "IntBuffer":
        return super(IntBuffer, cls).__new__(cls, tuple(), start_idx, scope_size, name) # type: ignore
        
    def __init__(self, max_idx : int, 
                 start_idx : int = 0,  
                 scope_size : int = 1, 
                 name : str | None = None) -> None:
        super().__init__(tuple(), start_idx, scope_size, name)
        self._max_idx : int = max_idx

    def next(self) -> tuple["IntBuffer", Token]:
        if self.empty:
            raise Exception
        
        new_buffer : IntBuffer = IntBuffer(self._max_idx, self._curr_idx + 1)
        return new_buffer, Token(self._curr_idx)
    
    @property
    def empty(self) -> bool:
        if self._curr_idx == self._max_idx:
            return True
        else:
            return False

    @property
    def top(self) -> Token:
        return Token(self._curr_idx)
    
    @property
    def scope(self) -> tuple[tuple[int, ...], ...]:
        num_retrieve : int = min(self._scope_size, len(self))
        num_padding : int = self._scope_size - num_retrieve

        scope : tuple[tuple[int, ...], ...] = tuple((i,) for i in range(self._curr_idx, self._curr_idx + num_retrieve))

        return scope + tuple(num_padding * ((-1,),))
    
    def __len__(self) -> int:
        return self._max_idx - self._curr_idx

    def format(self, token_info : Mapping[int, str] | None = None, padding : int = 0, show_name : bool = True) -> str:
        sequence : str
        if show_name:
            sequence = f"{self.name}({self._format(token_info)})"
        else:
            sequence = f"({self._format(token_info)})"
        return self.adjust(sequence, padding)
    
    def _format(self, token_info : Mapping[int, str] | None = None) -> str:
        return f"{Token(self._curr_idx).format(token_info)} : {self._max_idx}"
    
    def __repr__(self) -> str:
        if self._name is not None:
            return f"{self.__class__.__name__}({self.format(show_name = False)}, name={self.name})"
        else:
            return f"{self.__class__.__name__}({self.format(show_name = False)})"
    
class RepSet(FrozenSet[T], RepresentationHolder[T]):
    def __new__ (cls, content : Iterable[T] | None = None, name : str | None = None) -> "RepSet":
        if content is None:
            return super(RepSet, cls).__new__(cls, []) # type: ignore
        else:
            return super(RepSet, cls).__new__(cls, content) # type: ignore
    
    def __init__(self, content : Iterable[T] | None = None, name : str | None = None) -> None:
        """TODO"""
        self._name = name
    
    def some(self) -> T:
        return next(iter(self))
    
    def add(self, element : T) -> "RepSet[T]":
        return RepSet((*self, element))

    def remove(self, element : T) -> "RepSet[T]":
        return RepSet(self.difference((element,)))

    @property
    def empty(self) -> bool:
        return len(self) != 0
    
    @property
    def scope(self) -> tuple[tuple[int, ...], ...]:
        return tuple(rpr.scope for rpr in self)

    def _format(self, token_info : None | Mapping[int, str] = None) -> str:
        return ','.join([ccandidate.format(token_info) for ccandidate in self])
    
class SingleElement(tuple[T], OrderedRepresentationHolder[T]):
    def __new__ (cls, item : T | None = None, name : str | None = None) -> "SingleElement":
        if item is None:
            return super(SingleElement, cls).__new__(cls, tuple()) # type: ignore
        else:
            return super(SingleElement, cls).__new__(cls, (item, )) # type: ignore
        
    def __init__(self, item : T | None = None, name : str | None = None) -> None:
        """TODO"""
        self._name = name
        self._element : T | None = item

    def replace(self, item : T | None) -> tuple["SingleElement", T | None]:
        return SingleElement(item), self._element
    
    @property
    def empty(self) -> bool:
        return self._element is None

    @property
    def top(self) -> T | None:
        return self._element

    @property
    def scope(self) -> tuple[tuple[int, ...], ...]:
        if self.empty:
            return ((-1,),)
        else:
            assert(self._element is not None)
            return (self._element.scope, )
    
    def _format(self, token_info : None | Mapping[int, str] = None) -> str:
        if self._element is None:
            return "n.a."
        return self._element.format(token_info)