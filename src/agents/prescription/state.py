from typing import Annotated, Optional
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

from src.mock.patient import Patient
from src.mock.prescription import Prescription


class PrescriptionAgentState(BaseModel):
  remaining_steps: int = Field(default=10)
  messages: Annotated[list[AnyMessage], add_messages]

  patient: Patient

  available_prescriptions: list[Prescription] = Field(default_factory=list)
  selected_prescription: Optional[Prescription] = Field(default=None)