"""
TFT Training Script
Trains the Temporal Fusion Transformer model on synthetic disaster relief data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data.synthetic_timeseries import generate_synthetic_timeseries
from ml_models.tft_forecaster import TFTForecaster, get_variable_importance
import pandas as pd

def train_tft_model():
    """
    Complete training pipeline for TFT model.
    """
    print("=" * 60)
    print(" TFT Training Pipeline")
    print("=" * 60)
    
    # Step 1: Generate synthetic data
    print("\n Step 1: Generating synthetic training data...")
    df = generate_synthetic_timeseries(num_districts=10, num_days=365)
    print(f" Generated {len(df)} rows of data")
    print(f"   Districts: {df['district'].nunique()}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    
    # Step 2: Initialize TFT forecaster
    print("\n🔧 Step 2: Initializing TFT model...")
    forecaster = TFTForecaster(
        max_prediction_length=30,  # Forecast 30 days ahead
        max_encoder_length=90       # Use 90 days of history
    )
    
    # Step 3: Prepare data
    print("\n Step 3: Preparing datasets...")
    training_data, validation_data = forecaster.prepare_data(df)
    print(f" Training samples: {len(training_data)}")
    print(f" Validation samples: {len(validation_data)}")
    
    # Step 4: Create model
    print("\n  Step 4: Creating TFT model architecture...")
    model = forecaster.create_model()
    print(" Model created with:")
    print(f"   - Hidden size: 32")
    print(f"   - Attention heads: 1")
    print(f"   - Max prediction horizon: 30 days")
    
    # Step 5: Train model
    print("\n Step 5: Training model...")
    print("   (This will take 5-10 minutes)")
    trainer = forecaster.train(max_epochs=30, gpus=0)
    
    # Step 6: Save model
    print("\n Step 6: Saving trained model...")
    forecaster.save_model("ml_models/tft_model.ckpt")
    
    # Step 7: Test prediction
    print("\n Step 7: Testing predictions...")
    test_df = df[df['time_idx'] >= df['time_idx'].max() - 30]
    predictions = forecaster.predict(test_df, district='Mumbai', return_attention=True)
    print(f" Generated predictions for Mumbai")
    print(f"   Prediction shape: {predictions['predictions'].shape}")
    if predictions.get('attention'):
        print(f"   Attention weights extracted: ✓")
    
    # Step 8: Variable importance
    print("\n Step 8: Extracting variable importance...")
    try:
        importance = get_variable_importance(model, training_data)
        print(" Variable importance calculated")
    except Exception as e:
        print(f"  Could not extract importance: {e}")
    
    print("\n" + "=" * 60)
    print(" TFT TRAINING COMPLETE!")
    print("=" * 60)
    print("\n Next steps:")
    print("   1. Model saved to: ml_models/tft_model.ckpt")
    print("   2. Use the model via API: /api/tft/forecast")
    print("   3. View attention weights: /api/tft/attention")
    
    return forecaster, df

if __name__ == '__main__':
    try:
        forecaster, df = train_tft_model()
        print("\n Success! TFT model is ready for use.")
    except Exception as e:
        print(f"\n Error during training: {e}")
        import traceback
        traceback.print_exc()
