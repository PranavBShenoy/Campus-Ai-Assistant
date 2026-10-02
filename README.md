# CampusAI 🎓

**Your AI-powered academic assistant for smarter learning and exam preparation.**

CampusAI combines AI conversations, document-based question answering, and personalized study planning to help students organize their learning and prepare for exams.

## ✨ Features

* **AI Assistant:** Ask academic questions using an LLM powered by OpenRouter.
* **Academic RAG:** Retrieve relevant information from uploaded study materials and generate document-grounded answers.
* **Knowledge Base:** Upload PDF, DOCX, and TXT files for AI-assisted learning.
* **Study Planner:** Create personalized study schedules based on subjects, exam types, dates, daily study hours, and weekly off days.
* **Authentication:** Login and protected access to personal resources.
* **Chat History:** Keep track of academic conversations.

## 🛠️ Tech Stack

| Component       | Technologies                     |
| --------------- | -------------------------------- |
| Frontend        | Next.js, React, TypeScript       |
| Backend         | Python, FastAPI                  |
| AI Integration  | OpenRouter, LangChain, LangGraph |
| Database        | SQLite, SQLAlchemy               |
| Vector Database | ChromaDB                         |
| Embeddings      | Sentence Transformers            |

## 🚀 Getting Started

### Prerequisites

Install the following:

* Python 3.11
* Node.js and npm
* Git

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/CampusAI.git
cd CampusAI
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Configure the backend

Open PowerShell in the project root:

```powershell
Copy-Item backend\.env.example backend\.env
notepad backend\.env
```

Configure your OpenRouter API key and other required environment variables. Save the file.

Create a virtual environment and install dependencies:

```powershell
py -3.11 -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

### 3. Install frontend dependencies

Open a terminal in the project root:

```powershell
cd frontend
npm install
cd ..
```

### 4. Start CampusAI

If the project includes the startup script, run:

```powershell
.\start.ps1
```

Alternatively, start the backend and frontend in separate terminals.

**Backend terminal:**

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

**Frontend terminal:**

```powershell
cd frontend
npm run dev
```

If your backend entry point differs, use the entry point configured in your project.

### 5. Open the application

* **Website:** http://localhost:3000
* **Backend API:** http://127.0.0.1:8000
* **API documentation:** http://127.0.0.1:8000/docs

## 🔐 Environment Variables

Keep API keys and secrets in your local `.env` files. Never commit real credentials, private databases, or uploaded documents to GitHub. Use `.env.example` to document required variables with placeholder values.

## 📌 Project Status

CampusAI is an ongoing project. Core application components include the AI assistant, Knowledge Base, authentication, and Study Planner. AI document retrieval and other workflows should be tested with real credentials and uploaded materials.

## 👨‍💻 Author

**Pranav Shenoy**

* GitHub: [PranavBShenoy](https://github.com/PranavBShenoy)

---

*Built to make academic learning more organized, interactive, and accessible with AI.*
