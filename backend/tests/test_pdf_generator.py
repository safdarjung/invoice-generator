import pytest
import os
from pdf_generator import create_pdf
from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    description: str
    hsn_code: Optional[str] = None
    quantity: Optional[int] = None
    rate: float

class FormData(BaseModel):
    client_name: str
    client_address: str
    client_gstin: str
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    items: List[Item]
    gst_percentage: Optional[float] = None
    transport_charge: Optional[float] = None
    advance_payment: Optional[float] = None
    minimum_quantity: Optional[str] = None
    delivery_time: Optional[str] = None
    payment_terms: Optional[str] = None

# Sample form data for testing
@pytest.fixture
def sample_invoice_data():
    return FormData(
        client_name="Test Client Inc.",
        client_address="123 Test Street, Test City",
        client_gstin="GSTIN123TEST",
        invoice_number="INV-2024-001",
        invoice_date="2024-07-26",
        items=[
            Item(description="Product A", hsn_code="1234", quantity=2, rate=100.0),
            Item(description="Service B", hsn_code="5678", quantity=1, rate=250.0)
        ],
        gst_percentage=18.0,
        transport_charge=50.0,
        advance_payment=100.0,
        minimum_quantity=None,
        delivery_time=None,
        payment_terms=None,
    )

@pytest.fixture
def sample_quotation_data():
    return FormData(
        client_name="Test Client Corp.",
        client_address="456 Test Avenue, Test Town",
        client_gstin="GSTIN456QUOT",
        invoice_number=None,
        invoice_date=None,
        items=[
            Item(description="Consulting Services", hsn_code=None, quantity=1, rate=500.0),
            Item(description="Software License", hsn_code=None, quantity=1, rate=1000.0)
        ],
        gst_percentage=None,
        transport_charge=None,
        advance_payment=None,
        minimum_quantity="10 units",
        delivery_time="7 working days",
        payment_terms="50% upfront, 50% on delivery",
    )

# Teardown function to clean up generated PDF files
def teardown_function(function):
    if os.path.exists("test_invoice.pdf"):
        os.remove("test_invoice.pdf")
    if os.path.exists("test_quotation.pdf"):
        os.remove("test_quotation.pdf")

def test_create_invoice_pdf(sample_invoice_data):
    file_path = "test_invoice.pdf"
    create_pdf(sample_invoice_data.model_dump(), file_path)
    assert os.path.exists(file_path)
    assert os.path.getsize(file_path) > 0  # Check if file is not empty

def test_create_quotation_pdf(sample_quotation_data):
    file_path = "test_quotation.pdf"
    create_pdf(sample_quotation_data.model_dump(), file_path)
    assert os.path.exists(file_path)
    assert os.path.getsize(file_path) > 0  # Check if file is not empty