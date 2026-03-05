import os
import sys
import unittest
from sqlalchemy import text

# Add parent directory to sys.path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import engine, init_db, DB_PATH, DiscoveredJob, SessionLocal
from utils.hash import generate_job_hash

class TestDatabaseSchema(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize the database for testing
        init_db()

    def test_wal_mode_enabled(self):
        """Test if WAL mode and synchronous=NORMAL are enabled."""
        with engine.connect() as conn:
            result_journal = conn.execute(text("PRAGMA journal_mode")).fetchone()
            self.assertEqual(result_journal[0].lower(), 'wal')
            
            result_sync = conn.execute(text("PRAGMA synchronous")).fetchone()
            # 1 corresponds to NORMAL in SQLite
            self.assertEqual(result_sync[0], 1)

    def test_job_hashing_logic(self):
        """Test the deduplication hashing logic"""
        company = " OpenAI "
        jd = "We are   looking for a software engineer. " + " ".join([f"word{i}" for i in range(100)])
        
        # Test basic hashing
        hash1 = generate_job_hash(company, jd)
        hash2 = generate_job_hash("openai", jd) # Test company normalization
        
        self.assertEqual(hash1, hash2)
        
        # Test 50-word cutoff
        jd_short = "We are   looking for a software engineer. " + " ".join([f"word{i}" for i in range(41)])
        # jd and jd_short share the first 46 words, but differ afterwards.
        # Wait, the hash uses the FIRST 50 words. So if jd length > 50, and jd_short length == 46, they will be different.
        jd_same_first_50 = "We are looking for a software engineer. " + " ".join([f"word{i}" for i in range(43)]) + " extra extra"
        hash3 = generate_job_hash("openai", jd_same_first_50)
        self.assertEqual(hash1, hash3)
        
    def test_database_insert_and_deduplication(self):
        """Test inserting a job and verifying the unique constraint."""
        session = SessionLocal()
        company = "TestCorp"
        title = "Software Engineer"
        jd = "This is a test job description."
        job_hash = generate_job_hash(company, jd)
        
        new_job = DiscoveredJob(
            company_name=company,
            job_title=title,
            job_description=jd,
            dedup_hash=job_hash
        )
        
        # Insert should succeed
        session.add(new_job)
        session.commit()
        
        # Verify it was inserted
        inserted_job = session.query(DiscoveredJob).filter_by(dedup_hash=job_hash).first()
        self.assertIsNotNone(inserted_job)
        self.assertEqual(inserted_job.company_name, company)
        
        # Attempt to insert a duplicate (same hash)
        duplicate_job = DiscoveredJob(
            company_name=company,
            job_title="Different Title, Same JD",
            job_description=jd,
            dedup_hash=job_hash
        )
        session.add(duplicate_job)
        
        # This should raise an IntegrityError
        from sqlalchemy.exc import IntegrityError
        with self.assertRaises(IntegrityError):
            session.commit()
            
        session.rollback()
        
        # Cleanup
        session.delete(inserted_job)
        session.commit()
        session.close()

if __name__ == '__main__':
    unittest.main()
