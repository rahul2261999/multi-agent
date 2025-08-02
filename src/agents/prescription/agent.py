from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model

from src.core.llm_provider import LLMProvider, LLMModel
from src.libs.logger.manager import get_logger

logger = get_logger("prescription_agent")

prescription_agent = create_react_agent(
    model=init_chat_model(
      model=LLMModel.GPT_4O.value,
      model_provider=LLMProvider.AZURE.value,
      temperature=0.0,
    ),
    name="prescription_agent",
    tools=[],
    prompt="""
        You are a prescription agent.
        You are given a user's request to get a prescription.
        You need to get a prescription for the user.
        """
)