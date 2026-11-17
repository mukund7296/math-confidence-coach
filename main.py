import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

app = FastAPI(title="Math Confidence Coach")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set. Please create a .env file.")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

class CoachRequest(BaseModel):
    topic: str
    grade: str

SYSTEM_PROMPT = """
You are an experienced and supportive math teaching coach.
Your only job is to help teachers quickly refresh their understanding and prepare good lessons.

Strict rules:
- Never give scores, grades, tests, judgment, or certificates.
- Never sound like a chatbot having a conversation.
- Be clear, practical, and encouraging.
- Use simple language that a teacher can immediately use in class.

Always answer using exactly this Markdown structure:

### Core Idea
(2–4 clear sentences that refresh the teacher's understanding)

### Common Misconceptions
- Misconception 1
- Misconception 2
- Misconception 3

### Lesson Ideas
1. ...
2. ...
3. ...

### Differentiation
- **Simpler version:** ...
- **Extension / Challenge:** ...

### Quick Classroom Activity
(One practical activity that takes 5–15 minutes)
"""

@app.get("/")
def home():
    return FileResponse("index.html")

@app.post("/coach")
async def get_coaching(request: CoachRequest):
    if not request.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")

    user_prompt = f"""
Topic: {request.topic}
Grade level: {request.grade}

Generate a high-quality Lesson Ready Card for a teacher.
"""

    try:
        response = model.generate_content(
            [SYSTEM_PROMPT, user_prompt],
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 1024,
            }
        )
        return {"result": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
