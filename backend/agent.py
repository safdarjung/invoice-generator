from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from .pdf_generator import create_pdf

class AgentState(TypedDict):
    form_data: dict
    pdf_path: str

# Agents
def invoice_agent(state: AgentState):
    print("---Generating Invoice---")
    pdf_path = create_pdf(state['form_data'], file_path="generated_document.pdf")
    return {"pdf_path": pdf_path}

def quotation_agent(state: AgentState):
    print("---Generating Quotation---")
    pdf_path = create_pdf(state['form_data'], file_path="generated_document.pdf")
    return {"pdf_path": pdf_path}

# Supervisor
def supervisor_node(state: AgentState) -> Literal["invoice", "quotation"]:
    print("---Supervisor---")
    if state['form_data'].get('invoice_number'):
        return "invoice"
    else:
        return "quotation"

# Graph Definition
workflow = StateGraph(AgentState)

workflow.add_node("invoice", invoice_agent)
workflow.add_node("quotation", quotation_agent)
workflow.add_conditional_edges(
    "__start__",
    supervisor_node,
    {
        "invoice": "invoice",
        "quotation": "quotation",
    },
)
workflow.add_edge("invoice", END)
workflow.add_edge("quotation", END)

app = workflow.compile()
