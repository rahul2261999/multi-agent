from typing import Annotated, Literal
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from src.agents.supervisor.state import SupervisorState


@tool(
  "handoff_to_appointment_agent",
  description="Appointment agent is responsible for handling all appointment related queries (book, cancel, reschedule, list). It also able to anser the gnereal user queries related to appointment or treatment."
)
def handoff_to_appointment_agent(
  state: Annotated[SupervisorState, InjectedState], 
  tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command[Literal["appointment_agent"]]:
  
  return Command(
    goto="appointment_agent", 
    graph=Command.PARENT,
    update={
      **state.model_dump(),
      "messages": state.messages + [ToolMessage(
        content="successfully handoff to appointment agent", 
        tool_call_id=tool_call_id, 
      )],
    },
  )

@tool(
  "handoff_to_prescription_agent",
  description="Prescription agent is responsible for handling all prescription related queries (list, refill). It also able to anser the gnereal user queries related to prescription, disease, treatment etc."
)
def handoff_to_prescription_agent(
  state: Annotated[SupervisorState, InjectedState], 
  tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command[Literal["prescription_agent"]]:
  return Command(
    goto="prescription_agent",
    graph=Command.PARENT,
    update={
      **state.model_dump(),
      "messages": state.messages + [ToolMessage(
        content="successfully handoff to prescription agent", 
        tool_call_id=tool_call_id,
      )],
    },
  )