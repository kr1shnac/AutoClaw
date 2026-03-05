import hashlib
import re

def generate_job_hash(company_name: str, job_description: str) -> str:
    """
    Generates a unique SHA-256 hash for a job based on the company name 
    and the first 50 words of the job description to prevent duplicate applications.
    """
    # Normalize company name
    norm_company = company_name.lower().strip()
    
    # Normalize job description: lowercase, replace multiple whitespaces with single space
    norm_jd = re.sub(r'\s+', ' ', job_description.lower().strip())
    
    # Extract first 50 words
    words = norm_jd.split()
    first_50_words = ' '.join(words[:50])
    
    # Concatenate company name and the 50-word snippet
    combined_string = f"{norm_company}:{first_50_words}"
    
    # Generate SHA-256 hash
    return hashlib.sha256(combined_string.encode('utf-8')).hexdigest()
