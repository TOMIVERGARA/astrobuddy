import sqlite3
import json
from typing import List, Optional
from pydantic import BaseModel

class CelestialObject(BaseModel):
    id: str
    name: str # Common name like "Andromeda Galaxy"
    ngc: Optional[str] = None
    ra: float # Right Ascension in decimal degrees
    dec: float # Declination in decimal degrees
    mag: float # Visual Magnitude
    size: Optional[str] = None # Apparent dimension
    type: str # Galaxy, Nebula, Cluster, etc.
    constellation: Optional[str] = None
    description: Optional[str] = None
    catalog: Optional[str] = None # Name of the catalog (e.g., "Messier", "NGC", "IC")
    image_url: Optional[str] = None # URL to object image
    created_at: Optional[str] = None # Creation timestamp

class CatalogService:
    def __init__(self, db_path: str = "data/objects.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS objects (
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
        conn.commit()
        conn.close()

    def get_all_objects(self) -> List[CelestialObject]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM objects")
        rows = cursor.fetchall()
        conn.close()
        return [CelestialObject(**dict(row)) for row in rows]

    def get_objects_by_ids(self, ids: List[str]) -> List[CelestialObject]:
        if not ids:
            return []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        placeholders = ','.join('?' for _ in ids)
        cursor.execute(f"SELECT * FROM objects WHERE id IN ({placeholders})", ids)
        rows = cursor.fetchall()
        conn.close()
        return [CelestialObject(**dict(row)) for row in rows]
    
    def insert_objects(self, objects: List[dict]):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        for obj in objects:
            cursor.execute('''
                INSERT OR REPLACE INTO objects (id, name, ngc, ra, dec, mag, size, type, constellation, description, catalog, image_url, created_at)
                VALUES (:id, :name, :ngc, :ra, :dec, :mag, :size, :type, :constellation, :description, :catalog, :image_url, :created_at)
            ''', obj)
        conn.commit()
        conn.close()
    
    def get_object_by_id(self, object_id: str) -> Optional[CelestialObject]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM objects WHERE id = ?", (object_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return CelestialObject(**dict(row))
        return None
    
    def create_object(self, obj_data: dict) -> CelestialObject:
        from datetime import datetime
        if 'created_at' not in obj_data:
            obj_data['created_at'] = datetime.utcnow().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO objects (id, name, ngc, ra, dec, mag, size, type, constellation, description, catalog, image_url, created_at)
            VALUES (:id, :name, :ngc, :ra, :dec, :mag, :size, :type, :constellation, :description, :catalog, :image_url, :created_at)
        ''', obj_data)
        conn.commit()
        conn.close()
        return CelestialObject(**obj_data)
    
    def update_object(self, object_id: str, obj_data: dict) -> Optional[CelestialObject]:
        # Check if exists first
        existing = self.get_object_by_id(object_id)
        if not existing:
            return None
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Build update query dynamically based on provided fields
        fields = []
        values = []
        for key, value in obj_data.items():
            if key != 'id':  # Don't update ID
                fields.append(f"{key} = ?")
                values.append(value)
        
        values.append(object_id)
        query = f"UPDATE objects SET {', '.join(fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return self.get_object_by_id(object_id)
    
    def delete_object(self, object_id: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM objects WHERE id = ?", (object_id,))
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        return rows_affected > 0
    
    def search_objects(self, query: str) -> List[CelestialObject]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Search in id, name, ngc, type, constellation, catalog
        search_pattern = f"%{query}%"
        cursor.execute('''
            SELECT * FROM objects 
            WHERE id LIKE ? OR name LIKE ? OR ngc LIKE ? 
            OR type LIKE ? OR constellation LIKE ? OR catalog LIKE ?
            ORDER BY name
        ''', (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
        
        rows = cursor.fetchall()
        conn.close()
        return [CelestialObject(**dict(row)) for row in rows]
