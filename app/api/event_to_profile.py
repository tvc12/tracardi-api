from fastapi import APIRouter, Depends, HTTPException

from app.api.auth.permissions import Permissions
from app.config import server
from app.service.grouping import group_records
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.service.storage.driver import storage
from typing import Optional


router = APIRouter(
    dependencies=[Depends(Permissions(roles=["admin", "developer"]))]
)


@router.put("/event-to-profile/refresh", tags=["event-to-profile"], include_in_schema=server.expose_gui_api,
            response_model=dict)
async def refresh_event_to_profile():
    """
    Refreshes event to profile index
    """
    return await storage.driver.event_to_profile.refresh()


@router.post("/event-to-profile", tags=["event-to-profile"], include_in_schema=server.expose_gui_api,
             response_model=dict)
async def add_event_to_profile(event_to_profile: EventToProfile):

    """
    Creates new event to profile record in database
    """

    result = await storage.driver.event_to_profile.save(event_to_profile)
    await storage.driver.event_to_profile.refresh()

    if result.errors:
        raise ValueError(result.errors)

    return result


@router.get("/event-to-profile/{event_type}",
            tags=["event-type"],
            include_in_schema=server.expose_gui_api,
            response_model=dict)
async def get_event_to_profile(event_type: str):
    """
    Returns event to profile schema for given event type
    """

    records = await storage.driver.event_to_profile.get_event_to_profile(event_type)
    if records.total == 0:
        raise HTTPException(status_code=404, detail=f"Event to profile coping schema for {event_type} not found.")
    return records.dict()


@router.delete("/event-to-profile/{event_type}", tags=["event-type"], include_in_schema=server.expose_gui_api,
               response_model=dict)
async def del_event_type_metadata(event_type: str):
    """
    Deletes event to profile schema for given event type
    """
    result = await storage.driver.event_to_profile.del_event_type_metadata(event_type)
    await storage.driver.event_to_profile.refresh()

    return {"deleted": 1 if result is not None and result["result"] == "deleted" else 0}


@router.get("/events-to-profiles", tags=["event-type"], include_in_schema=server.expose_gui_api,
            response_model=list)
async def list_events_to_profiles(start: Optional[int] = 0, limit: Optional[int] = 10):
    """
    List all of events to profiles.
    """

    result = await storage.driver.event_to_profile.load_events_to_profiles(start, limit)
    return list(result)


@router.get("/events-to-profiles/by_tag", tags=["event-type"], include_in_schema=server.expose_gui_api,
            response_model=dict)
async def list_events_to_profiles_by_tag(query: str = None, start: Optional[int] = 0, limit: Optional[int] = 10):
    """
    Lists events to profiles coping schema by tag, according to given start (int), limit (int) and query (str)
    """
    result = await storage.driver.event_to_profile.load_events_to_profiles(start, limit)
    return group_records(result, query, group_by='tags', search_by='name', sort_by='name')

