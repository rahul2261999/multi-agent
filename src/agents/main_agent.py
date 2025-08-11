from ctypes import cast
from langgraph.graph import END, START, StateGraph

from src.agents.state import MainState
from src.agents.supervisor.agent import supervisor_agent
from src.agents.appointment.agent import appointment_agent
from src.agents.prescription.agent import prescription_agent




# def supervisor_node(state: MainState):

#   response = supervisor_agent.invoke(input={
#     "messages": state.messages,
#     "remaining_steps": state.remaining_steps,
#   })

#   return {
#     "messages": response["messages"],
#     "remaining_steps": response["remaining_steps"],
#   }

# def appointment_node(state: MainState):
#   response = appointment_agent.invoke(input={
#     "messages": state.messages,
#     "patient": state.patient,
#     "remaining_steps": state.remaining_steps,
#   })
  
#   return {
#     "messages": response["messages"],
#     "remaining_steps": response["remaining_steps"],
#   }

# def prescription_node(state: MainState):
#   response = prescription_agent.invoke(input={
#     "messages": state.messages,
#     "patient": state.patient,
#     "remaining_steps": state.remaining_steps,
#   })
  
#   return {
#     "messages": response["messages"],
#     "remaining_steps": response["remaining_steps"],
#   }



state_graph = StateGraph(state_schema=MainState)

state_graph.add_node("supervisor", supervisor_agent, destinations=tuple(["appointment_agent", "prescription_agent", END]))
state_graph.add_node("appointment_agent", appointment_agent)
state_graph.add_node("prescription_agent", prescription_agent)

state_graph.add_edge(START, "supervisor")
state_graph.add_edge("appointment_agent", END)
state_graph.add_edge("prescription_agent", END)

main_agent = state_graph.compile(name="main_agent")