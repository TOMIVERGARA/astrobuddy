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

# ===== CATALOG CRUD ENDPOINTS =====

class CelestialObjectCreate(BaseModel):
    id: str
    name: str
    ngc: Optional[str] = None
    ra: float
    dec: float
    mag: float
    size: Optional[str] = None
    type: str
    constellation: Optional[str] = None
    description: Optional[str] = None
    catalog: Optional[str] = None
    image_url: Optional[str] = None

class CelestialObjectUpdate(BaseModel):
    name: Optional[str] = None
    ngc: Optional[str] = None
    ra: Optional[float] = None
    dec: Optional[float] = None
    mag: Optional[float] = None
    size: Optional[str] = None
    type: Optional[str] = None
    constellation: Optional[str] = None
    description: Optional[str] = None
    catalog: Optional[str] = None
    image_url: Optional[str] = None

@app.get("/catalog/objects")
def list_objects(search: Optional[str] = None):
    """List all objects or search by query"""
    try:
        if search:
            objects = catalog_svc.search_objects(search)
        else:
            objects = catalog_svc.get_all_objects()
        return {"objects": [obj.dict() for obj in objects]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/catalog/objects/{object_id}")
def get_object(object_id: str):
    """Get a specific object by ID"""
    try:
        obj = catalog_svc.get_object_by_id(object_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
        return obj.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/catalog/objects")
def create_object(obj: CelestialObjectCreate):
    """Create a new celestial object"""
    try:
        # Check if object already exists
        existing = catalog_svc.get_object_by_id(obj.id)
        if existing:
            raise HTTPException(status_code=400, detail="Object with this ID already exists")
        
        new_obj = catalog_svc.create_object(obj.dict())
        return new_obj.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/catalog/objects/{object_id}")
def update_object(object_id: str, obj: CelestialObjectUpdate):
    """Update an existing object"""
    try:
        # Only include fields that are set
        update_data = {k: v for k, v in obj.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        updated_obj = catalog_svc.update_object(object_id, update_data)
        if not updated_obj:
            raise HTTPException(status_code=404, detail="Object not found")
        
        return updated_obj.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/catalog/objects/{object_id}")
def delete_object(object_id: str):
    """Delete an object"""
    try:
        success = catalog_svc.delete_object(object_id)
        if not success:
            raise HTTPException(status_code=404, detail="Object not found")
        
        return {"message": "Object deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/catalog/lookup/{object_id}")
def lookup_object(object_id: str):
    """Lookup object data from SIMBAD and VizieR using astroquery, with constellation calculation"""
    try:
        from astroquery.simbad import Simbad
        from astroquery.vizier import Vizier
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        
        print(f"[LOOKUP] Searching for object: {object_id}")
        
        # Configure Simbad to get comprehensive data
        # Note: SIMBAD returns RA/DEC in degrees by default (RA_d, DEC_d columns)
        custom_simbad = Simbad()
        custom_simbad.add_votable_fields('otype', 'flux(V)', 'flux(B)', 'dimensions')
        
        # Query SIMBAD
        print("[LOOKUP] Querying SIMBAD...")
        result = custom_simbad.query_object(object_id)
        
        if result is None or len(result) == 0:
            raise HTTPException(status_code=404, detail=f"Object '{object_id}' not found in SIMBAD")
        
        row = result[0]
        
        print(f"[LOOKUP] Available columns: {row.colnames}")
        
        # Extract coordinates - SIMBAD returns them as 'ra' and 'dec' (lowercase)
        ra = float(row['ra']) if 'ra' in row.colnames and row['ra'] is not None else None
        dec = float(row['dec']) if 'dec' in row.colnames and row['dec'] is not None else None
        
        print(f"[LOOKUP] Extracted RA={ra}, DEC={dec}")
        
        # Calculate constellation from RA/DEC using astropy
        constellation = None
        if ra is not None and dec is not None:
            try:
                coord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
                constellation = coord.get_constellation(short_name=True)
                print(f"[LOOKUP] Calculated constellation: {constellation}")
            except Exception as e:
                print(f"[LOOKUP] Could not calculate constellation: {e}")
        
        # Extract object type - convert SIMBAD codes to readable names
        obj_type = str(row['otype']) if 'otype' in row.colnames and row['otype'] else None
        if obj_type:
            # Common SIMBAD type mappings
            type_mappings = {
                'G': 'Galaxy',
                'GiG': 'Galaxy in Group',
                'GiC': 'Galaxy in Cluster',
                'PN': 'Planetary Nebula',
                'HII': 'HII Region',
                'EmO': 'Emission Object',
                'Neb': 'Nebula',
                'OpC': 'Open Cluster',
                'GlC': 'Globular Cluster',
                'ClG': 'Cluster of Galaxies',
                'SNR': 'Supernova Remnant',
                'RfN': 'Reflection Nebula',
                'DkN': 'Dark Nebula',
            }
            obj_type = type_mappings.get(obj_type, obj_type)
        
        # Get magnitude from SIMBAD - columns are 'V' and 'B' (lowercase)
        mag = None
        if 'V' in row.colnames and row['V'] is not None:
            mag = float(row['V'])
        elif 'B' in row.colnames and row['B'] is not None:
            mag = float(row['B'])
        
        # Get size from SIMBAD - column is 'galdim_majaxis' (lowercase)
        size = None
        if 'galdim_majaxis' in row.colnames and row['galdim_majaxis'] is not None:
            size = str(row['galdim_majaxis'])
        
        # Try to get additional data from VizieR if magnitude or size is missing
        if mag is None or size is None:
            try:
                print("[LOOKUP] Trying VizieR for additional data...")
                coord = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')
                
                # Query Messier catalog in VizieR
                v = Vizier(columns=['*'], row_limit=1)
                v.ROW_LIMIT = 1
                
                # Try Messier catalog (VII/118)
                messier_result = v.query_region(coord, radius=1*u.arcmin, catalog='VII/118')
                if messier_result and len(messier_result) > 0:
                    table = messier_result[0]
                    if len(table) > 0:
                        if mag is None and 'Vmag' in table.colnames:
                            mag = float(table['Vmag'][0]) if table['Vmag'][0] else None
                        if size is None and 'Diam' in table.colnames:
                            size = str(table['Diam'][0]) if table['Diam'][0] else None
                        print(f"[LOOKUP] Found data in Messier catalog")
                
                # If still missing, try NGC/IC catalog (VII/1B)
                if mag is None or size is None:
                    ngc_result = v.query_region(coord, radius=1*u.arcmin, catalog='VII/1B')
                    if ngc_result and len(ngc_result) > 0:
                        table = ngc_result[0]
                        if len(table) > 0:
                            if mag is None and 'Vmag' in table.colnames:
                                mag = float(table['Vmag'][0]) if table['Vmag'][0] else None
                            if size is None and 'MajDiam' in table.colnames:
                                size = str(table['MajDiam'][0]) if table['MajDiam'][0] else None
                            print(f"[LOOKUP] Found data in NGC/IC catalog")
            except Exception as e:
                print(f"[LOOKUP] VizieR query failed: {e}")
        
        # Build response
        data = {
            "id": object_id.upper(),
            "name": str(row['main_id']) if 'main_id' in row.colnames else object_id,
            "ra": ra,
            "dec": dec,
            "type": obj_type,
            "constellation": constellation,
            "mag": mag,
            "size": size,
        }
        
        print(f"[LOOKUP] Returning data: {data}")
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error querying astronomical databases: {str(e)}")

@app.get("/catalog/images/{object_id}")
def get_object_images(object_id: str):
    """Search NASA Image Library for object images"""
    try:
        import requests
        
        print(f"[IMAGES] Searching NASA API for: {object_id}")
        
        # Query NASA Images API
        url = f"https://images-api.nasa.gov/search?q={object_id}&media_type=image"
        response = requests.get(url, timeout=10)
        
        if not response.ok:
            raise HTTPException(status_code=response.status_code, detail="NASA API request failed")
        
        data = response.json()
        
        # Extract image URLs
        images = []
        items = data.get('collection', {}).get('items', [])
        
        for item in items[:10]:  # Limit to first 10 results
            links = item.get('links', [])
            item_data = item.get('data', [{}])[0]
            
            # Find the best quality image (prefer ~medium or ~large)
            image_url = None
            for link in links:
                if link.get('render') == 'image':
                    href = link.get('href', '')
                    # Prefer medium or large, but take any image
                    if '~medium' in href or '~large' in href:
                        image_url = href
                        break
                    elif not image_url:
                        image_url = href
            
            if image_url:
                images.append({
                    "url": image_url,
                    "title": item_data.get('title', ''),
                    "description": item_data.get('description', '')[:200] + '...' if item_data.get('description') else ''
                })
        
        print(f"[IMAGES] Found {len(images)} images")
        return {"images": images}
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error searching NASA images: {str(e)}")
