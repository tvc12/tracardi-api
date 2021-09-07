from typing import Union
from tracardi.domain.profile import Profiles
from tracardi.service.storage.helpers.profile_loader import load_profiles_to_merge


async def merge(profile, limit=2000) -> Union[Profiles, None]:
    # Merging, schedule save only if there is an update in flow.
    if profile.operation.needs_merging() and profile.operation.needs_update():
        return await profile.merge(load_profiles_to_merge, limit=limit)
    return None
