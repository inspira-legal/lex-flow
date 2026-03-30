"""Skill principal para criação rápida de workflows LexFlow."""

import os
import yaml
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.skill_protocol import BaseSkill, SkillMessage, SkillAction


class LexFlowQuick(BaseSkill):
    """Criação rápida de workflows com templates validados."""

    def __init__(self, router=None):
        super().__init__("lexflow-quick", router)
        self.templates = self.load_templates()
        self.available_opcodes = self.load_available_opcodes()

    def load_templates(self) -> Dict[str, Dict]:
        """Carrega templates disponíveis."""
        return {
            "csv_processor": {
                "triggers": ["csv", "planilha", "excel"],
                "opcodes": ["file_read", "csv_parse", "list_foreach", "file_write"],
                "validated": True,
                "template": "templates/csv_processor.yaml"
            },
            "json_transformer": {
                "triggers": ["json", "transformar", "converter"],
                "opcodes": ["json_parse", "dict_get", "dict_set", "json_stringify"],
                "validated": True,
                "template": "templates/json_transformer.yaml"
            },
            "api_fetcher": {
                "triggers": ["api", "buscar", "consultar", "rest"],
                "opcodes": ["http_get", "json_parse", "dict_get"],
                "validated": True,
                "template": "templates/api_fetcher.yaml"
            },
            "webhook_receiver": {
                "triggers": ["webhook", "receber", "endpoint"],
                "opcodes": ["workflow_start", "json_parse", "http_response"],
                "validated": True,
                "template": "templates/webhook_receiver.yaml"
            },
            "slack_notification": {
                "triggers": ["slack", "mensagem", "notificar"],
                "opcodes": ["slack_send"],  # Não existe ainda
                "validated": False,
                "requires_extension": True,
                "template": "templates/slack_notification.yaml"
            },
            "web_scraper": {
                "triggers": ["scraping", "extrair", "web", "html"],
                "opcodes": ["http_get", "html_parse", "html_select", "html_get_text"],
                "validated": True,
                "template": "templates/web_scraper.yaml"
            }
        }

    def load_available_opcodes(self) -> List[str]:
        """Carrega lista de opcodes disponíveis nativamente."""
        # Opcodes nativos do LexFlow
        return [
            # I/O
            "io_print", "io_input", "io_read_file", "io_write_file",

            # HTTP
            "http_get", "http_post", "http_put", "http_delete",

            # Data Processing
            "json_parse", "json_stringify", "csv_parse", "csv_write",
            "xml_parse", "yaml_parse",

            # HTML/Web
            "html_parse", "html_select", "html_select_one", "html_get_text",
            "html_get_attr",

            # Collections
            "list_foreach", "list_map", "list_filter", "list_reduce",
            "list_append", "list_contains", "list_length", "list_get",

            # Dict/Object
            "dict_get", "dict_set", "dict_keys", "dict_values",
            "dict_merge", "dict_contains",

            # String
            "string_concat", "string_split", "string_replace",
            "string_lower", "string_upper", "string_contains",

            # Control Flow
            "control_if_else", "control_foreach", "control_while",
            "control_switch", "control_parallel",

            # Workflow
            "workflow_start", "workflow_end", "workflow_call",

            # Data
            "data_set_variable_to", "data_get_variable",

            # Math
            "math_add", "math_subtract", "math_multiply", "math_divide",

            # Logic
            "operator_equals", "operator_not_equals", "operator_greater_than",
            "operator_less_than", "operator_and", "operator_or", "operator_not",

            # System
            "bash_run", "python_eval"
        ]

    def detect_pattern(self, user_input: str) -> Optional[str]:
        """Detecta o template apropriado baseado no input."""
        input_lower = user_input.lower()

        for template_name, config in self.templates.items():
            for trigger in config["triggers"]:
                if trigger in input_lower:
                    return template_name

        return None

    def validate_template(self, template_name: str) -> Dict[str, Any]:
        """Valida se o template pode ser usado."""
        template = self.templates.get(template_name)
        if not template:
            return {"valid": False, "reason": "Template not found"}

        # Verifica se todos os opcodes existem
        missing_opcodes = []
        for opcode in template["opcodes"]:
            if opcode not in self.available_opcodes:
                missing_opcodes.append(opcode)

        if missing_opcodes:
            return {
                "valid": False,
                "reason": "Missing opcodes",
                "missing": missing_opcodes,
                "requires_extension": True
            }

        return {"valid": True}

    def create_workflow(self, template_name: str, params: Dict[str, Any]) -> str:
        """Cria workflow baseado no template."""
        template = self.templates[template_name]

        # Carrega template base
        template_path = os.path.join(
            os.path.dirname(__file__),
            template["template"]
        )

        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                workflow = yaml.safe_load(f)
        else:
            # Cria workflow básico se template não existir
            workflow = self.create_basic_workflow(template_name, params)

        # Personaliza com parâmetros do usuário
        workflow = self.customize_workflow(workflow, params)

        # Salva workflow
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"workflow_{template_name}_{timestamp}.yaml"

        with open(output_path, 'w') as f:
            yaml.dump(workflow, f, default_flow_style=False)

        return output_path

    def create_basic_workflow(self, template_name: str, params: Dict[str, Any]) -> Dict:
        """Cria estrutura básica de workflow."""
        return {
            "workflows": [{
                "name": "main",
                "interface": {
                    "inputs": params.get("inputs", []),
                    "outputs": params.get("outputs", [])
                },
                "variables": params.get("variables", {}),
                "nodes": {
                    "start": {
                        "opcode": "workflow_start",
                        "next": "process",
                        "inputs": {}
                    },
                    "process": {
                        "opcode": "io_print",
                        "next": None,
                        "inputs": {
                            "STRING": {
                                "literal": f"Workflow {template_name} created"
                            }
                        }
                    }
                }
            }]
        }

    def customize_workflow(self, workflow: Dict, params: Dict[str, Any]) -> Dict:
        """Personaliza workflow com parâmetros do usuário."""
        # Atualiza variáveis
        if "variables" in params:
            workflow["workflows"][0]["variables"].update(params["variables"])

        # Atualiza inputs/outputs
        if "inputs" in params:
            workflow["workflows"][0]["interface"]["inputs"] = params["inputs"]
        if "outputs" in params:
            workflow["workflows"][0]["interface"]["outputs"] = params["outputs"]

        return workflow

    def handle_create_workflow(self, message: SkillMessage) -> SkillMessage:
        """Processa requisição de criação de workflow."""
        context = message.context
        user_input = context.get("user_input", "")

        # Detecta padrão
        template_name = self.detect_pattern(user_input)

        if not template_name:
            # Não encontrou padrão, pede mais informações
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={
                    "error": "Pattern not detected",
                    "message": "Não consegui identificar o tipo de workflow. Pode ser mais específico?"
                }
            )

        # Valida template
        validation = self.validate_template(template_name)

        if not validation["valid"]:
            if validation.get("requires_extension"):
                # Precisa criar novo opcode
                return SkillMessage(
                    source=self.name,
                    target="lexflow-extend",
                    action=SkillAction.CREATE_OPCODE,
                    context={
                        "missing_opcodes": validation["missing"],
                        "original_request": user_input,
                        "template_name": template_name,
                        "callback_to": self.name
                    }
                )
            else:
                return SkillMessage(
                    source=self.name,
                    target=message.source,
                    action=SkillAction.ERROR,
                    context={"error": validation["reason"]}
                )

        # Cria workflow
        workflow_path = self.create_workflow(
            template_name,
            context.get("params", {})
        )

        # Envia para deploy
        return SkillMessage(
            source=self.name,
            target="lexflow-deploy",
            action=SkillAction.DEPLOY,
            context={
                "workflow_path": workflow_path,
                "template_name": template_name,
                "environment": "production",
                "user_request": user_input
            }
        )

    def handle_opcode_ready(self, message: SkillMessage) -> SkillMessage:
        """Processa resposta de opcode criado."""
        context = message.context

        # Adiciona opcode temporariamente à lista
        opcode_name = context.get("opcode_name")
        if opcode_name:
            self.available_opcodes.append(opcode_name)

        # Recria workflow com novo opcode
        template_name = context.get("template_name")
        original_request = context.get("original_request", "")

        workflow_path = self.create_workflow(
            template_name,
            context.get("params", {})
        )

        # Envia para deploy
        return SkillMessage(
            source=self.name,
            target="lexflow-deploy",
            action=SkillAction.DEPLOY,
            context={
                "workflow_path": workflow_path,
                "template_name": template_name,
                "environment": "production",
                "user_request": original_request,
                "custom_opcodes": [opcode_name]
            }
        )

    def find_workflow(self, identifier: str) -> Optional[str]:
        """Busca workflow existente por nome ou ID.

        Args:
            identifier: Nome do workflow ou ID para buscar.

        Returns:
            Caminho do arquivo do workflow se encontrado, None caso contrário.
        """
        # Procura em workflows deployados
        search_dirs = [
            "workflows/production",
            "workflows/staging",
            "workflows/development",
            "workflows_saved"
        ]

        for dir_path in search_dirs:
            if not os.path.exists(dir_path):
                continue

            for file in os.listdir(dir_path):
                if not file.endswith('.yaml'):
                    continue

                # Verifica se o identificador está no nome do arquivo
                if identifier.lower() in file.lower():
                    return os.path.join(dir_path, file)

        # Procura também nos workflows não deployados (raiz do projeto)
        for file in os.listdir('.'):
            if file.endswith('.yaml') and identifier.lower() in file.lower():
                return file

        return None

    def load_workflow(self, workflow_path: str) -> Optional[Dict]:
        """Carrega workflow de um arquivo YAML.

        Args:
            workflow_path: Caminho do arquivo do workflow.

        Returns:
            Dicionário com conteúdo do workflow ou None se falhar.
        """
        try:
            with open(workflow_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            return None

    def detect_modification_type(self, user_input: str) -> Dict[str, Any]:
        """Detecta que tipo de modificação o usuário quer fazer.

        Args:
            user_input: Requisição do usuário descrevendo a mudança.

        Returns:
            Dicionário com tipo de modificação e parâmetros.
        """
        input_lower = user_input.lower()

        # Detecta adição de novo elemento
        if any(word in input_lower for word in ['adicionar', 'incluir', 'add', 'também']):
            return {
                "type": "add",
                "target": self._extract_target(input_lower),
                "description": user_input
            }

        # Detecta remoção
        if any(word in input_lower for word in ['remover', 'deletar', 'tirar', 'remove']):
            return {
                "type": "remove",
                "target": self._extract_target(input_lower),
                "description": user_input
            }

        # Detecta alteração de valor
        if any(word in input_lower for word in ['alterar', 'mudar', 'trocar', 'change', 'update']):
            return {
                "type": "update",
                "target": self._extract_target(input_lower),
                "description": user_input
            }

        # Detecta otimização
        if any(word in input_lower for word in ['otimizar', 'melhorar', 'optimize']):
            return {
                "type": "optimize",
                "description": user_input
            }

        # Padrão: update genérico
        return {
            "type": "update",
            "description": user_input
        }

    def _extract_target(self, text: str) -> Optional[str]:
        """Extrai o alvo da modificação do texto.

        Args:
            text: Texto com a descrição da mudança.

        Returns:
            String com o alvo identificado ou None.
        """
        # Procura por padrões comuns
        if 'canal' in text or 'channel' in text:
            return 'channel'
        if 'url' in text or 'endpoint' in text:
            return 'url'
        if 'mensagem' in text or 'message' in text:
            return 'message'
        if 'variável' in text or 'variable' in text:
            return 'variable'

        return None

    def apply_modification(self, workflow: Dict, modification: Dict[str, Any],
                          user_input: str) -> Dict:
        """Aplica modificação ao workflow.

        Args:
            workflow: Dicionário com conteúdo do workflow.
            modification: Tipo de modificação a aplicar.
            user_input: Requisição original do usuário.

        Returns:
            Workflow modificado.
        """
        mod_type = modification.get("type")
        target = modification.get("target")

        if mod_type == "add":
            workflow = self._add_to_workflow(workflow, target, user_input)
        elif mod_type == "remove":
            workflow = self._remove_from_workflow(workflow, target, user_input)
        elif mod_type == "update":
            workflow = self._update_workflow_value(workflow, target, user_input)
        elif mod_type == "optimize":
            workflow = self._optimize_workflow(workflow)

        return workflow

    def _add_to_workflow(self, workflow: Dict, target: Optional[str],
                        user_input: str) -> Dict:
        """Adiciona novo elemento ao workflow."""
        # Exemplo: adicionar novo canal no Slack
        if target == "channel":
            # Procura node de envio
            main_workflow = workflow["workflows"][0]
            for node_id, node in main_workflow["nodes"].items():
                if node.get("opcode") in ["slack_send", "http_post"]:
                    # Adiciona novo canal se houver lista
                    if "channels" in node.get("inputs", {}):
                        channels = node["inputs"]["channels"].get("literal", [])
                        # Extrai novo canal do input do usuário
                        import re
                        channel_match = re.search(r'#(\w+)', user_input)
                        if channel_match:
                            new_channel = channel_match.group(1)
                            if new_channel not in channels:
                                channels.append(new_channel)
                                node["inputs"]["channels"]["literal"] = channels

        return workflow

    def _remove_from_workflow(self, workflow: Dict, target: Optional[str],
                              user_input: str) -> Dict:
        """Remove elemento do workflow."""
        # Implementação similar a _add_to_workflow
        return workflow

    def _update_workflow_value(self, workflow: Dict, target: Optional[str],
                               user_input: str) -> Dict:
        """Atualiza valor no workflow."""
        # Implementação de atualização de valores
        return workflow

    def _optimize_workflow(self, workflow: Dict) -> Dict:
        """Otimiza estrutura do workflow."""
        # Pode adicionar caching, paralelização, etc
        return workflow

    def handle_edit_workflow(self, message: SkillMessage) -> SkillMessage:
        """Processa requisição de edição de workflow.

        Args:
            message: Mensagem com contexto da edição.

        Returns:
            Mensagem com resultado da operação.
        """
        context = message.context
        user_input = context.get("user_input", "")
        workflow_id = context.get("workflow_id", "")

        # Busca workflow existente
        workflow_path = self.find_workflow(workflow_id)

        if not workflow_path:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={
                    "error": "Workflow not found",
                    "message": f"Não encontrei workflow com identificador '{workflow_id}'"
                }
            )

        # Carrega workflow
        workflow = self.load_workflow(workflow_path)

        if not workflow:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={
                    "error": "Failed to load workflow",
                    "message": f"Erro ao carregar workflow de {workflow_path}"
                }
            )

        # Detecta tipo de modificação
        modification = self.detect_modification_type(user_input)

        # Aplica modificação
        modified_workflow = self.apply_modification(workflow, modification, user_input)

        # Salva versão modificada
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workflow_name = os.path.basename(workflow_path).replace('.yaml', '')
        new_path = f"workflow_{workflow_name}_edited_{timestamp}.yaml"

        with open(new_path, 'w') as f:
            yaml.dump(modified_workflow, f, default_flow_style=False)

        # Envia para deploy
        return SkillMessage(
            source=self.name,
            target="lexflow-deploy",
            action=SkillAction.DEPLOY,
            context={
                "workflow_path": new_path,
                "template_name": "edited",
                "environment": "production",
                "user_request": user_input,
                "is_edit": True,
                "original_workflow": workflow_path
            }
        )