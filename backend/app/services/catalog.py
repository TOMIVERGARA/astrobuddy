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
                description TEXT
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
                INSERT OR REPLACE INTO objects (id, name, ngc, ra, dec, mag, size, type, constellation, description)
                VALUES (:id, :name, :ngc, :ra, :dec, :mag, :size, :type, :constellation, :description)
            ''', obj)
        conn.commit()
        conn.close()
