# Math Confidence Coach 
### Helping teachers refresh, understand and prepare mathematics lessons with AI.
## 1. Project Description

**Math Confidence Coach** is an AI-powered mathematics teaching assistant designed to help teachers refresh their understanding of mathematical topics and prepare engaging classroom lessons.

Teachers can enter a mathematics topic, select a grade level and choose a language. The application uses an AI model to generate a structured lesson card containing explanations, worked examples, visual ASCII diagrams, common misconceptions, real-world examples and practice questions.

The goal is to make mathematics lesson preparation faster, easier and more accessible.

<img width="1042" height="560" alt="image" src="https://github.com/user-attachments/assets/4140e6b3-f90f-426f-8247-1596c04e8354" />


### Key Features

- **Topic-based learning:** Enter topics such as Fractions, Algebra, Geometry, or Powers and Exponents.
- **Grade levels:** Supports Grade 5 through Grade 12.
- **Multiple languages:** English, German, Swedish, Spanish and French.
- **Simple explanations:** Refresh mathematical concepts in understandable language.
- **Worked examples:** Step-by-step mathematical solutions.
- **Additional examples:** More examples to strengthen understanding.
- **ASCII diagrams:** Text-based visual explanations for mathematical concepts.
- **Teacher notes:** Teaching guidance and common student misconceptions.
- **Real-world examples:** Connect mathematical concepts to everyday situations.
- **Practice questions:** Questions with answers and explanations.
- **Differentiation:** Simpler explanations and extension activities.
- **Classroom activities:** Practical activities for lesson preparation.
- **Privacy-conscious design:** No accounts, student tests, or student scores.

## 2. System Architecture

The application follows a simple modular architecture. The frontend communicates with a FastAPI backend, which prepares prompts, retrieves relevant lesson content, calls the configured AI provider, validates the response and returns the lesson card.

### ASCII Architecture Diagram

```text
                  TEACHER
                     |
                     v
          +----------------------+
          |    FRONTEND UI       |
          |                      |
          |  Topic               |
          |  Grade               |
          |  Language            |
          +----------------------+
                     |
                     | POST /coach
                     v
          +----------------------+
          |      FASTAPI         |
          |                      |
          |  Request Validation  |
          +----------------------+
                     |
                     v
          +----------------------+
          |    COACH SERVICE     |
          |                      |
          |  Prompt Engineering  |
          |  Lesson Preparation  |
          +----------------------+
                |          |
                v          v
        +-------------+  +----------------+
        |  RETRIEVAL  |  |   LLM CLIENT   |
        |             |  |                |
        | Vetted      |  | HTTPX Client   |
        | Lessons     |  |                |
        +-------------+  +----------------+
                               |
                               v
                       +---------------+
                       |   GROQ API    |
                       |               |
                       | AI Model      |
                       +---------------+
                               |
                               v
                       +---------------+
                       | JSON Response |
                       +---------------+
                               |
                               v
                       +---------------+
                       | PYDANTIC      |
                       | VALIDATION    |
                       +---------------+
                               |
                               v
                       +---------------+
                       | CACHE / API   |
                       | RESPONSE      |
                       +---------------+
                               |
                               v
                       +---------------+
                       | LESSON CARD   |
                       | IN FRONTEND   |
                       +---------------+
```

### Request Flow

1. Teacher enters a mathematics topic.
2. Frontend sends the topic, grade and language to the backend.
3. FastAPI validates the request.
4. Coach service prepares the AI prompt.
5. Retrieval component searches for relevant vetted lesson content.
6. LLM client sends the request to Groq using an OpenAI-compatible API.
7. The AI generates structured JSON lesson content.
8. Pydantic validates the generated content.
9. The application returns the lesson card to the frontend.
10. The teacher reviews the generated learning material.

## 3. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python |
| API Framework | FastAPI |
| Validation | Pydantic |
| AI Provider | GroqCloud API |
| Server | Uvicorn |

## 4. Create a Groq Account and Get an API Key

This project uses **GroqCloud**, an API service that provides access to hosted AI models.

You do not need to download or install Groq. The application connects to Groq over HTTPS.

### Step 1: Create a free account

Open:

https://console.groq.com/

1. Click Sign Up.
2. Register using an available sign-up method.
3. Verify your account if requested.
4. Sign in to GroqCloud Console.

### Step 2: Generate an API key

Open:

https://console.groq.com/keys

1. Click **Create API Key**.
2. Give your key a name, such as `math-confidence-coach`.
3. Create the key.
4. Copy and securely store it.

**Important:** Your API key is a secret. Do not share it, commit it to GitHub, or put it in frontend JavaScript.

### Step 3: Choose an AI model

Available models can change. Check the current model list:

https://console.groq.com/docs/models

For this project, an example configuration is:

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=your_groq_api_key
LLM_MODEL=openai/gpt-oss-20b
LLM_JSON_MODE=true
```

The model ID must be available to your account and compatible with the API request used by the application.

### Step 4: Check API usage

Open:

https://console.groq.com/dashboard/usage

You can monitor API requests and token consumption.

## 5. Installation and Running the Application

### Prerequisites

- Python 3.10 or later
- pip
- Git
- GroqCloud account and API key

### Step 1: Clone the project

```bash
git clone https://github.com/mukund7296/math-confidence-coach.git

cd math-confidence-coach
```

### Step 2: Create a virtual environment

For macOS and Linux:

```bash
python3 -m venv .venv

source .venv/bin/activate
```

For Windows:

```bash
python -m venv .venv

.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure the environment

Create a `.env` file in the project root:

```env
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_API_KEY=your_groq_api_key  # here paste the key
LLM_MODEL=openai/gpt-oss-20b
LLM_JSON_MODE=true

CACHE_DB=coach_cache.sqlite3
RATE_LIMIT_PER_HOUR=20
```

Replace `your_groq_api_key` with your actual API key.

### Step 5: Start the FastAPI server

```bash
uvicorn app.main:app --reload
```

### Step 6: Open the application

Frontend:

http://127.0.0.1:8000

FastAPI interactive API documentation:

http://127.0.0.1:8000/docs

### Step 7: Generate your first lesson

Try the following input:

```text
Topic: Fractions
Grade: Grade 5
Language: English
```

Click **Prepare my lesson card**.

The application should generate a structured lesson with explanations, examples, visual diagrams and practice questions.

<img width="1062" height="755" alt="image" src="https://github.com/user-attachments/assets/98a24288-230f-40bc-a605-9ce7158bb4e5" />

<img width="1049" height="658" alt="image" src="https://github.com/user-attachments/assets/9bb4c2e8-e766-49dd-a120-60462c083100" />
<img width="1071" height="715" alt="image" src="https://github.com/user-attachments/assets/f91c6d29-b810-4b55-afef-cf5d3192aed3" />



## 6. Privacy and Security

Privacy is an important part of this project.

- No student accounts are required.
- No student names or email addresses are requested.
- No student scores or test results are collected.
- API credentials are stored in environment variables.
- Generated responses are validated before being returned.
- Topics entered by teachers are sent to the configured AI provider to generate lesson content.

Users should review the AI provider's privacy and data-retention policies before using the application with sensitive information.

## 7. Future Improvements

Possible enhancements include:

- Automated mathematical answer verification.
- More robust retry handling for invalid AI responses.
- Interactive mathematical diagrams.
- Export lesson cards to PDF.
- Save and reuse teacher lesson plans.
- Add automated backend and frontend tests.
- Add accessibility improvements.
- Support additional AI providers.
- many more

## 8. Project Purpose

This project demonstrates how an AI-powered application can combine:

- Python and FastAPI backend development.
- LLM integration through an API.
- Prompt engineering.
- Structured AI output using Pydantic.
- Retrieval of vetted lesson content.
- Caching and API validation.
- A simple frontend for an educational use case.

## 9. Customizing AI Responses – Prompt Engineering

**Want a different or more specific result? You can customize the prompt!**

The application follows a simple concept: we send the teacher's input to an LLM (Large Language Model), such as Groq, Gemini, Azure OpenAI, or another compatible AI provider. The model generates the response based on the instructions we provide in the prompt.

The quality and structure of the generated answer depend heavily on how clearly we define the prompt.

If you want to change the expected output, you do not necessarily need to change the entire application. Start by updating the system prompt in `app/coach.py`.

For example, you can request:

- More worked examples.
- Simpler explanations for younger students.
- More detailed ASCII diagrams.
- Specific teaching notes.
- More challenging practice questions.
- A different response structure or teaching style.

**The clearer and more specific the prompt, the closer the AI response can get to your expectations.**

### Simple AI Request Flow

```text
 Teacher Input
      |
      v
  System Prompt
  + User Input
      |
      v
  LLM API Request
      |
      v
 +-------------------------+
 |     AI Provider         |
 |                         |
 | Groq / Gemini / Azure   |
 | OpenAI / Other LLM      |
 +-------------------------+
      |
      v
 Generated JSON Response
      |
      v
 Pydantic Validation
      |
      v
  Final Lesson Card
```

**The key idea:** This is not rocket science! We provide input and clear instructions to an LLM and it generates the requested output. We can improve or customize the result by refining the prompt, changing the model, or adjusting the expected response schema.

The same application architecture can work with different LLM providers, provided they support the API format and features required by our integration.

**Math Confidence Coach — helping teachers refresh, understand and prepare mathematics lessons with AI.**
