import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime
import pytz

class WeatherService:
    def __init__(self):
        # Setup the Open-Meteo API client with cache and retry on error
        cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
        retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
        self.openmeteo = openmeteo_requests.Client(session = retry_session)

    def get_weather_forecast(self, lat: float, lon: float, start_time: datetime, end_time: datetime):
        """
        Get weather forecast for a specific location and TIME WINDOW.
        Returns hourly data strictly within the window.
        """
        if start_time.tzinfo is None: start_time = start_time.replace(tzinfo=pytz.utc)
        if end_time.tzinfo is None: end_time = end_time.replace(tzinfo=pytz.utc)
        
        # Open-Meteo accepts 'start_date' and 'end_date' (YYYY-MM-DD).
        # We need to cover the full window, which might span two days.
        start_date_str = start_time.strftime("%Y-%m-%d")
        end_date_str = end_time.strftime("%Y-%m-%d")
        
        url = "https://api.open-meteo.com/v1/forecast"
        
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ["temperature_2m", "relative_humidity_2m", "cloud_cover", "wind_speed_10m"],
            "start_date": start_date_str,
            "end_date": end_date_str,
            "timezone": "UTC"
        }

        responses = self.openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        # Process hourly data
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(1).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(2).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()
        
        # Create a DataFrame or similar structure to filter by time
        hourly_data = {
            "date": pd.date_range(
                start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
                end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
                freq = pd.Timedelta(seconds = hourly.Interval()),
                inclusive = "left"
            )
        }
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["cloud_cover"] = hourly_cloud_cover
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        
        df = pd.DataFrame(data = hourly_data)
        
        # Filter STRICTLY by the requested window
        mask = (df['date'] >= start_time) & (df['date'] <= end_time)
        window_df = df.loc[mask]
        
        # Build hourly list
        hourly_summary = []
        for index, row in window_df.iterrows():
            hourly_summary.append({
                "time": row['date'].strftime("%H:%00"), # Just hour for display
                "ts": row['date'].isoformat(),
                "temp": round(row['temperature_2m'], 1),
                "clouds": round(row['cloud_cover'], 0),
                "humidity": round(row['relative_humidity_2m'], 0),
                "wind": round(row['wind_speed_10m'], 1)
            })
            
        # Averages for summary
        if not window_df.empty:
            avg_cloud = window_df['cloud_cover'].mean()
            avg_temp = window_df['temperature_2m'].mean()
            avg_hum = window_df['relative_humidity_2m'].mean()
        else:
            avg_cloud = 0.0
            avg_temp = 0.0
            avg_hum = 0.0
        
        return {
            "summary": {
                "avg_cloud_cover": round(avg_cloud, 1),
                "temp_avg": round(avg_temp, 1),
                "humidity_avg": round(avg_hum, 1)
            },
            "hourly": hourly_summary
        }
