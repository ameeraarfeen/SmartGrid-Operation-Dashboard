import requests
import pandas as pd

url = "https://archive-api.open-meteo.com/v1/archive"
params = {
    "latitude": 51.51,
    "longitude": -0.13,
    "start_date": "2026-08-03",
    "end_date": "2026-08-16",
    "hourly": "shortwave_radiation",
    "timezone": "Europe/London",
}
r = requests.get(url, params=params, timeout=30)
r.raise_for_status()
data = r.json()

sun = pd.DataFrame({
    "time": pd.to_datetime(data["hourly"]["time"]),
    "ghi_wm2": data["hourly"]["shortwave_radiation"],
})
sun.to_csv("irradiance_london.csv", index=False)

print(sun.shape)
print(sun["ghi_wm2"].max())
print(sun.head())