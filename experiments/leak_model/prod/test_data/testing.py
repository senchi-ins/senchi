
import requests
from darts import TimeSeries


def test_predict():
    """Test the predict endpoint."""
    response = requests.post("http://localhost:8000/predict", params={"house_id": 1})
    assert response.status_code == 200
    resp = response.json()
    pred = TimeSeries.from_json(resp)
    print(pred.values()[:, 0])


if __name__ == "__main__":
    test_predict()