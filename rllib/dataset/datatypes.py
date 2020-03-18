"""Project Data-types."""
import numpy as np
import torch
from torch import Tensor
from typing import NamedTuple, Union, Tuple
from torch.distributions import Categorical
from gpytorch.distributions import Delta, MultivariateNormal


Array = Union[np.ndarray, torch.Tensor]
State = Union[int, float, Array]
Action = Union[int, float, Array]
Reward = Union[int, float, Array]
Probability = Union[int, float, Array]
Done = Union[bool, Array]
Gaussian = Union[MultivariateNormal, Delta]
Distribution = Union[MultivariateNormal, Delta, Categorical]
TupleDistribution = Union[Tensor, Tuple[Tensor, Tensor]]


class Observation(NamedTuple):
    """Observation datatype."""

    state: State
    action: Action
    reward: Reward = np.nan
    next_state: State = np.nan
    done: Done = True
    next_action: Action = np.nan  # SARSA algorithm.
    log_prob_action: Probability = np.nan  # Off-policy algorithms.
    entropy: Probability = np.nan  # Entropy of current policy.

    @staticmethod
    def _is_equal_nan(x, y):
        x, y = np.array(x), np.array(y)
        if ((np.isnan(x)) ^ (np.isnan(y))).all():  # XOR
            return False
        elif ((~np.isnan(x)) & (~np.isnan(y))).all():
            return np.allclose(x, y)
        else:
            return True

    def __eq__(self, other):
        """Check if two observations are equal."""
        if not isinstance(other, Observation):
            return NotImplemented
        is_equal = self._is_equal_nan(self.state, other.state)
        is_equal &= self._is_equal_nan(self.action, other.action)
        is_equal &= self._is_equal_nan(self.reward, other.reward)
        is_equal &= self._is_equal_nan(self.next_state, other.next_state)
        is_equal &= self._is_equal_nan(self.next_action, other.next_action)
        is_equal &= self._is_equal_nan(self.log_prob_action, other.log_prob_action)
        is_equal &= self.done == other.done
        return is_equal

    def __ne__(self, other):
        """Check if two observations are not equal."""
        return not self.__eq__(other)

    def to_torch(self):
        """Transform to torch."""
        return Observation(*map(
            lambda x: x if isinstance(x, torch.Tensor) else
            torch.tensor(x, dtype=torch.get_default_dtype()),
            self))
