from typing import Any

import torch.nn as nn
from torch import Tensor

from rllib.dataset.datatypes import Array, Observation

from .abstract_transform import AbstractTransform

class Normalizer(nn.Module):
    mean: Tensor
    variance: Tensor
    count: Tensor
    preserve_origin: bool
    def __init__(self, preserve_origin: bool = ...) -> None: ...
    def forward(self, *array: Tensor, **kwargs: Any) -> Tensor: ...
    def inverse(self, array: Tensor) -> Tensor: ...
    def update(self, array: Tensor) -> None: ...

class StateActionNormalizer(AbstractTransform):
    _state_normalizer: StateNormalizer
    _action_normalizer: ActionNormalizer
    def __init__(self, preserve_origin: bool = ...) -> None: ...
    def forward(self, *observation: Observation, **kwargs: Any) -> Observation: ...
    def inverse(self, observation: Observation) -> Observation: ...
    def update(self, observation: Observation) -> None: ...

class StateNormalizer(AbstractTransform):
    _normalizer: Normalizer
    def __init__(self, preserve_origin: bool = ...) -> None: ...
    def forward(self, *observation: Observation, **kwargs: Any) -> Observation: ...
    def inverse(self, observation: Observation) -> Observation: ...
    def update(self, observation: Observation) -> None: ...

class NextStateNormalizer(AbstractTransform):
    _normalizer: Normalizer
    def __init__(self, preserve_origin: bool = ...) -> None: ...

class ActionNormalizer(AbstractTransform):
    _normalizer: Normalizer
    def __init__(self, preserve_origin: bool = ...) -> None: ...
    def forward(self, *observation: Observation, **kwargs: Any) -> Observation: ...
    def inverse(self, observation: Observation) -> Observation: ...
    def update(self, observation: Observation) -> None: ...
