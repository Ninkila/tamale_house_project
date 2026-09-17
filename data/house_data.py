from pathlib import Path

import numpy as np
import pandas as pd


data = pd.read_csv(Path(__file__).resolve().parent / "tamale_house_rentals.csv")
print(data.head())