from rllib.dataset.datatypes import State, Action, Reward, Done
from .abstract_dpg_agent import AbstractDPGAgent
from typing import Tuple
from torch import Tensor


class DPGAgent(AbstractDPGAgent):

    def _td(self, state: State, action: Action, reward: Reward, next_state: State,
            done: Done) -> Tuple[Tensor, Tensor]: ...
