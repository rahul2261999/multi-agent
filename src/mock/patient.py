"""
Patient entity and in-memory PatientStore.

This module defines a simple Pydantic model that mimics what a row in a
`patients` table would look like and a corresponding
singleton-style store that behaves like an in-memory database table.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Patient(BaseModel):
    """Represents a patient record."""

    id: UUID = Field(default_factory=uuid4, description="Primary key")
    name: str
    age: int
    phone_number: str


class PatientStore:
    _patients: Dict[UUID, Patient]
    """Singleton in-memory store for `Patient` rows."""

    _instance: Optional["PatientStore"] = None

    def __new__(cls) -> "PatientStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # NOTE: initialise instance attributes directly after constructing
            cls._instance._patients = {}
        return cls._instance

    # ---------------------------------------------------------------------
    # CRUD helpers
    # ---------------------------------------------------------------------
    def add(self, patient: Patient) -> None:
        """Insert or update a patient row."""
        self._patients[patient.id] = patient

    def remove(self, patient_id: UUID) -> None:
        """Delete a patient row. Fails silently if the row does not exist."""
        self._patients.pop(patient_id, None)

    def get(self, patient_id: UUID) -> Optional[Patient]:
        """Retrieve a patient by its primary key."""
        return self._patients.get(patient_id)

    def all(self) -> List[Patient]:
        """Return **copies** of every row (to prevent accidental mutation)."""
        return list(self._patients.values())

    def clear(self) -> None:
        """Wipe the table (mostly useful in tests)."""
        self._patients.clear()


# A readily-importable singleton instance
patient_store = PatientStore()
