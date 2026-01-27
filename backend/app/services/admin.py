import sqlite3
import json
import os
import sys
from typing import List, Dict, Optional
from datetime import datetime

class AdminService:
    def __init__(self, db_path: str = "data/objects.db"):
        self.db_path = db_path
        self.json_path = "data/catalogue-de-messier.json"

    def _parse_ra(self, ra_str: str) -> Optional[float]:
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

    def _parse_dec(self, dec_str: str) -> Optional[float]:
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

    def _fetch_coordinates_from_simbad(self, object_name: str) -> tuple[Optional[float], Optional[float]]:
        """
        Query Simbad for object coordinates if missing in local data.
        Returns (ra_decimal_degrees, dec_decimal_degrees) or (None, None).
        """
        try:
            from astroquery.simbad import Simbad
            Simbad.add_votable_fields('ra(d)', 'dec(d)')
            
            print(f"Fetching coordinates for {object_name} from Simbad...")
            result_table = Simbad.query_object(object_name)
            if result_table is not None and len(result_table) > 0:
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

    def seed_messier_catalog(self) -> Dict:
        """
        Seeds the database with Messier catalog objects.
        Returns a status report.
        """
        try:
            if not os.path.exists(self.json_path):
                return {
                    "success": False,
                    "error": "Messier catalog JSON file not found",
                    "path": self.json_path
                }

            # Read JSON
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing Messier objects
            cursor.execute("DELETE FROM objects WHERE catalog = 'Messier'")
            
            inserted_count = 0
            skipped_count = 0
            errors = []
            
            for item in data:
                m_id = item.get('messier')
                if not m_id:
                    continue
                    
                ra_raw = item.get('ra')
                dec_raw = item.get('dec')
                
                ra = self._parse_ra(ra_raw)
                dec = self._parse_dec(dec_raw)
                
                # If RA/Dec missing, try Simbad
                if ra is None or dec is None:
                    s_ra, s_dec = self._fetch_coordinates_from_simbad(m_id)
                    if s_ra is not None and s_dec is not None:
                        ra = s_ra
                        dec = s_dec
                    else:
                        errors.append(f"Skipped {m_id}: Unable to determine coordinates")
                        skipped_count += 1
                        continue
                
                # Other fields
                name = item.get('english_name_nom_en_anglais') or item.get('french_name_nom_francais') or m_id
                ngc = item.get('ngc')
                mag = item.get('mag')
                size = item.get('dimension')
                obj_type = item.get('objet')
                constellation = item.get('const')
                desc = f"Season: {item.get('saison')}. Distance: {item.get('distance')} ly. Discoverer: {item.get('decouvreur')} ({item.get('annee')})."

                try:
                    cursor.execute('''
                        INSERT INTO objects (id, name, ngc, ra, dec, mag, size, type, constellation, description, catalog)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (m_id, name, ngc, ra, dec, mag, size, obj_type, constellation, desc, 'Messier'))
                    inserted_count += 1
                except Exception as e:
                    errors.append(f"Error inserting {m_id}: {str(e)}")
                    skipped_count += 1

            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "inserted": inserted_count,
                "skipped": skipped_count,
                "total": len(data),
                "errors": errors[:10] if errors else []  # Limit error messages
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def export_database(self) -> List[Dict]:
        """
        Exports all objects in the database as JSON.
        Returns list of all objects.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM objects ORDER BY id")
        rows = cursor.fetchall()
        
        objects = []
        for row in rows:
            objects.append(dict(row))
        
        conn.close()
        return objects

    def import_database(self, objects: List[Dict], replace: bool = False) -> Dict:
        """
        Imports objects into the database.
        
        Args:
            objects: List of object dictionaries to import
            replace: If True, clears the database before importing
            
        Returns:
            Status report
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if replace:
                cursor.execute("DELETE FROM objects")
            
            inserted_count = 0
            skipped_count = 0
            errors = []
            
            for obj in objects:
                try:
                    # Ensure we have required fields
                    if not obj.get('id') or obj.get('ra') is None or obj.get('dec') is None:
                        errors.append(f"Skipped object: Missing required fields (id, ra, or dec)")
                        skipped_count += 1
                        continue
                    
                    cursor.execute('''
                        INSERT OR REPLACE INTO objects 
                        (id, name, ngc, ra, dec, mag, size, type, constellation, description, catalog, image_url, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        obj.get('id'),
                        obj.get('name'),
                        obj.get('ngc'),
                        obj.get('ra'),
                        obj.get('dec'),
                        obj.get('mag'),
                        obj.get('size'),
                        obj.get('type'),
                        obj.get('constellation'),
                        obj.get('description'),
                        obj.get('catalog'),
                        obj.get('image_url'),
                        obj.get('created_at', datetime.now().isoformat())
                    ))
                    inserted_count += 1
                except Exception as e:
                    errors.append(f"Error importing object {obj.get('id', 'unknown')}: {str(e)}")
                    skipped_count += 1
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "inserted": inserted_count,
                "skipped": skipped_count,
                "total": len(objects),
                "replaced_all": replace,
                "errors": errors[:10] if errors else []
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_database_stats(self) -> Dict:
        """
        Returns statistics about the database.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM objects")
        total_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT catalog, COUNT(*) FROM objects GROUP BY catalog")
        catalog_counts = dict(cursor.fetchall())
        
        cursor.execute("SELECT type, COUNT(*) FROM objects GROUP BY type")
        type_counts = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_objects": total_count,
            "by_catalog": catalog_counts,
            "by_type": type_counts
        }
