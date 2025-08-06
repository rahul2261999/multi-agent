"""
Appointment entity and AppointmentStore.

An **appointment** is created when a patient books a slot.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from enum import Enum


class AppointmentStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Appointment(BaseModel):
    """Represents a booked appointment."""

    id: UUID = Field(default_factory=uuid4, description="Primary key")
    patient_id: UUID
    slot_id: UUID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: AppointmentStatus = Field(default=AppointmentStatus.CONFIRMED)


class AppointmentStore:
    _appointments: Dict[UUID, Appointment]
    """Singleton in-memory store for Appointment rows."""

    _instance: Optional["AppointmentStore"] = None

    def __new__(cls) -> "AppointmentStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialise instance attribute
            cls._instance._appointments = {}
        return cls._instance

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------
    def add(self, appointment: Appointment) -> None:
        self._appointments[appointment.id] = appointment

    def update(self, appointment: Appointment) -> None:
        self._appointments[appointment.id] = appointment

    def remove(self, appointment_id: UUID) -> None:
        self._appointments.pop(appointment_id, None)

    def get(self, appointment_id: UUID) -> Optional[Appointment]:
        return self._appointments.get(appointment_id)

    def all(self) -> List[Appointment]:
        return list(self._appointments.values())

    def get_by_patient_id(self, patient_id: UUID) -> List[Appointment]:
        return [appointment for appointment in self._appointments.values() if appointment.patient_id == patient_id]

    def clear(self) -> None:
        self._appointments.clear()


appointment_store = AppointmentStore()
