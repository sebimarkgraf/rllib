from .abstract_policy import AbstractPolicy
from rllib.dataset.datatypes import Distribution
from typing import List, Iterator
from torch import Tensor
from rllib.util.neural_networks import ProbabilisticNN


class NNPolicy(AbstractPolicy):
    policy: ProbabilisticNN
    tau: float

    def __init__(self, dim_state: int, dim_action: int,
                 num_states: int = None, num_actions: int = None,
                 layers: List[int] = None, biased_head: bool = True,
                 tau: float = 1., deterministic: bool = False) -> None: ...

    def __call__(self, state: Tensor) -> Distribution: ...

    def embeddings(self, state: Tensor, action: Tensor = None) -> Tensor: ...

    @property
    def parameters(self) -> Iterator: ...

    @parameters.setter
    def parameters(self, new_params: Iterator) -> None: ...


class FelixPolicy(NNPolicy):

    def __init__(self, dim_state: int, dim_action: int,
                 num_states: int = None, num_actions: int = None,
                 tau: float = 1., deterministic: bool = False) -> None: ...
