from typing import Any, Optional

import torch.nn as nn
from torch import Tensor
from torch.nn.modules.loss import _Loss

from rllib.dataset.datatypes import Observation, Termination
from rllib.model import AbstractModel
from rllib.policy import AbstractPolicy
from rllib.reward import AbstractReward
from rllib.util.utilities import RewardTransformer
from rllib.value_function import AbstractQFunction

from .abstract_algorithm import AbstractAlgorithm, ACLoss, TDLoss

class DPG(AbstractAlgorithm):
    q_function: AbstractQFunction
    q_target: AbstractQFunction
    policy: AbstractPolicy
    policy_target: AbstractPolicy
    criterion: _Loss
    gamma: float
    policy_noise: float
    noise_clip: float
    reward_transformer: RewardTransformer
    def __init__(
        self,
        q_function: AbstractQFunction,
        policy: AbstractPolicy,
        criterion: _Loss,
        policy_noise: float,
        noise_clip: float,
        gamma: float,
        reward_transformer: RewardTransformer = ...,
    ) -> None: ...
    def get_q_target(
        self, reward: Tensor, next_state: Tensor, done: Tensor
    ) -> Tensor: ...
    def actor_loss(self, state: Tensor) -> Tensor: ...
    def critic_loss(
        self, state: Tensor, action: Tensor, q_target: Tensor
    ) -> TDLoss: ...
    def forward(self, observation: Observation, **kwargs: Any) -> ACLoss: ...

class MBDPG(DPG):
    dynamical_model: AbstractModel
    reward_model: AbstractReward
    termination: Termination

    num_steps: int
    num_samples: int
    def __init__(
        self,
        q_function: AbstractQFunction,
        policy: AbstractPolicy,
        dynamical_model: AbstractModel,
        reward_model: AbstractReward,
        criterion: _Loss,
        policy_noise: float,
        noise_clip: float,
        gamma: float,
        reward_transformer: RewardTransformer = ...,
        termination: Optional[Termination] = ...,
        num_steps: int = ...,
        num_samples: int = ...,
    ) -> None: ...
    def forward(self, *args: Tensor, **kwargs: Any) -> ACLoss: ...
