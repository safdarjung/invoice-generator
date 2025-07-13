from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

class ChatbotState(TypedDict):
    messages: Annotated[List, add_messages]
    form_data: dict
    api_key: str

def chatbot_node(state: ChatbotState) -> dict:
    api_key = state.get("api_key")
    user_message = state["messages"][-1].content
    form_data = state["form_data"]

    # Compose a prompt that includes the form data and user message
    prompt = f"""
You are an invoice and quotation assistant. Here is the current form data:
{form_data}

User: {user_message}

Reply as a helpful assistant. If the user asks to update the form, reply with the new value and a confirmation. If the user asks a general question, answer naturally.
"""

    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key
    )
    response = llm.invoke(prompt)
    return {
        "form_data": form_data,  # Optionally, parse LLM output to update form_data
        "messages": [AIMessage(content=response.content)]
    }

workflow = StateGraph(ChatbotState)
workflow.add_node("chatbot", chatbot_node)
workflow.set_entry_point("chatbot")
workflow.add_edge("chatbot", END)

chatbot_app = workflow.compile()
