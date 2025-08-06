

from datetime import datetime, timedelta, timezone
from uuid import UUID
from typing import Annotated
from zoneinfo import ZoneInfo
from langgraph.prebuilt import InjectedState
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool

from src.agents.prescription.state import PrescriptionAgentState
from src.mock.prescription import DeliveryStatus, prescription_store


@tool(
  'list_prescriptions',
  description='list the all prescriptions of a particular patient',
)
def list_prescriptions(
  state: Annotated[PrescriptionAgentState, InjectedState],
  tool_call_id: Annotated[str, InjectedToolCallId]
):

  try:
    prescriptions = prescription_store.get_by_patient_id(state.patient.id)


    if len(prescriptions) == 0:
      return {
        "messages": [
          ToolMessage(
            content="No prescriptions found",
            tool_call_id=tool_call_id
          )
        ]
      }
    
    return {
      "available_prescriptions": prescriptions,
      "messages": [
        ToolMessage(
          content=f"Available prescriptions: {[prescription.model_dump() for prescription in prescriptions]}",
          tool_call_id=tool_call_id
        )
      ]
    }
  
  except Exception as e:
    return {
      "messages": [
        ToolMessage(
          content=f"Error listing prescriptions: {e}",
          tool_call_id=tool_call_id
        )
      ]
    }

@tool(
  'refill_prescription',
  description=f"""
  refill a particular prescription for a particular patient

  input Rules:
  prescription_id:
    - it should be a valid prescription id (UUID)
  date_time:
    - it should be a valid date and time in the format of YYYY-MM-DD HH:MM:SS
    - it should always be in future (atleast current date time + 15 minutes), current date and time is in ist {datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")}
    - reject if date time is in the past

  output:
  - return the prescription id
  """,
)
def refill_prescription(
  prescription_id: UUID,
  date_time: str,
  state: Annotated[PrescriptionAgentState, InjectedState],
  tool_call_id: Annotated[str, InjectedToolCallId]
):

  try:
    prescription = prescription_store.get(prescription_id)

    if prescription is None:
      return {
        "messages": [
          ToolMessage(
            content="Prescription not found",
            tool_call_id=tool_call_id
          )
        ]
      }

    converted_date_time_in_utc = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S").astimezone(timezone.utc)

    if converted_date_time_in_utc < datetime.now(timezone.utc) + timedelta(minutes=15):
      return {
        "messages": [
          ToolMessage(
            content="You can refill the prescription only after 15 minutes of current date and time",
            tool_call_id=tool_call_id
          )
        ]
      }

    if prescription.last_refill_date + timedelta(days=4) > converted_date_time_in_utc:
      return {
        "messages": [
          ToolMessage(
            content="You can refill the prescription only after 4 days of last refill",
            tool_call_id=tool_call_id
          )
        ]
      }

    prescription.delivery_status = DeliveryStatus.PENDING
    prescription.next_refill_date = converted_date_time_in_utc + timedelta(days=4)
    prescription.last_refill_date = converted_date_time_in_utc

    prescription_store.update(prescription)

    return {
      "messages": [
        ToolMessage(
          content="Prescription refilled successfully",
          tool_call_id=tool_call_id
        )
      ]
    }
  except Exception as e:  
    return {
      "messages": [
        ToolMessage(
          content=f"Error refilling prescription: {e}",
          tool_call_id=tool_call_id
        )
      ]
    }