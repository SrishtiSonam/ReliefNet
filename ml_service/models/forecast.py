#
# Reference Implementation for "An Explainable Forecasting System for Humanitarian Needs Assessment"
# Methodology based on Nair et al., AAAI-23 [1]
#
# This script demonstrates the dual-model approach:
# 1. A Gradient Boosting model for accurate forecasting.
# 2. A Linear Regression model for explainability and scenario analysis.
# 3. The SHAP library is used to provide feature importance for the complex model.
#

import pandas as pd
import numpy as np
import shap
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

def simulate_humanitarian_data(num_samples=1000):
    """
    Generates a synthetic dataset mimicking drivers of forced displacement.
    This simulates the kind of data the Foresight system would use.[1]
    """
    np.random.seed(42)
    data = {
        'conflict_events': np.random.randint(0, 500, num_samples),
        'gdp_per_capita': np.random.uniform(500, 5000, num_samples),
        'food_insecurity_index': np.random.uniform(0, 1, num_samples),
        'governance_score': np.random.uniform(-2.5, 2.5, num_samples),
        'unemployment_rate': np.random.uniform(2, 30, num_samples),
    }
    df = pd.DataFrame(data)

    # Create a non-linear target variable with interactions and noise
    df['displaced_persons'] = (
        50000 * (1 - df['governance_score'] / 5) +
        200 * df['conflict_events'] +
        10000 * df['food_insecurity_index']**2 -
        500 * df['gdp_per_capita'] * (df['governance_score'] > 0) +
        np.random.normal(0, 20000, num_samples)
    )
    df['displaced_persons'] = df['displaced_persons'].astype(int).clip(lower=0)
    return df

def perform_what_if_analysis(forecast_value, scenario, linear_model, feature_names):
    """
    Adjusts a forecast based on a user-defined scenario using linear model coefficients (elasticities).
    This function implements the "what-if" capability described in the paper.[1]
    
    Args:
        forecast_value (float): The baseline forecast from the primary model.
        scenario (dict): A dictionary like {'feature_name': percentage_change}, e.g., {'conflict_events': 0.10}.
        linear_model (LinearRegression): The trained linear model.
        feature_names (list): List of feature names.
        
    Returns:
        float: The adjusted forecast value.
    """
    adjusted_forecast = forecast_value
    coeffs = dict(zip(feature_names, linear_model.coef_))
    
    print("\n--- Scenario Analysis ---")
    print(f"Baseline Forecast: {forecast_value:,.0f} displaced persons")
    
    for feature, change in scenario.items():
        if feature in coeffs:
            # The change in forecast is the feature's current value * percentage change * coefficient
            # This is a simplification; a more robust way is to calculate the absolute change
            # For this example, we assume the change is an absolute increase/decrease for simplicity
            # A true elasticity would be percentage-based.
            adjustment = change * coeffs[feature]
            adjusted_forecast += adjustment
            print(f"Applying scenario: {change:.0f} unit change in '{feature}' -> Adjusting forecast by {adjustment:,.0f}")
        else:
            print(f"Warning: Feature '{feature}' not in the model.")
            
    print(f"Adjusted Forecast: {adjusted_forecast:,.0f} displaced persons")
    return adjusted_forecast

# --- Main Execution ---

# 1. Generate Data
humanitarian_df = simulate_humanitarian_data()
X = humanitarian_df.drop('displaced_persons', axis=1)
y = humanitarian_df['displaced_persons']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 2. Train the primary forecasting model (Gradient Boosting)
print("Training Gradient Boosting model for forecasting...")
gbt_model = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=3, random_state=42)
gbt_model.fit(X_train, y_train)
gbt_preds = gbt_model.predict(X_test)
gbt_rmse = np.sqrt(mean_squared_error(y_test, gbt_preds))
print(f"GBT Model RMSE: {gbt_rmse:,.2f}\n")

# 3. Train the explainability model (Linear Regression)
print("Training Linear Regression model for explainability...")
lr_model = LinearRegression()
lr_model.fit(X_train, y_train)
print("Learned Coefficients (Elasticities):")
for feature, coef in zip(X.columns, lr_model.coef_):
    print(f"  - {feature}: {coef:.2f}")

# 4. Perform a "What-If" Scenario Analysis on a sample prediction
sample_idx = 0
sample_data = X_test.iloc[[sample_idx]]
baseline_forecast = gbt_model.predict(sample_data)

# Define a scenario: conflict events increase by 100, and food insecurity worsens by 0.2
scenario = {
    'conflict_events': 100,
    'food_insecurity_index': 0.2
}

adjusted_forecast = perform_what_if_analysis(baseline_forecast, scenario, lr_model, X.columns)

# 5. Generate Explanations for the GBT model using SHAP
print("\n--- Generating SHAP Explanations for GBT Model ---")
explainer = shap.Explainer(gbt_model, X_train)
shap_values = explainer(X_test)

# Plot feature importance
print("Displaying SHAP summary plot...")
plt.title("SHAP Feature Importance for Displacement Forecast Model")
shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
plt.tight_layout()
plt.show()

# Plot detailed SHAP values
plt.title("Detailed SHAP Values for Individual Predictions")
shap.summary_plot(shap_values, X_test, show=False)
plt.tight_layout()
plt.show()