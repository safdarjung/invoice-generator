from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from agent import app as agent_app
from chatbot_agent import chatbot_app
from langchain_core.messages import HumanMessage
import os
import tempfile

app = FastAPI()

# CORS Middleware
origins = ["http://localhost:3000", "https://safdar1.pythonanywhere.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models for requests
class PdfRequest(BaseModel):
    form_data: Dict[str, Any]
    api_key: Optional[str] = None

class ChatbotRequest(BaseModel):
    command: str
    form_data: Dict[str, Any]
    api_key: Optional[str] = None

# Endpoints
@app.post("/generate_pdf")
async def generate_pdf_endpoint(request: PdfRequest):
    # The api_key is available via request.api_key if an agent needs it in the future
    initial_state = {"form_data": request.form_data}
    final_state = agent_app.invoke(initial_state)
    pdf_path = final_state.get("pdf_path", "invoice.pdf")
    return FileResponse(pdf_path, media_type='application/pdf', filename='generated_document.pdf')

@app.post("/chatbot")
async def chatbot_endpoint(request: ChatbotRequest):
    initial_state = {
        "messages": [HumanMessage(content=request.command)],
        "form_data": request.form_data,
        "api_key": request.api_key or ""
    }
    final_state = chatbot_app.invoke(initial_state)
    return {"form_data": final_state["form_data"], "chatbot_response": final_state["messages"][-1].content}

@app.post("/upload_template")
async def upload_template(file: UploadFile = File(...)):
    # Save uploaded files to the system temp directory for cross-platform compatibility
    template_dir = tempfile.gettempdir()
    template_path = os.path.join(template_dir, file.filename)
    with open(template_path, "wb") as buffer:
        buffer.write(file.file.read())
    # In a real app, you might store this path in a database.
    # For now, we just confirm it was "uploaded".
    return {"message": f"Template '{file.filename}' uploaded successfully."}

# Serve static files from the React build directory
static_files_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")

app.mount(
    "/",
    StaticFiles(directory=static_files_dir, html=True),
    name="static",
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
# Note: On PythonAnywhere, use wsgi.py to serve the app
