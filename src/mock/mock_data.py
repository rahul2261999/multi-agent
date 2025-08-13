"""
Utility module that pre-populates all singleton stores with deterministic but
*date-aware* data.

Running the application on any day will generate slots relative to the current
system date so that the mock data always looks fresh.
"""
from __future__ import annotations

from datetime import datetime, timedelta, time, timezone
from uuid import UUID


from src.libs.logger.manager import get_logger

from .patient import Patient, patient_store
from .provider import Provider, provider_store
from .slot import Slot, slot_store
from .prescription import Prescription, prescription_store, DeliveryStatus

logger = get_logger("mock_data")

# ---------------------------------------------------------------------------
# Patients – static dataset --------------------------------------------------
PATIENTS_DATA = [
    {"id": "4349d0aa-7d30-44fb-99f9-e7c0e5752fc0", "name": "Alice",  "age": 41, "phone_number": "+19876543210"},
    {"id": "9d9619a9-512a-4644-9891-4fc452b89bfe", "name": "Bob",    "age": 77, "phone_number": "+19876543211"},
    {"id": "95e76dd7-3b12-4b79-863d-9c8534c3af83", "name": "Charlie","age": 45, "phone_number": "+19876543216"},
    {"id": "64ea98c9-0106-409d-8597-45a75d766859", "name": "Daisy",  "age": 64, "phone_number": "+19876543212"},
    {"id": "5b8aeacf-7302-4c48-af1f-797c3f659c2d", "name": "Edward", "age": 42, "phone_number": "+19876543217"},
    {"id": "be48648b-33b1-4c5c-af7d-5516480c8a3f", "name": "Fay",    "age": 76, "phone_number": "+19876543214"},
    {"id": "7e545e38-ec97-4795-8938-3f1d6efd8370", "name": "Grace",  "age": 32, "phone_number": "+19876543211"},
    {"id": "62663735-f7d8-4cd8-af93-124521aa7b49", "name": "Henry",  "age": 55, "phone_number": "+19876543217"},
    {"id": "d11b46c1-dcd6-4572-944f-0458a489eab6", "name": "Isabel", "age": 62, "phone_number": "+19876543214"},
    {"id": "f389991b-7e81-4884-a3fc-3065d08d3c6d", "name": "Jack",   "age": 47, "phone_number": "+19876543212"},
]

for p in PATIENTS_DATA:
    patient = Patient(id=UUID(p["id"]), name=p["name"], age=p["age"], phone_number=p["phone_number"])
    patient_store.add(patient)
    # logger.success(f"Added patient: {patient.model_dump_json(indent=2)}")

# ---------------------------------------------------------------------------
# Providers – static dataset -------------------------------------------------
PROVIDERS_DATA = [
    {"id": "ad253a2e-a8c8-4863-8cb8-2fa0b9e28e79", "name": "Dr. Smith",   "specialization": "Cardiology"},
    {"id": "e5bb9aef-a484-4f9d-9658-c16816600ac7", "name": "Dr. Johnson", "specialization": "Dermatology"},
    {"id": "028d486e-5ae0-4662-9091-e4973e763fe7", "name": "Dr. Brown",   "specialization": "Neurology"},
]

for p in PROVIDERS_DATA:
    provider = Provider(id=UUID(p["id"]), name=p["name"], specialization=p["specialization"])
    provider_store.add(provider)
    # logger.success(f"Added provider: {provider.model_dump()}")

# ---------------------------------------------------------------------------
# Slots – generated for *each* provider
# ---------------------------------------------------------------------------

def _generate_slots_for_provider(provider: Provider, *, days_ahead: int = 15) -> None:
    """Generate **one-hour** slots for working hours 09:00-12:00 and 14:00-17:00 in **IST**
    (UTC+05:30) for the next *days_ahead* days. All stored times are UTC."""

    IST = timezone(timedelta(hours=5, minutes=30), name="IST")
    today_ist = datetime.now(IST).date()

    for day_offset in range(days_ahead):
        date_ist = today_ist + timedelta(days=day_offset)
        # Working hours (IST): 09-12 and 14-17
        for hour in list(range(9, 12)) + list(range(14, 17)):
            # Create datetime in IST, then convert to UTC for storage
            start_dt_ist = datetime.combine(date_ist, time(hour, 0, tzinfo=IST))
            end_dt_ist = start_dt_ist + timedelta(hours=1)

            start_dt_utc = start_dt_ist.astimezone(timezone.utc)
            end_dt_utc = end_dt_ist.astimezone(timezone.utc)

            new_slot = Slot(provider_id=provider.id, start=start_dt_utc, end=end_dt_utc)
            slot_store.add(new_slot)
            # logger.success(f"Added slot: {new_slot.model_dump_json(indent=2)}")
            # logger.success(f"utc slot start: {new_slot.start.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}, utc slot end: {new_slot.end.astimezone(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}")
            # logger.success(f"slot start: {new_slot.start.astimezone(IST).strftime('%Y-%m-%d %H:%M:%S')}, slot end: {new_slot.end.astimezone(IST).strftime('%Y-%m-%d %H:%M:%S')}")
            # logger.info("\n")

for provider in provider_store.all():
    _generate_slots_for_provider(provider)

# ---------------------------------------------------------------------------
# Prescriptions – static dataset --------------------------------------------
PRESCRIPTIONS_DATA = [
    {"id": "e3b34884-04e8-4c7b-b5ed-e77afb74b349", "patient_id": "4349d0aa-7d30-44fb-99f9-e7c0e5752fc0", "name": "Metformin",   "description": "Diabetes medication",     "last_refill_date": datetime(2025, 6, 5, 19, 24, 13, 85577, tzinfo=timezone.utc),  "delivery_status": DeliveryStatus.SHIPPED},
    {"id": "f9559ce8-fe7f-4ad2-aea4-a0e927d26bfa", "patient_id": "9d9619a9-512a-4644-9891-4fc452b89bfe", "name": "Omeprazole",  "description": "Acid reflux relief",     "last_refill_date": datetime(2025, 6, 13, 19, 24, 13, 86251, tzinfo=timezone.utc), "delivery_status": DeliveryStatus.PENDING},
    {"id": "7c0bfbf6-5f07-44a2-94aa-56c17b83aeaa", "patient_id": "95e76dd7-3b12-4b79-863d-9c8534c3af83", "name": "Omeprazole",  "description": "Acid reflux relief",     "last_refill_date": datetime(2025, 7, 10, 19, 24, 13, 86526, tzinfo=timezone.utc), "delivery_status": DeliveryStatus.SHIPPED},
    {"id": "cbd156ba-a491-4fc2-953f-a6d0e1ff80a5", "patient_id": "64ea98c9-0106-409d-8597-45a75d766859", "name": "Atorvastatin","description": "Cholesterol medication", "last_refill_date": datetime(2025, 6, 18, 19, 24, 13, 89502, tzinfo=timezone.utc), "delivery_status": DeliveryStatus.DELIVERED},
    {"id": "8da81c50-a1ec-49da-8588-df801bff659e", "patient_id": "5b8aeacf-7302-4c48-af1f-797c3f659c2d", "name": "Metformin",   "description": "Diabetes medication",     "last_refill_date": datetime(2025, 6, 29, 19, 24, 13, 89898, tzinfo=timezone.utc), "delivery_status": DeliveryStatus.PENDING},
    {"id": "196b1570-fd98-42f7-b97e-959b6ab06959", "patient_id": "be48648b-33b1-4c5c-af7d-5516480c8a3f", "name": "Atorvastatin","description": "Cholesterol medication", "last_refill_date": datetime(2025, 5, 13, 19, 24, 13, 90137, tzinfo=timezone.utc), "delivery_status": DeliveryStatus.SHIPPED},
    {"id": "1e65d85c-2e2e-481b-98a4-817820c1d5ee", "patient_id": "7e545e38-ec97-4795-8938-3f1d6efd8370", "name": "Omeprazole",  "description": "Acid reflux relief",     "last_refill_date": datetime(2025, 7, 13, 19, 24, 13, 90358, tzinfo=timezone.utc), "delivery_status": DeliveryStatus.PENDING},
    {"id": "4a22bc9d-0d01-434b-9425-cf9fd3374583", "patient_id": "62663735-f7d8-4cd8-af93-124521aa7b49", "name": "Lisinopril",  "description": "Blood pressure medication", "last_refill_date": datetime(2025, 5, 8, 19, 24, 13, 90974, tzinfo=timezone.utc), "delivery_status": DeliveryStatus.DELIVERED},
    {"id": "df952b8a-66f3-4550-8602-609157a2f77f", "patient_id": "d11b46c1-dcd6-4572-944f-0458a489eab6", "name": "Omeprazole",  "description": "Acid reflux relief",     "last_refill_date": datetime(2025, 5, 23, 19, 24, 13, 91344, tzinfo=timezone.utc), "delivery_status": DeliveryStatus.DELIVERED},
    {"id": "2b3cb67d-8b38-4a02-b36b-322ce56ba37e", "patient_id": "f389991b-7e81-4884-a3fc-3065d08d3c6d", "name": "Metformin",   "description": "Diabetes medication",     "last_refill_date": datetime(2025, 5, 21, 19, 24, 13, 91786, tzinfo=timezone.utc), "delivery_status": DeliveryStatus.SHIPPED},
]

for p in PRESCRIPTIONS_DATA:
    prescription = Prescription(
        id=UUID(p["id"]),
        patient_id=UUID(p["patient_id"]),
        name=p["name"],
        description=p["description"],
        last_refill_date=p["last_refill_date"],
        delivery_status=p["delivery_status"],
        next_refill_date=None,
    )
    prescription_store.add(prescription)
    # logger.success(f"Added prescription: {prescription.model_dump()}")
