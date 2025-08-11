from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from src.core.llm_provider import LLMProvider, LLMModel

from src.libs.logger.manager import get_logger
from src.agents.supervisor.state import SupervisorState
from src.agents.supervisor.tools import handoff_to_appointment_agent, handoff_to_prescription_agent

logger = get_logger("supervisor_agent")

supervisor_agent = create_react_agent(
  model=init_chat_model(
    model=LLMModel.GPT_4O_MINI.value,
    model_provider=LLMProvider.AZURE.value,
    temperature=0.0,
  ),
  name="supervisor_agent",
  tools=[
    handoff_to_appointment_agent,
    handoff_to_prescription_agent
  ],
  state_schema=SupervisorState,
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
)