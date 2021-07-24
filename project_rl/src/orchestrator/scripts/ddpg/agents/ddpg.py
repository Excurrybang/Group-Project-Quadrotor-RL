import numpy as np
import random
import copy
from collections import namedtuple, deque
from ddpg.agents.critic import Critic
from ddpg.agents.actor import Actor

import torch
import torch.nn.functional as F
import torch.optim as optim

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

class DDPG:

    def __init__ (self, task, lr_actor = 1e-4, lr_critic = 1e-3, gamma=0.98, tau=1e-3):

        self.task = task
        self.state_size = task.state_size
        self.action_size = task.action_size
        
        self.lr_actor = lr_actor
        self.lr_critic = lr_critic
        WEIGHT_DECAY = 0
        random_seed = 0
        self.seed = random.seed(random_seed)
        # Actor Network
        self.actor_local = Actor(self.state_size, self.action_size, random_seed).to(device)
        self.actor_target = Actor(self.state_size, self.action_size, random_seed).to(device)
        self.actor_optimizer = optim.Adam(self.actor_local.parameters(), lr=lr_actor)

        # Critic Network
        self.critic_local = Critic(self.state_size, self.action_size, random_seed).to(device)
        self.critic_target = Critic(self.state_size, self.action_size, random_seed).to(device)
        self.critic_optimizer = optim.Adam(self.critic_local.parameters(), lr=lr_critic, weight_decay=WEIGHT_DECAY)

        # Noise process
        self.noise = OUNoise(size = self.action_size, seed=random_seed)

        # Replay memory
        self.buffer_size = 100000
        self.batch_size = 128
        self.gamma = gamma
        self.tau = tau
        self.memory = ReplayBuffer(self.buffer_size, self.batch_size)


    def step(self, state, action, reward, next_state, done):
        # save the current information to memory
        self.memory.add(state, action, reward, next_state, done)

        if len(self.memory) > self.batch_size:
            experiences = self.memory.sample(self.batch_size)
            self.learn(experiences)


    def act(self, states, add_noise=True):
        # according to the current state, calculate the next action
        states = torch.from_numpy(states).float().to(device)
        self.actor_local.eval()
        with torch.no_grad():
            actions = self.actor_local(states.unsqueeze(0)).cpu().data.numpy()[0]

        self.actor_local.train()
        if add_noise:
            actions += self.noise.sample()

        return np.clip(actions, -1, 1)

    def reset(self):
        self.noise.reset()

    def learn(self, experiences):
        gamma = 0.98
        states, actions, rewards, next_states, dones = experiences
        actions_next = self.actor_target(next_states)
        Q_targets_next = self.critic_target(next_states, actions_next)
        
        # Compute Q targets for current states (y_i)
        Q_targets = rewards + (gamma * Q_targets_next * (1 - dones))
        # Compute Q value predictions
        Q_expected = self.critic_local(states, actions)

        # compute td error
        td_error = Q_targets - Q_expected

        # compute critic loss
        critic_loss = (td_error**2).mean()

        # Minimize the loss
        self.critic_optimizer.zero_grad()
        critic_loss.backward()
        self.critic_optimizer.step()

        # ---------------------------- update actor ---------------------------- #
        # Compute actor loss
        actions_pred = self.actor_local(states)
        actor_loss = -(self.critic_local(states, actions_pred).squeeze()).mean()

        # Minimize the loss
        self.actor_optimizer.zero_grad()
        actor_loss.backward()
        self.actor_optimizer.step()

        # ----------------------- update target networks ----------------------- #
        self.soft_update(self.critic_local, self.critic_target, self.tau)
        self.soft_update(self.actor_local, self.actor_target, self.tau)

        print("DDPG.learn(): rewards = {}".format(max(rewards)))

    def soft_update(self, local_model, target_model, tau):
        self.tau = tau

        """Soft update model parameters.
        θ_target = τ*θ_local + (1 - τ)*θ_target
        Params
        ======
            local_model: PyTorch model (weights will be copied from)
            target_model: PyTorch model (weights will be copied to)
            tau (float): interpolation parameter
        """
        for target_param, local_param in zip(target_model.parameters(), local_model.parameters()):
            target_param.data.copy_(tau*local_param.data + (1.0-tau)*target_param.data)



class OUNoise:
    """Ornstein-Uhlenbeck process."""

    def __init__(self, size, seed, mu=0., theta=0.15, sigma_start=1.0,sigma_decay=0.9999,sigma_end=1e-2):
        """Initialize parameters and noise process."""
        self.mu = mu * np.ones(size)
        self.theta = theta
        self.size = size
        self.seed = random.seed(seed)
        self.reset()

        self.sigma = sigma_start
        self.sigma_decay = sigma_decay
        self.sigma_end = sigma_end

    def reset(self):
        """Reset the internal state (= noise) to mean (mu)."""
        self.state = copy.copy(self.mu)

    def sample(self):
        """Update internal state and return it as a noise sample."""
        x = self.state
        dx = self.theta * (self.mu - x) + self.sigma * np.random.standard_normal(self.size)#np.array([random.random() for i in range(len(x))])
        self.state = x + dx

        self.sigma = max(self.sigma_decay*self.sigma,self.sigma_end)
        return self.state



class ReplayBuffer:
    """Fixed-size buffer to store experience tuples."""

    def __init__(self, buffer_size, batch_size):
        """Initialize a ReplayBuffer object.
        Params
        ======
            buffer_size: maximum size of buffer
            batch_size: size of each training batch
        """
        self.memory = deque(maxlen=buffer_size)  # internal memory (deque)
        self.batch_size = batch_size
        self.experience = namedtuple("Experience", field_names=["state", "action", "reward", "next_state", "done"])

    def add(self, state, action, reward, next_state, done):
        """Add a new experience to memory."""
        e = self.experience(state, action, reward, next_state, done)
        self.memory.append(e)

    def sample(self,batch_size):
        """Randomly sample a batch of experiences from memory."""
        experiences = random.sample(self.memory, k=batch_size)

        states = torch.from_numpy(np.vstack([e.state for e in experiences if e is not None])).float().to(device)
        actions = torch.from_numpy(np.vstack([e.action for e in experiences if e is not None])).float().to(device)
        rewards = torch.from_numpy(np.vstack([e.reward for e in experiences if e is not None])).float().to(device)
        next_states = torch.from_numpy(np.vstack([e.next_state for e in experiences if e is not None])).float().to(device)
        dones = torch.from_numpy(np.vstack([e.done for e in experiences if e is not None]).astype(np.uint8)).float().to(device)

        return (states, actions, rewards, next_states, dones)

    def __len__(self):
        """Return the current size of internal memory."""
        return len(self.memory)
