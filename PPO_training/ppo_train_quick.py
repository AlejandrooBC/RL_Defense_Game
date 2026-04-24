import os
import sys
import csv
import json
import argparse
import importlib.util
from typing import List, Tuple

# Headless defaults for training
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

def load_module_alias(module_name: str, candidates: List[str]):
    """Load a module from one of several candidate filenames and register it under module_name."""
    if module_name in sys.modules:
        return sys.modules[module_name]

    for path in candidates:
        if os.path.exists(path):
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not build import spec for {path}")
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module

    raise FileNotFoundError(
        f"Could not find a file for module '{module_name}'. Tried: {candidates}"
    )

def preload_project_modules(base_dir: str) -> None:
    """Make imports work for different filenames."""
    order = [
        "player_bullet_class",
        "infantryman_bullet_class",
        "sniper_bullet_class",
        "tile_class",
        "ruby_class",
        "ruby_maker_class",
        "player_class",
        "infantryman_class",
        "sniper_class",
        "game_class",
    ]

    for name in order:
        candidates = [
            os.path.join(base_dir, f"{name}.py"),
            os.path.join(base_dir, f"{name}(4).py"),
        ]
        load_module_alias(name, candidates)

class SilentSound:
    def play(self, *args, **kwargs):
        return None

    def set_volume(self, *args, **kwargs):
        return None

    def get_num_channels(self, *args, **kwargs):
        return 0

_ASSETS_PATCHED = False

def patch_pygame_assets_for_missing_files() -> None:
    """Allow headless training even if image/sound/font assets are missing."""
    global _ASSETS_PATCHED
    if _ASSETS_PATCHED:
        return

    import pygame

    original_image_load = pygame.image.load
    original_sound = pygame.mixer.Sound
    original_font = pygame.font.Font

    def safe_image_load(path: str):
        try:
            return original_image_load(path)
        except Exception:
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 0))
            return surf

    def safe_sound(path: str):
        try:
            return original_sound(path)
        except Exception:
            return SilentSound()

    def safe_font(path, size: int):
        try:
            return original_font(path, size)
        except Exception:
            return pygame.font.SysFont(None, size)

    pygame.image.load = safe_image_load
    pygame.mixer.Sound = safe_sound
    pygame.font.Font = safe_font
    _ASSETS_PATCHED = True

def make_env_module(base_dir: str):
    env_path = os.path.join(base_dir, "fortress_defense_env.py")
    if not os.path.exists(env_path):
        raise FileNotFoundError(f"Missing {env_path}")
    spec = importlib.util.spec_from_file_location("fortress_defense_env", env_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not import {env_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["fortress_defense_env"] = module
    spec.loader.exec_module(module)
    return module

def moving_average(values: List[float], window: int = 20) -> List[float]:
    out = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        out.append(sum(values[start:i + 1]) / (i - start + 1))
    return out

def parse_monitor_csv(path: str) -> Tuple[List[float], List[float], List[float]]:
    rewards, lengths, times = [], [], []
    if not os.path.exists(path):
        return rewards, lengths, times

    with open(path, "r", newline="") as f:
        lines = [line for line in f if not line.startswith("#")]

    if not lines:
        return rewards, lengths, times

    reader = csv.DictReader(lines)
    for row in reader:
        rewards.append(float(row["r"]))
        lengths.append(float(row["l"]))
        times.append(float(row["t"]))

    return rewards, lengths, times

def make_training_plot(monitor_path: str, out_path: str) -> None:
    try:
        import matplotlib.pyplot as plt
    except Exception as exc:
        print(f"Skipping plot because matplotlib is unavailable: {exc}")
        return

    rewards, lengths, _ = parse_monitor_csv(monitor_path)
    if not rewards:
        print("No episode data found in monitor.csv; skipping plot.")
        return

    smoothed_rewards = moving_average(rewards, window=min(20, len(rewards)))
    smoothed_lengths = moving_average(lengths, window=min(20, len(lengths)))

    plt.figure(figsize=(10, 5))
    plt.plot(rewards, label="Episode reward", alpha=0.4)
    plt.plot(smoothed_rewards, label="Reward moving average")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.title("PPO training rewards")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()

    plt.figure(figsize=(10, 5))
    plt.plot(lengths, label="Episode length", alpha=0.4)
    plt.plot(smoothed_lengths, label="Length moving average")
    plt.xlabel("Episode")
    plt.ylabel("Episode length")
    plt.title("PPO episode lengths")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path.replace(".png", "_lengths.png"))
    plt.close()

def run_eval_episodes(model, env_factory, n_episodes: int = 10):
    stats = []
    for _ in range(n_episodes):
        env = env_factory(render=False)
        obs, info = env.reset()
        done = False
        total_reward = 0.0
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(int(action))
            total_reward += float(reward)
            done = terminated or truncated

        stats.append({
            "total_reward": total_reward,
            "kills": int(info.get("eliminations", 0)),
            "fortress_integrity": int(info.get("fortress_integrity", 0)),
            "player_health": int(info.get("player_health", 0)),
            "round_number": int(info.get("round_number", 0)),
            "round_time": int(info.get("round_time", 0)),
            "step_count": int(info.get("step_count", 0)),
        })
        env.close()

    def mean(key: str) -> float:
        return sum(s[key] for s in stats) / len(stats) if stats else 0.0

    summary = {
        "episodes": n_episodes,
        "mean_total_reward": mean("total_reward"),
        "mean_kills": mean("kills"),
        "mean_fortress_integrity": mean("fortress_integrity"),
        "mean_player_health": mean("player_health"),
        "mean_round_number": mean("round_number"),
        "mean_step_count": mean("step_count"),
        "raw_episode_stats": stats,
    }
    return summary

def build_env_factory(base_dir: str, render: bool, max_episode_steps: int):
    preload_project_modules(base_dir)
    patch_pygame_assets_for_missing_files()
    env_module = make_env_module(base_dir)

    # Make the episodes shorter for faster training and cleaner plots
    env_module.MAX_STEPS_PER_EPISODE = max_episode_steps

    FortressDefenseEnv = env_module.FortressDefenseEnv

    def env_factory(render: bool = False):
        env = FortressDefenseEnv(render_mode="human" if render else None)

        original_reset = env.reset
        original_step = env.step

        env.prev_round_number = 1
        env.prev_enemy_health_sum = 0.0

        def current_enemy_health_sum():
            total = 0.0
            for enemy in env.enemy_group:
                total += max(0.0, float(getattr(enemy, "health", 0.0)))
            return total

        def patched_reset(*args, **kwargs):
            obs, info = original_reset(*args, **kwargs)
            env.prev_round_number = env.game.round_number
            env.prev_enemy_health_sum = current_enemy_health_sum()
            return obs, info

        def patched_compute_reward():
            reward = 0.0

            # Dense combat reward: reward actual damage, not just final kills
            current_enemy_sum = current_enemy_health_sum()
            damage_dealt = max(0.0, env.prev_enemy_health_sum - current_enemy_sum)
            reward += 3.0 * damage_dealt

            # Keep a strong kill reward
            elim_diff = env.player.player_eliminations - env.prev_eliminations
            reward += 100.0 * elim_diff

            # Make defending the fortress matter more
            fortress_diff = env.prev_fortress - env.game.fortress_integrity
            reward -= 3.0 * fortress_diff

            # Still penalize taking damage
            health_diff = env.prev_health - env.player.player_health
            reward -= 0.5 * health_diff

            # Small living cost
            reward -= 0.02

            # Smaller round-completion bonus so survival alone does not dominate
            if env.game.round_number > env.prev_round_number:
                reward += 10.0

            # Strong terminal penalty
            if env.game.game_over:
                reward -= 150.0

            # Corner-camping penalty
            px = env.player.position.x / env.WINDOW_WIDTH
            py = env.player.position.y / env.WINDOW_HEIGHT
            if px > 0.80 and (py < 0.25 or py > 0.75):
                reward -= 0.30

            return reward

        def patched_step(action):
            obs, reward, terminated, truncated, info = original_step(action)
            env.prev_round_number = env.game.round_number
            env.prev_enemy_health_sum = current_enemy_health_sum()
            return obs, reward, terminated, truncated, info

        env.reset = patched_reset
        env._compute_reward = patched_compute_reward
        env.step = patched_step
        return env

    return env_factory

def main():
    parser = argparse.ArgumentParser(description="Quick PPO trainer for the fortress defense RL project.")
    parser.add_argument("--timesteps", type=int, default=100000, help="Total PPO timesteps.")
    parser.add_argument("--max-episode-steps", type=int, default=1200, help="Episode truncation horizon.")
    parser.add_argument("--eval-episodes", type=int, default=10, help="How many deterministic eval episodes to run after training.")
    parser.add_argument("--results-dir", type=str, default="ppo_results", help="Where to save outputs.")
    parser.add_argument("--checkpoint-freq", type=int, default=10000, help="How often to save PPO checkpoints, in timesteps.")
    args = parser.parse_args()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(args.results_dir, exist_ok=True)

    try:
        import pygame  # noqa: F401
        import gymnasium  # noqa: F401
        from stable_baselines3 import PPO
        from stable_baselines3.common.callbacks import CheckpointCallback
        from stable_baselines3.common.monitor import Monitor
        from stable_baselines3.common.vec_env import DummyVecEnv
    except Exception as exc:
        print("Missing dependency.")
        print("Install with:")
        print("  pip install stable-baselines3 gymnasium pygame matplotlib")
        print(f"Import error: {exc}")
        raise

    env_factory = build_env_factory(
        base_dir=base_dir,
        render=False,
        max_episode_steps=args.max_episode_steps,
    )

    monitor_path = os.path.join(args.results_dir, "monitor.csv")
    if os.path.exists(monitor_path):
        os.remove(monitor_path)

    def make_monitored_env():
        env = env_factory(render=False)
        return Monitor(env, filename=monitor_path)

    train_env = DummyVecEnv([make_monitored_env])

    model = PPO(
        policy="MlpPolicy",
        env=train_env,
        learning_rate=3e-4,
        n_steps=512,
        batch_size=128,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.02,
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=1,
        device="auto",
        tensorboard_log=os.path.join(args.results_dir, "tensorboard"),
    )

    checkpoint_callback = CheckpointCallback(
        save_freq=max(args.checkpoint_freq, 1),
        save_path=args.results_dir,
        name_prefix="ppo_checkpoint",
    )

    print("Starting PPO training...")
    print(f"Timesteps: {args.timesteps}")
    print(f"Episode horizon: {args.max_episode_steps}")
    print(f"Results dir: {args.results_dir}")

    model.learn(total_timesteps=args.timesteps, callback=checkpoint_callback, progress_bar=False)

    final_model_path = os.path.join(args.results_dir, "ppo_final_model")
    model.save(final_model_path)
    print(f"Saved final model to {final_model_path}")

    eval_summary = run_eval_episodes(model, env_factory, n_episodes=args.eval_episodes)
    eval_path = os.path.join(args.results_dir, "eval_summary.json")
    with open(eval_path, "w", encoding="utf-8") as f:
        json.dump(eval_summary, f, indent=2)
    print(f"Saved evaluation summary to {eval_path}")

    plot_path = os.path.join(args.results_dir, "ppo_training_rewards.png")
    make_training_plot(monitor_path, plot_path)
    print(f"Saved training plots to {plot_path}")

    print("\nEvaluation summary:")
    print(json.dumps(eval_summary, indent=2))

if __name__ == "__main__":
    main()