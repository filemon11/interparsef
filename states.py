
from transitions import Transition
from containers import Container

from typing import List, TypeVar, Generic, Iterable, FrozenSet, Mapping, Tuple, DefaultDict, Self, Type

Tr = TypeVar('Tr', bound = Transition)

class State(Container["State"], DefaultDict[Type[Tr], "State | None"]):
    def __init__(self, name : str | None = None) -> None:
        super().__init__(lambda : None)
        self._name : str = name if name is not None else str(id(self))

    def _format(self, token_info : Mapping[int, str] | None = None, padding : int = 0,
               show_name : bool = True) -> str:
        def tr(transition : Type[Tr], state : State) -> str:
            return f"{transition.__name__} => {state.name}"
        return ', '.join([tr(transition, self[transition]) # type: ignore
                                                for transition in self.keys() if self[transition] is not None])
    
    def __str__(self) -> str:
        return self.format(padding = 0)
    
    def __repr(self) -> str:
        return str(self)
    

from transitions import SetTransition, SetOdd, SetEven, SetShift, SetCombine, SetLabel, SetNoLabel
from configurations import init_SetConfiguration
c = init_SetConfiguration(2)

q1 : State[SetTransition] = State("q1")
q2 : State[SetTransition] = State("q2")
q1[SetShift] = q2
q1[SetCombine] = q2
q2[SetLabel] = q1
q2[SetNoLabel] = q1

print(q1.format())
print(q2.format())
