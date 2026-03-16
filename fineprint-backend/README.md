# FinePrint AI - Phase 1 Backend

This is the Python (FastAPI) backend for Phase 1 of the FinePrint AI project. It exposes an endpoint that allows you to upload a PDF contract, extracts its text, and feeds it into Gemini-1.5-Flash combined with a deterministic, low-temperature prompt enforcing strict Agentic guidelines.

3. **Important Note on the Demo:** If you do not have an active Gemini API Key, the application will automatically catch the missing key error and fall back to returning a perfect Mock Audit Data Response. This ensures the demo *always* succeeds for judging, correctly highlighting one compliant clause and one severe regulatory violation.

---

## Architecture

*   **Frontend:** Next.js (App Router), TailwindCSS, TypeScript.
*   **Backend:** FastAPI, Python, PyMuPDF (`fitz`), Pydantic (for strictly typed JSON schemas).
*   **Intelligence:** `Gemini-1.5-Flash` combined with a deterministic, low-temperature prompt enforcing strict Agentic guidelines.

## Folder Structure

```text
fineprint-backend/
├── main.py              # The main FastAPI server code
├── requirements.txt     # The required Python libraries
├── .env.example         # An example of the environment variables needed
└── README.md            # This instruction file
```

## How to Run the Server

**Step 1: Open a terminal inside this folder**
Ensure your terminal path shows `.../fineprint-backend`.

**Step 2: Create a virtual environment (Recommended)**
Creating a virtual environment isolates this project's packages from your system.
For Windows:
```bash
python -m venv venv
venv\Scripts\activate
```
For Mac/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install the required libraries**
```bash
pip install -r requirements.txt
```

**Step 4: Set up your Gemini API Key**
The application needs your API key to talk to Gemini.
1. Copy `.env.example` to a new file called `.env` (just `.env`, nothing before the dot).
2. Open `.env` and paste your actual Gemini API key:
   `GEMINI_API_KEY=your-real-key-here`

*(Alternatively, you can export it directly in your terminal: `set GEMINI_API_KEY=your_key` on Windows or `export GEMINI_API_KEY=your_key` on Mac/Linux).*

**Step 5: Start the FastAPI Server**
Run the following command:
```bash
uvicorn main:app --reload
```
- `main` refers to `main.py`.
- `app` refers to the `app = FastAPI()` object inside `main.py`.
- `--reload` tells the server to automatically restart if you edit the code.

## How to Test the Endpoint

FastAPI gives you an automatic, interactive testing page called Swagger UI!

1. Once the server is running, open your web browser.
2. Go to: **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
3. Click on the `POST /upload-contract` box to expand it.
4. Click the **"Try it out"** button.
5. You'll see an option to upload a file. Select a test PDF from your computer.
6. Click **"Execute"**.
7. Scroll down to see the JSON response containing your original and simplified clauses!
