from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages # Corrected import
from langchain_core.messages import HumanMessage, AIMessage
import re

# Define the state
class ChatbotState(TypedDict):
    messages: Annotated[List, add_messages]
    form_data: dict

# Rule-based command processing
def process_command(command: str, form_data: dict) -> dict:
    command = command.lower().strip()
    response_message = "I couldn't understand that command. Please try again."

    # Update client details
    if "change client name to" in command:
        match = re.search(r"change client name to (.+)", command)
        if match:
            form_data["client_name"] = match.group(1).strip()
            response_message = f"Client name updated to {form_data['client_name']}."
    elif "change client address to" in command:
        match = re.search(r"change client address to (.+)", command)
        if match:
            form_data["client_address"] = match.group(1).strip()
            response_message = f"Client address updated to {form_data['client_address']}."
    elif "change client gstin to" in command:
        match = re.search(r"change client gstin to (.+)", command)
        if match:
            form_data["client_gstin"] = match.group(1).strip()
            response_message = f"Client GSTIN updated to {form_data['client_gstin']}."

    # Add item
    elif "add" in command and "item" in command:
        try:
            command_data = command.split("item", 1)[1]
            if command_data.startswith(":"):
                command_data = command_data[1:].strip()

            parts = [p.strip() for p in command_data.split(",")]
            description = parts[0]
            
            item_data = {"description": description}
            
            for part in parts[1:]:
                if ":" in part:
                    key, value = part.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key in ["hsn", "rate", "price", "qty"]:
                        item_data[key] = value

            if "price" in item_data:
                item_data["rate"] = item_data["price"]
            
            if "rate" not in item_data:
                raise ValueError("Rate/Price is required to add an item.")

            new_item = {
                "description": item_data["description"],
                "hsn_code": item_data.get("hsn"),
                "rate": float(item_data["rate"]),
                "quantity": int(item_data.get("qty", 1))
            }
            
            form_data["items"].append(new_item)
            response_message = f"Added item: {new_item['description']}."

        except Exception as e:
            response_message = f"Error adding item: {e}. Please use the format: add item <desc>, hsn <hs_code>, rate <rate>, qty <qty>"


    # Remove item
    elif "remove item number" in command:
        match = re.search(r"remove item number (\d+)", command)
        if match:
            item_number = int(match.group(1))
            if 1 <= item_number <= len(form_data["items"]):
                removed_item = form_data["items"].pop(item_number - 1)
                response_message = f"Removed item: {removed_item['description']}."
            else:
                response_message = "Item number out of range."
        else:
            response_message = "Invalid 'remove item' command format. Use: 'remove item number [number]'."

    # Apply discount
    elif "apply discount" in command:
        match = re.search(r"apply discount (\d+\.?\d*)%", command)
        if match:
            discount_percentage = float(match.group(1))
            for item in form_data["items"]:
                item["rate"] *= (1 - discount_percentage / 100)
            response_message = f"Applied {discount_percentage}% discount to all items."
        else:
            response_message = "Invalid 'apply discount' command format. Use: 'apply discount [percentage]%'"
    
    # Update invoice/quotation specific fields
    elif "change invoice number to" in command:
        match = re.search(r"change invoice number to (.+)", command)
        if match:
            form_data["invoice_number"] = match.group(1).strip()
            response_message = f"Invoice number updated to {form_data['invoice_number']}."
    elif "change invoice date to" in command:
        match = re.search(r"change invoice date to (.+)", command)
        if match:
            form_data["invoice_date"] = match.group(1).strip()
            response_message = f"Invoice date updated to {form_data['invoice_date']}."
    elif "change gst percentage to" in command:
        match = re.search(r"change gst percentage to (\d+\.?\d*)", command)
        if match:
            form_data["gst_percentage"] = float(match.group(1))
            response_message = f"GST percentage updated to {form_data['gst_percentage']}%."
    elif "change transport charge to" in command:
        match = re.search(r"change transport charge to (\d+\.?\d*)", command)
        if match:
            form_data["transport_charge"] = float(match.group(1))
            response_message = f"Transport charge updated to {form_data['transport_charge']}."
    elif "change advance payment to" in command:
        match = re.search(r"change advance payment to (\d+\.?\d*)", command)
        if match:
            form_data["advance_payment"] = float(match.group(1))
            response_message = f"Advance payment updated to {form_data['advance_payment']}."
    elif "change minimum quantity to" in command:
        match = re.search(r"change minimum quantity to (.+)", command)
        if match:
            form_data["minimum_quantity"] = match.group(1).strip()
            response_message = f"Minimum quantity updated to {form_data['minimum_quantity']}."
    elif "change delivery time to" in command:
        match = re.search(r"change delivery time to (.+)", command)
        if match:
            form_data["delivery_time"] = match.group(1).strip()
            response_message = f"Delivery time updated to {form_data['delivery_time']}."
    elif "change payment terms to" in command:
        match = re.search(r"change payment terms to (.+)", command)
        if match:
            form_data["payment_terms"] = match.group(1).strip()
            response_message = f"Payment terms updated to {form_data['payment_terms']}."

    form_data["chatbot_response"] = response_message # Add chatbot response to form_data for frontend display
    return form_data

def chatbot_node(state: ChatbotState) -> dict:
    command = state["messages"][-1].content
    updated_form_data = process_command(command, state["form_data"])
    return {"form_data": updated_form_data, "messages": [AIMessage(content=updated_form_data["chatbot_response"])]}

# Build the graph
workflow = StateGraph(ChatbotState)
workflow.add_node("chatbot", chatbot_node)
workflow.set_entry_point("chatbot")
workflow.add_edge("chatbot", END)

chatbot_app = workflow.compile()
