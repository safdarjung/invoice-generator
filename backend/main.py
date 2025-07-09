from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from agent import app as agent_app
from chatbot_agent import chatbot_app
from langchain_core.messages import HumanMessage
import os

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

class ApiKeyRequest(BaseModel):
    api_key: str

class ChatbotRequest(BaseModel):
    command: str
    form_data: Dict[str, Any]

@app.post("/set_api_key")
async def set_api_key(request: ApiKeyRequest):
    os.environ["GEMINI_API_KEY"] = request.api_key
    return {"message": "API key set successfully"}

@app.post("/generate_pdf")
async def generate_pdf_endpoint(form_data: Dict[str, Any]):
    initial_state = {"form_data": form_data}
    final_state = agent_app.invoke(initial_state)
    pdf_path = final_state.get("pdf_path", "invoice.pdf")
    return FileResponse(pdf_path, media_type='application/pdf', filename='generated_document.pdf')

@app.post("/chatbot")
async def chatbot_endpoint(request: ChatbotRequest):
    initial_state = {
        "messages": [HumanMessage(content=request.command)],
        "form_data": request.form_data
    }
    final_state = chatbot_app.invoke(initial_state)
    return {"form_data": final_state["form_data"], "chatbot_response": final_state["messages"][-1].content}

@app.post("/upload_template")
async def upload_template(file: UploadFile = File(...)):
    template_path = os.path.join("templates", file.filename)
    with open(template_path, "wb") as buffer:
        buffer.write(file.file.read())
    return {"message": "Template uploaded successfully"}

if not os.path.exists("templates"):
    os.makedirs("templates")

# Serve static files from the React build directory
# Construct the path to the frontend build directory
static_files_dir = os.path.join(os.path.dirname(__file__), "..", "frontend", "build")

app.mount(
    "/",
    StaticFiles(directory=static_files_dir, html=True),
    name="static",
)