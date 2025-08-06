"""
Provider entity and in-memory ProviderStore.

A **provider** is someone who offers appointments (e.g. a doctor).
The store behaves like an in-memory table.
"""
from __future__ import annotations

from typing import Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Provider(BaseModel):
    """Represents a provider (e.g. doctor) row."""

    id: UUID = Field(default_factory=uuid4, description="Primary key")
    name: str
    specialization: str


class ProviderStore:
    _providers: Dict[UUID, Provider]
    """Singleton in-memory store for Provider rows."""

    _instance: Optional["ProviderStore"] = None

    def __new__(cls) -> "ProviderStore":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._providers = {}
        return cls._instance

    # ------------------------------------------------------------------
    # CRUD helpers
    # ------------------------------------------------------------------
    def add(self, provider: Provider) -> None:
        self._providers[provider.id] = provider

    def remove(self, provider_id: UUID) -> None:
        self._providers.pop(provider_id, None)

    def get(self, provider_id: UUID) -> Optional[Provider]:
        return self._providers.get(provider_id)

    def all(self) -> List[Provider]:
        return list(self._providers.values())

    def clear(self) -> None:
        self._providers.clear()


provider_store = ProviderStore()
