"""Evaluate all trained agents and baselines on the fortress defense environment."""
import torch
import numpy as np

# DQN and DDQN use the original env, DDQN v2 uses the v2 env
from fortress_defense_env import FortressDefenseEnv as EnvOriginal
from fortress_defense_env_v2 import FortressDefenseEnv as EnvV2
from dqn_agent import DQNAgent as DQNAgent128
from dqn_agent import QNetwork  # needed for loading
from doubledqn_agent import DQNAgent as DDQNAgent128
from doubledqn_agent_v2 import DQNAgent as DDQNAgentV2


def evaluate_learned(agent_class, env_class, model_path, label, num_episodes=50):
    env = env_class(render_mode=None)
    state_size = env.observation_space.shape[0]
    action_size = env.action_space.n
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    agent = agent_class(state_size, action_size, device)
    agent.load(model_path)
    agent.epsilon = 0.0  # pure exploitation

    rewards, survivals, kills = [], [], []

    for ep in range(1, num_episodes + 1):
        state, info = env.reset()
        total_reward = 0
        done = False
        while not done:
            action = agent.pick_action(state)
            state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated
        rewards.append(total_reward)
        survivals.append(info["step_count"])
        kills.append(info["eliminations"])

    env.close()
    print("=" * 60)
    print(label)
    print("-" * 60)
    print("  Reward:   {:.2f} +/- {:.2f}".format(np.mean(rewards), np.std(rewards)))
    print("  Survival: {:.2f} +/- {:.2f}".format(np.mean(survivals), np.std(survivals)))
    print("  Kills:    {:.2f} +/- {:.2f}".format(np.mean(kills), np.std(kills)))
    print()


def evaluate_random(env_class, num_episodes=50):
    env = env_class(render_mode=None)
    rewards, survivals, kills = [], [], []

    for ep in range(1, num_episodes + 1):
        state, info = env.reset()
        total_reward = 0
        done = False
        while not done:
            action = env.action_space.sample()
            state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated
        rewards.append(total_reward)
        survivals.append(info["step_count"])
        kills.append(info["eliminations"])

    env.close()
    print("=" * 60)
    print("Random Policy")
    print("-" * 60)
    print("  Reward:   {:.2f} +/- {:.2f}".format(np.mean(rewards), np.std(rewards)))
    print("  Survival: {:.2f} +/- {:.2f}".format(np.mean(survivals), np.std(survivals)))
    print("  Kills:    {:.2f} +/- {:.2f}".format(np.mean(kills), np.std(kills)))
    print()


def evaluate_heuristic(env_class, num_episodes=50):
    """Same heuristic logic from heuristic_agent.py."""
    SHOOT_RANGE = 0.5
    LOW_HEALTH = 0.4

    # State indices
    HEALTH = 2
    E1_DX, E1_DY, E1_HP = 8, 9, 10
    RUBY_EXISTS, RUBY_DX, RUBY_DY = 23, 24, 25

    ACTION_NOOP = 0
    ACTION_LEFT = 1
    ACTION_RIGHT = 2
    ACTION_UP = 3
    ACTION_DOWN = 4
    ACTION_SHOOT = 5

    def move_toward(dx, dy):
        if abs(dx) > abs(dy):
            return ACTION_LEFT if dx < 0 else ACTION_RIGHT
        else:
            return ACTION_UP if dy < 0 else ACTION_DOWN

    def heuristic_policy(state):
        health = state[HEALTH]
        edx, edy, ehp = state[E1_DX], state[E1_DY], state[E1_HP]
        dist = (edx**2 + edy**2) ** 0.5
        ruby = state[RUBY_EXISTS]
        rdx, rdy = state[RUBY_DX], state[RUBY_DY]

        if health < LOW_HEALTH and ruby > 0.5:
            return move_toward(rdx, rdy)
        if ehp < 0.01 and edx == 0.0 and edy == 0.0:
            return ACTION_NOOP
        if 0.01 < dist < SHOOT_RANGE:
            return ACTION_SHOOT
        return move_toward(edx, edy)

    env = env_class(render_mode=None)
    rewards, survivals, kills = [], [], []

    for ep in range(1, num_episodes + 1):
        state, info = env.reset()
        total_reward = 0
        done = False
        while not done:
            action = heuristic_policy(state)
            state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated
        rewards.append(total_reward)
        survivals.append(info["step_count"])
        kills.append(info["eliminations"])

    env.close()
    print("=" * 60)
    print("Heuristic Policy")
    print("-" * 60)
    print("  Reward:   {:.2f} +/- {:.2f}".format(np.mean(rewards), np.std(rewards)))
    print("  Survival: {:.2f} +/- {:.2f}".format(np.mean(survivals), np.std(survivals)))
    print("  Kills:    {:.2f} +/- {:.2f}".format(np.mean(kills), np.std(kills)))
    print()


if __name__ == "__main__":
    print("\n>>> Evaluating all methods (50 episodes each) <<<\n")

    # Baselines (use original env)
    evaluate_random(EnvOriginal, num_episodes=50)
    evaluate_heuristic(EnvOriginal, num_episodes=50)

    # DQN 128 on original env
    evaluate_learned(
        DQNAgent128, EnvOriginal,
        "dqn_results/final_model.pt",
        "DQN (128, fixed env)",
        num_episodes=50
    )

    # Double DQN 128 on original env
    evaluate_learned(
        DDQNAgent128, EnvOriginal,
        "ddqn_results/checkpoint_ep5000.pt",
        "Double DQN (128, fixed env)",
        num_episodes=50
    )

    # Double DQN v2 (256) on v2 env
    evaluate_learned(
        DDQNAgentV2, EnvV2,
        "ddqn_v2_results/final_model.pt",
        "Double DQN v2 (256, fixed env)",
        num_episodes=50
    )

    print(">>> Done! <<<")