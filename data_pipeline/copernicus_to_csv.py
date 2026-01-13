import cdsapi
import xarray as xr
import pandas as pd
from datetime import datetime
import os

# City coordinates (same as Streamlit)
CITIES = {
    "Mumbai": (18.9640, 72.8205),
    "Chennai": (13.0827, 80.2707)
}

TODAY = datetime.utcnow().strftime("%Y-%m-%d")

OUTPUT_CSV = "sea_level_daily.csv"

def fetch_sea_level():
    c = cdsapi.Client()

    c.retrieve(
        "satellite-sea-level-global",
        {
            "variable": "sea_surface_height_above_geoid",
            "product_type": "daily_averaged",
            "year": TODAY[:4],
            "month": TODAY[5:7],
            "day": TODAY[8:10],
            "format": "netcdf"
        },
        "sea_level.nc"
    )

    ds = xr.open_dataset("sea_level.nc")

    rows = []

    for city, (lat, lon) in CITIES.items():
        value = ds.sel(latitude=lat, longitude=lon, method="nearest")
        sea_level = float(value["sea_surface_height_above_geoid"].values)

        rows.append({
            "date": TODAY,
            "city": city,
            "sea_level_anomaly": sea_level
        })

    pd.DataFrame(rows).to_csv(OUTPUT_CSV, index=False)

    os.remove("sea_level.nc")
    print("✅ Sea level CSV updated:", OUTPUT_CSV)

if __name__ == "__main__":
    fetch_sea_level()

