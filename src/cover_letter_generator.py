from pydantic import BaseModel, Field
import instructor
from openai import OpenAI

# Initialize the OpenAI client pointing to the local Ollama instance
client = instructor.from_openai(
    OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",  # Ollama doesn't require a real API key
    ),
    mode=instructor.Mode.JSON,
)

class CoverLetter(BaseModel):
    """
    Structured output defining the generated cover letter.
    Using Pydantic here ensures the LLM doesn't wrap the cover letter in conversational text
    like "Here is your cover letter:". 
    """
    content: str = Field(
        ..., 
        description="The exact text of the cover letter. Must be under 120 words. Professional and concise."
    )

def generate_cover_letter(resume: str, job_description: str, model_name: str = "llama3.1") -> str:
    """
    Generates a highly-targeted, short cover letter strictly based on the provided resume and job description.
    """
    prompt = f"""
    You are an AI acting as the candidate. Write a concise, professional cover letter for the following job description, strictly using facts from the provided resume.
    
    RULES:
    1. The cover letter MUST be under 120 words.
    2. DO NOT make up any skills, experiences, or facts not present in the resume.
    3. Be direct and confident. Do not use overly formal fluff.
    4. Focus specifically on how the resume skills match the job description requirements.
    
    CANDIDATE RESUME:
    ---
    {resume}
    ---
    
    JOB DESCRIPTION:
    ---
    {job_description}
    ---
    """

    try:
        response = client.chat.completions.create(
            model=model_name,
            response_model=CoverLetter,
            messages=[
                {"role": "system", "content": "You are a precise, professional cover letter generator. Output pure JSON."},
                {"role": "user", "content": prompt},
            ],
            # Use slightly higher temperature (0.3) than the evaluation script (0.1) 
            # to allow for natural sounding language generation.
            temperature=0.3,  
        )
        return response.content
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return f"Error: Failed to generate cover letter. {str(e)}"

if __name__ == "__main__":
    # Dummy data for testing
    dummy_resume = "Full-stack Python engineer with 2 years of experience. Built a self-healing web scraper using Playwright and local LLMs (Ollama) to automate 500+ job applications. Proficient in Pydantic, SQLite, and Streamlit."
    dummy_job = "Seeking an Automation Engineer. The ideal candidate will have extensive experience with Python, Playwright, and building robust, resilient scraping pipelines that can handle dynamic DOMs. Familiarity with AI tools is a plus."
    
    print("Generating cover letter using Ollama (llama3.1)...\n")
    cover_letter_text = generate_cover_letter(dummy_resume, dummy_job)
    
    print("--- GENERATED COVER LETTER ---")
    print(cover_letter_text)
    print("------------------------------")
    
    # Simple word count check
    word_count = len(cover_letter_text.split())
    print(f"\nWord Count: {word_count} words")
