# Math Confidence Coach

A focused prototype that helps math teachers quickly refresh their knowledge and prepare lessons.

## How to Run

1. Unzip the repository and open a terminal in the project folder.

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your free Gemini API key:
   ```bash
   cp .env.example .env
   ```
   Then edit `.env` and replace `your_gemini_api_key_here` with your real key  
   (Get a free key at: https://aistudio.google.com/app/apikey)

4. Start the server:
   ```bash
   uvicorn main:app --reload
   ```

5. Open http://localhost:8000 in your browser.

## Product Decisions

**Problem I focused on**  
Many math teachers lack confidence in the topics they teach. They need a fast way to refresh their understanding and get practical lesson ideas — without feeling tested or judged.

**What the coach does**  
The teacher enters a topic + grade level and instantly receives a structured “Lesson Ready Card” containing:
- Core idea (knowledge refresh)
- Common student misconceptions
- Practical lesson ideas
- Differentiation (simpler + extension)
- One quick classroom activity

**Why this form?**
- Teachers in the brief dislike chatbots → I avoided a conversational interface completely.
- They do not want tests or scores → The coach never evaluates the teacher.
- They learn alone and need something fast → One-click structured output is more useful than a long chat.

**Trade-offs**
- I chose depth on a clear interaction over building many features.
- Stateless design keeps cost and complexity very low.
- Frontend is intentionally simple but clean and professional.

## What I Skipped and Why

- User accounts / login (not needed for the core value)
- Chat history (conflicts with “dislike chatbots”)
- Tests or quizzes (explicitly unwanted)
- Complex RAG / vector database (unnecessary for a strong 2-hour prototype)
- Multi-agent system (would add complexity without clear benefit at this stage)

## Time Spent
Approximately 1 hour 50 minutes.

## How I Ensure Good Answers

1. Strong, opinionated system prompt that forces a consistent useful structure.
2. Low temperature (0.4) for more reliable output.
3. Clear separation of concerns in the prompt (Core Idea, Misconceptions, Lesson Ideas, etc.).
4. Manual testing on several topics (fractions, linear equations, Pythagoras, quadratic equations).

## Cost per Teacher per Month

Using Gemini 1.5 Flash:

- Average request ≈ 900–1200 tokens
- Realistic usage: 8–12 requests per teacher per month
- Estimated cost: **$0.015 – $0.04 per teacher per month**

Ways to lower cost further:
- Cache popular topics
- Move frequent topics to static content + light LLM polishing
- Use Gemini Flash-8B for simpler requests
- Add a lightweight RAG layer later so the model generates less text

## Data Handling (Plain Language)

The coach only receives the math topic and grade level that the teacher types.  
This information is sent to Google’s Gemini API to generate the response.  

We do not store:
- Teacher names
- Email addresses
- Conversation history
- Any personal data

The current version is completely stateless.

## Architecture Notes

- Simple and extensible FastAPI backend
- Easy to add caching, RAG, or more grade-specific content later
- Frontend can be replaced by any client without changing the API

---
Built as a focused prototype for the Akelius AI Engineer assignment.
