import os
from livekit import api

LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")


async def dispatch_agent(room_name: str, lang: str):
    lk = api.LiveKitAPI(
        LIVEKIT_URL,
        LIVEKIT_API_KEY,
        LIVEKIT_API_SECRET,
    )

    # 🔥 SELECT AGENT BASED ON LANGUAGE
    if lang == "ar":
        agent_name = "booking-voice-ar"
    else:
        agent_name = "booking-voice-en"

    await lk.agent_dispatch.create_dispatch(
        api.CreateAgentDispatchRequest(
            agent_name=agent_name,
            room=room_name,
        )
    )