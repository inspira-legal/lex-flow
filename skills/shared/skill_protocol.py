"""Protocolo de comunicação entre skills LexFlow."""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum
import json


class SkillAction(Enum):
    """Ações possíveis entre skills."""
    # lexflow-quick actions
    CREATE_WORKFLOW = "CREATE_WORKFLOW"
    EDIT_WORKFLOW = "EDIT_WORKFLOW"
    VALIDATE_TEMPLATE = "VALIDATE_TEMPLATE"
    DELEGATE_EXTENSION = "DELEGATE_EXTENSION"

    # lexflow-extend actions
    CREATE_OPCODE = "CREATE_OPCODE"
    CHECK_OPCODE_EXISTS = "CHECK_OPCODE_EXISTS"
    OPCODE_READY = "OPCODE_READY"

    # lexflow-deploy actions
    DEPLOY = "DEPLOY"
    ROLLBACK = "ROLLBACK"
    GET_STATUS = "GET_STATUS"
    DEPLOYMENT_COMPLETE = "DEPLOYMENT_COMPLETE"

    # General actions
    ERROR = "ERROR"
    SUCCESS = "SUCCESS"
    NOTIFY_USER = "NOTIFY_USER"


@dataclass
class SkillMessage:
    """Formato padrão de comunicação entre skills."""
    source: str  # Skill origem
    target: str  # Skill destino
    action: SkillAction  # Ação solicitada
    context: Dict[str, Any]  # Dados contextuais
    callback: Optional[str] = None  # Como retornar resposta

    def to_json(self) -> str:
        """Serializa mensagem para JSON."""
        return json.dumps({
            "source": self.source,
            "target": self.target,
            "action": self.action.value,
            "context": self.context,
            "callback": self.callback
        })

    @classmethod
    def from_json(cls, data: str) -> 'SkillMessage':
        """Deserializa mensagem de JSON."""
        obj = json.loads(data)
        return cls(
            source=obj["source"],
            target=obj["target"],
            action=SkillAction(obj["action"]),
            context=obj["context"],
            callback=obj.get("callback")
        )


class SkillRouter:
    """Roteador de mensagens entre skills."""

    def __init__(self):
        self.skills = {}

    def register(self, skill_name: str, skill_instance):
        """Registra uma skill no roteador."""
        self.skills[skill_name] = skill_instance

    def route(self, message: SkillMessage) -> Optional[SkillMessage]:
        """Roteia mensagem para skill apropriada."""
        target_skill = self.skills.get(message.target)
        if target_skill:
            return target_skill.handle_message(message)
        else:
            return SkillMessage(
                source="router",
                target=message.source,
                action=SkillAction.ERROR,
                context={"error": f"Skill '{message.target}' not found"}
            )


class BaseSkill:
    """Classe base para todas as skills."""

    def __init__(self, name: str, router: Optional[SkillRouter] = None):
        self.name = name
        self.router = router

    def handle_message(self, message: SkillMessage) -> Optional[SkillMessage]:
        """Processa mensagem recebida."""
        handler = getattr(self, f"handle_{message.action.value.lower()}", None)
        if handler:
            return handler(message)
        else:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={"error": f"Action '{message.action}' not supported"}
            )

    def send_message(self, message: SkillMessage) -> Optional[SkillMessage]:
        """Envia mensagem para outra skill."""
        if self.router:
            return self.router.route(message)
        return None