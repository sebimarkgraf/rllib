"""Implementation of different Neural Networks with pytorch."""

import torch.nn as nn
from torch import Tensor
from typing import List
from rllib.dataset.datatypes import TupleDistribution


class DeterministicNN(nn.Module):
    layers = List[int]
    embedding_dim: int
    hidden_layers: nn.Sequential
    head: nn.Linear

    def __init__(self, in_dim: int, out_dim: int, layers: List[int] = None,
                 biased_head: bool = True) -> None: ...

    def forward(self, *args: Tensor, **kwargs) -> TupleDistribution: ...

    def last_layer_embeddings(self, x: Tensor) -> Tensor: ...


class ProbabilisticNN(DeterministicNN):

    def __init__(self, in_dim: int, out_dim: int, layers: List[int] = None,
                 biased_head: bool = True) -> None: ...


class HeteroGaussianNN(ProbabilisticNN):
    _covariance: nn.Linear

    def __init__(self, in_dim: int, out_dim: int, layers: List[int] = None,
                 biased_head: bool = True, squashed_output: bool = True) -> None: ...


    def forward(self, *args: Tensor, **kwargs) -> TupleDistribution: ...


class HomoGaussianNN(ProbabilisticNN):
    _covariance: nn.Parameter

    def __init__(self, in_dim: int, out_dim: int, layers: List[int] = None,
                 biased_head: bool = True, squashed_output: bool = True) -> None: ...

    def forward(self, *args: Tensor, **kwargs) -> TupleDistribution: ...


class CategoricalNN(ProbabilisticNN):

    def __init__(self, in_dim: int, out_dim: int, layers: List[int] = None,
                 biased_head: bool = True) -> None: ...

    def forward(self, *args: Tensor, **kwargs) -> TupleDistribution: ...


class EnsembleNN(ProbabilisticNN):
    num_heads: int

    def __init__(self, in_dim: int, out_dim: int, layers: List[int] = None,
                 biased_head: bool = True) -> None: ...

    def forward(self, *args: Tensor, **kwargs) -> TupleDistribution: ...


class FelixNet(nn.Module):
    layers: List[int]
    linear1: nn.Linear
    linear2: nn.Linear
    _mean: nn.Linear
    _covariance: nn.Linear

    def __init__(self, in_dim: int, out_dim: int) -> None: ...

    def forward(self, *args: Tensor, **kwargs) -> TupleDistribution: ...