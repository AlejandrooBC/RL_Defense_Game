"""
DQN Agent for the Fortress Defense environment.

"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
import matplotlib.pyplot as plt
import os
import time
from tqdm import tqdm

# Import our environment wrapper
from fortress_defense_env_v2 import FortressDefenseEnv


# PART 1: THE Q-NETWORK

class QNetwork(nn.Module):
    """A neural network that estimates Q-values for each action."""

    def __init__(self, state_size, action_size):
        super(QNetwork, self).__init__()

        # Three fully connected layers
        self.layer1 = nn.Linear(state_size, 256)
        self.layer2 = nn.Linear(256, 256)
        self.layer3 = nn.Linear(256, action_size)

        # ReLU activation function
        self.relu = nn.ReLU()

    def forward(self, state):
        """
        Pass a state through the network to get Q-values.
        Input:  state tensor of shape (batch_size, 26)
        Output: Q-values tensor of shape (batch_size, 10)
        """
        x = self.relu(self.layer1(state))
        x = self.relu(self.layer2(x))
        q_values = self.layer3(x)  # no activation on output layer
        return q_values


# PART 2: THE REPLAY BUFFER

class ReplayBuffer:
    """Stores experiences and provides random batches for training."""

    def __init__(self, max_size):
        # deque automatically removes oldest items when full
        self.buffer = deque(maxlen=max_size)

    def add(self, state, action, reward, next_state, done):
        """Store one experience."""
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        """
        Randomly sample a batch of experiences.
        Returns 5 numpy arrays: states, actions, rewards, next_states, dones
        """
        batch = random.sample(self.buffer, batch_size)

        states = []
        actions = []
        rewards = []
        next_states = []
        dones = []

        for experience in batch:
            s, a, r, ns, d = experience
            states.append(s)
            actions.append(a)
            rewards.append(r)
            next_states.append(ns)
            dones.append(d)

        states = np.array(states, dtype=np.float32)
        actions = np.array(actions, dtype=np.int64)
        rewards = np.array(rewards, dtype=np.float32)
        next_states = np.array(next_states, dtype=np.float32)
        dones = np.array(dones, dtype=np.float32)

        return states, actions, rewards, next_states, dones

    def size(self):
        """How many experiences are stored."""
        return len(self.buffer)

# PART 3: THE DQN AGENT

class DQNAgent:
    """The DQN agent that learns to play the fortress defense game."""

    def __init__(self, state_size, action_size, device):
        self.state_size = state_size
        self.action_size = action_size
        self.device = device

        # ---------- Hyperparameters ----------
        self.gamma = 0.99           # discount factor
        self.lr = 0.0001            # learning rate for the optimizer
        self.batch_size = 64        # how many experiences to learn from at once
        self.buffer_size = 100000   # max experiences in replay buffer
        self.target_update = 1000   # update target network every N training steps
        self.min_buffer_size = 1000 # don't start training until buffer has this many

        # ---------- Epsilon (exploration) ----------
        self.epsilon = 1.0          # start fully random
        self.epsilon_min = 0.10     # never go below 10% random
        self.epsilon_decay = 0.995  # multiply epsilon by this after each episode

        # ---------- Networks ----------
        # Policy network
        self.policy_net = QNetwork(state_size, action_size).to(device)

        # Target network: frozen copy for stable Q-targets
        self.target_net = QNetwork(state_size, action_size).to(device)

        # Copy policy weights into target 
        self.target_net.load_state_dict(self.policy_net.state_dict())

        # ---------- Optimizer and loss ----------
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=self.lr)
        self.loss_fn = nn.MSELoss()

        # ---------- Replay buffer ----------
        self.buffer = ReplayBuffer(self.buffer_size)

        # Training step counter (for target network updates)
        self.train_step_count = 0

    def pick_action(self, state):
        """
        Pick an action using epsilon-greedy.
        """
        # Exploration
        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)

        # Exploitation
        # Convert state to a tensor and add batch dimension
        state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        # Turn off gradient computation 
        with torch.no_grad():
            q_values = self.policy_net(state_tensor)

        # Return the action with the highest Q-value
        best_action = q_values.argmax(dim=1).item()
        return best_action

    def store_experience(self, state, action, reward, next_state, done):
        """Save an experience to the replay buffer."""
        self.buffer.add(state, action, reward, next_state, done)

    def learn(self):
        """
        Sample a batch from the replay buffer and do one training step.
        This is where the actual learning happens.
        """
        # Don't train if we don't have enough experiences yet
        if self.buffer.size() < self.min_buffer_size:
            return None

        # Step 1: Sample a random batch
        states, actions, rewards, next_states, dones = self.buffer.sample(
            self.batch_size
        )

        # Step 2: Convert everything to tensors and move to GPU
        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        # Step 3: Compute current Q-values
        all_q_values = self.policy_net(states)
        current_q = all_q_values.gather(1, actions.unsqueeze(1)).squeeze(1)

        # Step 4: Compute target Q-values using the target network
        
        with torch.no_grad():
            # Double DQN: use policy network to pick best action,
            # use target network to evaluate it
            next_actions = self.policy_net(next_states).argmax(dim=1, keepdim=True)
            next_q_values = self.target_net(next_states).gather(1, next_actions).squeeze(1)
            target_q = rewards + (1 - dones) * self.gamma * next_q_values
                
            # (1 - dones) makes the future term zero when the episode ended

        # Step 5: Compute loss (how far off our predictions are)
        loss = self.loss_fn(current_q, target_q)

        # Step 6: Backpropagate and update weights
        self.optimizer.zero_grad()
        loss.backward()
        # Clip gradients to prevent exploding updates
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=10)
        self.optimizer.step()

        # Step 7: Periodically update the target network
        self.train_step_count += 1
        if self.train_step_count % self.target_update == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())

        return loss.item()

    def decay_epsilon(self):
        """Reduce exploration rate after each episode."""
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)

    def save(self, filepath):
        """Save the trained network to a file."""
        torch.save({
            "policy_net": self.policy_net.state_dict(),
            "target_net": self.target_net.state_dict(),
            "epsilon": self.epsilon,
            "train_step_count": self.train_step_count,
        }, filepath)
        print("Model saved to " + filepath)

    def load(self, filepath):
        """Load a previously trained network from a file."""
        checkpoint = torch.load(filepath, map_location=self.device)
        self.policy_net.load_state_dict(checkpoint["policy_net"])
        self.target_net.load_state_dict(checkpoint["target_net"])
        self.epsilon = checkpoint["epsilon"]
        self.train_step_count = checkpoint["train_step_count"]
        print("Model loaded from " + filepath)


# PART 4: THE TRAINING LOOP

def train(num_episodes=2000, render=False):
    """
    Train the DQN agent on the fortress defense environment.

    Args:
        num_episodes: how many games to play
        render: if True, show the game window (slow but visual)
    """

    #Setup
    render_mode = "human" if render else None
    env = FortressDefenseEnv(render_mode=render_mode)

    # Get state and action sizes from the environment
    state_size = env.observation_space.shape[0]  # 26
    action_size = env.action_space.n              # 10

    # Use GPU if available, otherwise CPU
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device: " + str(device))

    # Create the agent
    agent = DQNAgent(state_size, action_size, device)

    # Tracking variables
    all_rewards = []         # total reward per episode
    all_survivals = []       # steps survived per episode
    all_eliminations = []    # enemies killed per episode
    all_losses = []          # average loss per episode
    all_epsilons = []        # epsilon value per episode

    # For printing averages every N episodes
    print_every = 10

    # Create a folder to save results
    save_dir = "ddqn_v2_results"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    print("Starting training for " + str(num_episodes) + " episodes...")
    print("State size: " + str(state_size))
    print("Action size: " + str(action_size))
    print("-" * 60)

    training_start_time = time.time()

    # Main training loop 
    for episode in range(1, num_episodes + 1):
        # Reset the environment for a new episode
        state, info = env.reset()
        total_reward = 0
        episode_losses = []
        done = False

        # Play one full episode
        while not done:
            # Agent picks an action
            action = agent.pick_action(state)

            # Environment executes the action
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            # Agent stores the experience
            agent.store_experience(
                state, action, reward, next_state, float(done)
            )

            # Agent learns from a random batch of past experiences
            loss = agent.learn()
            if loss is not None:
                episode_losses.append(loss)

            # Move to the next state
            state = next_state
            total_reward += reward

        # Episode finished — decay exploration
        agent.decay_epsilon()

        # Record stats
        all_rewards.append(total_reward)
        all_survivals.append(info["step_count"])
        all_eliminations.append(info["eliminations"])
        all_epsilons.append(agent.epsilon)
        if len(episode_losses) > 0:
            avg_loss = sum(episode_losses) / len(episode_losses)
        else:
            avg_loss = 0
        all_losses.append(avg_loss)

        # Print progress every N episodes
        if episode % print_every == 0:
            # Compute averages over the last N episodes
            recent_rewards = all_rewards[-print_every:]
            recent_survivals = all_survivals[-print_every:]
            recent_elims = all_eliminations[-print_every:]
            avg_reward = sum(recent_rewards) / len(recent_rewards)
            avg_survival = sum(recent_survivals) / len(recent_survivals)
            avg_elims = sum(recent_elims) / len(recent_elims)

            elapsed = time.time() - training_start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)

            print(
                "Episode " + str(episode)
                + " | Avg Reward: " + str(round(avg_reward, 1))
                + " | Avg Survival: " + str(round(avg_survival, 1))
                + " | Avg Kills: " + str(round(avg_elims, 1))
                + " | Epsilon: " + str(round(agent.epsilon, 3))
                + " | Loss: " + str(round(avg_loss, 4))
                + " | Time: " + str(mins) + "m " + str(secs) + "s"
            )

        # Save checkpoint every 100 episodes
        if episode % 100 == 0:
            agent.save(save_dir + "/checkpoint_ep" + str(episode) + ".pt")
            # Also save training curves so far
            np.save(save_dir + "/rewards.npy", np.array(all_rewards))
            np.save(save_dir + "/survivals.npy", np.array(all_survivals))
            np.save(save_dir + "/eliminations.npy", np.array(all_eliminations))
            np.save(save_dir + "/losses.npy", np.array(all_losses))
            np.save(save_dir + "/epsilons.npy", np.array(all_epsilons))
            print("  -> Checkpoint and curves saved.")

    total_time = time.time() - training_start_time
    print("-" * 60)
    print("Training complete! Total time: " + str(round(total_time / 60, 1)) + " minutes")

    agent.save(save_dir + "/final_model.pt")
    np.save(save_dir + "/rewards.npy", np.array(all_rewards))
    np.save(save_dir + "/survivals.npy", np.array(all_survivals))
    np.save(save_dir + "/eliminations.npy", np.array(all_eliminations))
    np.save(save_dir + "/losses.npy", np.array(all_losses))
    np.save(save_dir + "/epsilons.npy", np.array(all_epsilons))

    env.close()

    plot_results(all_rewards, all_survivals, all_eliminations, all_losses,
                 all_epsilons, save_dir)
    
def continue_training(checkpoint_path, additional_episodes=2000, render=False):
    """
    Continue training from a saved checkpoint.
    
    Args:
        checkpoint_path: path to the saved model (e.g., "ddqn_v2_results/final_model.pt")
        additional_episodes: how many more episodes to train for
        render: if True, show the game window
    """
    
    # Setup (same as train())
    render_mode = "human" if render else None
    env = FortressDefenseEnv(render_mode=render_mode)
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Using device: " + str(device))
    
    # Create agent and load the checkpoint
    agent = DQNAgent(state_size, action_size, device)
    agent.load(checkpoint_path)
    print("Continuing from epsilon: " + str(agent.epsilon))
    print("Previous training steps: " + str(agent.train_step_count))
    
    # Load previous training curves so we can append to them
    save_dir = "ddqn_v2_results"
    try:
        all_rewards = list(np.load(save_dir + "/rewards.npy"))
        all_survivals = list(np.load(save_dir + "/survivals.npy"))
        all_eliminations = list(np.load(save_dir + "/eliminations.npy"))
        all_losses = list(np.load(save_dir + "/losses.npy"))
        all_epsilons = list(np.load(save_dir + "/epsilons.npy"))
        previous_episodes = len(all_rewards)
        print("Loaded " + str(previous_episodes) + " previous episodes of curves")
    except Exception as e:
        print("Could not load previous curves: " + str(e))
        all_rewards = []
        all_survivals = []
        all_eliminations = []
        all_losses = []
        all_epsilons = []
        previous_episodes = 0
    
    print_every = 10
    training_start_time = time.time()
    
    print("Continuing training for " + str(additional_episodes) + " more episodes...")
    print("-" * 60)
    
    for episode in tqdm(range(1, additional_episodes + 1), desc="Training"):
        state, info = env.reset()
        total_reward = 0
        episode_losses = []
        done = False
        
        while not done:
            action = agent.pick_action(state)
            next_state, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            agent.store_experience(state, action, reward, next_state, float(done))
            loss = agent.learn()
            if loss is not None:
                episode_losses.append(loss)
            state = next_state
            total_reward += reward
        
        agent.decay_epsilon()
        
        all_rewards.append(total_reward)
        all_survivals.append(info["step_count"])
        all_eliminations.append(info["eliminations"])
        all_epsilons.append(agent.epsilon)
        if len(episode_losses) > 0:
            avg_loss = sum(episode_losses) / len(episode_losses)
        else:
            avg_loss = 0
        all_losses.append(avg_loss)
        
        total_episode_num = previous_episodes + episode
        
        if episode % print_every == 0:
            recent_rewards = all_rewards[-print_every:]
            recent_survivals = all_survivals[-print_every:]
            recent_elims = all_eliminations[-print_every:]
            avg_reward = sum(recent_rewards) / len(recent_rewards)
            avg_survival = sum(recent_survivals) / len(recent_survivals)
            avg_elims = sum(recent_elims) / len(recent_elims)
            
            elapsed = time.time() - training_start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            
            print(
                "Total Episode " + str(total_episode_num)
                + " | Avg Reward: " + str(round(avg_reward, 1))
                + " | Avg Survival: " + str(round(avg_survival, 1))
                + " | Avg Kills: " + str(round(avg_elims, 1))
                + " | Epsilon: " + str(round(agent.epsilon, 3))
                + " | Loss: " + str(round(avg_loss, 4))
                + " | Time: " + str(mins) + "m " + str(secs) + "s"
            )
        
        if episode % 100 == 0:
            agent.save(save_dir + "/checkpoint_ep" + str(total_episode_num) + ".pt")
            np.save(save_dir + "/rewards.npy", np.array(all_rewards))
            np.save(save_dir + "/survivals.npy", np.array(all_survivals))
            np.save(save_dir + "/eliminations.npy", np.array(all_eliminations))
            np.save(save_dir + "/losses.npy", np.array(all_losses))
            np.save(save_dir + "/epsilons.npy", np.array(all_epsilons))
            print("  -> Checkpoint and curves saved.")
    
    total_time = time.time() - training_start_time
    print("-" * 60)
    print("Continued training complete! Time: " + str(round(total_time / 60, 1)) + " minutes")
    
    agent.save(save_dir + "/final_model.pt")
    np.save(save_dir + "/rewards.npy", np.array(all_rewards))
    np.save(save_dir + "/survivals.npy", np.array(all_survivals))
    np.save(save_dir + "/eliminations.npy", np.array(all_eliminations))
    np.save(save_dir + "/losses.npy", np.array(all_losses))
    np.save(save_dir + "/epsilons.npy", np.array(all_epsilons))
    
    env.close()
    
    plot_results(all_rewards, all_survivals, all_eliminations, all_losses,
                 all_epsilons, save_dir)


   


# PART 5: PLOTTING RESULTS

def plot_results(rewards, survivals, eliminations, losses, epsilons, save_dir):
    """Plot and save training curves."""

    # Helper: compute a moving average to smooth noisy curves
    def moving_average(data, window=50):
        smoothed = []
        for i in range(len(data)):
            start = max(0, i - window + 1)
            chunk = data[start:i + 1]
            avg = sum(chunk) / len(chunk)
            smoothed.append(avg)
        return smoothed

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Plot 1: Total reward per episode
    axes[0][0].plot(rewards, alpha=0.3, color="blue", label="Raw")
    axes[0][0].plot(moving_average(rewards), color="blue", label="Smoothed (50 ep)")
    axes[0][0].set_xlabel("Episode")
    axes[0][0].set_ylabel("Total Reward")
    axes[0][0].set_title("Total Reward per Episode")
    axes[0][0].legend()

    # Plot 2: Steps survived per episode
    axes[0][1].plot(survivals, alpha=0.3, color="green", label="Raw")
    axes[0][1].plot(moving_average(survivals), color="green", label="Smoothed (50 ep)")
    axes[0][1].set_xlabel("Episode")
    axes[0][1].set_ylabel("Steps Survived")
    axes[0][1].set_title("Survival Time per Episode")
    axes[0][1].legend()

    # Plot 3: Enemies eliminated per episode
    axes[1][0].plot(eliminations, alpha=0.3, color="red", label="Raw")
    axes[1][0].plot(moving_average(eliminations), color="red", label="Smoothed (50 ep)")
    axes[1][0].set_xlabel("Episode")
    axes[1][0].set_ylabel("Eliminations")
    axes[1][0].set_title("Enemies Eliminated per Episode")
    axes[1][0].legend()

    # Plot 4: Epsilon decay
    axes[1][1].plot(epsilons, color="purple")
    axes[1][1].set_xlabel("Episode")
    axes[1][1].set_ylabel("Epsilon")
    axes[1][1].set_title("Exploration Rate (Epsilon) Decay")

    plt.tight_layout()
    plt.savefig(save_dir + "/training_curves.png", dpi=150)
    plt.show()
    print("Training curves saved to " + save_dir + "/training_curves.png")


# PART 6: WATCH A TRAINED AGENT PLAY

def watch(model_path):
    """
    Load a trained agent and watch it play one episode with visuals.
    Usage: change the if __name__ block at the bottom to call watch().
    """
    env = FortressDefenseEnv(render_mode="human")
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Create agent and load trained weights
    agent = DQNAgent(state_size, action_size, device)
    agent.load(model_path)
    agent.epsilon = 0.0  # no exploration, pure exploitation

    state, info = env.reset()
    total_reward = 0
    done = False

    while not done:
        action = agent.pick_action(state)
        state, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        done = terminated or truncated

    print("Episode finished!")
    print("Total reward: " + str(round(total_reward, 2)))
    print("Final info: " + str(info))
    env.close()


# MAIN - Run training or watch a trained agent

if __name__ == "__main__":
    # train(num_episodes=5000, render=False)
    continue_training("ddqn_v2_results/final_model.pt", additional_episodes=5000, render=False)

    # To train with visuals (slow, but you can watch):
    # train(num_episodes=100, render=True)

    # To watch a trained agent play:
    # watch("ddqn_v2_results/final_model.pt")