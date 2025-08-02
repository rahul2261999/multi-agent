from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from src.core.llm_provider import LLMProvider, LLMModel

from src.libs.logger.manager import get_logger
from src.agents.appointment.agent import appointment_agent
from src.agents.prescription.agent import prescription_agent

logger = get_logger("supervisor_agent")

supervisor_agent = create_supervisor(
    model=init_chat_model(
      model=LLMModel.GPT_4O_MINI.value,
      model_provider=LLMProvider.AZURE.value,
      temperature=0.0,
    ),
    agents=[appointment_agent, prescription_agent],

    prompt="""
        You are a supervisor agent.
        You are given a user's request.
        You need to decide which agent to use to handle the request.
        """
).compile(name="supervisor_agent")