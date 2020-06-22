from abc import ABCMeta
from typing import Optional, Tuple

import torch.nn as nn
from torch import Tensor

from rllib.dataset.datatypes import Action, TupleDistribution

class AbstractPolicy(nn.Module, metaclass=ABCMeta):
    dim_state: int
    dim_action: int
    num_states: int
    num_actions: int
    deterministic: bool
    tau: float
    discrete_state: bool
    discrete_action: bool
    action_scale: Tensor
    goal: Optional[Tensor]
    def __init__(
        self,
        dim_state: int,
        dim_action: int,
        num_states: int = ...,
        num_actions: int = ...,
        tau: float = ...,
        deterministic: bool = ...,
        action_scale: Action = ...,
        goal: Optional[Tensor] = ...,
    ) -> None: ...
    def forward(self, *args: Tensor, **kwargs) -> TupleDistribution: ...
    def random(
        self, batch_size: Optional[Tuple[int]] = ..., normalized: bool = ...
    ) -> TupleDistribution: ...
    def reset(self) -> None: ...
    def update(self) -> None: ...
    def set_goal(self, goal: Optional[Tensor]) -> None: ...
