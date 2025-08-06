"""
Slot entity and SlotStore.

A **slot** represents a bookable time window for a given provider.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Slot(BaseModel):
    """Represents an appointment slot for a provider."""

    id: UUID = Field(default_factory=uuid4, description="Primary key")
    provider_id: UUID
    start: datetime
    end: datetime
    is_available: bool = True

    def book(self) -> None:
        """Mark slot as no longer available."""
        self.is_available = False

    def cancel(self) -> None:
        """Mark slot as available again."""
        self.is_available = True


class SlotStore:
    _slots: Dict[UUID, Slot]
    """Singleton in-memory store for slots."""

    _instance: Optional["SlotStore"] = None

    def __new__(cls) -> "SlotStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._slots = {}
        return cls._instance

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------
    def add(self, slot: Slot) -> None:
        self._slots[slot.id] = slot

    def remove(self, slot_id: UUID) -> None:
        self._slots.pop(slot_id, None)

    def get(self, slot_id: UUID) -> Optional[Slot]:
        return self._slots.get(slot_id)

    def all(self) -> List[Slot]:
        return list(self._slots.values())

    def for_provider(self, provider_id: UUID) -> List[Slot]:
        return [s for s in self._slots.values() if s.provider_id == provider_id]

    def available(self) -> List[Slot]:
        return [s for s in self._slots.values() if s.is_available]

    def clear(self) -> None:
        self._slots.clear()


slot_store = SlotStore()
