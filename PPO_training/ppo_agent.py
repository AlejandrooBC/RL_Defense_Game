import csv
import json
import os
from typing import List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from fortress_defense_env import FortressDefenseEnv
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

class PPOFortressDefenseEnv(FortressDefenseEnv):
    """Small PPO-focused wrapper around the existing environment."""

    def __init__(self, render_mode=None, fast_max_steps=1500):
        super().__init__(render_mode=render_mode)
        self.fast_max_steps = fast_max_steps
        self.prev_round_number = 1

    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        self.prev_round_number = self.game.round_number
        return obs, info

    def step(self, action):
        # Save values from before the parent env updates them
        score_before = self.prev_score
        round_before = self.prev_round_number

        obs, reward, terminated, truncated, info = super().step(action)

        score_diff = info["score"] - score_before
        round_diff = info["round_number"] - round_before

        if score_diff >= 100 and round_diff == 0:
            reward -= 100.0

        # Add an explicit round-completion bonus instead
        if round_diff > 0:
            reward += 50.0 * round_diff

        # Truncate earlier so training finishes faster tonight
        if self.step_count >= self.fast_max_steps:
            truncated = True

        self.prev_round_number = info["round_number"]
        return obs, reward, terminated, truncated, info

def make_env(save_dir: str, render_mode=None, fast_max_steps: int = 1500):
    """Create one monitored environment."""

    def _init():
        env = PPOFortressDefenseEnv(
            render_mode=render_mode,
            fast_max_steps=fast_max_steps,
        )
        env = Monitor(env, filename=os.path.join(save_dir, "monitor.csv"))
        return env

    return _init

def train(
    total_timesteps: int = 25000,
    save_dir: str = "ppo_results",
    fast_max_steps: int = 1500,
):

    os.makedirs(save_dir, exist_ok=True)

    # One environment is safer here because the game uses PyGame and a lot of custom logic
    vec_env = DummyVecEnv([
        make_env(save_dir=save_dir, render_mode=None, fast_max_steps=fast_max_steps)
    ])

    # Normalize observations and rewards for stability
    vec_env = VecNormalize(
        vec_env,
        norm_obs=True,
        norm_reward=True,
        clip_obs=10.0,
    )

    policy_kwargs = dict(net_arch=[128, 128])

    model = PPO(
        policy="MlpPolicy",
        env=vec_env,
        learning_rate=3e-4,
        n_steps=512,
        batch_size=128,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,
        vf_coef=0.5,
        policy_kwargs=policy_kwargs,
        verbose=1,
        tensorboard_log=os.path.join(save_dir, "tensorboard"),
        device="auto",
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=10000,
        save_path=os.path.join(save_dir, "checkpoints"),
        name_prefix="ppo_fortress",
    )

    model.learn(total_timesteps=total_timesteps, callback=checkpoint_callback)

    model_path = os.path.join(save_dir, "final_model")
    vecnorm_path = os.path.join(save_dir, "vec_normalize.pkl")

    model.save(model_path)
    vec_env.save(vecnorm_path)
    vec_env.close()

    print(f"Saved PPO model to {model_path}.zip")
    print(f"Saved VecNormalize stats to {vecnorm_path}")

    rewards, lengths, times = load_monitor_csv(os.path.join(save_dir, "monitor.csv"))
    if len(rewards) > 0:
        plot_training_curves(rewards, lengths, save_dir)

    summary = evaluate(
        model_path=model_path + ".zip",
        vecnorm_path=vecnorm_path,
        n_eval_episodes=5,
        render=False,
        save_dir=save_dir,
        fast_max_steps=fast_max_steps,
    )

    return summary

def load_monitor_csv(path: str) -> Tuple[List[float], List[int], List[float]]:
    """Load episode rewards, lengths, and wall-clock times from Monitor CSV."""
    rewards = []
    lengths = []
    times = []

    if not os.path.exists(path):
        return rewards, lengths, times

    with open(path, "r", newline="") as f:
        reader = csv.DictReader(row for row in f if not row.startswith("#"))
        for row in reader:
            rewards.append(float(row["r"]))
            lengths.append(int(float(row["l"])))
            times.append(float(row["t"]))

    return rewards, lengths, times

def moving_average(values: List[float], window: int = 10) -> np.ndarray:
    """Simple moving average for noisy curves."""
    if len(values) == 0:
        return np.array([])

    smoothed = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        smoothed.append(np.mean(values[start:i + 1]))
    return np.array(smoothed)

def plot_training_curves(rewards: List[float], lengths: List[int], save_dir: str):
    """Save training plots for the report."""
    plt.figure(figsize=(10, 5))
    plt.plot(rewards, alpha=0.35, label="Episode reward")
    plt.plot(moving_average(rewards, window=10), label="Reward moving avg (10 ep)")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.title("PPO Training Reward")
    plt.legend()
    plt.tight_layout()
    reward_path = os.path.join(save_dir, "ppo_reward_curve.png")
    plt.savefig(reward_path, dpi=150)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(lengths, alpha=0.35, label="Episode length")
    plt.plot(moving_average(lengths, window=10), label="Length moving avg (10 ep)")
    plt.xlabel("Episode")
    plt.ylabel("Steps survived")
    plt.title("PPO Survival Length")
    plt.legend()
    plt.tight_layout()
    length_path = os.path.join(save_dir, "ppo_survival_curve.png")
    plt.savefig(length_path, dpi=150)
    plt.close()

    print(f"Saved reward plot to {reward_path}")
    print(f"Saved survival plot to {length_path}")

def evaluate(
    model_path: str,
    vecnorm_path: str,
    n_eval_episodes: int = 5,
    render: bool = False,
    save_dir: str = "ppo_results",
    fast_max_steps: int = 1500,
):
    """Run a few evaluation episodes and save a summary."""
    eval_render_mode = "human" if render else None

    eval_env = DummyVecEnv([
        make_env(save_dir=save_dir, render_mode=eval_render_mode, fast_max_steps=fast_max_steps)
    ])

    eval_env = VecNormalize.load(vecnorm_path, eval_env)
    eval_env.training = False
    eval_env.norm_reward = False

    model = PPO.load(model_path, env=eval_env, device="auto")

    episode_rewards = []
    episode_lengths = []
    final_infos = []

    for episode in range(n_eval_episodes):
        obs = eval_env.reset()
        done = False
        total_reward = 0.0
        steps = 0
        last_info = None

        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, dones, infos = eval_env.step(action)
            total_reward += float(reward[0])
            done = bool(dones[0])
            steps += 1
            last_info = infos[0]

        episode_rewards.append(total_reward)
        episode_lengths.append(steps)
        final_infos.append(last_info)

        print(
            f"Eval episode {episode + 1}: reward={total_reward:.2f}, "
            f"steps={steps}, kills={last_info.get('eliminations', 'NA')}, "
            f"fortress={last_info.get('fortress_integrity', 'NA')}, "
            f"health={last_info.get('player_health', 'NA')}"
        )

    summary = {
        "mean_reward": float(np.mean(episode_rewards)) if episode_rewards else 0.0,
        "std_reward": float(np.std(episode_rewards)) if episode_rewards else 0.0,
        "mean_steps": float(np.mean(episode_lengths)) if episode_lengths else 0.0,
        "episode_rewards": episode_rewards,
        "episode_lengths": episode_lengths,
        "final_infos": final_infos,
    }

    summary_path = os.path.join(save_dir, "evaluation_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"Saved evaluation summary to {summary_path}")
    eval_env.close()
    return summary

def watch(
    model_path: str = "ppo_results/final_model.zip",
    vecnorm_path: str = "ppo_results/vec_normalize.pkl",
    fast_max_steps: int = 1500,
):
    """Watch one trained PPO episode with rendering."""
    evaluate(
        model_path=model_path,
        vecnorm_path=vecnorm_path,
        n_eval_episodes=1,
        render=True,
        save_dir="ppo_results",
        fast_max_steps=fast_max_steps,
    )

if __name__ == "__main__":
    summary = train(total_timesteps=50000, save_dir="ppo_results", fast_max_steps=1500)
    print("Final evaluation summary:")
    print(json.dumps(summary, indent=2))