"""Database module for CorroSim"""

import sqlite3
import uuid
import datetime
import pandas as pd
from io import StringIO


class Database:
    """SQLite database for storing corrosion analysis samples"""
    
    def __init__(self, db_path='corrosion.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS samples (
                id TEXT PRIMARY KEY,
                name TEXT,
                test_type TEXT,
                date TEXT,
                data TEXT,
                ecorr REAL,
                icorr REAL,
                cr REAL,
                ba REAL,
                bc REAL
            )
        ''')
        self.conn.commit()
    
    def save(self, name, test_type, data):
        """Save a new sample to the database"""
        sid = str(uuid.uuid4())[:8]
        data_csv = data.to_csv(index=False)
        date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        
        self.cursor.execute(
            "INSERT INTO samples VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (sid, name, test_type, date, data_csv, None, None, None, None, None)
        )
        self.conn.commit()
        return sid
    
    def update(self, sid, ecorr, icorr, cr, ba, bc):
        """Update analysis results for a sample"""
        self.cursor.execute(
            "UPDATE samples SET ecorr=?, icorr=?, cr=?, ba=?, bc=? WHERE id=?",
            (ecorr, icorr, cr, ba, bc, sid)
        )
        self.conn.commit()
    
    def get_all(self):
        """Get all samples ordered by date"""
        self.cursor.execute("SELECT * FROM samples ORDER BY date DESC")
        return self.cursor.fetchall()
    
    def get_latest(self):
        """Get the most recent sample"""
        self.cursor.execute("SELECT * FROM samples ORDER BY date DESC LIMIT 1")
        return self.cursor.fetchone()
    
    def get_by_id(self, sid):
        """Get a specific sample by ID"""
        self.cursor.execute("SELECT * FROM samples WHERE id=?", (sid,))
        return self.cursor.fetchone()
    
    def delete(self, sid):
        """Delete a sample by ID"""
        self.cursor.execute("DELETE FROM samples WHERE id=?", (sid,))
        self.conn.commit()
    
    def get_count(self):
        """Get total number of samples"""
        self.cursor.execute("SELECT COUNT(*) FROM samples")
        return self.cursor.fetchone()[0]
    
    def close(self):
        """Close database connection"""
        self.conn.close()
