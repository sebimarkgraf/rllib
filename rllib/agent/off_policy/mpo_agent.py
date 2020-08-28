"""MPO Agent Implementation."""
from itertools import chain

import torch.nn.modules.loss as loss
from torch.optim import Adam

from rllib.algorithms.mpo import MPO
from rllib.dataset.experience_replay import ExperienceReplay
from rllib.policy import NNPolicy
from rllib.value_function import NNQFunction

from .off_policy_agent import OffPolicyAgent


class MPOAgent(OffPolicyAgent):
    """Implementation of an agent that runs MPO."""

    def __init__(
        self,
        policy,
        q_function,
        criterion,
        num_action_samples=15,
        epsilon=0.1,
        epsilon_mean=0.1,
        epsilon_var=0.001,
        regularization=False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.algorithm = MPO(
            policy=policy,
            critic=q_function,
            num_action_samples=num_action_samples,
            criterion=criterion(reduction="none"),
            epsilon=epsilon,
            epsilon_mean=epsilon_mean,
            epsilon_var=epsilon_var,
            regularization=regularization,
            gamma=self.gamma,
        )
        # Over-write optimizer.
        self.optimizer = type(self.optimizer)(
            [
                p
                for name, p in self.algorithm.named_parameters()
                if "target" not in name
            ],
            **self.optimizer.defaults,
        )
        self.policy = self.algorithm.policy

    @classmethod
    def default(cls, environment, *args, **kwargs):
        """See `AbstractAgent.default'."""
        q_function = NNQFunction.default(environment)
        policy = NNPolicy.default(environment, layers=[100, 100])

        optimizer = Adam(chain(policy.parameters(), q_function.parameters()), lr=5e-4)
        criterion = loss.MSELoss
        memory = ExperienceReplay(max_len=50000, num_steps=0)

        if environment.num_actions > 0:
            epsilon = 0.1
            epsilon_mean = 0.5
            epsilon_var = None
        else:
            epsilon = 0.1
            epsilon_mean = 0.1
            epsilon_var = 1e-4

        return cls(
            policy=policy,
            q_function=q_function,
            optimizer=optimizer,
            memory=memory,
            criterion=criterion,
            num_action_samples=15,
            epsilon=epsilon,
            epsilon_mean=epsilon_mean,
            epsilon_var=epsilon_var,
            regularization=False,
            num_iter=5 if kwargs.get("test", False) else 1000,
            batch_size=100,
            target_update_frequency=1,
            train_frequency=0,
            num_rollouts=2,
            comment=environment.name,
            *args,
            **kwargs,
        )
