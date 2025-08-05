import pandas as pd
from darts.models import TCNModel

from .config import HYPERPARAMS


class Predictor:
    def __init__(self, model_input_path: str):
        self.model = self.load_model(model_input_path)

    def load_model(self, input_path: str) -> TCNModel:
        model = TCNModel(
            input_chunk_length = HYPERPARAMS["INPUT_CHUNK"],
            output_chunk_length = HYPERPARAMS["OUTPUT_CHUNK"],
            output_chunk_shift = HYPERPARAMS["OUTPUT_CHUNK_SHIFT"],
            likelihood = HYPERPARAMS["LIKELIHOOD"], 
            n_epochs = HYPERPARAMS["N_EPOCHS"],
            batch_size = HYPERPARAMS["BATCH_SIZE"],
            num_layers = HYPERPARAMS["NUM_LAYERS"],
            num_filters = HYPERPARAMS["NUM_FILTERS"],
            kernel_size = HYPERPARAMS["KERNEL_SIZE"],
            dilation_base = HYPERPARAMS["DILATION"],
            dropout = HYPERPARAMS["DROPOUT"],
            random_state = HYPERPARAMS["RANDOM_STATE"],
        )
        model.load_weights(input_path)
        return model

    def predict(
            self,
            house_feature_series: dict,
            house_target_series: dict,
            house_id: int,
        ) -> pd.DataFrame:
        """
        Make a prediction for a given house.
        """
        feats_ts = house_feature_series[house_id]
        targ_ts = house_target_series[house_id]
        minimum_length = HYPERPARAMS["INPUT_CHUNK"] + HYPERPARAMS["OUTPUT_CHUNK"]

        if len(targ_ts) >= minimum_length:
            hist = targ_ts[:-HYPERPARAMS["OUTPUT_CHUNK"]]
            
            preds = self.model.predict(
                n=HYPERPARAMS["OUTPUT_CHUNK"],
                series=hist,
                past_covariates=feats_ts,
            )
            
            return preds
        else:
            raise ValueError(f"House {house_id} has less than {minimum_length} rows") 