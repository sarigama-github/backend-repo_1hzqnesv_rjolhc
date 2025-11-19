"""
CRM Database Schemas for Tour Operator

Each Pydantic model maps to a MongoDB collection using the lowercase class name
as the collection name (e.g., Client -> "client").
"""
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, EmailStr
from datetime import date

# Core CRM
class Client(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    country: Optional[str] = None
    preferences: Optional[List[str]] = Field(default_factory=list)
    demographics: Optional[dict] = Field(default_factory=dict)
    travel_history: Optional[List[dict]] = Field(default_factory=list, description="list of past trips with dates and destinations")
    documents: Optional[List[dict]] = Field(default_factory=list, description="[{name, url}] uploaded docs")
    tags: Optional[List[str]] = Field(default_factory=list)

class Lead(BaseModel):
    client_id: Optional[str] = Field(None, description="linked client")
    source: Optional[str] = None
    stage: Literal["new", "qualified", "proposal", "won", "lost"] = "new"
    interested_destinations: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = None
    value: Optional[float] = None
    currency: Literal["USD", "EUR", "GBP", "AUD", "CAD", "KES", "ZAR", "INR"] = "USD"
    due_date: Optional[date] = None

class Task(BaseModel):
    title: str
    due_date: Optional[date] = None
    status: Literal["open", "done", "snoozed"] = "open"
    lead_id: Optional[str] = None
    client_id: Optional[str] = None
    reminder: Optional[str] = None

# Suppliers & Products
class Supplier(BaseModel):
    name: str
    type: Literal["hotel", "guide", "transport", "activity", "other"] = "other"
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    rates: Optional[List[dict]] = Field(default_factory=list)
    contracts: Optional[List[dict]] = Field(default_factory=list)
    commission_pct: Optional[float] = Field(default=0.0)
    markup_pct: Optional[float] = Field(default=0.0)
    availability: Optional[List[dict]] = Field(default_factory=list)
    address: Optional[str] = None

# Itineraries
class Itinerary(BaseModel):
    lead_id: Optional[str] = None
    client_id: Optional[str] = None
    title: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    currency: Literal["USD", "EUR", "GBP", "AUD", "CAD", "KES", "ZAR", "INR"] = "USD"
    version: int = 1
    shared_token: Optional[str] = None

class ItineraryItem(BaseModel):
    itinerary_id: str
    day: int
    title: str
    description: Optional[str] = None
    supplier_id: Optional[str] = None
    cost: Optional[float] = 0.0
    price: Optional[float] = 0.0

# Bookings, Quotes & Payments
class Quote(BaseModel):
    lead_id: Optional[str] = None
    itinerary_id: Optional[str] = None
    total_price: float
    currency: Literal["USD", "EUR", "GBP", "AUD", "CAD", "KES", "ZAR", "INR"] = "USD"
    status: Literal["draft", "sent", "accepted", "rejected"] = "draft"

class Booking(BaseModel):
    client_id: str
    itinerary_id: Optional[str] = None
    status: Literal["pending", "confirmed", "cancelled"] = "pending"
    payment_state: Literal["unpaid", "deposit_paid", "paid", "refunded"] = "unpaid"
    capacity: Optional[int] = None
    supplier_links: Optional[List[str]] = Field(default_factory=list)

class Invoice(BaseModel):
    booking_id: str
    amount: float
    currency: Literal["USD", "EUR", "GBP", "AUD", "CAD", "KES", "ZAR", "INR"] = "USD"
    tax_rate_pct: float = 0.0
    status: Literal["draft", "sent", "partially_paid", "paid", "void"] = "draft"

class Payment(BaseModel):
    booking_id: str
    invoice_id: Optional[str] = None
    amount: float
    currency: Literal["USD", "EUR", "GBP", "AUD", "CAD", "KES", "ZAR", "INR"] = "USD"
    method: Literal["card", "bank", "cash", "paypal", "stripe", "other"] = "other"
    status: Literal["initiated", "succeeded", "failed", "refunded"] = "initiated"

# Communications and Timeline
class Communication(BaseModel):
    client_id: Optional[str] = None
    lead_id: Optional[str] = None
    channel: Literal["email", "sms", "whatsapp", "note"] = "email"
    subject: Optional[str] = None
    body: Optional[str] = None
    to: Optional[str] = None
    template: Optional[str] = None

# Operations
class OperationEvent(BaseModel):
    date: date
    type: Literal["departure", "arrival", "pickup", "dropoff", "activity"] = "activity"
    booking_id: Optional[str] = None
    notes: Optional[str] = None

