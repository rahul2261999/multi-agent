"""
Prescription entity and PrescriptionStore.

A **prescription** represents medication information for a patient.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"


class Prescription(BaseModel):
    """Represents a prescription row."""

    id: UUID = Field(default_factory=uuid4, description="Primary key")
    patient_id: UUID
    name: str
    description: str
    last_refill_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delivery_status: DeliveryStatus = Field(default=DeliveryStatus.PENDING)
    next_refill_date: Optional[datetime] = None


class PrescriptionStore:
    """Singleton in-memory store for `Prescription` rows."""

    _prescriptions: Dict[UUID, Prescription]
    _instance: Optional["PrescriptionStore"] = None

    def __new__(cls) -> "PrescriptionStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._prescriptions = {}
        return cls._instance

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------
    def add(self, prescription: Prescription) -> None:
        self._prescriptions[prescription.id] = prescription

    def remove(self, prescription_id: UUID) -> None:
        self._prescriptions.pop(prescription_id, None)

    def get(self, prescription_id: UUID) -> Optional[Prescription]:
        return self._prescriptions.get(prescription_id)

    def all(self) -> List[Prescription]:
        return list(self._prescriptions.values())

    def clear(self) -> None:
        self._prescriptions.clear()

    def get_by_patient_id(self, patient_id: UUID) -> List[Prescription]:
        return [prescription for prescription in self._prescriptions.values() if prescription.patient_id == patient_id]

    def update(self, prescription: Prescription) -> None:
        self._prescriptions[prescription.id] = prescription


prescription_store = PrescriptionStore()
