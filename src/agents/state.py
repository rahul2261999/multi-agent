from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from pydantic import BaseModel, Field

from src.mock.patient import Patient

class Configuration(TypedDict):
  """Configurable parameters for the agent.

  Set these when creating assistants OR when invoking the graph.
  See: https://langchain-ai.github.io/langgraph/cloud/how-tos/configuration_cloud/
  """

  recursion_limit: int
  thread_id: str


class MainState(BaseModel):
  remaining_steps: int = Field(default=10)
  messages: Annotated[list[AnyMessage], add_messages]
  patient: Patient
