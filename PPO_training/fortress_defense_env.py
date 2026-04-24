"""
FortressDefenseEnv - Gymnasium wrapper for the Audition Absurdity PyGame game.
Wraps the existing game code so an RL agent can interact with it via step/reset.

Usage:
    env = FortressDefenseEnv(render_mode=None)  # headless for training
    env = FortressDefenseEnv(render_mode="human")  # with visuals for demo
    
    obs, info = env.reset()
    for _ in range(1000):
        action = env.action_space.sample()  # replace with agent's action
        obs, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            obs, info = env.reset()
    env.close()
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import os
import warnings
warnings.filterwarnings("ignore")

# ============================================================
# ACTION DEFINITIONS
# ============================================================
# 0: NOOP (stand still)
# 1: LEFT
# 2: RIGHT
# 3: UP
# 4: DOWN
# 5: SHOOT
# 6: UP-LEFT (diagonal)
# 7: UP-RIGHT (diagonal)
# 8: DOWN-LEFT (diagonal)
# 9: DOWN-RIGHT (diagonal)
NUM_ACTIONS = 10

# How many game frames to advance per env.step() call.
# At 60 FPS, FRAMES_PER_STEP=4 means ~15 decisions per second.
FRAMES_PER_STEP = 4

# Maximum steps per episode (prevents infinite episodes).
MAX_STEPS_PER_EPISODE = 5000

# Top-K nearest enemies to include in the state vector.
TOP_K_ENEMIES = 5


class FortressDefenseEnv(gym.Env):
    """Gymnasium environment wrapping the Audition Absurdity fortress defense game."""

    metadata = {"render_modes": ["human", None], "render_fps": 60}

    def __init__(self, render_mode=None):
        super().__init__()

        self.render_mode = render_mode
        self.action_space = spaces.Discrete(NUM_ACTIONS)

        # State vector layout:
        # [player_x, player_y, player_health, player_ammo,
        #  fortress_integrity, round_time, round_number, player_eliminations,
        #  enemy_1_dx, enemy_1_dy, enemy_1_health,
        #  enemy_2_dx, enemy_2_dy, enemy_2_health,
        #  ...  (TOP_K_ENEMIES enemies, 3 features each)
        #  ruby_exists, ruby_dx, ruby_dy]
        # Total = 8 + TOP_K_ENEMIES * 3 + 3
        state_size = 8 + TOP_K_ENEMIES * 3 + 3
        # Using large bounds; values will be normalized during training
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf,
            shape=(state_size,), dtype=np.float32
        )

        # Internal state
        self.game = None
        self.player = None
        self.current_action = 0
        self.step_count = 0
        self.prev_score = 0
        self.prev_fortress = 0
        self.prev_health = 0
        self.prev_eliminations = 0

        # Game constants (from main.py)
        self.WINDOW_WIDTH = 1280
        self.WINDOW_HEIGHT = 736
        self.FPS = 60

        # Pygame initialization flag
        self._pygame_initialized = False

    def _init_pygame(self):
        """Initialize pygame with or without display."""
        if self._pygame_initialized:
            return

        if self.render_mode == "human":
            pygame.init()
            self.display_surface = pygame.display.set_mode(
                (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            )
            pygame.display.set_caption("Fortress Defense - RL Training")
        else:
            # Headless mode: no display, dummy audio
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["SDL_AUDIODRIVER"] = "dummy"
            pygame.init()
            self.display_surface = pygame.Surface(
                (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
            )

        self.clock = pygame.time.Clock()
        self._pygame_initialized = True

    def _create_game(self):
        """
        Create a fresh game instance. 
        This mirrors the setup in main.py but patches key behaviors.
        """
        # Import game classes (they must be on the Python path)
        from game_class import Game
        from tile_class import Tile
        from player_class import Player
        from ruby_maker_class import RubyMaker

        # Create sprite groups
        main_tile_group = pygame.sprite.Group()
        platform_group = pygame.sprite.Group()
        barrier_group = pygame.sprite.Group()
        player_group = pygame.sprite.Group()
        player_bullet_group = pygame.sprite.Group()
        ally_group = pygame.sprite.Group()
        ally_bullet_group = pygame.sprite.Group()
        enemy_group = pygame.sprite.Group()
        enemy_bullet_group = pygame.sprite.Group()
        ruby_group = pygame.sprite.Group()

        # The tile map (copied from main.py)
        tile_map = [
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,4,2,2,8,8,8,8,8,8,8,8,8,2,2,4,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,9,5,5,5,5,5,5,5,9,5,5,3,1],
            [-2,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1,8,5,5,5,-6,5,5,5,5,5,5,5,5,5,3,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,5,5,7,5,5,5,5,5,3,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,5,5,7,5,5,5,5,5,2,1],
            [-3,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1,8,5,5,5,5,5,-1,5,7,5,5,5,5,5,3,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,5,5,5,5,5,5,5,5,2,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,5,5,5,5,5,5,5,5,8,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,-5,5,5,5,5,5,5,5,8,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,5,5,5,5,5,5,5,5,8,1],
            [-3,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1,8,5,5,5,5,5,5,5,7,5,5,5,5,5,8,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,5,5,7,5,5,5,5,5,8,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,5,5,7,5,5,5,5,5,8,1],
            [-2,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,6,1,8,5,5,5,5,5,5,5,5,5,5,5,5,5,8,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,5,5,5,5,5,5,5,5,8,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,8,5,5,5,5,5,5,5,5,5,5,5,-4,5,8,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,4,8,8,8,8,8,8,8,8,8,8,8,8,8,4,1],
            [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
        ]

        # Build tiles (same logic as main.py)
        player = None
        for i in range(len(tile_map)):
            for j in range(len(tile_map[i])):
                val = tile_map[i][j]
                if val == 1:
                    Tile(j*32, i*32, 1, main_tile_group, platform_group)
                elif val == 2:
                    Tile(j*32, i*32, 5, main_tile_group)
                    Tile(j*32, i*32, 2, main_tile_group)
                elif val == 3:
                    Tile(j*32, i*32, 5, main_tile_group)
                    Tile(j*32, i*32, 3, main_tile_group, platform_group)
                elif val == 4:
                    Tile(j*32, i*32, 5, main_tile_group)
                    Tile(j*32, i*32, 4, main_tile_group)
                elif val == 5:
                    Tile(j*32, i*32, 5, main_tile_group)
                elif val == 6:
                    Tile(j*32, i*32, 6, main_tile_group)
                elif val == 7:
                    Tile(j*32, i*32, 7, main_tile_group, platform_group, barrier_group)
                elif val == 8:
                    Tile(j*32, i*32, 5, main_tile_group)
                    Tile(j*32, i*32, 8, main_tile_group)
                elif val == 9:
                    Tile(j*32, i*32, 5, main_tile_group)
                    Tile(j*32, i*32, 9, main_tile_group)
                elif val == -1:
                    player = Player(
                        self.WINDOW_WIDTH, self.WINDOW_HEIGHT,
                        j*32 - 32, i*32 + 32,
                        platform_group, barrier_group,
                        player_bullet_group, enemy_bullet_group
                    )
                    player_group.add(player)
                    Tile(j*32, i*32, 5, main_tile_group)
                elif val == -4:
                    Tile(j*32, i*32, 5, main_tile_group)
                    RubyMaker(j*32, i*32, main_tile_group)

        # Create the Game object
        game = Game(
            tile_map, self.WINDOW_WIDTH, self.WINDOW_HEIGHT,
            self.FPS, self.clock, self.display_surface, player,
            player_bullet_group, enemy_group, enemy_bullet_group,
            main_tile_group, platform_group, barrier_group, ruby_group
        )

        # ---- CRITICAL PATCHES ----

        # 1. Override pause_game so it doesn't block waiting for input
        game.pause_game = lambda main_text, sub_text: None

    

        # 2. Patch start_new_round and reset_game to skip ally references
        original_start_new_round = game.start_new_round
        def patched_start_new_round():
            """Reset round without touching allies."""
            game.round_number += 1
            game.round_time = game.STARTING_ROUND_TIME
            game.fortress_integrity = game.STARTING_FORTRESS_INTEGRITY

            game.player.player_health = game.player.STARTING_PLAYER_HEALTH
            game.player.player_ammo = game.player.STARTING_PLAYER_AMMO
            game.player.player_eliminations = game.player.STARTING_PLAYER_ELIMINATIONS
            game.player.reset()

            game.ruby_add_eliminations = game.STARTING_RUBY_ADD_ELIMINATIONS

            game.enemy_group.empty()
            game.enemy_bullet_group.empty()
            game.ruby_group.empty()
            game.player_bullet_group.empty()
          
            # Skip pause_game — already patched to do nothing

        game.start_new_round = patched_start_new_round

        original_reset_game = game.reset_game
        def patched_reset_game():
            """Reset game without touching allies."""
            game.fortress_integrity = game.STARTING_FORTRESS_INTEGRITY
            game.round_number = game.STARTING_ROUND_NUMBER
            game.round_time = game.STARTING_ROUND_TIME

            game.infantryman_creation_time = game.STARTING_INFANTRYMAN_CREATION_TIME
            game.sniper_creation_time = game.STARTING_SNIPER_CREATION_TIME
            game.ruby_add_eliminations = game.STARTING_RUBY_ADD_ELIMINATIONS

            game.player.player_score = game.player.STARTING_PLAYER_SCORE
            game.player.player_health = game.player.STARTING_PLAYER_HEALTH
            game.player.player_ammo = game.player.STARTING_PLAYER_AMMO
            game.player.player_eliminations = game.player.STARTING_PLAYER_ELIMINATIONS
            game.player.reset()

            game.enemy_group.empty()
            game.enemy_bullet_group.empty()
            game.ruby_group.empty()
            game.player_bullet_group.empty()
           

        game.reset_game = patched_reset_game

        # 3. Patch game over checks to set a flag instead of resetting
        #    This lets the wrapper detect game over BEFORE the game resets
        game.game_over = False

        def patched_check_game_over_health():
            if game.player.player_health <= 0:
                game.game_over = True

        def patched_check_game_over_fortress():
            if game.fortress_integrity <= 0:
                game.game_over = True

        game.check_game_over_health = patched_check_game_over_health
        game.check_game_over_fortress = patched_check_game_over_fortress

        # 4. Patch check_ruby_collisions to skip ally healing
        def patched_check_ruby_collisions():
            """Ruby pickup that only affects the player, not allies."""
            if pygame.sprite.spritecollide(game.player, game.ruby_group, True):
                game.ruby_pickup_sound.play()
                game.player.player_score += 100
                game.player.player_health += 10
                if game.player.player_health > game.player.STARTING_PLAYER_HEALTH:
                    game.player.player_health = game.player.STARTING_PLAYER_HEALTH

        game.check_ruby_collisions = patched_check_ruby_collisions

        # 5. Monkey-patch the player's move method to use RL actions
        #    instead of reading the keyboard
        env_ref = self  # capture reference for the closure

        def patched_move(self_player):
            """Replacement for Player.move() that reads action from env."""
            self_player.acceleration = pygame.math.Vector2(0, 0)
            action = env_ref.current_action

            # Determine acceleration based on action
            if action == 1:    # LEFT
                self_player.is_still = False
                self_player.acceleration.x = -1 * self_player.HORIZONTAL_ACCELERATION
                self_player.animate(self_player.move_left_sprites, 0.25)
            elif action == 2:  # RIGHT
                self_player.is_still = False
                self_player.acceleration.x = self_player.HORIZONTAL_ACCELERATION
                self_player.animate(self_player.move_right_sprites, 0.25)
            elif action == 3:  # UP
                self_player.is_still = False
                self_player.acceleration.y = -1 * self_player.VERTICAL_ACCELERATION
                self_player.animate(self_player.move_right_sprites, 0.25)
            elif action == 4:  # DOWN
                self_player.is_still = False
                self_player.acceleration.y = self_player.VERTICAL_ACCELERATION
                self_player.animate(self_player.move_left_sprites, 0.25)
            elif action == 5:  # SHOOT
                self_player.is_still = True
                self_player.fire()
                if self_player.velocity.x > 0:
                    self_player.animate(self_player.aim_right_sprites, 0.5)
                else:
                    self_player.animate(self_player.aim_left_sprites, 0.5)
            elif action == 6:  # UP-LEFT
                self_player.is_still = False
                self_player.acceleration.x = -1 * self_player.HORIZONTAL_ACCELERATION
                self_player.acceleration.y = -1 * self_player.VERTICAL_ACCELERATION
                self_player.animate(self_player.move_left_sprites, 0.25)
            elif action == 7:  # UP-RIGHT
                self_player.is_still = False
                self_player.acceleration.x = self_player.HORIZONTAL_ACCELERATION
                self_player.acceleration.y = -1 * self_player.VERTICAL_ACCELERATION
                self_player.animate(self_player.move_right_sprites, 0.25)
            elif action == 8:  # DOWN-LEFT
                self_player.is_still = False
                self_player.acceleration.x = -1 * self_player.HORIZONTAL_ACCELERATION
                self_player.acceleration.y = self_player.VERTICAL_ACCELERATION
                self_player.animate(self_player.move_left_sprites, 0.25)
            elif action == 9:  # DOWN-RIGHT
                self_player.is_still = False
                self_player.acceleration.x = self_player.HORIZONTAL_ACCELERATION
                self_player.acceleration.y = self_player.VERTICAL_ACCELERATION
                self_player.animate(self_player.move_right_sprites, 0.25)
            else:  # NOOP (action == 0)
                self_player.is_still = True
                if self_player.velocity.x > 0:
                    self_player.animate(self_player.aim_right_sprites, 0.5)
                else:
                    self_player.animate(self_player.aim_left_sprites, 0.5)

            # Physics update (same as original)
            self_player.acceleration.x -= self_player.velocity.x * self_player.HORIZONTAL_FRICTION
            self_player.acceleration.y -= self_player.velocity.y * self_player.VERTICAL_FRICTION
            self_player.velocity += self_player.acceleration
            self_player.position += self_player.velocity + (0.5 * self_player.acceleration)
            self_player.rect.bottomleft = self_player.position

        # Bind the patched move to the player instance
        import types
        player.move = types.MethodType(patched_move, player)

        return game, player, main_tile_group, platform_group, barrier_group, \
               player_group, player_bullet_group, ally_group, ally_bullet_group, \
               enemy_group, enemy_bullet_group, ruby_group

    def reset(self, seed=None, options=None):
        """Reset the environment and return the initial observation."""
        super().reset(seed=seed)

        self._init_pygame()

        # Create a fresh game
        (self.game, self.player,
         self.main_tile_group, self.platform_group, self.barrier_group,
         self.player_group, self.player_bullet_group,
         self.ally_group, self.ally_bullet_group,
         self.enemy_group, self.enemy_bullet_group,
         self.ruby_group) = self._create_game()

        # Reset tracking variables
        self.current_action = 0
        self.step_count = 0
        self.prev_score = 0
        self.prev_fortress = self.game.fortress_integrity
        self.prev_health = self.player.player_health
        self.prev_eliminations = self.player.player_eliminations

        obs = self._get_observation()
        info = self._get_info()
        return obs, info

    def step(self, action):
        """
        Execute one agent action by advancing the game FRAMES_PER_STEP frames.
        Returns (observation, reward, terminated, truncated, info).
        """
        self.current_action = action
        self.step_count += 1

        # Advance the game by FRAMES_PER_STEP frames
        for _ in range(FRAMES_PER_STEP):
            # Process pygame events (needed to prevent freezing)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.close()
                    return self._get_observation(), 0.0, True, False, self._get_info()

            # Update all sprite groups (mirrors main.py game loop)
            self.main_tile_group.update()
            self.platform_group.update()
            self.barrier_group.update()
            self.player_group.update()
            self.player_bullet_group.update()
            self.ally_group.update()
            self.ally_bullet_group.update()
            self.enemy_group.update()
            self.enemy_bullet_group.update()
            self.ruby_group.update()
            self.game.update()

            # Render if in human mode
            if self.render_mode == "human":
                self._render_frame()

        # Compute reward
        reward = self._compute_reward()

        # Check termination conditions
        terminated = self.game.game_over

        # Check truncation (max steps reached)
        truncated = (self.step_count >= MAX_STEPS_PER_EPISODE)

        # Update previous values for reward computation
        self.prev_score = self.player.player_score
        self.prev_fortress = self.game.fortress_integrity
        self.prev_health = self.player.player_health
        self.prev_eliminations = self.player.player_eliminations

        obs = self._get_observation()
        info = self._get_info()

        return obs, reward, terminated, truncated, info

    def _compute_reward(self):
        """
        Compute reward based on changes since the last step.
        Reward components (tune these as needed):
        """
        reward = 0.0

        # Kills should matter a lot more
        elim_diff = self.player.player_eliminations - self.prev_eliminations
        reward += 100.0 * elim_diff

        # Fortress damage should be painful
        fortress_diff = self.prev_fortress - self.game.fortress_integrity
        reward -= 2.0 * fortress_diff

        # Player damage penalty
        health_diff = self.prev_health - self.player.player_health
        reward -= 0.5 * health_diff

        # Small living penalty so the agent cannot just stall forever
        reward -= 0.02

        # Strong terminal penalty
        if self.game.game_over:
            reward -= 150.0

        # Correct wave-survival bonus
        score_diff = self.player.player_score - self.prev_score
        if score_diff == 50:
            reward += 50.0

        # Light penalty for camping in corners
        px = self.player.position.x / self.WINDOW_WIDTH
        py = self.player.position.y / self.WINDOW_HEIGHT

        if px > 0.80 and (py < 0.25 or py > 0.75):
            reward -= 0.25

        return reward

    def _get_observation(self):
        """
        Build the state vector from game objects.
        """
        # Player info (normalized by starting values)
        px = self.player.position.x / self.WINDOW_WIDTH
        py = self.player.position.y / self.WINDOW_HEIGHT
        p_health = self.player.player_health / self.player.STARTING_PLAYER_HEALTH
        p_ammo = self.player.player_ammo / self.player.STARTING_PLAYER_AMMO

        # Game info
        fortress = self.game.fortress_integrity / self.game.STARTING_FORTRESS_INTEGRITY
        round_time = self.game.round_time / self.game.STARTING_ROUND_TIME
        round_num = self.game.round_number / 10.0  # normalize assuming ~10 rounds max
        eliminations = self.player.player_eliminations / 20.0  # normalize

        state = [px, py, p_health, p_ammo,
                 fortress, round_time, round_num, eliminations]

        # Top-K nearest enemies (relative position + health)
        enemies = list(self.enemy_group)
        # Compute distances and sort by nearest
        enemy_data = []
        for e in enemies:
            dx = (e.position.x - self.player.position.x) / self.WINDOW_WIDTH
            dy = (e.position.y - self.player.position.y) / self.WINDOW_HEIGHT
            e_health = e.health / e.STARTING_HEALTH
            dist = (dx ** 2 + dy ** 2) ** 0.5
            enemy_data.append((dist, dx, dy, e_health))

        # Sort by distance (nearest first)
        enemy_data.sort(key=lambda x: x[0])

        # Take top K, pad with zeros if fewer than K
        for k in range(TOP_K_ENEMIES):
            if k < len(enemy_data):
                _, dx, dy, e_health = enemy_data[k]
                state.extend([dx, dy, e_health])
            else:
                state.extend([0.0, 0.0, 0.0])

        # Ruby info (nearest ruby)
        rubies = list(self.ruby_group)
        if len(rubies) > 0:
            # Find nearest ruby
            nearest_ruby = min(
                rubies,
                key=lambda r: (
                    (r.position.x - self.player.position.x) ** 2
                    + (r.position.y - self.player.position.y) ** 2
                )
            )
            ruby_exists = 1.0
            ruby_dx = (nearest_ruby.position.x - self.player.position.x) / self.WINDOW_WIDTH
            ruby_dy = (nearest_ruby.position.y - self.player.position.y) / self.WINDOW_HEIGHT
        else:
            ruby_exists = 0.0
            ruby_dx = 0.0
            ruby_dy = 0.0

        state.extend([ruby_exists, ruby_dx, ruby_dy])

        return np.array(state, dtype=np.float32)

    def _get_info(self):
        """Return auxiliary info dict."""
        return {
            "score": self.player.player_score,
            "eliminations": self.player.player_eliminations,
            "fortress_integrity": self.game.fortress_integrity,
            "player_health": self.player.player_health,
            "round_number": self.game.round_number,
            "round_time": self.game.round_time,
            "step_count": self.step_count,
        }

    def _render_frame(self):
        """Render a single frame (only called in 'human' mode)."""
        # Load background
        bg = pygame.transform.scale(
            pygame.image.load("images/background.png"),
            (self.WINDOW_WIDTH, self.WINDOW_HEIGHT)
        )
        self.display_surface.blit(bg, (0, 0))

        # Draw all sprite groups
        self.main_tile_group.draw(self.display_surface)
        self.platform_group.draw(self.display_surface)
        self.barrier_group.draw(self.display_surface)
        self.player_group.draw(self.display_surface)
        self.player_bullet_group.draw(self.display_surface)
        self.ally_group.draw(self.display_surface)
        self.ally_bullet_group.draw(self.display_surface)
        self.enemy_group.draw(self.display_surface)
        self.enemy_bullet_group.draw(self.display_surface)
        self.ruby_group.draw(self.display_surface)

        # Draw HUD
        self.game.draw()

        pygame.display.update()
        self.clock.tick(self.FPS)

    def render(self):
        """Public render method (Gymnasium API)."""
        if self.render_mode == "human":
            self._render_frame()

    def close(self):
        """Clean up pygame resources."""
        if self._pygame_initialized:
            pygame.quit()
            self._pygame_initialized = False


# QUICK TEST 
# ============================================================
if __name__ == "__main__":
    print("Testing FortressDefenseEnv with random actions...")
    env = FortressDefenseEnv(render_mode="human")
    obs, info = env.reset()
    print(f"Observation shape: {obs.shape}")
    print(f"Initial observation: {obs}")
    print(f"Initial info: {info}")

    total_reward = 0
    done = False
    step = 0

    while not done:
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        done = terminated or truncated
        step += 1

        if step % 100 == 0:
            print(f"Step {step}: reward={reward:.2f}, total={total_reward:.2f}, "
                  f"fortress={info['fortress_integrity']}, "
                  f"health={info['player_health']}, "
                  f"kills={info['eliminations']}")

    print(f"\nEpisode finished after {step} steps")
    print(f"Total reward: {total_reward:.2f}")
    print(f"Final info: {info}")
    env.close()