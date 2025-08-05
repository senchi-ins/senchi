import json
import uvicorn
import pandas as pd
from fastapi import FastAPI
from contextlib import asynccontextmanager


from .pipeline import LeakModelPipeline
from .pred import Predictor


pipeline = None
predictor = None

scalar_input_path = "models/feature_scaler.pkl"
model_input_path = "models/tcn_fold5_20250805_084646.pt"
data_input_path = "test_data/synthetic_water_data_minute_100.csv"

@asynccontextmanager
async def startup_event(app):
    global pipeline, predictor
    pipeline = LeakModelPipeline(
        scalar_input_path=scalar_input_path,
    )
    predictor = Predictor(
        model_input_path=model_input_path,
    )

    yield

app = FastAPI(lifespan=startup_event)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Leak model API is running"}

@app.post("/predict")
async def predict(
    house_id: int,
):
    house_feature_series, house_target_series = pipeline.run(
        data_input_path=data_input_path,
    )
    prediction = predictor.predict(
        house_feature_series=house_feature_series,
        house_target_series=house_target_series,
        house_id=house_id,
    )
    return prediction.to_json()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 