from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model

from src.core.llm_provider import LLMProvider, LLMModel
from src.libs.logger.manager import get_logger

logger = get_logger("appointment_agent")

appointment_agent = create_react_agent(
    model=init_chat_model(
      model=LLMModel.GPT_4O_MINI.value,
      model_provider=LLMProvider.AZURE.value,
      temperature=0.0,
    ),
    name="appointment_agent",
    tools=[],
    prompt="""
        You are an appointment agent.
        You are given a user's request to book an appointment.
        You need to book an appointment for the user.
        """
)