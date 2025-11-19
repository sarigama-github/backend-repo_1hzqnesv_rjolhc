import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from bson import ObjectId

from database import db, create_document, get_documents

app = FastAPI(title="Tour Operator CRM API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilities
class IdModel(BaseModel):
    id: str


def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")


@app.get("/")
def read_root():
    return {"message": "Tour Operator CRM API"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, "name", None) or "Unknown"
            response["connection_status"] = "Connected"
            try:
                response["collections"] = db.list_collection_names()[:20]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"
    return response


# ---- Minimal CRUD for core entities to support prototype UI ----
# We intentionally scope endpoints to cover initial flows: clients, leads, itineraries, bookings, tasks, payments, communications.

from fastapi import Body


def insert_and_return(collection: str, data: Dict):
    new_id = create_document(collection, data)
    doc = db[collection].find_one({"_id": ObjectId(new_id)})
    doc["id"] = str(doc.pop("_id"))
    return doc


def list_collection(collection: str, filter_dict: Dict | None = None, limit: int | None = 100):
    items = get_documents(collection, filter_dict or {}, limit)
    for it in items:
        it["id"] = str(it.pop("_id"))
    return items


@app.post("/clients")
def create_client(payload: Dict = Body(...)):
    return insert_and_return("client", payload)


@app.get("/clients")
def list_clients():
    return list_collection("client", {}, 200)


@app.post("/leads")
def create_lead(payload: Dict = Body(...)):
    return insert_and_return("lead", payload)


@app.get("/leads")
def list_leads():
    return list_collection("lead", {}, 200)


@app.post("/tasks")
def create_task(payload: Dict = Body(...)):
    return insert_and_return("task", payload)


@app.get("/tasks")
def list_tasks():
    return list_collection("task", {}, 200)


@app.post("/suppliers")
def create_supplier(payload: Dict = Body(...)):
    return insert_and_return("supplier", payload)


@app.get("/suppliers")
def list_suppliers():
    return list_collection("supplier", {}, 200)


@app.post("/itineraries")
def create_itinerary(payload: Dict = Body(...)):
    return insert_and_return("itinerary", payload)


@app.get("/itineraries")
def list_itineraries():
    return list_collection("itinerary", {}, 200)


@app.post("/itinerary-items")
def create_itinerary_item(payload: Dict = Body(...)):
    return insert_and_return("itineraryitem", payload)


@app.get("/itinerary-items")
def list_itinerary_items(itinerary_id: Optional[str] = None):
    filter_q = {"itinerary_id": itinerary_id} if itinerary_id else {}
    return list_collection("itineraryitem", filter_q, 500)


@app.post("/quotes")
def create_quote(payload: Dict = Body(...)):
    return insert_and_return("quote", payload)


@app.get("/quotes")
def list_quotes():
    return list_collection("quote", {}, 200)


@app.post("/bookings")
def create_booking(payload: Dict = Body(...)):
    return insert_and_return("booking", payload)


@app.get("/bookings")
def list_bookings():
    return list_collection("booking", {}, 200)


@app.post("/invoices")
def create_invoice(payload: Dict = Body(...)):
    return insert_and_return("invoice", payload)


@app.get("/invoices")
def list_invoices():
    return list_collection("invoice", {}, 200)


@app.post("/payments")
def create_payment(payload: Dict = Body(...)):
    return insert_and_return("payment", payload)


@app.get("/payments")
def list_payments():
    return list_collection("payment", {}, 200)


@app.post("/communications")
def create_communication(payload: Dict = Body(...)):
    return insert_and_return("communication", payload)


@app.get("/communications")
def list_communications():
    return list_collection("communication", {}, 200)


@app.post("/operations")
def create_operation(payload: Dict = Body(...)):
    return insert_and_return("operationevent", payload)


@app.get("/operations")
def list_operations():
    return list_collection("operationevent", {}, 500)


# Simple activity log for changes
@app.get("/logs")
def list_logs(limit: int = 200):
    try:
        logs = db["_changelog"].find().sort("created_at", -1).limit(limit)
        out = []
        for l in logs:
            l["id"] = str(l.pop("_id"))
            out.append(l)
        return out
    except Exception:
        return []


# Basic hook to log any creation; this can be extended in future
from fastapi.middleware import Middleware
from starlette.requests import Request
from starlette.responses import Response


@app.middleware("http")
async def change_logger(request: Request, call_next):
    response: Response
    response = await call_next(request)
    try:
        if request.method == "POST" and response.status_code in (200, 201):
            body = await request.body()
            db["_changelog"].insert_one({
                "path": request.url.path,
                "method": request.method,
                "status": response.status_code,
                "created_at": __import__("datetime").datetime.utcnow(),
            })
    except Exception:
        pass
    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
