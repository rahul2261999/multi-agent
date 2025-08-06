from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model

from src.agents.appointment.state import AppointmentAgentState
from src.core.llm_provider import LLMProvider, LLMModel
from src.libs.logger.manager import get_logger
from src.agents.appointment.prompt import agent_prompt
from src.agents.appointment.tools import (
    list_appointments,
    book_appointment,
    reschedule_appointment,
    cancel_appointment,
    confirm_appointment,
    get_providers,
    get_available_slots,
    get_slot_for_reschedule,
)

logger = get_logger("appointment_agent")

model = init_chat_model(
    model=LLMModel.GPT_4O_MINI.value,
    model_provider=LLMProvider.AZURE.value,
    temperature=0.0,
)

all_tools = [
    list_appointments,
    get_providers,
    get_available_slots,
    book_appointment,
    get_slot_for_reschedule,
    reschedule_appointment,
    cancel_appointment,
    confirm_appointment,
]


def message_history_prompt(state: AppointmentAgentState):
    system_prompt = agent_prompt(state)

    return [SystemMessage(content=system_prompt)] + state.messages


appointment_agent = create_react_agent(
    model=model.bind_tools(tools=all_tools, parallel_tool_calls=False),
    name="appointment_agent",
    tools=all_tools,
    prompt=message_history_prompt,
    state_schema=AppointmentAgentState,
)
