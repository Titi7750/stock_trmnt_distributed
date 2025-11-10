import os
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

script_dir = Path(__file__).parent
data_dir = script_dir / "data"
data_dir.mkdir(exist_ok=True)

number_of_lines = 1_000_000

start_time = datetime(2025, 10, 12, 8, 0, 0)

timestamps = []
for line in range(number_of_lines):
    timestamps.append(start_time + timedelta(seconds=line))

user_ids = np.random.randint(1, 5000, number_of_lines)

urls = np.random.choice(
    [
        "https://edf.com/home",
        "https://edf.com/dashboard",
        "https://edf.com/login",
        "https://edf.com/settings",
        "https://edf.com/contact",
        "https://edf.com/analytics",
        "https://edf.com/help"
    ],
    number_of_lines
)

response_times = np.round(
    np.random.uniform(0.05, 1.5, number_of_lines),
    3
)

status_codes = np.random.choice(
    [
        200,
        200,
        200,
        403,
        404,
        500
    ],
    number_of_lines,
    p=[
        0.7,
        0.1,
        0.05,
        0.05,
        0.05,
        0.05
    ]
)

user_agents = np.random.choice(
    [
        "Chrome",
        "Firefox",
        "Edge",
        "Safari"
    ],
    number_of_lines
)

dataframe = pd.DataFrame({
    "timestamp": timestamps,
    "user_id": user_ids,
    "url": urls,
    "response_time": response_times,
    "status_code": status_codes,
    "user_agent": user_agents
})

output_path = data_dir / "logs_web.csv"
dataframe.to_csv(output_path, index=False)

print("Dataset généré avec succès !")
