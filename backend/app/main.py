from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from fastapi.responses import FileResponse
import os
import uuid
import json

# Services
from app.services.astronomy import AstronomyService
from app.services.catalog import CatalogService
from app.services.weather import WeatherService
from app.services.ai import AIService
from app.services.pdf import generate_pdf
from app.services.charts import ChartsService

app = FastAPI(title="AstroBuddy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class PlanRequest(BaseModel):
    lat: float
    lon: float
    date: datetime
    telescope: str # Description like "8 inch Dobsonian"

# Global Service Instances
astronomy_svc = AstronomyService()
catalog_svc = CatalogService()
weather_svc = WeatherService()
ai_svc = AIService()
charts_svc = ChartsService()

@app.post("/generate-plan")
async def create_plan(req: PlanRequest):
    try:
        print("\n=== STARTING NEW PLAN GENERATION ===")
        print(f"Request: Lat={req.lat}, Lon={req.lon}, Date={req.date}, Scope={req.telescope}")

        # 1. Astronomy Calc (Darkness Window, Moon, Timezone)
        print("1. [ASTRO] Calculating night info...")
        night_info = astronomy_svc.calculate_night_info(req.lat, req.lon, req.date)
        
        # Extract critical windows
        darkness = night_info.get("darkness_window", {})
        start_str = darkness.get("start")
        end_str = darkness.get("end")
        
        # Timezone for logging/logic
        tz_str = night_info.get("timezone", "UTC")
        print(f"   [ASTRO] Timezone detected: {tz_str}")
        
        if start_str and end_str:
            obs_start = datetime.fromisoformat(start_str)
            obs_end = datetime.fromisoformat(end_str)
            print(f"   [ASTRO] Darkness Window: {start_str} to {end_str}")
        else:
            print("   [ASTRO] No astronomical darkness found. Usage generic night window.")
            # Fallback: 10pm to 4am local time? Or just use UTC offsets?
            # Simplest: Use req.date 22:00 to next day 04:00 (Naive -> UTC)
            obs_start = req.date.replace(hour=22, minute=0, second=0)
            obs_end = req.date.replace(hour=4, minute=0, second=0)

        # 2. Weather (Precise Window)
        print("2. [WEATHER] Fetching precise hourly forecast...")
        weather_info = weather_svc.get_weather_forecast(req.lat, req.lon, obs_start, obs_end)
        
        # 3. Planets (Filtered by Darkness Window)
        print("3. [ASTRO] Calculating visible planets...")
        planets = astronomy_svc.get_visible_planets(req.lat, req.lon, req.date, darkness)
        print(f"   [ASTRO] Calculated {len(planets)} visible planets.")

        # 4. Get Objects & Filter
        print("4. [CATALOG] Fetching and filtering objects...")
        all_objects = catalog_svc.get_all_objects()
        visible_objects = astronomy_svc.filter_visible_objects(req.lat, req.lon, req.date, all_objects)
        print(f"   [CATALOG] {len(visible_objects)} objects visible.")
        
        # 5. Enrich Objects with Schedule
        print("5. [ASTRO] Calculating schedules for visible objects...")
        enriched_objects = []
        for obj in visible_objects:
            obj_dict = obj.dict()
            # Calculate events
            events = astronomy_svc.calculate_object_events(req.lat, req.lon, req.date, obj.ra / 15.0, obj.dec)
            obj_dict.update(events)
            enriched_objects.append(obj_dict)

        # 6. AI Curation
        print("6. [AI] Generative curation starting...")
        ai_plan = ai_svc.generate_observation_plan(
            enriched_objects, 
            weather_info['summary'], 
            {"lat": req.lat, "lon": req.lon}, 
            {"type": req.telescope}
        )
        print("   [AI] Plan generated.")
        
        # Merge logic
        final_objects = []
        tech_map = {obj['id']: obj for obj in enriched_objects}
        
        for ai_obj in ai_plan.get('objects', []):
            o_id = ai_obj.get('id')
            if o_id in tech_map:
                merged = tech_map[o_id].copy()
                merged.update(ai_obj) 
                final_objects.append(merged)
            else:
                final_objects.append(ai_obj)
        ai_plan['objects'] = final_objects
        
        # 7. PDF Generation
        print("7. [PDF] Rendering document...")
        data = {
            "location": {"lat": req.lat, "lon": req.lon},
            "date": req.date.strftime("%Y-%m-%d"),
            "timezone": tz_str,
            "astro": night_info, 
            "planets": planets,
            "weather": weather_info, 
            "ai": ai_plan,
            "charts": charts_svc,
            "telescope": req.telescope
        }
        
        filename = f"plan_{uuid.uuid4()}.pdf"
        filepath = os.path.join("backend/data", filename)
        generate_pdf(data, filepath)
        print(f"   [PDF] Saved to {filepath}")
        
        print("=== GENERATION COMPLETE ===\n")
        return FileResponse(filepath, media_type='application/pdf', filename="observation_plan.pdf")

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health():
    return {"status": "ok"}
