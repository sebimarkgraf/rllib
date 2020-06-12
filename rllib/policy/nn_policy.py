"""Policies parametrized with Neural Networks."""

import torch
import torch.nn.functional

from rllib.util.neural_networks import (CategoricalNN, FelixNet,
                                        HeteroGaussianNN, one_hot_encode)

from .abstract_policy import AbstractPolicy


class NNPolicy(AbstractPolicy):
    """Implementation of a Policy implemented with a Neural Network.

    Parameters
    ----------
    dim_state: int
        dimension of state.
    dim_action: int
        dimension of action.
    num_states: int, optional
        number of discrete states (None if state is continuous).
    num_actions: int, optional
        number of discrete actions (None if action is continuous).
    layers: list, optional
        width of layers, each layer is connected with ReLUs non-linearities.
    biased_head: bool, optional
        flag that indicates if head of NN has a bias term or not.
    action_scale: float, optional.
        Magnitude of action scale.
    """

    def __init__(self, dim_state, dim_action, num_states=-1, num_actions=-1,
                 layers=None, biased_head=True, non_linearity='ReLU',
                 squashed_output=True, action_scale=1.,
                 tau=0.0, deterministic=False, input_transform=None):
        super().__init__(dim_state, dim_action, num_states, num_actions, tau,
                         deterministic, action_scale=action_scale)
        if self.discrete_state:
            in_dim = self.num_states
        else:
            in_dim = self.dim_state

        self.input_transform = input_transform
        if hasattr(input_transform, 'extra_dim'):
            in_dim += getattr(input_transform, 'extra_dim')

        if self.discrete_action:
            self.nn = CategoricalNN(in_dim, self.num_actions, layers=layers,
                                    non_linearity=non_linearity,
                                    biased_head=biased_head)
        else:
            self.nn = HeteroGaussianNN(in_dim, self.dim_action, layers=layers,
                                       non_linearity=non_linearity,
                                       biased_head=biased_head,
                                       squashed_output=squashed_output)

    @classmethod
    def from_other(cls, other, copy=True):
        """Create new NN Policy from another policy."""
        new = cls(dim_state=other.dim_state, dim_action=other.dim_action,
                  num_states=other.num_states, num_actions=other.num_actions,
                  tau=other.tau, deterministic=other.deterministic,
                  action_scale=other.action_scale,
                  input_transform=other.input_transform)
        new.nn = other.nn.__class__.from_other(other.nn, copy=copy)
        return new

    @classmethod
    def from_nn(cls, module, dim_state, dim_action, num_states=-1, num_actions=-1,
                tau=0.0, deterministic=False, action_scale=1.,
                input_transform=None):
        """Create new NN Policy from a Neural Network Implementation."""
        new = cls(dim_state=dim_state, dim_action=dim_action,
                  num_states=num_states, num_actions=num_actions,
                  tau=tau, deterministic=deterministic, action_scale=action_scale,
                  input_transform=input_transform)
        new.nn = module
        return new

    def forward(self, state, **kwargs):
        """Get distribution over actions."""
        if self.input_transform is not None:
            state = self.input_transform(state)

        if self.discrete_state:
            state = one_hot_encode(state.long(), num_classes=self.num_states)

        out = self.nn(state)
        if (not self.discrete_action) and not kwargs.get('normalized', False):
            out = (self.action_scale * out[0], self.action_scale * out[1])

        if self.deterministic:
            return out[0], torch.zeros(1)
        else:
            return out

    @torch.jit.export
    def embeddings(self, state):
        """Get embeddings of the value-function at a given state."""
        if self.discrete_state:
            state = one_hot_encode(state.long(), num_classes=self.num_states)

        features = self.nn.last_layer_embeddings(state)
        return features.squeeze()


class FelixPolicy(NNPolicy):
    """Implementation of a NN Policy using FelixNet (designed by Felix Berkenkamp).

    Parameters
    ----------
    dim_state: int
        dimension of state.
    dim_action: int
        dimension of action.
    num_states: int, optional
        number of discrete states (None if state is continuous).
    num_actions: int, optional
        number of discrete actions (None if action is continuous).

    Notes
    -----
    This class is only implemented for continuous state and action spaces.

    """

    def __init__(self, dim_state, dim_action, num_states=-1, num_actions=-1,
                 tau=0.0, deterministic=False, action_scale=1.,
                 input_transform=None):
        super().__init__(dim_state, dim_action, num_states, num_actions, tau=tau,
                         deterministic=deterministic, input_transform=input_transform,
                         action_scale=action_scale)
        self.nn = FelixNet(self.nn.kwargs['in_dim'], self.nn.kwargs['out_dim'])
        if self.discrete_state or self.discrete_action:
            raise ValueError("num_states and num_actions have to be set to -1.")
