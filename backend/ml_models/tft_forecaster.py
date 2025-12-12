"""
Temporal Fusion Transformer (TFT) Model for Disaster Relief Forecasting
Uses PyTorch Forecasting library for multi-horizon time series prediction
"""

import torch
import pytorch_lightning as pl
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.data import GroupNormalizer
from pytorch_forecasting.metrics import QuantileLoss
import pandas as pd
import numpy as np
from pathlib import Path

class TFTForecaster:
    """
    Temporal Fusion Transformer for disaster relief demand forecasting.
    
    Features:
    - Multi-horizon forecasting (1-30 days)
    - Attention mechanisms for interpretability
    - Uncertainty quantification
    - Multiple time series (districts)
    """
    
    def __init__(self, max_prediction_length=30, max_encoder_length=90):
        self.max_prediction_length = max_prediction_length
        self.max_encoder_length = max_encoder_length
        self.model = None
        self.training_data = None
        self.validation_data = None
        
    def prepare_data(self, df):
        """
        Prepare data for TFT training.
        
        Args:
            df: DataFrame with columns: date, district, time_idx, target variables, features
        """
        # Define the dataset
        self.training_data = TimeSeriesDataSet(
            df[lambda x: x.time_idx <= df['time_idx'].max() - self.max_prediction_length],
            time_idx="time_idx",
            target="food_demand",  # Primary target
            group_ids=["district"],
            min_encoder_length=self.max_encoder_length // 2,
            max_encoder_length=self.max_encoder_length,
            min_prediction_length=1,
            max_prediction_length=self.max_prediction_length,
            
            # Static features (don't change over time)
            static_categoricals=["district"],
            static_reals=["population", "infrastructure", "coastal"],
            
            # Time-varying known features (known in future)
            time_varying_known_categoricals=["month", "day_of_week"],
            time_varying_known_reals=["time_idx", "day_of_year"],
            
            # Time-varying unknown features (only known historically)
            time_varying_unknown_categoricals=["disaster_event"],
            time_varying_unknown_reals=[
                "rainfall", "temperature",
                "water_demand", "medicine_demand", "shelter_demand"
            ],
            
            # Normalization
            target_normalizer=GroupNormalizer(
                groups=["district"], transformation="softplus"
            ),
            add_relative_time_idx=True,
            add_target_scales=True,
            add_encoder_length=True,
        )
        
        # Validation dataset
        self.validation_data = TimeSeriesDataSet.from_dataset(
            self.training_data,
            df,
            predict=True,
            stop_randomization=True
        )
        
        return self.training_data, self.validation_data
    
    def create_model(self):
        """Create TFT model"""
        self.model = TemporalFusionTransformer.from_dataset(
            self.training_data,
            learning_rate=0.03,
            hidden_size=32,  # Smaller for faster training
            attention_head_size=1,
            dropout=0.1,
            hidden_continuous_size=16,
            output_size=7,  # 7 quantiles for uncertainty
            loss=QuantileLoss(),
            log_interval=10,
            reduce_on_plateau_patience=4,
        )
        return self.model
    
    def train(self, max_epochs=30, gpus=0):
        """
        Train the TFT model.
        
        Args:
            max_epochs: Maximum training epochs
            gpus: Number of GPUs (0 for CPU)
        """
        # Create dataloaders
        train_dataloader = self.training_data.to_dataloader(
            train=True, batch_size=64, num_workers=0
        )
        val_dataloader = self.validation_data.to_dataloader(
            train=False, batch_size=64, num_workers=0
        )
        
        # Create trainer
        trainer = pl.Trainer(
            max_epochs=max_epochs,
            accelerator="cpu" if gpus == 0 else "gpu",
            devices=1 if gpus == 0 else gpus,
            gradient_clip_val=0.1,
            enable_progress_bar=True,
            enable_model_summary=True,
        )
        
        # Train
        print("🚀 Starting TFT training...")
        trainer.fit(
            self.model,
            train_dataloaders=train_dataloader,
            val_dataloaders=val_dataloader,
        )
        print("✅ Training complete!")
        
        return trainer
    
    def predict(self, df, district=None, return_attention=False):
        """
        Make predictions with the trained model.
        
        Args:
            df: Input dataframe
            district: Specific district to predict (None for all)
            return_attention: Whether to return attention weights
        
        Returns:
            predictions: Dictionary with predictions and optionally attention weights
        """
        if self.model is None:
            raise ValueError("Model not trained yet!")
        
        # Filter for specific district if requested
        if district:
            df = df[df['district'] == district]
        
        # Create prediction dataset
        pred_dataset = TimeSeriesDataSet.from_dataset(
            self.training_data, df, predict=True, stop_randomization=True
        )
        pred_dataloader = pred_dataset.to_dataloader(
            train=False, batch_size=64, num_workers=0
        )
        
        # Make predictions
        raw_predictions, x = self.model.predict(
            pred_dataloader, mode="raw", return_x=True
        )
        
        result = {
            "predictions": raw_predictions["prediction"].cpu().numpy(),
            "quantiles": raw_predictions["quantiles"].cpu().numpy() if "quantiles" in raw_predictions else None,
        }
        
        # Extract attention weights if requested
        if return_attention:
            result["attention"] = self._extract_attention(raw_predictions)
        
        return result
    
    def _extract_attention(self, raw_predictions):
        """Extract and process attention weights"""
        attention_weights = {}
        
        if "attention" in raw_predictions:
            attn = raw_predictions["attention"].cpu().numpy()
            attention_weights["encoder_attention"] = attn
        
        if "static_variable_selection" in raw_predictions:
            attention_weights["static_vars"] = raw_predictions["static_variable_selection"].cpu().numpy()
        
        return attention_weights
    
    def save_model(self, path="ml_models/tft_model.ckpt"):
        """Save trained model"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)
        print(f"✅ Model saved to {path}")
    
    def load_model(self, path="ml_models/tft_model.ckpt"):
        """Load trained model"""
        if self.model is None:
            raise ValueError("Create model first using create_model()")
        self.model.load_state_dict(torch.load(path))
        print(f"✅ Model loaded from {path}")

def get_variable_importance(model, training_data):
    """
    Extract variable importance from trained TFT model.
    
    Returns:
        Dictionary with importance scores for each variable type
    """
    interpretation = model.interpret_output(
        training_data.to_dataloader(train=False, batch_size=1, num_workers=0),
        reduction="sum"
    )
    
    return {
        "encoder_variables": interpretation.get("encoder_variables", {}),
        "decoder_variables": interpretation.get("decoder_variables", {}),
        "static_variables": interpretation.get("static_variables", {}),
    }
