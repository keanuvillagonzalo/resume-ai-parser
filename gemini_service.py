import os
import PyPDF2
from google import genai

from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv("API_KEY")
DATABASE_URL=os.getenv("DATABASE_URL")



class GeminiService:


    def __init__(self, api_key: str):


        # Initialize the client with the provided key


        self.client = genai.Client(api_key=API_KEY)



    def extract_text(self, file_path):


        """Extracts all text content from a PDF file."""


        text = ""


        try:


            with open(file_path, "rb") as f:


                reader = PyPDF2.PdfReader(f)


                for page in reader.pages:


                    content = page.extract_text()


                    if content:


                        text += content + "\n"


            return text


        except Exception as e:


            print(f"Error reading PDF: {e}")


            raise e



    def parse_resume(self, text):


        """Sends resume text to Gemini 2.5 Flash-Lite for structured extraction."""


        


        # Defining the system behavior clearly


        system_instruction = (


            "You are a specialized HR data extractor. Your goal is to extract "


            "work experience into a strictly valid JSON list of objects."


        )



        prompt = f"""


        For each work experience entry in the following resume, extract:


        - job_title


        - employer_name


        - start_date


        - end_date


        - location


        - description (Include all bullet points or summary text)




        In the output, be sure to replace '\n' with ' '



        Resume Content:


        {text}


        """



        try:


            response = self.client.models.generate_content(


                model="gemini-2.5-flash-lite",


                contents=prompt,


                config={


                    "system_instruction": system_instruction,


                    "response_mime_type": "application/json"


                }


            )


            return response.text


        except Exception as e:


            print(f"Gemini API Error: {e}")


            raise e




    def match_experience_to_jd(self, stored_experiences, job_description):


        prompt = f"""


    You are an expert Resume Tailor. 


    


    INPUT DATA:


    1. JOB DESCRIPTION: {job_description}


    2. CANDIDATE EXPERIENCES: {stored_experiences}



    TASK:


    - Identify the top 3 most relevant experiences from the candidate's history.


    - For each of those 3 experiences, REWRITE the 'description' bullet points.


    - The new bullet points must:


        a) Incorporate keywords and technologies found in the Job Description (e.g., if the JD mentions 'Scalability', ensure the bullet points emphasize how the candidate scaled a project).


        b) Maintain the original metrics (e.g., if they achieved 98% accuracy, keep that number).


        c) Use strong action verbs.


    


    OUTPUT FORMAT (Markdown):


    # Optimized Resume Content


    


    ## [Job Title] at [Employer Name]


    * [Tailored Bullet Point 1]


    * [Tailored Bullet Point 2]


    


    ## [Next Job Title]...


    """


    


        response = self.client.models.generate_content(


        model="gemini-2.5-flash-lite",


        contents=prompt


    )


        return response.text  