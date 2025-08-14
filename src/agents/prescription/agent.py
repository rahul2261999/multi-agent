from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage

from src.agents.prescription.prompt import agent_prompt
from src.agents.prescription.tools import list_prescriptions, refill_prescription
from src.agents.prescription.state import PrescriptionAgentState
from src.core.llm_provider import LLMProvider, LLMModel
from src.libs.logger.manager import get_logger

logger = get_logger("prescription_agent")

all_tools = [
  list_prescriptions,
  refill_prescription
]

model = init_chat_model(
  model=LLMModel.GPT_4O_MINI.value,
  model_provider=LLMProvider.OPENAI.value,
  temperature=0.0,
)

def message_history_prompt(state: PrescriptionAgentState):
    system_prompt = agent_prompt(state)

    return [SystemMessage(content=system_prompt)] + state.messages

prescription_agent = create_react_agent(
    model=model.bind_tools(tools=all_tools, parallel_tool_calls=False),
    name="prescription_agent",
    tools=all_tools,
    prompt=message_history_prompt,
    state_schema=PrescriptionAgentState,
    checkpointer=True
)