from pensieve_mind.search.mind_service import MindService

_mind_service: MindService | None = None


def get_mind_service() -> MindService:
    global _mind_service
    if _mind_service is None:
        _mind_service = MindService()
    return _mind_service
