import joblib
import pandas as pd
from darts import TimeSeries

from .config import (
    FEATURES,
    TARGETS,
    TARGET_COLUMNS,
    NAN_COLS,
    NUMERICAL_FEATURES_v2, 
)
from .utils import (
    load_data,
    calculate_errors,
    create_feature_encodings,
    prepare_categorical_targets,
    create_supervised_learning_targets,
)


class LeakModelPipeline:
    """Pipeline for processing leak model data and creating time series."""
    
    def __init__(self, scalar_input_path: str):
        """Initialize the pipeline with the feature scaler.
        
        Args:
            scalar_input_path: Path to the feature scaler file
        """
        self.scalar_input_path = scalar_input_path
        self.feature_scaler = self._load_scaler()
    
    def _load_scaler(self):
        """Load the feature scaler from the specified path."""
        return joblib.load(self.scalar_input_path)
    
    def _prepare_data(self, data_input_path: str) -> pd.DataFrame:
        """Load and prepare the initial dataset."""
        df = load_data(data_input_path)
        leak_df = df.copy()
        leak_df[NAN_COLS] = leak_df[NAN_COLS].fillna(value='none')
        calculate_errors(leak_df)
        return leak_df
    
    def _create_features(self, leak_df: pd.DataFrame) -> pd.DataFrame:
        """Create feature encodings and prepare targets."""
        feat_eng_df = create_feature_encodings(leak_df)
        feat_eng_df = prepare_categorical_targets(feat_eng_df, TARGET_COLUMNS)
        feat_eng_df = create_supervised_learning_targets(feat_eng_df)
        return feat_eng_df
    
    def _scale_features(self, feat_eng_df: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features using the loaded scaler."""
        ff_scaled = feat_eng_df.copy()
        ff_scaled[NUMERICAL_FEATURES_v2] = self.feature_scaler.transform(feat_eng_df[NUMERICAL_FEATURES_v2])
        return ff_scaled
    
    def _clean_and_sort_data(self, ff_scaled: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates, handle missing values, and sort by house_id and timestamp."""
        dup_df = (
            ff_scaled
            .sort_values(['house_id', 'timestamp'])
            .drop_duplicates(subset=['house_id', 'timestamp'], keep='first')
            .reset_index(drop=True)
        )
        
        drop_cols = FEATURES + TARGETS
        df_ts = dup_df.dropna(subset=drop_cols)
        
        df_ts['timestamp'] = pd.to_datetime(df_ts['timestamp'])
        df_ts = df_ts.sort_values(['house_id', 'timestamp'])
        
        df_ts[TARGETS] = df_ts[TARGETS].astype("float32")
        df_ts[FEATURES] = df_ts[FEATURES].astype("float32")
        
        return df_ts
    
    def _create_time_series_for_house(self, group: pd.DataFrame, house_id: int) -> tuple[TimeSeries, TimeSeries]:
        """Create feature and target time series for a single house."""
        group = group.set_index('timestamp', drop=False)
        
        feat_ts = TimeSeries.from_dataframe(
            group,
            time_col='timestamp',
            value_cols=FEATURES,
            freq='15min',
        ).with_static_covariates(pd.DataFrame({'house_id': [house_id]}))
        
        targ_ts = TimeSeries.from_dataframe(
            group,
            time_col='timestamp',
            value_cols=TARGETS,
            freq='15min',
        ).with_static_covariates(pd.DataFrame({'house_id': [house_id]}))
        
        return feat_ts, targ_ts
    
    def _build_house_series(self, df_ts: pd.DataFrame) -> tuple[dict, dict]:
        """Build time series dictionaries for all houses."""
        house_feature_series = {}
        house_target_series = {}
        
        for house_id, group in df_ts.groupby('house_id', sort=False):
            feat_ts, targ_ts = self._create_time_series_for_house(group, house_id)
            house_feature_series[house_id] = feat_ts
            house_target_series[house_id] = targ_ts
        
        return house_feature_series, house_target_series
    
    def run(self, data_input_path: str) -> tuple[dict, dict]:
        """Run the complete data processing pipeline.
        
        Args:
            data_input_path: Path to the input data file
            
        Returns:
            Tuple of (house_feature_series, house_target_series) dictionaries
        """
        leak_df = self._prepare_data(data_input_path)
        feat_eng_df = self._create_features(leak_df)
        ff_scaled = self._scale_features(feat_eng_df)
        df_ts = self._clean_and_sort_data(ff_scaled)
        return self._build_house_series(df_ts)


# Backward compatibility function
def run_pipeline(
    data_input_path: str,
    scalar_input_path: str,
) -> tuple[dict, dict]:
    """Run the complete data processing pipeline (legacy function).
    
    Args:
        data_input_path: Path to the input data file
        scalar_input_path: Path to the feature scaler file
        
    Returns:
        Tuple of (house_feature_series, house_target_series) dictionaries
    """
    pipeline = LeakModelPipeline(scalar_input_path)
    return pipeline.run(data_input_path) 