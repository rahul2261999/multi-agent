import asyncio
from pprint import pformat
from uuid import UUID, uuid4
from typing import Any, Callable
import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from langgraph.graph.state import RunnableConfig
from langchain_core.messages import AIMessageChunk, HumanMessage

from src.agents.main_agent import build_main_agent_with_checkpointer
from src.libs.logger.manager import get_logger
from src.libs.redis.redis import get_checkpoint_saver
from src.mock.patient import patient_store
from src.agents.state import MainState


logger = get_logger("chat_api")
checkpointer = get_checkpoint_saver()
main_agent = build_main_agent_with_checkpointer(checkpointer)


chat_router = APIRouter(tags=["Chat"])

async def generate_response(
    text: str, sessionId: str, stream_callback: Callable[[str, bool], Any]
):
    """Stream an LLM response token-by-token via the provided callback."""

    try:
        config: RunnableConfig = {
            "configurable": {
                "thread_id": sessionId,
                "recursion_limit": 10,
            }
        }

        get_config = await checkpointer.aget(config)
        patient = patient_store.get(UUID("4349d0aa-7d30-44fb-99f9-e7c0e5752fc0"))

        if get_config is None:
            logger.info(f"No config found for thread {sessionId}, creating new state")

            if patient is None:
                raise ValueError("Patient not found")

            initial_state = MainState(
                messages=[HumanMessage(content=text)],
                remaining_steps=10,
                patient=patient,
            )

            logger.info(f"Initial state:\n {initial_state}")

            response = ""

            async for token in main_agent.astream(
                initial_state, config=config, stream_mode="messages", subgraphs=True
            ):
                logger.debug(f"Token:\n {pformat(token, indent=2)}")

                if isinstance(token, tuple):
                    _, data = token
                    messagechunk = data[0] if isinstance(data, tuple) else data
                    if isinstance(messagechunk, AIMessageChunk) and isinstance(
                        messagechunk.content, str
                    ):
                        response += messagechunk.content
                        await stream_callback(messagechunk.content, False)

            logger.info(f"Full response generated {response}")
            await stream_callback("", True)

        else:
            logger.info(f"Config found for thread {sessionId}, resuming state")

            existing_state = await main_agent.aget_state(config)
            logger.debug(f"Existing state:\n {existing_state}")

            message_delta: MainState = MainState(**existing_state.values)
            message_delta.messages.append(HumanMessage(content=text))

            response = ""

            async for token in main_agent.astream(
                message_delta,
                config=config,
                stream_mode="messages",
                subgraphs=True,
            ):
                logger.debug(f"Token:\n {pformat(token, indent=2)}")

                if isinstance(token, tuple):
                    _, data = token
                    messagechunk = data[0] if isinstance(data, tuple) else data
                    if isinstance(messagechunk, AIMessageChunk) and isinstance(
                        messagechunk.content, str
                    ):
                        response += messagechunk.content
                        await stream_callback(messagechunk.content, False)

            logger.info(f"Full response generated {response}")
            await stream_callback("", True)

    except Exception as e:
        await stream_callback("Something went wrong, please try again later", False)
        await stream_callback("", True)
        logger.error(f"Error generating response: {e}")



@chat_router.websocket("/websocket")
async def chat_websocket(websocket: WebSocket) -> None:
    """WebSocket endpoint for chat streaming.

    Contract mirrors the voice endpoint:
    - Resolves `x-session-id` or `sessionId`, generates if missing, emits `session.init`
    - Accepts `user_message_event` with `{message: {id, role: 'user', content}}`
    - Streams tokens via `ai_message_chunk` and finishes with `ai_message_end`
    - Supports `ping`/`heartbeat` → `pong`
    """

    # Resolve session id prior to acceptance
    session_id: str | None = (
        websocket.headers.get("x-session-id") or websocket.query_params.get("sessionId")
    )
    is_new_session = False
    if not session_id:
        session_id = str(uuid4())
        is_new_session = True

    await websocket.accept()
    await websocket.send_json(
        {"type": "session.init", "sessionId": session_id, "isNew": is_new_session}
    )

    try:
        while True:
            incoming_text = await websocket.receive_text()
            try:
                payload: dict[str, Any] = json.loads(incoming_text)
            except json.JSONDecodeError:
                payload = {
                    "type": "user_message_event",
                    "message": {
                        "id": str(uuid4()),
                        "role": "user",
                        "content": incoming_text,
                    },
                }

            event_type = payload.get("type")

            # Heartbeat handling
            if event_type in ("ping", "heartbeat"):
                await websocket.send_json({"type": "pong"})
                continue

            if event_type != "user_message_event":
                await websocket.send_json(
                    {
                        "type": "error",
                        "error": "Unsupported event type",
                        "detail": event_type,
                    }
                )
                continue

            message = payload.get("message") or {}
            role = message.get("role")
            content = message.get("content")
            if role != "user" or not isinstance(content, str) or not content.strip():
                await websocket.send_json(
                    {"type": "error", "error": "Invalid message payload"}
                )
                continue

            ai_message_id = str(uuid4())

            async def stream_callback(chunk: str, is_end: bool) -> None:
                if is_end:
                    await websocket.send_json(
                        {"type": "ai_message_end", "messageId": ai_message_id}
                    )
                else:
                    await websocket.send_json(
                        {
                            "type": "ai_message_chunk",
                            "messageId": ai_message_id,
                            "delta": chunk,
                        }
                    )

            await generate_response(content, session_id, stream_callback)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")




