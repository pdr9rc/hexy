#!/usr/bin/env python3
"""
The Dying Lands - S3 Database Manager
S3-based database manager for AWS Lambda deployment.
"""

import os
import json
import sqlite3
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError
from backend.database_manager import DatabaseManager

class S3DatabaseManager(DatabaseManager):
    """S3-based database manager that caches SQLite databases locally."""
    
    def __init__(self, s3_bucket: str, region: str = 'us-east-1'):
        """
        Initialize S3 database manager.
        
        Args:
            s3_bucket: S3 bucket name for database storage
            region: AWS region
        """
        super().__init__()
        self.s3_bucket = s3_bucket
        self.s3_client = boto3.client('s3', region_name=region)
        self.local_cache_dir = Path('/tmp/hexy_databases')
        self.local_cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache = {}
        
    def _get_s3_key(self, db_name: str) -> str:
        """Get S3 key for database file."""
        return f"databases/{db_name}.db"
    
    def _download_database(self, db_name: str) -> Path:
        """Download database from S3 to local cache."""
        s3_key = self._get_s3_key(db_name)
        local_path = self.local_cache_dir / f"{db_name}.db"
        
        try:
            # Check if file exists in S3
            self.s3_client.head_object(Bucket=self.s3_bucket, Key=s3_key)
            
            # Download file
            self.s3_client.download_file(self.s3_bucket, s3_key, str(local_path))
            print(f"✅ Downloaded {db_name}.db from S3")
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                print(f"⚠️  Database {db_name}.db not found in S3, creating new one")
                # Create empty database
                conn = sqlite3.connect(str(local_path))
                conn.close()
            else:
                raise e
                
        return local_path
    
    def _upload_database(self, db_name: str, local_path: Path) -> None:
        """Upload database to S3."""
        s3_key = self._get_s3_key(db_name)
        
        try:
            self.s3_client.upload_file(str(local_path), self.s3_bucket, s3_key)
            print(f"✅ Uploaded {db_name}.db to S3")
        except ClientError as e:
            print(f"❌ Failed to upload {db_name}.db to S3: {e}")
            raise e
    
    def get_database_path(self, db_name: str) -> Path:
        """Get local database path, downloading from S3 if needed."""
        if db_name not in self._cache:
            local_path = self._download_database(db_name)
            self._cache[db_name] = local_path
            
        return self._cache[db_name]
    
    def execute_query(self, db_name: str, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute query on database."""
        local_path = self.get_database_path(db_name)
        
        conn = sqlite3.connect(str(local_path))
        conn.row_factory = sqlite3.Row
        
        try:
            cursor = conn.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            return results
        finally:
            conn.close()
    
    def execute_insert(self, db_name: str, query: str, params: tuple = ()) -> int:
        """Execute insert query and return last row ID."""
        local_path = self.get_database_path(db_name)
        
        conn = sqlite3.connect(str(local_path))
        
        try:
            cursor = conn.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def sync_to_s3(self, db_name: str) -> None:
        """Sync local database changes to S3."""
        if db_name in self._cache:
            local_path = self._cache[db_name]
            self._upload_database(db_name, local_path)
    
    def sync_all_to_s3(self) -> None:
        """Sync all cached databases to S3."""
        for db_name in self._cache:
            self.sync_to_s3(db_name)
    
    def get_random_item(self, db_name: str, category: str) -> Optional[Dict[str, Any]]:
        """Get random item from database category."""
        local_path = self.get_database_path(db_name)
        
        conn = sqlite3.connect(str(local_path))
        conn.row_factory = sqlite3.Row
        
        try:
            cursor = conn.execute(
                "SELECT * FROM items WHERE category = ? ORDER BY RANDOM() LIMIT 1",
                (category,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_all_categories(self, db_name: str) -> List[str]:
        """Get all categories from database."""
        local_path = self.get_database_path(db_name)
        
        conn = sqlite3.connect(str(local_path))
        
        try:
            cursor = conn.execute("SELECT DISTINCT category FROM items")
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def clear_cache(self) -> None:
        """Clear local database cache."""
        self._cache.clear()
        if self.local_cache_dir.exists():
            import shutil
            shutil.rmtree(self.local_cache_dir)
            self.local_cache_dir.mkdir(parents=True, exist_ok=True)
        print("✅ Database cache cleared")

# Global instance for Lambda
s3_db_manager = None

def get_s3_db_manager() -> S3DatabaseManager:
    """Get global S3 database manager instance."""
    global s3_db_manager
    
    if s3_db_manager is None:
        bucket = os.environ.get('AWS_S3_BUCKET', 'hexy-dying-lands-data')
        region = os.environ.get('AWS_S3_REGION', 'us-east-1')
        s3_db_manager = S3DatabaseManager(bucket, region)
    
    return s3_db_manager
