"""Mock in-memory database layer.

Importing this package will automatically populate mock data so that
all `*_store` singletons come pre-filled with patients, providers and
slots relative to the current date.

Example
-------
>>> from src.mock import patient_store, provider_store, slot_store
>>> len(patient_store.all())
10

If you want to start with a clean slate in tests, call `clear()` on the
individual stores or simply `importlib.reload(src.mock.mock_data)`.
"""
from __future__ import annotations

# Re-export entities and stores for convenience
from .patient import Patient, patient_store
from .provider import Provider, provider_store
from .slot import Slot, slot_store
from .appointment import Appointment, appointment_store
from .prescription import Prescription, prescription_store

# Populate with deterministic mock data relative to *today*
from . import mock_data  # noqa: F401 – triggers side-effects
