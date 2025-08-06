from typing import Annotated, Optional
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.mock.patient import Patient
from src.mock.provider import Provider
from src.mock.slot import Slot


class AppointmentAgentState(BaseModel): 
  remaining_steps: int = Field(default=10)
  messages: Annotated[list[AnyMessage], add_messages]

  patient: Patient

  providers: list[Provider] = Field(default_factory=list)
  selected_provider: Optional[Provider] = Field(default=None)
  
  available_slots: list[Slot] = Field(default_factory=list)
  selected_slot: Optional[Slot] = Field(default=None)
