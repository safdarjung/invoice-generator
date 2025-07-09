import pytest
from unittest.mock import patch
from agent import app as agent_app

# Sample form data for testing
@pytest.fixture
def sample_invoice_data():
    return {
        "client_name": "Test Client Inc.",
        "invoice_number": "INV-2024-001",
        "invoice_date": "2024-07-26",
        "items": [
            {"description": "Product A", "quantity": 2, "rate": 100.0},
        ],
    }

@pytest.fixture
def sample_quotation_data():
    return {
        "client_name": "Test Client Corp.",
        "items": [
            {"description": "Consulting Services", "rate": 500.0},
        ],
        "minimum_quantity": "10 units",
    }

# Test supervisor_node
def test_supervisor_node_invoice(sample_invoice_data):
    initial_state = {"form_data": sample_invoice_data}
    # The supervisor node is the entry point, so we invoke the app directly
    # and check the final state's messages or the path taken.
    # For a simple supervisor, we can directly call the node function.
    from agent import supervisor_node
    result = supervisor_node(initial_state)
    assert result == "invoice"

def test_supervisor_node_quotation(sample_quotation_data):
    initial_state = {"form_data": sample_quotation_data}
    from agent import supervisor_node
    result = supervisor_node(initial_state)
    assert result == "quotation"

# Test invoice_agent and quotation_agent with mocked create_pdf
@patch('agent.create_pdf')
def test_invoice_agent(mock_create_pdf, sample_invoice_data):
    mock_create_pdf.return_value = "mock_invoice.pdf"
    initial_state = {"form_data": sample_invoice_data}
    
    # Invoke the LangGraph app with the initial state
    final_state = agent_app.invoke(initial_state)

    # Assert that create_pdf was called with the correct data
    mock_create_pdf.assert_called_once_with(sample_invoice_data, file_path="generated_document.pdf")
    # Assert that the final state contains the correct pdf_path
    assert final_state['pdf_path'] == "mock_invoice.pdf"

@patch('agent.create_pdf')
def test_quotation_agent(mock_create_pdf, sample_quotation_data):
    mock_create_pdf.return_value = "mock_quotation.pdf"
    initial_state = {"form_data": sample_quotation_data}

    # Invoke the LangGraph app with the initial state
    final_state = agent_app.invoke(initial_state)

    # Assert that create_pdf was called with the correct data
    mock_create_pdf.assert_called_once_with(sample_quotation_data, file_path="generated_document.pdf")
    # Assert that the final state contains the correct pdf_path
    assert final_state['pdf_path'] == "mock_quotation.pdf"
