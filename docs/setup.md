# CampusAI Setup Guide

This guide will walk you through setting up CampusAI on your local machine.

## Prerequisites

1. **Python 3.9, 3.10, or 3.11** (Note: Python 3.12+ may have issues compiling some AI packages like `chromadb`)
2. **Node.js 18+** and `npm`
3. An **OpenRouter API key**

## Step 1: Backend Setup

1. Open a terminal and navigate to the backend directory:
   ```powershell
   cd campus-ai\backend
   ```

2. Create a virtual environment and activate it:
   ```powershell
   py -3.9 -m venv venv
   .\venv\Scripts\activate
   ```

3. Install the Python dependencies:
   ```powershell
   python -m pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```powershell
   Copy-Item .env.example .env
   ```
   Open the `.env` file in a text editor and add your API key:
   ```
   OPENROUTER_API_KEY=your_actual_key_here
   ```

5. Start the backend server:
   ```powershell
   python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   The backend should now be running at http://localhost:8000.

## Step 2: Frontend Setup

1. Open a *new* terminal and navigate to the frontend directory:
   ```powershell
   cd campus-ai\frontend
   ```

2. Install the Node dependencies:
   ```powershell
   npm install
   ```

3. Start the Next.js development server:
   ```powershell
   npm run dev
   ```
   The frontend should now be running at http://localhost:3000.

## Step 3: Initialization & Usage

1. Open your browser and go to http://localhost:3000.
2. Navigate to the **Knowledge Base** page from the sidebar.
3. Upload the sample documents located in `campus-ai/backend/data/sample_documents/`.
4. Wait a moment for them to be processed (status will change to "Indexed").
5. Navigate to the **AI Assistant** page, select "Academic RAG" mode, and start asking questions!

## Using the Quick Start Scripts (Windows)

For convenience, two startup scripts are provided in the root `campus-ai` folder:
- `start.ps1` (PowerShell script)
- `start.bat` (Batch script)

You can run these scripts to automatically launch both the backend and frontend servers simultaneously.
