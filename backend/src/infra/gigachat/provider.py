from dishka import Provider, Scope, provide_all, provide
from src.infra.gigachat.agents.career import CareerAgent
from src.infra.gigachat.agents.learning import LearningAgent
from src.infra.gigachat.agents.orchestrator import OrchestratorAgent
from src.infra.gigachat.chat import Gigachat


class GigachatProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def _get_by_id_gate(self) -> Gigachat:
        return Gigachat()


    _get_agents = provide_all(
        OrchestratorAgent,
        LearningAgent,
        CareerAgent,
    )

