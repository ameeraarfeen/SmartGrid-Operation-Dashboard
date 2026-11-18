import pandas as pd

times = pd.date_range("2024-01-01", periods=1344, freq="15min")

print(len(times))
print(times[0])
print(times[-1])