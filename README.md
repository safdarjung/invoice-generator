# Invoice Generator

## Running Locally

### Backend (FastAPI)
1. Open a terminal and navigate to the backend directory:
   ```sh
   cd backend
   ```
2. (Optional but recommended) Create and activate a virtual environment:
   ```sh
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   # or
   source venv/bin/activate  # On Mac/Linux
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
4. Start the backend server:
   ```sh
   python main.py
   ```
   The backend will be available at http://localhost:5000

### Frontend (React)
1. Open a new terminal and navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Start the React development server:
   ```sh
   npm start
   ```
   The frontend will be available at http://localhost:3000

---

## Deploying on PythonAnywhere

### Backend (FastAPI)
1. Upload the `backend` folder to your PythonAnywhere account.
2. Set up a virtual environment and install dependencies:
   ```sh
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure your PythonAnywhere web app to use the `backend/wsgi.py` file as the WSGI entry point.

### Frontend (React)
1. Build the frontend for production:
   ```sh
   cd frontend
   npm install
   npm run build
   ```
2. The build output will be in `frontend/build`. This is automatically served by FastAPI if present.
   - Alternatively, you can configure PythonAnywhere to serve the `build` directory as static files.

---

## Notes
- The backend is set up to serve the React build as static files if the build directory exists.
- For local development, use the React dev server for hot reloading.
- For production (PythonAnywhere), use the built React app and serve it via FastAPI or as static files.
- Make sure to update CORS origins in `backend/main.py` if your deployment URLs change. 