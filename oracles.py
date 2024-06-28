from configurations import Configuration, SetConfiguration
from transitions import Transition, SetTransition
from containers import RepSet, Container, RepresentationHolder
from representations import Constituent, Representation

from typing import Callable, TypeVar

from abc import ABC, abstractmethod, abstractclassmethod

R = TypeVar("R", bound = Representation)

def set_oracle(configuration : SetConfiguration, gold_tree : RepSet[Constituent]) -> SetTransition:
    pass