"""
Heuristic baseline for the fortress defense environment.

This agent uses hand-coded rules to decide actions:
  1. If health is low, move toward the nearest ruby
  2. If an enemy is close, shoot it
  3. Otherwise, move toward the nearest enemy to engage
  4. Stay inside the fortress area

Run this file to evaluate the heuristic over multiple episodes and
compare against random and DQN baselines.
"""

import numpy as np
from fortress_defense_env import FortressDefenseEnv


# Thresholds for the heuristic rules
LOW_HEALTH_THRESHOLD = 0.4    # if health < 40%, seek rubies
SHOOT_RANGE = 0.5            # if nearest enemy is within this distance, shoot


# State vector indices (from fortress_defense_env.py layout)
PLAYER_X_IDX = 0
PLAYER_Y_IDX = 1
PLAYER_HEALTH_IDX = 2
FORTRESS_IDX = 4
ENEMY_1_DX_IDX = 8
ENEMY_1_DY_IDX = 9
ENEMY_1_HEALTH_IDX = 10
RUBY_EXISTS_IDX = 23
RUBY_DX_IDX = 24
RUBY_DY_IDX = 25

# Action indices
ACTION_NOOP = 0
ACTION_LEFT = 1
ACTION_RIGHT = 2
ACTION_UP = 3
ACTION_DOWN = 4
ACTION_SHOOT = 5
ACTION_UP_LEFT = 6
ACTION_UP_RIGHT = 7
ACTION_DOWN_LEFT = 8
ACTION_DOWN_RIGHT = 9


def move_toward(dx, dy):
    """
    Given a relative direction (dx, dy), return the action that moves
    most directly toward that target.
    """
    # If the target is very close, just stand still
    if abs(dx) < 0.02 and abs(dy) < 0.02:
        return ACTION_NOOP

    # Pick direction based on signs of dx and dy
    if dx > 0 and dy > 0:
        return ACTION_DOWN_RIGHT
    elif dx > 0 and dy < 0:
        return ACTION_UP_RIGHT
    elif dx < 0 and dy > 0:
        return ACTION_DOWN_LEFT
    elif dx < 0 and dy < 0:
        return ACTION_UP_LEFT
    elif dx > 0:
        return ACTION_RIGHT
    elif dx < 0:
        return ACTION_LEFT
    elif dy > 0:
        return ACTION_DOWN
    elif dy < 0:
        return ACTION_UP
    else:
        return ACTION_NOOP


def heuristic_policy(state):
    """
    Pick an action based on the current state using hand-coded rules.
    """
    player_health = state[PLAYER_HEALTH_IDX]

    # Enemy info (nearest enemy)
    enemy_dx = state[ENEMY_1_DX_IDX]
    enemy_dy = state[ENEMY_1_DY_IDX]
    enemy_health = state[ENEMY_1_HEALTH_IDX]
    enemy_distance = (enemy_dx ** 2 + enemy_dy ** 2) ** 0.5

    # Ruby info
    ruby_exists = state[RUBY_EXISTS_IDX]
    ruby_dx = state[RUBY_DX_IDX]
    ruby_dy = state[RUBY_DY_IDX]

    # Rule 1: if health is low and a ruby exists, go for it
    if player_health < LOW_HEALTH_THRESHOLD and ruby_exists > 0.5:
        return move_toward(ruby_dx, ruby_dy)

    # Rule 2: if there's no enemy alive, stand still
    if enemy_health < 0.01 and enemy_dx == 0.0 and enemy_dy == 0.0:
        return ACTION_NOOP

    # Rule 3: if enemy is close enough, shoot
    if enemy_distance < SHOOT_RANGE and enemy_distance > 0.01:
        return ACTION_SHOOT

    # Rule 4: move toward the nearest enemy to get in range
    return move_toward(enemy_dx, enemy_dy)


def evaluate(num_episodes=10, render=False):
    """Evaluate the heuristic policy over several episodes."""
    render_mode = "human" if render else None
    env = FortressDefenseEnv(render_mode=render_mode)

    results = {
        "reward": [],
        "survival": [],
        "eliminations": [],
        "fortress": [],
        "health": [],
    }

    print("Evaluating heuristic policy over " + str(num_episodes) + " episodes...")
    print("-" * 60)

    for ep in range(1, num_episodes + 1):
        state, info = env.reset()
        total_reward = 0
        done = False

        while not done:
            action = heuristic_policy(state)
            state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated

        results["reward"].append(total_reward)
        results["survival"].append(info["step_count"])
        results["eliminations"].append(info["eliminations"])
        results["fortress"].append(info["fortress_integrity"])
        results["health"].append(info["player_health"])

        print(
            "Episode " + str(ep)
            + " | Reward: " + str(round(total_reward, 1))
            + " | Survival: " + str(info["step_count"])
            + " | Kills: " + str(info["eliminations"])
            + " | Fortress: " + str(info["fortress_integrity"])
            + " | Health: " + str(info["player_health"])
        )

    env.close()

    # Print summary statistics
    print("-" * 60)
    print("Summary over " + str(num_episodes) + " episodes:")
    print("  Mean reward:       " + str(round(np.mean(results["reward"]), 2))
          + " (std " + str(round(np.std(results["reward"]), 2)) + ")")
    print("  Mean survival:     " + str(round(np.mean(results["survival"]), 2))
          + " (std " + str(round(np.std(results["survival"]), 2)) + ")")
    print("  Mean eliminations: " + str(round(np.mean(results["eliminations"]), 2))
          + " (std " + str(round(np.std(results["eliminations"]), 2)) + ")")
    print("  Mean fortress:     " + str(round(np.mean(results["fortress"]), 2)))
    print("  Mean health:       " + str(round(np.mean(results["health"]), 2)))

    return results


def evaluate_random(num_episodes=10):
    """Evaluate a uniform random policy for comparison."""
    env = FortressDefenseEnv(render_mode=None)

    results = {
        "reward": [],
        "survival": [],
        "eliminations": [],
        "fortress": [],
        "health": [],
    }

    print("Evaluating random policy over " + str(num_episodes) + " episodes...")
    print("-" * 60)

    for ep in range(1, num_episodes + 1):
        state, info = env.reset()
        total_reward = 0
        done = False

        while not done:
            action = env.action_space.sample()
            state, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            done = terminated or truncated

        results["reward"].append(total_reward)
        results["survival"].append(info["step_count"])
        results["eliminations"].append(info["eliminations"])
        results["fortress"].append(info["fortress_integrity"])
        results["health"].append(info["player_health"])

    env.close()

    print("Random policy summary over " + str(num_episodes) + " episodes:")
    print("  Mean reward:       " + str(round(np.mean(results["reward"]), 2)))
    print("  Mean survival:     " + str(round(np.mean(results["survival"]), 2)))
    print("  Mean eliminations: " + str(round(np.mean(results["eliminations"]), 2)))

    return results


if __name__ == "__main__":
    # Evaluate the heuristic
    heuristic_results = evaluate(num_episodes=50)

    # Also run a random baseline for comparison
    print("\n")
    random_results = evaluate_random(num_episodes=50)