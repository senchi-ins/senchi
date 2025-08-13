# TCN Leak Detection Model Implementation Plan

## Overview
Build a global TCN (Temporal Convolutional Network) model using Darts library to predict pipe leaks across 1000 homes with 15-minute interval data over a full year. The model will predict multiple leak-related targets 24 hours ahead while supporting real-time inference on streaming data from any house.

## Data Characteristics
- **Dataset**: 35M+ rows (1000 houses × 35,040 timestamps per house)
- **Temporal Resolution**: 15-minute intervals for full year (2025)
- **Features**: 12 sensor/pipe characteristics per house
- **Targets**: 5 leak-related variables (binary + categorical)
- **Static Info**: House-specific pipe material, dimensions (constant per house)

## Implementation Steps

### 1. Data Preparation & Feature Engineering
- Handle missing values in leak columns (currently filled with 'none')
- Create one-hot encoding for categorical targets:
  - `leak_type` → `leak_type_A`, `leak_type_B`, etc.
  - `leak_category` → multiple binary columns
  - `leak_branch`, `leak_pipe` → encoded appropriately
- One-hot encode `pipe_material` (Copper/PEX/etc.)
- Scale numerical features (`velocity_m_per_s`, `flow_m3_s`, etc.)
- Create future-shifted targets for 24h ahead prediction
- Verify data quality and temporal consistency

**Features (12 covariates)**:
```
velocity_m_per_s, flow_m3_s, upstream_transit_time_s, 
downstream_transit_time_s, delta_t_ns, pipe_width_in,
od_mm, wall_mm, id_mm, c_est_m_per_s, temp_est_c
```

**Static Covariates**:
```
pipe_material_Copper, pipe_material_PEX, house_id_embedding
```

### 2. Target Engineering & Labeling Strategy
- Create binary `pipe_burst_leak` target (already exists)
- Engineer "leak probability in next 24h" labels by forward-shifting targets
- Handle class imbalance (leaks are rare events)
- Create multivariate target TimeSeries with all leak variables
- Validate target distributions across houses

### 3. Cross-Validation Strategy (Nested Approach)

**Outer Loop - House-Level Split**:
- Use `GroupKFold(n_splits=5)` with `groups=house_id`
- Ensures entire houses are held out for generalization testing
- Tests model's ability to work on completely new houses

**Inner Loop - Temporal Split**:
- Use `TimeSeriesSplit(n_splits=6, test_size=96, gap=96)` 
- 96 = 24 hours × 4 samples/hour
- Gap prevents data leakage between train/test
- Tests model's temporal forecasting ability

### 4. Model Architecture & Training

**TCN Configuration**:
```python
TCNModel(
    input_chunk_length=7*96,    # 1 week history (672 timesteps)
    output_chunk_length=96,     # 24h forecast horizon
    n_epochs=50,                # Adjust based on early stopping
    batch_size=32,              # Memory permitting
    num_layers=3,               # TCN depth
    num_filters=64,             # Convolutional filters
    kernel_size=3,              # Convolution kernel
    dilation_base=2,            # Exponential dilation
    dropout=0.1,                # Regularization
    likelihood=GaussianLikelihood(),  # For probabilistic outputs
    optimizer_kwargs={"lr": 1e-3},
    random_state=42
)
```

**Training Strategy**:
- Train single global model on all houses
- Use static covariates for house-specific info
- Implement early stopping on validation loss
- Save best model weights based on validation metrics

### 5. Model Training Implementation
- Build Darts TimeSeries objects for each house
- Combine all houses into training dataset
- Implement training loop with proper validation
- Use appropriate loss function for multi-target prediction
- Monitor training metrics (loss, AUROC, PR-AUC)
- Save model checkpoints and final weights

### 6. Model Evaluation & Validation

**Metrics to Track**:
- **Binary Classification**: AUROC, PR-AUC, F1-score for `pipe_burst_leak`
- **Multi-class**: Accuracy, macro/micro F1 for categorical targets  
- **Temporal**: MAE, MAPE for regression components
- **Probabilistic**: Calibration plots, reliability diagrams

**Evaluation Outputs**:
- Cross-validation results summary
- Per-house performance analysis
- Temporal performance across forecast horizons
- Final model weights and artifacts

## Technical Considerations

### Memory Management
- 35M+ rows may require chunked processing
- Consider Darts' lazy loading capabilities
- Use efficient data types (float32 vs float64)

### Class Imbalance
- Leaks are rare events → use class weights or focal loss
- Consider SMOTE or other oversampling techniques
- Monitor precision/recall trade-offs

### Hyperparameter Tuning
- Use inner CV fold for hyperparameter optimization
- Focus on: learning rate, network depth, chunk lengths
- Consider Bayesian optimization for efficiency

## Expected Deliverables
1. **Trained Model**: Global TCN with optimal weights
2. **Preprocessing Pipeline**: Scalers, encoders, feature engineering
3. **Evaluation Report**: CV results, performance metrics

## Success Criteria
- **Generalization**: Good performance on unseen houses (outer CV)
- **Temporal Accuracy**: Reliable 24h ahead predictions (inner CV)
- **Practical Utility**: AUROC > 0.8 for leak detection
