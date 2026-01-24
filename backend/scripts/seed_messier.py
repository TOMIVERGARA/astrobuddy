
import sqlite3
import json
import os
import sys
from typing import List, Dict, Optional, Tuple

# Add backend directory to path to allow imports from app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from astroquery.simbad import Simbad
    from astropy.table import Table
    Simbad.add_votable_fields('ra(d)', 'dec(d)')
except ImportError:
    print("Error: astroquery not installed. Please run: pip install astroquery")
    sys.exit(1)

DB_PATH = os.path.join(os.path.dirname(__file__), '../data/objects.db')
JSON_PATH = os.path.join(os.path.dirname(__file__), '../data/catalogue-de-messier.json')

def parse_ra(ra_str: str) -> Optional[float]:
    """
    Convert RA string "HH:MM:SS.ss" to decimal degrees.
    Returns None if format is invalid or empty.
    """
    if not ra_str:
        return None
    try:
        parts = ra_str.split(':')
        if len(parts) != 3:
            return None
        h, m, s = map(float, parts)
        # 15 degrees per hour
        return (h + m/60 + s/3600) * 15
    except ValueError:
        return None

def parse_dec(dec_str: str) -> Optional[float]:
    """
    Convert Dec string "+/-DD:MM:SS.s" to decimal degrees.
    Returns None if format is invalid or empty.
    """
    if not dec_str:
        return None
    try:
        # Handle sign
        sign = 1
        if dec_str.startswith('-'):
            sign = -1
            dec_str = dec_str[1:]
        elif dec_str.startswith('+'):
            dec_str = dec_str[1:]
            
        parts = dec_str.split(':')
        if len(parts) != 3:
            return None
        d, m, s = map(float, parts)
        return sign * (d + m/60 + s/3600)
    except ValueError:
        return None

def fetch_coordinates_from_simbad(object_name: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Query Simbad for object coordinates if missing in local data.
    Returns (ra_decimal_degrees, dec_decimal_degrees) or (None, None).
    """
    print(f"Fetching coordinates for {object_name} from Simbad...")
    try:
        result_table = Simbad.query_object(object_name)
        if result_table is not None and len(result_table) > 0:
            # Check for column names (deprecation warning: ra(d) -> ra, dec(d) -> dec)
            # Simbad might return 'ra'/'dec' or 'RA_d'/'DEC_d' depending on version
            cols = result_table.colnames
            
            ra_col = 'ra' if 'ra' in cols else 'RA_d'
            dec_col = 'dec' if 'dec' in cols else 'DEC_d'
            
            if ra_col in cols and dec_col in cols:
                ra_d = result_table[ra_col][0]
                dec_d = result_table[dec_col][0]
                return float(ra_d), float(dec_d)
            else:
                print(f"Columns {ra_col}/{dec_col} not found. Available: {cols}")
    except Exception as e:
        print(f"Failed to fetch {object_name}: {e}")
    return None, None

def seed():
    print(f"Database path: {DB_PATH}")
    print(f"JSON path: {JSON_PATH}")
    
    if not os.path.exists(JSON_PATH):
        print("JSON file not found!")
        return

    # 1. Reset Database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("Dropping existing objects table...")
    cursor.execute("DROP TABLE IF EXISTS objects")
    
    print("Creating new objects table...")
    # Schema matching CatalogService but matching existing schema we saw in CatalogService?
    # CatalogService uses: id, name, ngc, ra, dec, mag, size, type, constellation, description
    cursor.execute('''
        CREATE TABLE objects (
            id TEXT PRIMARY KEY,
            name TEXT,
            ngc TEXT,
            ra REAL,
            dec REAL,
            mag REAL,
            size TEXT,
            type TEXT,
            constellation TEXT,
            description TEXT,
            catalog TEXT,
            image_url TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 2. Read JSON
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    print(f"Found {len(data)} items in JSON.")
    
    inserted_count = 0
    skipped_count = 0
    
    for item in data:
        # Map fields
        # JSON: messier (M1), ngc (NGC 1952), objet (Supernova remnant), mag (8.4), ra (05:34:31.97), dec (+22:00:52.1)
        # DB: id, name, ngc, ra, dec, mag, size, type, constellation, description
        
        m_id = item.get('messier')
        if not m_id:
            continue
            
        ra_raw = item.get('ra')
        dec_raw = item.get('dec')
        
        ra = parse_ra(ra_raw)
        dec = parse_dec(dec_raw)
        
        # If RA/Dec missing, try Simbad
        if ra is None or dec is None:
            print(f"Missing coordinates for {m_id}. Attempting Simbad fallback...")
            # Ideally use 'messier' ID or 'ngc' ID if messier fails
            query_id = m_id
            s_ra, s_dec = fetch_coordinates_from_simbad(query_id)
            if s_ra is not None and s_dec is not None:
                ra = s_ra
                dec = s_dec
                print(f"Recovered {m_id}: RA={ra:.4f}, Dec={dec:.4f}")
            else:
                print(f"Skipping {m_id}: Unable to determine coordinates.")
                skipped_count += 1
                continue
        
        # Other fields
        name = item.get('english_name_nom_en_anglais') or item.get('french_name_nom_francais') or m_id
        ngc = item.get('ngc')
        mag = item.get('mag')
        size = item.get('dimension')
        obj_type = item.get('objet')
        constellation = item.get('const') # JSON uses 'const' (e.g. 'Tau'), DB expects 'constellation'
        desc = f"Season: {item.get('saison')}. Distance: {item.get('distance')} ly. Discoverer: {item.get('decouvreur')} ({item.get('annee')})."

        try:
            cursor.execute('''
                INSERT INTO objects (id, name, ngc, ra, dec, mag, size, type, constellation, description, catalog)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (m_id, name, ngc, ra, dec, mag, size, obj_type, constellation, desc, 'Messier'))
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting {m_id}: {e}")
            skipped_count += 1

    conn.commit()
    conn.close()
    
    print(f"Seeding complete.")
    print(f"Inserted: {inserted_count}")
    print(f"Skipped: {skipped_count}")

if __name__ == '__main__':
    seed()
