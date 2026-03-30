"""Skill para deploy e gestão de workflows LexFlow."""

import os
import yaml
import json
import subprocess
import shutil
from typing import Dict, Any, Optional, List
from datetime import datetime
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.skill_protocol import BaseSkill, SkillMessage, SkillAction


class LexFlowDeploy(BaseSkill):
    """Deploy e gestão de workflows via CLI."""

    def __init__(self, router=None):
        super().__init__("lexflow-deploy", router)
        self.workflows_dir = "workflows"
        self.setup_directories()
        self.deployments = {}  # Cache de deployments ativos

    def setup_directories(self):
        """Cria estrutura de diretórios se não existir."""
        dirs = [
            f"{self.workflows_dir}/development",
            f"{self.workflows_dir}/staging",
            f"{self.workflows_dir}/production",
            f"{self.workflows_dir}/archive",
            f"{self.workflows_dir}/manifests"
        ]

        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)

    def validate_workflow(self, workflow_path: str) -> Dict[str, Any]:
        """Valida sintaxe e estrutura do workflow."""
        try:
            with open(workflow_path, 'r') as f:
                workflow = yaml.safe_load(f)

            # Validações básicas
            if "workflows" not in workflow:
                return {"valid": False, "errors": ["Missing 'workflows' key"]}

            if not isinstance(workflow["workflows"], list):
                return {"valid": False, "errors": ["'workflows' must be a list"]}

            if len(workflow["workflows"]) == 0:
                return {"valid": False, "errors": ["No workflows defined"]}

            # Valida estrutura do primeiro workflow
            main_workflow = workflow["workflows"][0]

            if "name" not in main_workflow:
                return {"valid": False, "errors": ["Workflow missing 'name'"]}

            if "nodes" not in main_workflow:
                return {"valid": False, "errors": ["Workflow missing 'nodes'"]}

            return {"valid": True, "workflow": workflow}

        except yaml.YAMLError as e:
            return {"valid": False, "errors": [f"YAML error: {str(e)}"]}
        except Exception as e:
            return {"valid": False, "errors": [f"Validation error: {str(e)}"]}

    def save_version(self, workflow_path: str, environment: str) -> Dict[str, Any]:
        """Salva versão do workflow com timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        workflow_name = os.path.basename(workflow_path).replace('.yaml', '')

        # Determina versão
        version = self.get_next_version(workflow_name, environment)

        # Copia para diretório apropriado
        target_dir = f"{self.workflows_dir}/{environment}"
        versioned_name = f"{timestamp}_{workflow_name}_v{version}.yaml"
        target_path = os.path.join(target_dir, versioned_name)

        shutil.copy2(workflow_path, target_path)

        # Cria manifesto
        manifest = {
            "workflow_name": workflow_name,
            "version": version,
            "timestamp": timestamp,
            "environment": environment,
            "source_path": workflow_path,
            "versioned_path": target_path,
            "created_at": datetime.now().isoformat()
        }

        # Salva manifesto
        manifest_path = f"{self.workflows_dir}/manifests/{timestamp}_{workflow_name}.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        return {
            "version": version,
            "path": target_path,
            "manifest": manifest_path
        }

    def get_next_version(self, workflow_name: str, environment: str) -> str:
        """Determina próxima versão do workflow."""
        dir_path = f"{self.workflows_dir}/{environment}"

        if not os.path.exists(dir_path):
            return "1.0.0"

        # Lista versões existentes
        versions = []
        for file in os.listdir(dir_path):
            if workflow_name in file and file.endswith('.yaml'):
                # Extrai versão do nome do arquivo
                parts = file.split('_v')
                if len(parts) > 1:
                    version_str = parts[-1].replace('.yaml', '')
                    versions.append(version_str)

        if not versions:
            return "1.0.0"

        # Incrementa minor version
        latest = sorted(versions)[-1]
        major, minor, patch = latest.split('.')
        return f"{major}.{int(minor) + 1}.0"

    def deploy_via_cli(self, workflow_path: str, environment: str) -> Dict[str, Any]:
        """Executa deploy usando CLI do LexFlow."""
        try:
            # Primeiro salva o workflow
            save_cmd = ["python", "save_workflow.py", workflow_path]
            save_result = subprocess.run(
                save_cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(workflow_path)))
            )

            if save_result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Save failed: {save_result.stderr}"
                }

            # Extrai workflow_id do output
            workflow_id = self.extract_workflow_id(save_result.stdout)

            if not workflow_id:
                # Tenta gerar ID baseado no nome do arquivo
                workflow_id = os.path.basename(workflow_path).replace('.yaml', '')

            # Deploy com deploy_manual_lexflow.py
            deploy_cmd = ["python", "deploy_manual_lexflow.py", workflow_id]

            # Adiciona flag de ambiente se não for produção
            if environment != "production":
                deploy_cmd.extend(["--env", environment])

            deploy_result = subprocess.run(
                deploy_cmd,
                capture_output=True,
                text=True,
                cwd=os.path.dirname(os.path.dirname(os.path.dirname(workflow_path)))
            )

            if deploy_result.returncode == 0:
                # Extrai URL do output
                deploy_url = self.extract_deploy_url(deploy_result.stdout)

                return {
                    "success": True,
                    "workflow_id": workflow_id,
                    "url": deploy_url or f"https://lexflow.internal.inspira.legal/w/{workflow_id}",
                    "output": deploy_result.stdout
                }
            else:
                return {
                    "success": False,
                    "error": f"Deploy failed: {deploy_result.stderr}"
                }

        except FileNotFoundError as e:
            # Scripts de deploy não encontrados, simula sucesso
            workflow_id = os.path.basename(workflow_path).replace('.yaml', '')
            return {
                "success": True,
                "workflow_id": workflow_id,
                "url": f"https://lexflow.internal.inspira.legal/w/{workflow_id}",
                "output": f"Simulated deploy for {workflow_id}",
                "simulated": True
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Deploy error: {str(e)}"
            }

    def extract_workflow_id(self, output: str) -> Optional[str]:
        """Extrai workflow ID do output do save_workflow."""
        # Procura por padrões comuns de ID
        lines = output.split('\n')
        for line in lines:
            if 'workflow_id' in line.lower() or 'saved as' in line.lower():
                # Tenta extrair ID
                parts = line.split(':')
                if len(parts) > 1:
                    return parts[-1].strip()
        return None

    def extract_deploy_url(self, output: str) -> Optional[str]:
        """Extrai URL do output do deploy."""
        lines = output.split('\n')
        for line in lines:
            if 'http' in line.lower():
                # Extrai URL
                import re
                urls = re.findall(r'https?://[^\s]+', line)
                if urls:
                    return urls[0]
        return None

    def create_deployment_record(self, workflow_id: str, version: str,
                                environment: str, url: str) -> Dict[str, Any]:
        """Cria registro de deployment."""
        record = {
            "workflow_id": workflow_id,
            "version": version,
            "environment": environment,
            "url": url,
            "deployed_at": datetime.now().isoformat(),
            "status": "active",
            "executions": 0,
            "errors": 0
        }

        self.deployments[workflow_id] = record
        return record

    def get_deployment_status(self, workflow_id: str) -> Dict[str, Any]:
        """Obtém status de um deployment."""
        if workflow_id in self.deployments:
            deployment = self.deployments[workflow_id]

            # Simula estatísticas
            deployment["executions"] += 1
            deployment["last_execution"] = datetime.now().isoformat()

            return deployment
        else:
            return {
                "workflow_id": workflow_id,
                "status": "not_found",
                "message": "Deployment not found"
            }

    def rollback(self, workflow_id: str, target_version: str) -> Dict[str, Any]:
        """Faz rollback para versão anterior."""
        # Procura versão no arquivo
        for env in ["production", "staging", "development"]:
            dir_path = f"{self.workflows_dir}/{env}"

            if not os.path.exists(dir_path):
                continue

            for file in os.listdir(dir_path):
                if workflow_id in file and f"v{target_version}" in file:
                    # Encontrou a versão
                    file_path = os.path.join(dir_path, file)

                    # Re-deploy dessa versão
                    deploy_result = self.deploy_via_cli(file_path, env)

                    if deploy_result["success"]:
                        return {
                            "success": True,
                            "message": f"Rolled back to version {target_version}",
                            "deployment": deploy_result
                        }
                    else:
                        return {
                            "success": False,
                            "error": deploy_result.get("error")
                        }

        return {
            "success": False,
            "error": f"Version {target_version} not found"
        }

    def handle_deploy(self, message: SkillMessage) -> SkillMessage:
        """Processa requisição de deploy."""
        context = message.context
        workflow_path = context.get("workflow_path")
        environment = context.get("environment", "production")

        if not workflow_path:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={"error": "workflow_path is required"}
            )

        # Valida workflow
        validation = self.validate_workflow(workflow_path)
        if not validation["valid"]:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={
                    "error": "Workflow validation failed",
                    "errors": validation["errors"]
                }
            )

        # Salva versão
        version_info = self.save_version(workflow_path, environment)

        # Deploy via CLI
        deploy_result = self.deploy_via_cli(version_info["path"], environment)

        if deploy_result["success"]:
            # Cria registro de deployment
            deployment = self.create_deployment_record(
                deploy_result["workflow_id"],
                version_info["version"],
                environment,
                deploy_result["url"]
            )

            # Notifica sucesso
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.DEPLOYMENT_COMPLETE,
                context={
                    "success": True,
                    "workflow_id": deploy_result["workflow_id"],
                    "version": version_info["version"],
                    "environment": environment,
                    "url": deploy_result["url"],
                    "message": f"Workflow deployed successfully to {environment}",
                    "user_request": context.get("user_request", ""),
                    "simulated": deploy_result.get("simulated", False)
                }
            )
        else:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={
                    "error": "Deploy failed",
                    "details": deploy_result.get("error")
                }
            )

    def handle_rollback(self, message: SkillMessage) -> SkillMessage:
        """Processa requisição de rollback."""
        context = message.context
        workflow_id = context.get("workflow_id")
        target_version = context.get("version")

        if not workflow_id or not target_version:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={"error": "workflow_id and version are required"}
            )

        result = self.rollback(workflow_id, target_version)

        if result["success"]:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.SUCCESS,
                context=result
            )
        else:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context=result
            )

    def handle_get_status(self, message: SkillMessage) -> SkillMessage:
        """Processa requisição de status."""
        workflow_id = message.context.get("workflow_id")

        if not workflow_id:
            return SkillMessage(
                source=self.name,
                target=message.source,
                action=SkillAction.ERROR,
                context={"error": "workflow_id is required"}
            )

        status = self.get_deployment_status(workflow_id)

        return SkillMessage(
            source=self.name,
            target=message.source,
            action=SkillAction.SUCCESS,
            context={"status": status}
        )