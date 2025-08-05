import pandas as pd
import numpy as np

from config import CATEGORICAL_FEATURES_v1


def load_data(input_path: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    return df

def calculate_errors(df: pd.DataFrame) -> pd.DataFrame:
    theta_deg = 60
    theta_cos = np.cos(np.radians(theta_deg))
    epsilon = 1e-10

    # Extract needed fields as arrays
    L = df['l_path_m'].values
    t_u = df['upstream_transit_time_s'].values
    t_d = df['downstream_transit_time_s'].values
    V_actual = df['velocity_m_per_s'].values
    Q_actual = df['flow_m3_s'].values
    id_m = df['id_mm'].values / 1000  # mm to m

    # Step 1: Estimate velocity
    V_est = (L / (2 * theta_cos)) * ((1 / t_d) - (1 / t_u))

    # Step 2: Area of circular pipe
    A = (np.pi/4) * (id_m ** 2)

    # Step 3: Estimate flow
    Q_est = V_est * A

    # Step 4: Error metrics
    velocity_error = np.abs(V_actual - V_est) / np.maximum(np.abs(V_actual), epsilon)
    flow_rate_error = np.abs(Q_actual - Q_est) / np.maximum(np.abs(Q_actual), epsilon)

    # Step 5: Add to DataFrame
    df['V_est'] = V_est
    df['Q_est'] = Q_est
    df['velocity_error'] = velocity_error
    df['flow_rate_error'] = flow_rate_error
    df['velocity_error_pass'] = velocity_error <= 0.05
    df['flow_rate_error_pass'] = flow_rate_error <= 0.05

    return df

def create_feature_encodings(df: pd.DataFrame) -> pd.DataFrame:
    """Create one-hot encodings for categorical features"""
    df_encoded = df.copy()
    
    # One-hot encode categorical features
    for cat_feature in CATEGORICAL_FEATURES_v1:
        if cat_feature in df_encoded.columns:
            # Get unique values
            unique_vals = df_encoded[cat_feature].unique()
            
            # Create one-hot encoding
            encoded_cols = pd.get_dummies(df_encoded[cat_feature], 
                                        prefix=f'{cat_feature}_onehot', 
                                        prefix_sep='_')
            
            # Add encoded columns to dataframe
            df_encoded = pd.concat([df_encoded, encoded_cols], axis=1)
    
    return df_encoded

def prepare_categorical_targets(df: pd.DataFrame, target_cols: list) -> pd.DataFrame:
    """Prepare both binary and categorical targets"""
    df_targets = df.copy()
    
    for target_col in target_cols:
        if target_col in df_targets.columns:
            unique_vals = df_targets[target_col].unique()
            
            if target_col == 'pipe_burst_leak':
                # Binary target - keep as is (boolean/binary)
                # TODO: Refactor
                pass
                
            elif target_col == 'leak_branch':
                # Categorical target - we have options:
                
                # One-hot encode for multi-output
                target_encoded = pd.get_dummies(df_targets[target_col], 
                                              prefix=f'{target_col}_onehot', 
                                              prefix_sep='_')
                df_targets = pd.concat([df_targets, target_encoded], axis=1)
    
    return df_targets

def create_supervised_learning_targets(df, forecast_horizon: int = 24): # 24 15-min sections = 6 hours
    """
    Create supervised learning targets for the TCN model. Currently, this 
    creates a prediction if there will be any leaks in the next 24 hours.
    """
    
    df_with_targets = df.copy()
    df_with_targets["timestamp"] = pd.to_datetime(df_with_targets["timestamp"])
    df_with_targets = df_with_targets.sort_values(["house_id", "timestamp"])
    
    future_targets = []
    
    for house_id in df_with_targets["house_id"].unique():
        house_data = df_with_targets[df_with_targets["house_id"] == house_id].copy()
        
        # Rolling window - predict if leak occurs anywhere in next 24 hours
        house_data["pipe_burst_leak_next_24h"] = (
            house_data["pipe_burst_leak"]
            .rolling(window=forecast_horizon, min_periods=1)
            .max()
            .shift(-forecast_horizon + 1)
            .fillna(False)
            .astype(bool)
        )
        
        onehot_cols = [col for col in house_data.columns if col.startswith("leak_branch_onehot_")]
        
        for col in onehot_cols:
            # Only mark branch as True if leak happens on that specific branch
            leak_on_this_branch = (house_data[col] & house_data["pipe_burst_leak"])
            
            house_data[f"{col}_next_24h"] = (
                leak_on_this_branch
                .rolling(window=forecast_horizon, min_periods=1)
                .max()
                .shift(-forecast_horizon + 1)
                .fillna(False)
                .astype(bool)
            )
        
        # Handle "none" case - True only when no leak predicted at all
        none_flag = f"leak_branch_onehot_none_next_24h"
        if none_flag in house_data.columns:
            house_data[none_flag] = (
                house_data["pipe_burst_leak_next_24h"] == False
            )
        
        future_targets.append(house_data)
    
    return pd.concat(future_targets, axis=0, ignore_index=True).dropna(
        subset=["pipe_burst_leak_next_24h"]
    ) 