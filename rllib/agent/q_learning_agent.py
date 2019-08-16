"""Implementation of QLearning Algorithms."""
from .abstract_agent import AbstractAgent
from abc import abstractmethod
import torch
from torch.distributions import Categorical
from torch.utils.data import DataLoader

__all__ = ['QLearningAgent', 'GQLearningAgent', 'DQNAgent', 'DDQNAgent']


class AbstractQLearningAgent(AbstractAgent):
    """Abstract Implementation of the Q-Learning Algorithm.

    The AbstractQLearning algorithm implements the Q-Learning algorithm except for the
    computation of the TD-Error, which leads to different algorithms.

    Parameters
    ----------
    q_function: AbstractQFunction
        q_function that is learned.
    q_target: AbstractQFunction
        q_function used for TD-Error target.
    exploration: AbstractExplorationStrategy.
        exploration strategy that returns the actions.
    criterion: nn.Module
    optimizer: nn.optim
    memory: ExperienceReplay
        memory where to store the observations.
    hyper_params: dict
        algorithm hyperparameters.

    References
    ----------
    Watkins, C. J., & Dayan, P. (1992). Q-learning. Machine learning, 8(3-4), 279-292.

    """

    def __init__(self, q_function, q_target, exploration, criterion, optimizer, memory,
                 hyper_params):
        super().__init__()
        self._q_function = q_function
        self._q_target = q_target
        self._exploration = exploration
        self._criterion = criterion
        self._memory = memory
        self._hyper_params = hyper_params
        self._optimizer = optimizer(self._q_function.parameters,
                                    lr=self._hyper_params['learning_rate'])

        self._data_loader = DataLoader(self._memory,
                                       batch_size=self._hyper_params['batch_size'])

    def act(self, state):
        logits = self._q_function(torch.tensor(state).float())
        action_distribution = Categorical(logits=logits)
        return self._exploration(action_distribution, self._steps['total'])

    def observe(self, observation):
        super().observe(observation)
        self._memory.append(observation)
        if len(self._memory) >= self._hyper_params['batch_size']:
            self._train()

    def end_episode(self):
        if self.num_episodes % self._hyper_params['target_update_frequency'] == 0:
            self._q_target.parameters = self._q_function.parameters

    @property
    def policy(self):
        return self._q_function.extract_policy(temperature=0.001)

    def _train(self, batches=1):
        """Train the DQN for `batches' batches.

        Parameters
        ----------
        batches: int

        """
        self._memory.shuffle()
        for i, observation in enumerate(self._data_loader):
            state, action, reward, next_state, done = observation
            pred_q, target_q = self._td(state.float(), action.float(), reward.float(),
                                        next_state.float(), done.float())

            loss = self._criterion(pred_q, target_q)
            self._optimizer.zero_grad()
            loss.backward()
            self._optimizer.step()
            if i + 1 == batches:
                break

    @abstractmethod
    def _td(self, state, action, reward, next_state, done):
        raise NotImplementedError


class QLearningAgent(AbstractQLearningAgent):
    """Implementation of Q-Learning algorithm.

    loss = l[Q(x, a), r + Q(x', arg max Q(x', a))]

    References
    ----------
    Watkins, C. J., & Dayan, P. (1992). Q-learning. Machine learning, 8(3-4), 279-292.
    """

    def _td(self, state, action, reward, next_state, done):
        pred_q = self._q_function(state, action)

        # target = r + gamma * max Q(x', a) and don't stop gradient.
        target_q = self._q_function.max(next_state)
        target_q = reward + self._hyper_params['gamma'] * target_q * (1 - done)

        return pred_q, target_q


class GQLearningAgent(AbstractQLearningAgent):
    """Implementation of Gradient Q-Learning algorithm.

    loss = l[Q(x, a), r + Q(x', arg max Q(x', a)).stop_gradient]

    References
    ----------
    Sutton, Richard S., et al. "Fast gradient-descent methods for temporal-difference
    learning with linear function approximation." Proceedings of the 26th Annual
    International Conference on Machine Learning. ACM, 2009.

    """

    def _td(self, state, action, reward, next_state, done):
        pred_q = self._q_function(state, action)

        # target = r + gamma * max Q(x', a) and stop gradient.
        next_q = self._q_function.max(next_state)
        target_q = reward + self._hyper_params['gamma'] * next_q * (1 - done)

        return pred_q, target_q.detach()


class DQNAgent(AbstractQLearningAgent):
    """Implementation of DQN algorithm.

    loss = l[Q(x, a), r + max_a Q'(x', a)]

    References
    ----------
    Mnih, Volodymyr, et al. "Human-level control through deep reinforcement learning."
    Nature 518.7540 (2015): 529.
    """

    def _td(self, state, action, reward, next_state, done):
        pred_q = self._q_function(state, action)

        # target = r + gamma * max Q_target(x', a)
        next_q = self._q_target.max(next_state)
        target_q = reward + self._hyper_params['gamma'] * next_q * (1 - done)

        return pred_q, target_q.detach()


class DDQNAgent(AbstractQLearningAgent):
    """Implementation of Double DQN algorithm.

    loss = l[Q(x, a), r + Q'(x', argmax Q(x,a))]

    References
    ----------
    Van Hasselt, Hado, Arthur Guez, and David Silver. "Deep reinforcement learning
    with double q-learning." Thirtieth AAAI conference on artificial intelligence. 2016.
    """

    def _td(self, state, action, reward, next_state, done):
        pred_q = self._q_function(state, action)

        # target = r + gamma * Q_target(x', argmax Q(x', a))

        next_action = self._q_function.argmax(next_state)
        next_q = self._q_target(next_state, next_action)
        target_q = reward + self._hyper_params['gamma'] * next_q * (1 - done)

        return pred_q, target_q.detach()
