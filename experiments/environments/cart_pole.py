"""Python Script Template."""
import matplotlib.pyplot as plt
from rllib.agent import DDQNAgent
from rllib.environment import GymEnvironment
from rllib.value_function import NNQFunction
from rllib.dataset import ExperienceReplay
from rllib.exploration_strategies import EpsGreedy
from rllib.util import rollout_agent
import pickle

import numpy as np
import torch
import torch.nn.functional as func


ENVIRONMENT = 'CartPole-v0'
NUM_EPISODES = 50
MILESTONES = [0, 18, 49]
MAX_STEPS = 200
TARGET_UPDATE_FREQUENCY = 4
TARGET_UPDATE_TAU = 0.99
MEMORY_MAX_SIZE = 5000
BATCH_SIZE = 64
LEARNING_RATE = 1e-2
WEIGHT_DECAY = 1e-4
GAMMA = 0.99
EPS_START = 1.0
EPS_END = 0.01
EPS_DECAY = 500
LAYERS = [64, 64]
SEED = 0

torch.manual_seed(SEED)
np.random.seed(SEED)

environment = GymEnvironment(ENVIRONMENT, SEED)
exploration = EpsGreedy(EPS_START, EPS_END, EPS_DECAY)
q_function = NNQFunction(environment.dim_state, environment.dim_action,
                         num_states=environment.num_states,
                         num_actions=environment.num_actions,
                         layers=LAYERS,
                         tau=TARGET_UPDATE_TAU)

optimizer = torch.optim.SGD(q_function.parameters, lr=LEARNING_RATE,
                            momentum=0.1, weight_decay=WEIGHT_DECAY)
criterion = func.mse_loss
memory = ExperienceReplay(max_len=MEMORY_MAX_SIZE, batch_size=BATCH_SIZE)

agent = DDQNAgent(q_function, exploration, criterion, optimizer, memory,
                  target_update_frequency=TARGET_UPDATE_FREQUENCY, gamma=GAMMA,
                  episode_length=MAX_STEPS)
with open('{}_{}.pkl'.format(environment.name, agent.name), 'wb') as file:
    pickle.dump(agent, file)

rollout_agent(environment, agent, max_steps=MAX_STEPS, num_episodes=NUM_EPISODES,
              milestones=MILESTONES)

plt.plot(agent.episodes_cumulative_rewards)
plt.xlabel('Episode')
plt.ylabel('Rewards')
plt.title('{} in {}'.format(agent.__class__.__name__, ENVIRONMENT))
plt.show()

