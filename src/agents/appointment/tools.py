from datetime import datetime, timezone
from typing import Annotated
from uuid import UUID
from zoneinfo import ZoneInfo
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.prebuilt import InjectedState
from langgraph.types import Command

from src.agents.appointment.state import AppointmentAgentState
from src.libs.logger.manager import get_logger
from src.mock.appointment import Appointment, AppointmentStatus, appointment_store
from src.mock.provider import provider_store
from src.mock.slot import Slot, slot_store

logger = get_logger("appointment_agent")


@tool(
    "list_appointments",
    description="list the all appoinments of a particular patient",
)
def list_appointments(
    state: Annotated[AppointmentAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    try:
        if state.patient is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Patient not found", tool_call_id=tool_call_id
                        )
                    ]
                },
            )

        appointments = appointment_store.get_by_patient_id(state.patient.id)

        if len(appointments) == 0:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="No appointments found", tool_call_id=tool_call_id
                        )
                    ]
                },
            )

        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Appointments: {[appointment.model_dump() for appointment in appointments]}",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )

    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error listing appointments: {e}",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )


@tool(
    "get_providers",
    description="get the all providers",
)
def get_providers(
    state: Annotated[AppointmentAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    try:
        available_providers = provider_store.all()
        return Command(
            update={
                "providers": available_providers,
                "messages": [
                    ToolMessage(
                        content=f"Available providers: {[provider.model_dump() for provider in available_providers]}",
                        tool_call_id=tool_call_id,
                    )
                ],
            },
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error getting providers: {e}",
                        tool_call_id=tool_call_id,
                    )
                ],
            },
        )


@tool(
    "get_available_slots",
    description=f"""
  'get the available slots for a particular date and time for a particular provider.
 
  input Rules:
  provider_id:
    - it should be a valid provider id
     
  date_time:
    - it should be a valid date and time in the format of YYYY-MM-DD HH:MM:SS
    - it should always be in future (atleast current date time + 15 minutes), current date and time is in ist {datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S")}
    - reject if date time is in the past

  output:
  - return the list of available slots
  """,
)
def get_available_slots(
    provider_id: str,
    date_time: str,
    state: Annotated[AppointmentAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    try:
        if len(state.providers) == 0:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="No providers found", tool_call_id=tool_call_id
                        )
                    ]
                },
            )

        provider = next(
            (
                provider
                for provider in state.providers
                if provider.id == UUID(provider_id)
            ),
            None,
        )

        if provider is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Provider not found", tool_call_id=tool_call_id
                        )
                    ]
                },
            )

        converted_date_time_in_utc = datetime.strptime(
            date_time, "%Y-%m-%d %H:%M:%S"
        ).astimezone(timezone.utc)

        logger.info(f"Converted date time in UTC: {converted_date_time_in_utc}")

        slots = slot_store.for_provider(UUID(provider_id))

        converted_slots_in_ist = []
        for slot in slots:
            if slot.start.date() == converted_date_time_in_utc.date():
                slot.start = slot.start.astimezone(ZoneInfo("Asia/Kolkata"))
                slot.end = slot.end.astimezone(ZoneInfo("Asia/Kolkata"))
                converted_slots_in_ist.append(slot.model_dump())
            
        return Command(
            update={
                "available_slots": converted_slots_in_ist,
                "messages": [
                    ToolMessage(
                        content=f"Available slots: {converted_slots_in_ist}",
                        tool_call_id=tool_call_id,
                    )
                ],
            },
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error getting available slots: {e}",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )


@tool(
    "book_appointment",
    description="book a new appointment for a particular patient",
)
def book_appointment(
    slot_id: str,
    state: Annotated[AppointmentAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    try:
        if state.patient is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Patient not found", tool_call_id=tool_call_id
                        )
                    ]
                },
            )

        selected_slot = next(
            (slot for slot in state.available_slots if slot.id == UUID(slot_id)), None
        )

        if selected_slot is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(content="Slot not found", tool_call_id=tool_call_id)
                    ]
                },
            )

        if not selected_slot.is_available:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Selected slot is not available",
                            tool_call_id=tool_call_id,
                        )
                    ]
                },
            )
        appointment = Appointment(
            patient_id=state.patient.id,
            slot_id=selected_slot.id,
        )

        appointment_store.add(appointment)
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Appointment booked successfully",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error booking appointment: {e}",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )


@tool(
    "cancel_appointment",
    description="cancel a particular appointment for a particular patient",
)
def cancel_appointment(
    appointment_id: UUID,
    state: Annotated[AppointmentAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    try:
        appointment = appointment_store.get(appointment_id)

        if appointment is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment not found", tool_call_id=tool_call_id
                        )
                    ]
                },
            )

        if appointment.status == AppointmentStatus.COMPLETED:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment is already completed",
                            tool_call_id=tool_call_id,
                        )
                    ]
                },
            )

        if appointment.status == AppointmentStatus.CANCELLED:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment is already cancelled",
                            tool_call_id=tool_call_id,
                        )
                    ]
                },
            )

        appointment_store.remove(appointment.id)
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Appointment canceled successfully",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error canceling appointment: {e}",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )


@tool(
    "confirm_appointment",
    description="confirm a particular appointment for a particular patient",
)
def confirm_appointment(
    appointment_id: UUID,
    state: Annotated[AppointmentAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    try:
        appointment = appointment_store.get(appointment_id)

        if appointment is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment not found", tool_call_id=tool_call_id
                        )
                    ]
                },
            )

        if appointment.status == AppointmentStatus.COMPLETED:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment is already completed",
                            tool_call_id=tool_call_id,
                        )
                    ]
                },
            )

        if appointment.status == AppointmentStatus.CANCELLED:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment is already cancelled",
                            tool_call_id=tool_call_id,
                        )
                    ]
                },
            )

        if appointment.status == AppointmentStatus.CONFIRMED:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment is already confirmed",
                            tool_call_id=tool_call_id,
                        )
                    ]
                },
            )

        appointment.status = AppointmentStatus.CONFIRMED
        appointment_store.update(appointment)

        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content="Appointment confirmed successfully",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )
    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error confirming appointment: {e}",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )


@tool(
    "get_slot_for_reschedule",
    description="get the slot for reschedule a particular appointment for a particular patient",
)
def get_slot_for_reschedule(
    appointment_id: UUID,
    state: Annotated[AppointmentAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    try:
        appointment = appointment_store.get(appointment_id)

        if appointment is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment not found", tool_call_id=tool_call_id
                        )
                    ]
                },
            )

        if appointment.status == AppointmentStatus.COMPLETED:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment is already completed",
                            tool_call_id=tool_call_id,
                        )
                    ]
                },
            )

        current_slot = slot_store.get(appointment.slot_id)

        if current_slot is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(content="Slot not found", tool_call_id=tool_call_id)
                    ]
                },
            )

        slots = slot_store.for_provider(current_slot.provider_id)

        available_slots: list[Slot] = []

        for slot in slots:
            if slot.start > current_slot.end and slot.id != current_slot.id:
                available_slots.append(slot)

        if len(available_slots) == 0:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="No available slots found for reschedule, do you want to change the provider?",
                            tool_call_id=tool_call_id,
                        )
                    ]
                },
            )

        return Command(
            update={
                "available_slots": [slot.model_dump() for slot in available_slots],
                "messages": [
                    ToolMessage(
                        content=f"Available slots: {[slot.model_dump() for slot in available_slots]}",
                        tool_call_id=tool_call_id,
                    )
                ],
            },
        )

    except Exception as e:
        return Command(
            update={
                "messages": [
                    ToolMessage(
                        content=f"Error getting slot for reschedule: {e}",
                        tool_call_id=tool_call_id,
                    )
                ]
            },
        )


@tool(
    "reschedule_appointment",
    description="reschedule a particular appointment for a particular patient",
)
def reschedule_appointment(
    appointment_id: UUID,
    new_slot_id: UUID,
    state: Annotated[AppointmentAgentState, InjectedState],
    tool_call_id: Annotated[str, InjectedToolCallId],
):
    try:
        appointment = appointment_store.get(appointment_id)

        if appointment is None:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment not found", tool_call_id=tool_call_id
                        )
                    ]
                },
            )

        if appointment.status == AppointmentStatus.COMPLETED:
            return Command(
                update={
                    "messages": [
                        ToolMessage(
                            content="Appointment is already completed",
                            tool_call_id=tool_call_id,
                        )
                    ]
                },
            )

        selected_slot = next(
            (slot for slot in state.available_slots if slot.id == new_slot_id), None
        )

        if selected_slot is None:
            return {
                "messages": [
                    ToolMessage(content="Slot not found", tool_call_id=tool_call_id)
                ]
            }

        if not selected_slot.is_available:
            return {
                "messages": [
                    ToolMessage(
                        content="Slot is not available", tool_call_id=tool_call_id
                    )
                ]
            }

        appointment.slot_id = new_slot_id
        appointment.status = AppointmentStatus.CONFIRMED
        appointment_store.update(appointment)

        return {
            "messages": [
                ToolMessage(
                    content="Appointment rescheduled successfully",
                    tool_call_id=tool_call_id,
                )
            ]
        }
    except Exception as e:
        return {
            "messages": [
                ToolMessage(
                    content=f"Error rescheduling appointment: {e}",
                    tool_call_id=tool_call_id,
                )
            ]
        }
