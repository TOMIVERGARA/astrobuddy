import sys
import os
import json

# Add backend to path so we can import app.services
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.services.catalog import CatalogService

def load_objects():
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'enriched_catalogue.json')
    if not os.path.exists(data_path):
        print(f"Warning: {data_path} not found. Please run enrich_catalogue.py first.")
        return []
        
    with open(data_path, 'r') as f:
        data = json.load(f)

    valid_objects = []
    
    print(f"Loaded {len(data)} items from JSON.")

    for item in data:
        # Check if basic requirements are met
        if not item.get('found', False):
             continue
        
        # Ensure critical fields exist
        if 'ra' not in item or 'dec' not in item:
            print(f"Skipping {item.get('id')} - Missing Coordinates")
            continue

        # Prepare object for DB
        obj = {
            "id": item.get('id'),
            "name": item.get('name', item.get('id')),
            "ngc": item.get('ngc'),
            "ra": item.get('ra'),
            "dec": item.get('dec'),
            "mag": item.get('mag', 99.9), # Default to high mag if missing, so it's faint
            "size": item.get('size', 'Unknown'),
            "type": item.get('type', 'Unknown'),
            "constellation": item.get('constellation', 'Unknown'),
            "description": f"Object from {item.get('catalog')} Catalog"
        }
        valid_objects.append(obj)
        
    return valid_objects

if __name__ == "__main__":
    objects = load_objects()
    if objects:
        print(f"Seeding {len(objects)} objects into DB...")
        svc = CatalogService(db_path="backend/data/objects.db")
        svc.insert_objects(objects)
        print("Done.")
    else:
        print("No valid objects to seed.")

