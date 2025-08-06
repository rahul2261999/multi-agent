from typing import Annotated, Optional, TypedDict 
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.mock.patient import Patient
from src.mock.prescription import Prescription
from src.mock.provider import Provider
from src.mock.slot import Slot


class MainState(TypedDict):
  remaining_steps: int
  
  messages: Annotated[list[AnyMessage], add_messages]
  
  patient: Patient

  providers: list[Provider]
  selected_provider: Optional[Provider]
  
  available_slots: list[Slot]
  selected_slot: Optional[Slot]


  available_prescriptions: list[Prescription]
  selected_prescription: Optional[Prescription]