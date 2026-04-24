# Script used to visually evaluate the trained policy
from stable_baselines3 import PPO
from fortress_defense_env import FortressDefenseEnv

env = FortressDefenseEnv(render_mode="human")
model = PPO.load("ppo_results_shoot_30k/ppo_final_model")

obs, info = env.reset()
done = False

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(int(action))
    done = terminated or truncated

print(info)
env.close()