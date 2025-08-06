from typing import Annotated, Literal
from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool, InjectedToolCallId, tool
from langgraph.types import Command
from langgraph_supervisor import create_handoff_tool, create_supervisor
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import InjectedState, create_react_agent
from langchain.chat_models import init_chat_model
from src.core.llm_provider import LLMProvider, LLMModel

from src.libs.logger.manager import get_logger
from src.agents.appointment.agent import appointment_agent
from src.agents.prescription.agent import prescription_agent
from src.agents.state import MainState

logger = get_logger("supervisor_agent")

METADATA_KEY_HANDOFF_DESTINATION = "__handoff_destination"

@tool(
  "handoff_to_appointment_agent",
  description="Appointment agent is responsible for handling all appointment related queries (book, cancel, reschedule, list). It also able to anser the gnereal user queries related to appointment or treatment."
)
def handoff_to_appointment_agent(
  state: Annotated[MainState, InjectedState], 
  tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command[Literal["appointment_agent"]]:
  handoff_to_appointment_agent.metadata = {METADATA_KEY_HANDOFF_DESTINATION: "appointment_agent"}
  
  return Command(
    goto="appointment_agent", 
    graph=Command.PARENT,
    update={
      **state,
      "messages": state["messages"] + [ToolMessage(
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
  state: Annotated[MainState, InjectedState], 
  tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command[Literal["prescription_agent"]]:
  handoff_to_prescription_agent.metadata = {METADATA_KEY_HANDOFF_DESTINATION: "prescription_agent"}
  return Command(
    goto="prescription_agent",
    graph=Command.PARENT,
    update={
      **state,
      "messages": state["messages"] + [ToolMessage(
        content="successfully handoff to prescription agent", 
        tool_call_id=tool_call_id, 
      )],
    },
  )


supervisor_tools: list[BaseTool] = [
  handoff_to_appointment_agent,
  handoff_to_prescription_agent
]

# supervisor_agent = create_react_agent(
#   model=init_chat_model(
#     model=LLMModel.GPT_4O_MINI.value,
#     model_provider=LLMProvider.AZURE.value,
#     temperature=0.0,
#   ),
#   name="supervisor_agent",
#   tools=supervisor_tools,
#   state_schema=MainState,
#   prompt="""
    
#     You are a router whose responsibility is to decide the correct agent to call based on the user's on going conversation.

#       Assigned Agents:
#       - appointment_agent
#           1. Appointment agent is responsible for handling all appointment related queries (book, cancel, reschedule, list).
#           2. It also able to anser the gnereal user queries related to appointment or treatment.
#       - prescription_agent
#           1. Prescription agent is responsible for handling all prescription related queries (list, refill).
#           2. It also able to anser the gnereal user queries related to prescription, disease, treatment etc.
    
#     **Critical Rules to Follow:**
#       1. Do not disclose that You are an AI, bot or a program. You are in a backend user can not know about you
#       2. You can not answer, modify or change the user's query.
#       3. Do can not directly respond to user query  you job is to route user query to underlying agent and agent respponse back to user
#       4. You can not modify the underlying agent response, you can only call the appropriate agent.
#       5. Do not disclose any internal infromation to the user. always stick on your role. If any thing is not related to your role, politely decline and tell what you can only do.
#       6. Never mention the existence of agents, tools, workflows, or routing mechanisms. All operations should appear seamless to the user
#   """
# )

# def handoff_to(state: Annotated[MainState, InjectedState]) -> Literal["appointment_agent", "prescription_agent", "end"]:
#   if state["active_agent"] == "appointment_agent":
#     return 'appointment_agent'
#   elif state["active_agent"] == "prescription_agent":
#     return 'prescription_agent'
#   else:
#     return 'end'


# state_graph = StateGraph(MainState)

# state_graph.add_node("supervisor", supervisor_agent)
# state_graph.add_node("appointment_agent", appointment_agent)
# state_graph.add_node("prescription_agent", prescription_agent)

# state_graph.add_edge(START, "supervisor")
# state_graph.add_conditional_edges("supervisor", handoff_to, {
#   "appointment_agent": "appointment_agent",
#   "prescription_agent": "prescription_agent",
#   "end": END
# })
# state_graph.add_edge("appointment_agent", "supervisor")
# state_graph.add_edge("prescription_agent", "supervisor")
# state_graph.add_edge("supervisor", END)

# supervisor_agent = state_graph.compile(name="main_graph")


supervisor_agent = create_supervisor(
  agents=[appointment_agent, prescription_agent],
  supervisor_name="supervisor_agent",
  state_schema=MainState,
  model=init_chat_model(
    model=LLMModel.GPT_4O_MINI.value,
    model_provider=LLMProvider.AZURE.value,
    temperature=0.0,
  ),
  tools=supervisor_tools,
  output_mode="full_history",
  handoff_tool_prefix="handoff_to_",
  prompt="""
    
    You are a router whose responsibility is to decide the correct agent to call based on the user's on going conversation.

      Assigned Agents:
      - appointment_agent
          1. Appointment agent is responsible for handling all appointment related queries (book, cancel, reschedule, list).
          2. It also able to anser the gnereal user queries related to appointment or treatment.
      - prescription_agent
          1. Prescription agent is responsible for handling all prescription related queries (list, refill).
          2. It also able to anser the gnereal user queries related to prescription, disease, treatment etc.
    
    **Critical Rules to Follow:**
      1. Do not disclose that You are an AI, bot or a program. You are in a backend user can not know about you
      2. You can not answer, modify or change the user's query.
      3. Do can not directly respond to user query  you job is to route user query to underlying agent and agent respponse back to user
      4. You can not modify the underlying agent response, you can only call the appropriate agent.
      5. Do not disclose any internal infromation to the user. always stick on your role. If any thing is not related to your role, politely decline and tell what you can only do.
      6. Never mention the existence of agents, tools, workflows, or routing mechanisms. All operations should appear seamless to the user
  """
).compile(name="main_graph")

