from abc import ABCMeta
from rllib.policy import AbstractPolicy
from torch import Tensor
import torch.nn as nn
import torch.jit
from torch.nn import Parameter
from typing import Iterator


class AbstractValueFunction(nn.Module, metaclass=ABCMeta):
    dim_state: int
    num_states: int
    tau: float
    discrete_state: bool

    def __init__(self, dim_state: int, num_states: int = None, tau: float = 1.) -> None: ...

    def forward(self, *args:Tensor, **kwargs) -> Tensor: ...

    def update_parameters(self, new_parameters: Iterator[Parameter]) -> None: ...


class AbstractQFunction(AbstractValueFunction):
    dim_action: int
    num_actions: int
    discrete_action: bool

    def __init__(self, dim_state: int, dim_action: int,
                 num_states: int = None, num_actions: int = None, tau: float = 1.) -> None: ...

    def value(self, state: Tensor, policy: AbstractPolicy, n_samples: int = 1
              ) -> Tensor: ...
