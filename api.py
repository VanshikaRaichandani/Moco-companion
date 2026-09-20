from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chatbot.prompts import SYSTEM_PROMPT
from chatbot.llm import generate_response
from chatbot.database import (
    create_tables,
    create_conversation,
    load_messages,
    save_message
)

app = FastAPI(title="Moco API")

# Ensure database tables exist on server startup
@app.on_event("startup")
def startup_event():
    create_tables()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    conversation_id: int | None = None

@app.get("/")
def home():
    return {"message": "Moco API is running!"}

@app.post("/chat")
def chat(request: ChatRequest):
    # Create a new conversation if one doesn't exist
    if request.conversation_id is None:
        conversation_id = create_conversation()
        messages = []
    else:
        conversation_id = request.conversation_id
        messages = load_messages(conversation_id)

    # Save user message
    messages.append({
        "role": "user",
        "content": request.message
    })

    save_message(
        conversation_id,
        "user",
        request.message
    )

    # Generate Moco's response
    full_response = ""
    for chunk in generate_response(messages, SYSTEM_PROMPT):
        full_response += chunk

    # Save assistant message
    messages.append({
        "role": "assistant",
        "content": full_response
    })

    save_message(
        conversation_id,
        "assistant",
        full_response
    )

    return {
        "conversation_id": conversation_id,
        "reply": full_response
    }