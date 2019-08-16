from rllib.policy import NNPolicy, FelixPolicy
from rllib.util.neural_networks import random_tensor
import torch
from torch.distributions import MultivariateNormal, Categorical
import pytest


@pytest.fixture(params=[True, False])
def discrete_state(request):
    return request.param


@pytest.fixture(params=[True, False])
def discrete_action(request):
    return request.param


@pytest.fixture(params=[1, 4])
def dim_state(request):
    return request.param


@pytest.fixture(params=[1, 4])
def dim_action(request):
    return request.param


@pytest.fixture(params=[None, 0.1, 1.0])
def temperature(request):
    return request.param


@pytest.fixture(params=[None, 1, 4])
def batch_size(request):
    return request.param


class TestNNPolicy(object):
    def init(self, discrete_state, discrete_action, dim_state, dim_action,
             temperature=None):

        if discrete_state:
            self.num_states = dim_state
            self.dim_state = 1
        else:
            self.num_states = None
            self.dim_state = dim_state

        if discrete_action:
            self.num_actions = dim_action
            self.dim_action = 1
        else:
            self.num_actions = None
            self.dim_action = dim_action

        if temperature is None:
            self.policy = NNPolicy(self.dim_state, self.dim_action,
                                   self.num_states, self.num_actions,
                                   layers=[32, 32])
        else:
            self.policy = NNPolicy(self.dim_state, self.dim_action,
                                   self.num_states, self.num_actions, temperature,
                                   layers=[32, 32])

    def test_num_states_actions(self, discrete_state, discrete_action, dim_state,
                                dim_action, temperature):
        self.init(discrete_state, discrete_action, dim_state, dim_action, temperature)
        assert self.num_states == self.policy.num_states
        assert self.num_actions == self.policy.num_actions

        if not discrete_state:
            assert self.policy.num_states is None
        if not discrete_action:
            assert self.policy.num_actions is None

        assert discrete_state == self.policy.discrete_state
        assert discrete_action == self.policy.discrete_action

        if temperature is None:
            assert self.policy.temperature == 1.
        else:
            assert self.policy.temperature == temperature

    def test_random_action(self, discrete_state, discrete_action, dim_state,
                           dim_action):
        self.init(discrete_state, discrete_action, dim_state, dim_action)

        distribution = self.policy.random()
        sample = distribution.sample()

        if distribution.has_enumerate_support:  # Discrete
            assert distribution.logits.shape == (self.num_actions,)
            assert sample.shape == ()
        else:  # Continuous
            assert distribution.mean.shape == (self.dim_action,)
            assert sample.shape == (dim_action,)

    def test_call(self, discrete_state, discrete_action, dim_state, dim_action,
                  batch_size):
        self.init(discrete_state, discrete_action, dim_state, dim_action)
        state = random_tensor(discrete_state, dim_state, batch_size)

        distribution = self.policy(state)
        sample = distribution.sample()

        if distribution.has_enumerate_support:  # Discrete
            assert type(distribution) is Categorical
            if batch_size:
                assert distribution.logits.shape == (batch_size, self.num_actions,)
                assert sample.shape == (batch_size,)
            else:
                assert distribution.logits.shape == (self.num_actions,)
                assert sample.shape == ()
        else:  # Continuous
            assert type(distribution) is MultivariateNormal
            if batch_size:
                assert distribution.mean.shape == (batch_size, self.dim_action,)
                assert distribution.covariance_matrix.shape == (batch_size,
                                                                self.dim_action,
                                                                self.dim_action)
                assert sample.shape == (batch_size, dim_action,)
            else:
                assert distribution.mean.shape == (self.dim_action,)
                assert distribution.covariance_matrix.shape == (self.dim_action,
                                                                self.dim_action)
                assert sample.shape == (dim_action,)

    def test_parameters(self, discrete_state, discrete_action, dim_state, dim_action):
        self.init(discrete_state, discrete_action, dim_state, dim_action)
        old_parameter = self.policy.parameters
        self.policy.parameters = old_parameter


class TestFelixNet(object):
    def init(self, dim_state, dim_action, temperature=None):
        if temperature is None:
            self.policy = FelixPolicy(dim_state, dim_action)
        else:
            self.policy = FelixPolicy(dim_state, dim_action, temperature=temperature)

    def test_discrete(self, dim_state, dim_action):
        with pytest.raises(ValueError):
            FelixPolicy(1, dim_action, num_states=dim_state)
        with pytest.raises(ValueError):
            FelixPolicy(dim_state, 1, num_actions=dim_action)
        with pytest.raises(ValueError):
            FelixPolicy(1, 1, num_states=dim_state, num_actions=dim_action)

    def test_num_states_actions(self, dim_state, dim_action, temperature):
        self.init(dim_state, dim_action, temperature)
        assert self.policy.num_states is None
        assert self.policy.num_actions is None
        assert not self.policy.discrete_state
        assert not self.policy.discrete_action
        assert self.policy.dim_state == dim_state
        assert self.policy.dim_action == dim_action

        if temperature is None:
            assert self.policy.temperature == 1.
        else:
            assert self.policy.temperature == temperature

    def test_random_action(self, dim_state, dim_action):
        self.init(dim_state, dim_action)

        distribution = self.policy.random()
        sample = distribution.sample()

        assert distribution.mean.shape == (dim_action,)
        assert sample.shape == (dim_action,)

    def test_call(self, dim_state, dim_action, batch_size):
        self.init(dim_state, dim_action)
        state = random_tensor(False, dim_state, batch_size)

        distribution = self.policy(state)
        sample = distribution.sample()

        assert type(distribution) is MultivariateNormal
        if batch_size:
            assert distribution.mean.shape == (batch_size, dim_action,)
            assert distribution.covariance_matrix.shape == (batch_size,
                                                            dim_action, dim_action)
            assert sample.shape == (batch_size, dim_action,)
        else:
            assert distribution.mean.shape == (dim_action,)
            assert distribution.covariance_matrix.shape == (dim_action, dim_action)
            assert sample.shape == (dim_action,)

    def test_parameters(self, dim_state, dim_action):
        self.init(dim_state, dim_action)
        old_parameter = self.policy.parameters
        self.policy.parameters = old_parameter
