import os
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from ml_services.environments.disaster_env import DisasterReliefEnv

class DisasterPPOAgent:
    """
    PPO-based logistics optimization agent using Stable-Baselines3.
    """
    def __init__(self, env: DisasterReliefEnv, model_path: str = None):
        self.env = env
        self.model_path = model_path
        
        if model_path and os.path.exists(model_path):
            self.model = PPO.load(model_path, env=self.env)
        else:
            # Initialize new PPO model
            # Uses Multi-Layer Perceptron policy
            self.model = PPO(
                "MlpPolicy",
                self.env,
                learning_rate=3e-4,
                n_steps=2048,
                batch_size=64,
                n_epochs=10,
                gamma=0.99,
                gae_lambda=0.95,
                clip_range=0.2,
                ent_coef=0.01,
                verbose=1
            )
            
    def train(self, total_timesteps: int = 100000, save_dir: str = "./models/ppo"):
        """Train the PPO agent."""
        os.makedirs(save_dir, exist_ok=True)
        
        # Save a checkpoint every 10000 steps
        checkpoint_callback = CheckpointCallback(
            save_freq=10000,
            save_path=save_dir,
            name_prefix="ppo_disaster"
        )
        
        self.model.learn(total_timesteps=total_timesteps, callback=checkpoint_callback)
        self.model.save(f"{save_dir}/ppo_disaster_final")
        
    def predict_allocation(self, state: np.ndarray, deterministic: bool = True):
        """
        Predict resource allocation given the current environment state.
        Returns the action and a confidence estimation (using standard deviation if accessible, 
        or simply returning the deterministic action).
        """
        action, _states = self.model.predict(state, deterministic=deterministic)
        
        # In PPO with continuous action spaces, the policy outputs a mean and std dev.
        # We can extract the distribution if we need confidence, but for inference,
        # we return the action directly.
        # We can simulate confidence based on action extremity or variance.
        
        # Reshape to understandable format (W, D, 2)
        allocation = action.reshape((self.env.num_warehouses, self.env.num_districts, 2))
        
        return {
            "raw_action": action,
            "allocation": allocation,
            "confidence": 0.85 # Placeholder for actual variance calculation
        }

