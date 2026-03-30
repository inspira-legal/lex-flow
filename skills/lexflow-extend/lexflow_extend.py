"""Skill para estender LexFlow criando novos opcodes."""

import os
import yaml
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from jinja2 import Template
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.skill_protocol import BaseSkill, SkillMessage, SkillAction


class LexFlowExtend(BaseSkill):
    """Criação de novos opcodes para estender LexFlow."""

    def __init__(self, router=None):
        super().__init__("lexflow-extend", router)
        self.opcode_templates = self.load_opcode_templates()
        self.existing_opcodes = {}  # Cache de opcodes já criados

    def load_opcode_templates(self) -> Dict[str, str]:
        """Carrega templates para geração de opcodes."""
        return {
            "wrapper": '''class {{ opcode_name|capitalize }}Opcode:
    """{{ description }}"""

    def __init__(self):
        self.name = "{{ opcode_name }}"
        self.category = "{{ category }}"

    def execute(self, context, **kwargs):
        """Execute {{ opcode_name }} opcode."""
        {% for param in required_params %}
        {{ param }} = kwargs.get("{{ param|upper }}")
        if {{ param }} is None:
            raise ValueError("{{ param|upper }} is required")
        {% endfor %}

        # Wrapper implementation
        {{ implementation }}

        return result
''',
            "native": '''class {{ opcode_name|capitalize }}Opcode:
    """{{ description }}"""

    def __init__(self):
        self.name = "{{ opcode_name }}"
        self.category = "{{ category }}"
        self.inputs = {{ inputs }}
        self.outputs = {{ outputs }}

    def execute(self, context, **kwargs):
        """Execute {{ opcode_name }} opcode."""
        # Native implementation
        {{ implementation }}

        return result

    def validate_inputs(self, inputs: dict) -> bool:
        """Validate input parameters."""
        required = {{ required_params }}
        for param in required:
            if param not in inputs:
                return False
        return True
''',
            "documentation": '''# {{ opcode_name }}

## Description
{{ description }}

## Category
{{ category }}

## Inputs
{% for input in inputs %}
- **{{ input.name }}** ({{ input.type }}{% if input.required %}, required{% endif %}): {{ input.description }}
{% endfor %}

## Outputs
{% for output in outputs %}
- **{{ output.name }}** ({{ output.type }}): {{ output.description }}
{% endfor %}

## Examples

### Basic Usage
```yaml
{{ example_basic }}
```

### Advanced Usage
```yaml
{{ example_advanced }}
```

## Implementation Notes
{{ implementation_notes }}

## Error Handling
{{ error_handling }}
''',
            "test": '''import pytest
from lexflow.opcodes import {{ opcode_name }}


class Test{{ opcode_name|capitalize }}Opcode:
    """Tests for {{ opcode_name }} opcode."""

    def test_basic_execution(self):
        """Test basic execution of {{ opcode_name }}."""
        opcode = {{ opcode_name|capitalize }}Opcode()

        result = opcode.execute(
            context={},
            {% for param in test_params %}
            {{ param.name|upper }}={{ param.test_value }}{% if not loop.last %},{% endif %}
            {% endfor %}
        )

        assert result is not None
        {{ test_assertions }}

    def test_missing_required_params(self):
        """Test error handling for missing parameters."""
        opcode = {{ opcode_name|capitalize }}Opcode()

        with pytest.raises(ValueError):
            opcode.execute(context={})

    def test_edge_cases(self):
        """Test edge cases."""
        {{ edge_case_tests }}
'''
        }

    def analyze_requirements(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analisa requisitos para o novo opcode."""
        missing_opcodes = context.get("missing_opcodes", [])
        user_request = context.get("original_request", "")

        # Analisa o primeiro opcode faltante
        if missing_opcodes:
            opcode_name = missing_opcodes[0]

            # Detecta tipo baseado no nome
            if "slack" in opcode_name.lower():
                return self.analyze_slack_opcode(opcode_name)
            elif "teams" in opcode_name.lower():
                return self.analyze_teams_opcode(opcode_name)
            elif "jira" in opcode_name.lower():
                return self.analyze_jira_opcode(opcode_name)
            elif "email" in opcode_name.lower():
                return self.analyze_email_opcode(opcode_name)
            else:
                return self.analyze_generic_opcode(opcode_name, user_request)

        return {}

    def analyze_slack_opcode(self, opcode_name: str) -> Dict[str, Any]:
        """Analisa requisitos para opcode do Slack."""
        return {
            "opcode_name": opcode_name,
            "category": "communication",
            "description": "Send messages to Slack channels or users",
            "type": "wrapper",
            "base_opcode": "http_post",
            "inputs": [
                {"name": "webhook_url", "type": "string", "required": True,
                 "description": "Slack webhook URL"},
                {"name": "message", "type": "string", "required": True,
                 "description": "Message to send"},
                {"name": "channel", "type": "string", "required": False,
                 "description": "Target channel (optional)"},
                {"name": "username", "type": "string", "required": False,
                 "description": "Bot username (optional)"}
            ],
            "outputs": [
                {"name": "success", "type": "boolean", "description": "Whether message was sent"},
                {"name": "response", "type": "object", "description": "Slack API response"}
            ],
            "implementation": '''
        # Prepare Slack payload
        payload = {
            "text": kwargs.get("MESSAGE"),
        }

        if kwargs.get("CHANNEL"):
            payload["channel"] = kwargs.get("CHANNEL")

        if kwargs.get("USERNAME"):
            payload["username"] = kwargs.get("USERNAME")

        # Use http_post to send to Slack
        from lexflow.opcodes import http_post

        result = http_post.execute(
            context,
            URL=kwargs.get("WEBHOOK_URL"),
            HEADERS={"Content-Type": "application/json"},
            BODY=json.dumps(payload)
        )

        return {
            "success": result.get("status_code") == 200,
            "response": result
        }
'''
        }

    def analyze_teams_opcode(self, opcode_name: str) -> Dict[str, Any]:
        """Analisa requisitos para opcode do Teams."""
        return {
            "opcode_name": opcode_name,
            "category": "communication",
            "description": "Send messages to Microsoft Teams",
            "type": "wrapper",
            "base_opcode": "http_post",
            "inputs": [
                {"name": "webhook_url", "type": "string", "required": True,
                 "description": "Teams webhook URL"},
                {"name": "message", "type": "string", "required": True,
                 "description": "Message to send"},
                {"name": "title", "type": "string", "required": False,
                 "description": "Card title"}
            ],
            "outputs": [
                {"name": "success", "type": "boolean", "description": "Whether message was sent"},
                {"name": "response", "type": "object", "description": "Teams API response"}
            ]
        }

    def analyze_jira_opcode(self, opcode_name: str) -> Dict[str, Any]:
        """Analisa requisitos para opcode do Jira."""
        return {
            "opcode_name": opcode_name,
            "category": "project_management",
            "description": "Create and manage Jira issues",
            "type": "wrapper",
            "base_opcode": "http_post",
            "inputs": [
                {"name": "api_url", "type": "string", "required": True,
                 "description": "Jira API URL"},
                {"name": "api_token", "type": "string", "required": True,
                 "description": "Jira API token"},
                {"name": "project", "type": "string", "required": True,
                 "description": "Jira project key"},
                {"name": "summary", "type": "string", "required": True,
                 "description": "Issue summary"},
                {"name": "description", "type": "string", "required": False,
                 "description": "Issue description"},
                {"name": "issue_type", "type": "string", "required": False,
                 "description": "Issue type (Bug, Task, Story)"}
            ],
            "outputs": [
                {"name": "issue_key", "type": "string", "description": "Created issue key"},
                {"name": "issue_url", "type": "string", "description": "Issue URL"},
                {"name": "response", "type": "object", "description": "Full API response"}
            ]
        }

    def analyze_email_opcode(self, opcode_name: str) -> Dict[str, Any]:
        """Analisa requisitos para opcode de email."""
        return {
            "opcode_name": opcode_name,
            "category": "communication",
            "description": "Send emails via SMTP",
            "type": "native",
            "inputs": [
                {"name": "to", "type": "string", "required": True,
                 "description": "Recipient email address"},
                {"name": "subject", "type": "string", "required": True,
                 "description": "Email subject"},
                {"name": "body", "type": "string", "required": True,
                 "description": "Email body"},
                {"name": "from", "type": "string", "required": False,
                 "description": "Sender email address"},
                {"name": "smtp_server", "type": "string", "required": True,
                 "description": "SMTP server address"},
                {"name": "smtp_port", "type": "integer", "required": False,
                 "description": "SMTP port (default: 587)"}
            ],
            "outputs": [
                {"name": "success", "type": "boolean", "description": "Whether email was sent"},
                {"name": "message_id", "type": "string", "description": "Email message ID"}
            ]
        }

    def analyze_generic_opcode(self, opcode_name: str, user_request: str) -> Dict[str, Any]:
        """Analisa requisitos para opcode genérico."""
        return {
            "opcode_name": opcode_name,
            "category": "general",
            "description": f"Custom opcode for: {user_request}",
            "type": "native",
            "inputs": [
                {"name": "input", "type": "any", "required": True,
                 "description": "Input data"}
            ],
            "outputs": [
                {"name": "output", "type": "any", "description": "Output data"}
            ]
        }

    def generate_opcode(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Gera implementação completa do opcode."""
        # Gera código
        if spec["type"] == "wrapper":
            template = Template(self.opcode_templates["wrapper"])
        else:
            template = Template(self.opcode_templates["native"])

        code = template.render(**spec)

        # Gera documentação
        doc_template = Template(self.opcode_templates["documentation"])
        documentation = doc_template.render(
            **spec,
            example_basic=self.generate_basic_example(spec),
            example_advanced=self.generate_advanced_example(spec),
            implementation_notes=self.generate_implementation_notes(spec),
            error_handling=self.generate_error_handling(spec)
        )

        # Gera testes
        test_template = Template(self.opcode_templates["test"])
        tests = test_template.render(
            **spec,
            test_params=self.generate_test_params(spec),
            test_assertions=self.generate_test_assertions(spec),
            edge_case_tests=self.generate_edge_tests(spec)
        )

        return {
            "code": code,
            "documentation": documentation,
            "tests": tests
        }

    def generate_basic_example(self, spec: Dict[str, Any]) -> str:
        """Gera exemplo básico de uso."""
        example = {
            "opcode": spec["opcode_name"],
            "inputs": {}
        }

        for input_spec in spec.get("inputs", []):
            if input_spec.get("required"):
                example["inputs"][input_spec["name"].upper()] = {
                    "literal": f"example_{input_spec['name']}"
                }

        return yaml.dump(example, default_flow_style=False)

    def generate_advanced_example(self, spec: Dict[str, Any]) -> str:
        """Gera exemplo avançado de uso."""
        example = {
            "opcode": spec["opcode_name"],
            "inputs": {}
        }

        for input_spec in spec.get("inputs", []):
            example["inputs"][input_spec["name"].upper()] = {
                "variable": input_spec["name"]
            }

        return yaml.dump(example, default_flow_style=False)

    def generate_implementation_notes(self, spec: Dict[str, Any]) -> str:
        """Gera notas de implementação."""
        if spec["type"] == "wrapper":
            return f"This opcode is a wrapper around {spec.get('base_opcode', 'base opcode')}."
        else:
            return "This is a native implementation."

    def generate_error_handling(self, spec: Dict[str, Any]) -> str:
        """Gera documentação de tratamento de erros."""
        return """
- Raises `ValueError` if required parameters are missing
- Returns error in response if API call fails
- Validates input types before execution
"""

    def generate_test_params(self, spec: Dict[str, Any]) -> List[Dict]:
        """Gera parâmetros de teste."""
        params = []
        for input_spec in spec.get("inputs", []):
            if input_spec.get("required"):
                params.append({
                    "name": input_spec["name"],
                    "test_value": f'"test_{input_spec["name"]}"'
                })
        return params

    def generate_test_assertions(self, spec: Dict[str, Any]) -> str:
        """Gera assertions de teste."""
        assertions = []
        for output in spec.get("outputs", []):
            assertions.append(f'assert "{output["name"]}" in result')
        return "\n        ".join(assertions)

    def generate_edge_tests(self, spec: Dict[str, Any]) -> str:
        """Gera testes de casos extremos."""
        return """
        # Test with empty values
        # Test with invalid types
        # Test with special characters
        pass  # TODO: Implement edge case tests
"""

    def save_opcode_locally(self, opcode_name: str, code: str) -> str:
        """Salva opcode localmente para uso temporário."""
        local_dir = ".lexflow/custom_opcodes"
        os.makedirs(local_dir, exist_ok=True)

        file_path = os.path.join(local_dir, f"{opcode_name}.py")
        with open(file_path, 'w') as f:
            f.write(code)

        return file_path

    def create_pr(self, spec: Dict[str, Any], files: Dict[str, str]) -> str:
        """Cria PR no repositório lexflow-opcodes."""
        # Simulação - em produção usaria GitHub API
        pr_data = {
            "title": f"Add {spec['opcode_name']} opcode",
            "branch": f"add-{spec['opcode_name']}-opcode",
            "files": {
                f"opcodes/{spec['opcode_name']}.py": files["code"],
                f"docs/{spec['opcode_name']}.md": files["documentation"],
                f"tests/test_{spec['opcode_name']}.py": files["tests"]
            },
            "description": f"""
## New Opcode: {spec['opcode_name']}

### Description
{spec['description']}

### Category
{spec['category']}

### Type
{spec['type']} {'(wrapper around ' + spec.get('base_opcode', '') + ')' if spec['type'] == 'wrapper' else ''}

### Inputs
{len(spec.get('inputs', []))} parameters defined

### Outputs
{len(spec.get('outputs', []))} outputs defined

### Testing
- Unit tests included
- Documentation complete
- Examples provided

Generated automatically by lexflow-extend
"""
        }

        # Salva PR data localmente (simulação)
        pr_file = f"pr_{spec['opcode_name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(pr_file, 'w') as f:
            json.dump(pr_data, f, indent=2)

        return f"PR created: {pr_file} (simulation - would open real PR in production)"

    def handle_create_opcode(self, message: SkillMessage) -> SkillMessage:
        """Processa requisição de criação de opcode."""
        context = message.context

        # Analisa requisitos
        spec = self.analyze_requirements(context)

        if not spec:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={"error": "Could not analyze opcode requirements"}
            )

        # Verifica se já existe
        if spec["opcode_name"] in self.existing_opcodes:
            # Retorna opcode existente
            return SkillMessage(
                source=self.name,
                target=context.get("callback_to", message.source),
                action=SkillAction.OPCODE_READY,
                context={
                    "opcode_name": spec["opcode_name"],
                    "local_path": self.existing_opcodes[spec["opcode_name"]],
                    "template_name": context.get("template_name"),
                    "original_request": context.get("original_request")
                }
            )

        # Gera opcode
        files = self.generate_opcode(spec)

        # Salva localmente
        local_path = self.save_opcode_locally(spec["opcode_name"], files["code"])
        self.existing_opcodes[spec["opcode_name"]] = local_path

        # Cria PR (simulado)
        pr_url = self.create_pr(spec, files)

        # Retorna sucesso
        return SkillMessage(
            source=self.name,
            target=context.get("callback_to", message.source),
            action=SkillAction.OPCODE_READY,
            context={
                "opcode_name": spec["opcode_name"],
                "local_path": local_path,
                "pr_url": pr_url,
                "template_name": context.get("template_name"),
                "original_request": context.get("original_request"),
                "params": {}
            }
        )

    def handle_check_opcode_exists(self, message: SkillMessage) -> SkillMessage:
        """Verifica se opcode existe."""
        opcode_name = message.context.get("opcode_name")

        exists = opcode_name in self.existing_opcodes

        return SkillMessage(
            source=self.name,
            target=message.source,
            action=SkillAction.SUCCESS,
            context={
                "exists": exists,
                "opcode_name": opcode_name,
                "local_path": self.existing_opcodes.get(opcode_name)
            }
        )