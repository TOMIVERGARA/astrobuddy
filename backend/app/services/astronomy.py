from skyfield.api import Loader, Topos, wgs84, Star, load as skyfield_load
from skyfield.almanac import dark_twilight_day, find_discrete, risings_and_settings, moon_phase as calc_moon_phase, fraction_illuminated
from skyfield import almanac
from skyfield.magnitudelib import planetary_magnitude
from datetime import datetime, timedelta
import pytz
from typing import List, Dict, Tuple, Optional
import math
import os
import requests
from timezonefinder import TimezoneFinder

from app.services.catalog import CelestialObject

class AstronomyService:
    def __init__(self, data_dir: str = 'backend/data'):
        # Load ephemeris (planets and moon)
        load = Loader(data_dir)
        self.ts = load.timescale()
        self.eph = load('de421.bsp')
        self.sun = self.eph['sun']
        self.moon = self.eph['moon']
        self.earth = self.eph['earth']
        
        self.tf = TimezoneFinder()
        
        # Planet dictionary
        self.planets = {
            'Mercury': self.eph['mercury'],
            'Venus': self.eph['venus'],
            'Mars': self.eph['mars'],
            'Jupiter': self.eph['jupiter barycenter'],
            'Saturn': self.eph['saturn barycenter'],
            'Uranus': self.eph['uranus barycenter'],
            'Neptune': self.eph['neptune barycenter']
        }

    def get_timezone(self, lat: float, lon: float) -> str:
        """Find timezone string from coordinates."""
        tz_str = self.tf.timezone_at(lng=lon, lat=lat)
        return tz_str if tz_str else 'UTC'

    def calculate_night_info(self, lat: float, lon: float, date: datetime):
        """
        Calculate twilight times, darkness window (Astronomical Twilight), and moon info.
        """
        # Ensure UTC used for calculation
        if date.tzinfo is None:
            date = date.replace(tzinfo=pytz.utc)
        
        # Define 24h window from noon of this day to noon of next day to capture "tonight"
        # If request is late night, we might want "tonight" relative to date.
        # Assuming date passed is the "Start Date" of observation (e.g. today).
        
        t0 = self.ts.from_datetime(date.replace(hour=12, minute=0, second=0))
        t1 = self.ts.from_datetime(date.replace(hour=12) + timedelta(days=1))

        observer = wgs84.latlon(lat, lon)
        
        # Calculate Astronomical Twilight (Sun < -18 degrees)
        f = dark_twilight_day(self.eph, observer)
        times, events = find_discrete(t0, t1, f)
        
        darkness_start = None
        darkness_end = None
        
        # Events: 0=Darkness, 1=Astro Twi, 2=Nautical, 3=Civil, 4=Day
        # We look for transition TO 0 (Start) and FROM 0 (End)
        
        for t, event in zip(times, events):
            dt = t.utc_datetime()
            if event == 0: # Entering Darkness
                darkness_start = dt
            elif event != 0 and darkness_start: # Leaving Darkness
                darkness_end = dt
                break
        
        # Fallback if no full darkness
        if not darkness_start:
             # Try Nautical Twilight (-12)? Or just None
             pass

        # Sun Rise/Set for general context
        f_sun = almanac.sunrise_sunset(self.eph, observer)
        sun_times, sun_events = find_discrete(t0, t1, f_sun)
        sunset = None
        sunrise = None
        for t, ev in zip(sun_times, sun_events):
            if ev == 0: # Set? Almanac sunrise_sunset returns True(Rise)/False(Set)? 
             # Wait, almanac.sunrise_sunset is deprecated->risings_and_settings logic better?
             # risings_and_settings(eph, sun, observer) -> 1=Rise, 0=Set
             pass

        # Let's use generic risings_and_settings for Sun
        radius_sun = 0.8333 # Standard refraction
        f_sun_rs = almanac.risings_and_settings(self.eph, self.sun, observer)
        s_times, s_events = find_discrete(t0, t1, f_sun_rs)
        for t, ev in zip(s_times, s_events):
            if ev == 0: sunset = t.utc_datetime()
            if ev == 1: sunrise = t.utc_datetime()

        moon_details = self.get_moon_details(lat, lon, date)

        return {
            "timezone": self.get_timezone(lat, lon),
            "darkness_window": {
                "start": darkness_start.isoformat() if darkness_start else None,
                "end": darkness_end.isoformat() if darkness_end else None
            },
            "sun": {
                "set": sunset.isoformat() if sunset else None,
                "rise": sunrise.isoformat() if sunrise else None
            },
            "moon": moon_details
        }

    def get_moon_details(self, lat: float, lon: float, date: datetime) -> dict:
        if date.tzinfo is None:
            date = date.replace(tzinfo=pytz.utc)

        t = self.ts.from_datetime(date)
        observer = wgs84.latlon(lat, lon)
        
        mp = calc_moon_phase(self.eph, t)
        phase_deg = mp.degrees
        illumination_pct = fraction_illuminated(self.eph, 'moon', t) * 100
        
        # Phase Name
        phase_name = ""
        if phase_deg < 10 or phase_deg > 350: phase_name = "New Moon"
        elif phase_deg < 80: phase_name = "Waxing Crescent"
        elif phase_deg < 100: phase_name = "First Quarter"
        elif phase_deg < 170: phase_name = "Waxing Gibbous"
        elif phase_deg < 190: phase_name = "Full Moon"
        elif phase_deg < 260: phase_name = "Waning Gibbous"
        elif phase_deg < 280: phase_name = "Last Quarter"
        else: phase_name = "Waning Crescent"

        # Rise/Set
        t0 = self.ts.from_datetime(date)
        t1 = self.ts.from_datetime(date + timedelta(hours=24))
        t_rise, t_set = self._find_rise_set(self.moon, observer, t0, t1)
        
        # NASA Dial-a-Moon API integration
        # API Format: https://svs.gsfc.nasa.gov/api/dialamoon/YYYY-MM-DDTHH:MM
        # We need to round to nearest hour or just use current hour? 
        # User provided: 2026-01-21T20:00. Let's use the date provided formatted similarly.
        # Ensure UTC or Local? The API likely expects UTC time for the moon phase.
        # Let's use the UTC date passed in.
        
        image_url = None
        try:
            # Format: YYYY-MM-DDTHH:00
            api_date_str = date.strftime("%Y-%m-%dT%H:00")
            api_url = f"https://svs.gsfc.nasa.gov/api/dialamoon/{api_date_str}"
            
            # Simple User-Agent to be polite
            headers = {'User-Agent': 'AstroBuddy/1.0'}
            resp = requests.get(api_url, headers=headers, timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                # Check "image" -> "url"
                if "image" in data and "url" in data["image"]:
                    image_url = data["image"]["url"]
            else:
                print(f"[ASTRO] Moon API Failed: {resp.status_code}")
                
        except Exception as e:
            print(f"[ASTRO] Error fetching Moon Image: {e}")

        return {
            "phase_name": phase_name,
            "illumination": round(illumination_pct, 1),
            "rise": t_rise.isoformat() if t_rise else None,
            "set": t_set.isoformat() if t_set else None,
            "age_days": round(phase_deg / 360 * 29.53, 1),
            "image_url": image_url
        }

    def get_visible_planets(self, lat: float, lon: float, date: datetime, darkness_window: dict) -> List[dict]:
        """
        Calculate visible planets. strictly within or overlapping night.
        Calculates Magnitude.
        """
        if date.tzinfo is None:
            date = date.replace(tzinfo=pytz.utc)
            
        t0 = self.ts.from_datetime(date)
        t1 = self.ts.from_datetime(date + timedelta(hours=24))
        observer = wgs84.latlon(lat, lon)
        
        # Parse darkness window/night window for visibility check
        # If darkness window is None, assume "Night" is roughly Sunset to Sunrise.
        # But for strictly visibility, we just check if it's up *at all* during dark hours?
        # User said: "adecuado a la ventana de oscuridad".
        # So we should filter: Rise or Set is inside window, OR is up during window.
        
        d_start_s = darkness_window.get("start")
        d_end_s = darkness_window.get("end")
        
        visible_planets = []
        
        for name, body in self.planets.items():
            astrometric = (self.earth + observer).at(t0).observe(body)
            app = astrometric.apparent()
            alt, az, distance = app.altaz()
            
            # Magnitude
            try:
                mag = planetary_magnitude(app)
            except:
                mag = 0.0 # Fallback
            
            # Rise/Set
            rise, set_time = self._find_rise_set(body, observer, t0, t1)
            
            # Visibility Check Logic
            # Is it visible during darkness?
            # Simple check: Is specific planet Altitude > 10 degrees at any point in darkness?
            # Or simplified: if it rises OR sets during darkness, or is up for the whole darkness?
            
            is_visible = False
            
            # Use darkness window if available, else generic night
            check_start = datetime.fromisoformat(d_start_s) if d_start_s else t0.utc_datetime()
            check_end = datetime.fromisoformat(d_end_s) if d_end_s else t1.utc_datetime()
            
            # 1. Rising inside window?
            if rise and check_start <= rise <= check_end: is_visible = True
            # 2. Setting inside window?
            if set_time and check_start <= set_time <= check_end: is_visible = True
            # 3. Up for whole window? (Rise < Start AND Set > End) - harder to check with just single event
            # Check mid-darkness altitude
            if d_start_s and d_end_s and not is_visible:
                 mid_point = check_start + (check_end - check_start)/2
                 t_mid = self.ts.from_datetime(mid_point)
                 alt_mid, _, _ = (self.earth + observer).at(t_mid).observe(body).apparent().altaz()
                 if alt_mid.degrees > 10: 
                     is_visible = True

            if is_visible:
                visible_planets.append({
                    "name": name,
                    "magnitude": round(float(mag), 1),
                    "distance_au": round(distance.au, 2),
                    "rise": rise.isoformat() if rise else None,
                    "set": set_time.isoformat() if set_time else None,
                    "is_visible": True
                })
            
        return visible_planets

    def calculate_object_events(self, lat: float, lon: float, date: datetime, ra_decimal_hours: float, dec_decimal_degrees: float) -> dict:
        """
        Calculate Rise, Transit, Set times.
        """
        if date.tzinfo is None:
            date = date.replace(tzinfo=pytz.utc)
            
        observer = wgs84.latlon(lat, lon)
        # Scan 24h from noon
        t_start = date.replace(hour=12, minute=0, second=0)
        t0 = self.ts.from_datetime(t_start)
        t1 = self.ts.from_datetime(t_start + timedelta(hours=24))
        
        body = Star(ra_hours=ra_decimal_hours, dec_degrees=dec_decimal_degrees)
        
        rise, set_time = self._find_rise_set(body, observer, t0, t1)
        
        # Transit
        f_transit = almanac.meridian_transits(self.eph, body, observer)
        times_tr, events_tr = find_discrete(t0, t1, f_transit)
        
        transit = None
        transit_alt = 0.0
        
        for t, event in zip(times_tr, events_tr):
            if event == 1: # Meridian transit
                transit = t.utc_datetime()
                astrometric = (self.earth + observer).at(t).observe(body)
                alt, _, _ = astrometric.apparent().altaz()
                transit_alt = alt.degrees
                break

        return {
            "rise": rise.isoformat() if rise else None,
            "set": set_time.isoformat() if set_time else None,
            "transit": transit.isoformat() if transit else None,
            "transit_altitude": round(transit_alt, 1)
        }

    def _find_rise_set(self, body, observer, t0, t1) -> Tuple[Optional[datetime], Optional[datetime]]:
        f = almanac.risings_and_settings(self.eph, body, observer)
        times, events = find_discrete(t0, t1, f)
        
        rise = None
        set_time = None
        
        for t, event in zip(times, events):
            if event == 1: # Rise
                rise = t.utc_datetime()
            elif event == 0: # Set
                set_time = t.utc_datetime()
                
        return rise, set_time

    def filter_visible_objects(self, observer_lat: float, observer_lon: float, 
                               date: datetime, objects: List[CelestialObject], 
                               min_altitude: float = 30.0) -> List[CelestialObject]:
        # Simple visible check logic retained
        if date.tzinfo is None:
             date = date.replace(tzinfo=pytz.utc)

        observer = self.earth + wgs84.latlon(observer_lat, observer_lon)
        t = self.ts.from_datetime(date)
        
        visible = []
        for obj in objects:
            body = Star(ra_hours=obj.ra / 15.0, dec_degrees=obj.dec)
            astrometric = observer.at(t).observe(body)
            alt, az, d = astrometric.apparent().altaz()
            if alt.degrees >= min_altitude:
                visible.append(obj)
        return visible
