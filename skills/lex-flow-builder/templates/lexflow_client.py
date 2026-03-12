"""
Cliente Python para API do LexFlow com auto-refresh de token

Permite criar, editar e executar workflows direto da IDE sem precisar
atualizar tokens manualmente.

Uso:
    from lexflow_client import get_client

    # Carrega credenciais automaticamente de ~/.config/lexflow/auth.json
    client = get_client()

    # Criar workflow
    result = client.create_workflow_from_file("meu_workflow.yaml")

    # Executar workflow
    result = client.execute_workflow_from_file("meu_workflow.yaml")
"""

import requests
import json
import base64
import time
from typing import Dict, Any, Optional
from pathlib import Path


class LexFlowClient:
    """Cliente para interagir com a API do LexFlow com auto-refresh de token"""

    def __init__(
        self,
        auth_token: str,
        refresh_token: Optional[str] = None,
        base_url: str = "https://lexflow.internal.inspira.legal"
    ):
        """
        Inicializa o cliente com token do Firebase

        Args:
            auth_token: Token JWT do Firebase
            refresh_token: Refresh token para renovação automática
            base_url: URL base da API

        Nota:
            Use get_client() ao invés de instanciar diretamente.
            Ele carrega as credenciais automaticamente.
        """
        self.base_url = base_url
        self.auth_token = auth_token
        self.refresh_token = refresh_token
        self.firebase_api_key = "AIzaSyBCm6Puaap_bRh_TMeb0LupseAabrx2p6I"

        # Headers base
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {auth_token}"
        }
        self.cookies = {
            "auth_token": auth_token
        }

    def _is_token_expired(self) -> bool:
        """Verifica se o Firebase token está expirado"""
        try:
            payload_b64 = self.auth_token.split(".")[1]
            padding = 4 - len(payload_b64) % 4
            payload_b64 += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            exp = payload.get("exp", 0)
            # Considerar expirado 60s antes
            return time.time() >= (exp - 60)
        except Exception:
            return True

    def _refresh_firebase_token(self) -> None:
        """Renova o Firebase token usando refresh_token"""
        if not self.refresh_token:
            raise ValueError(
                "Token expirado e refresh_token não disponível.\n"
                "Execute: python lexflow_auth.py login"
            )

        response = requests.post(
            f"https://securetoken.googleapis.com/v1/token?key={self.firebase_api_key}",
            data={
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10.0,
        )

        if response.status_code != 200:
            raise ValueError(
                "Falha ao renovar token. Execute: python lexflow_auth.py login"
            )

        body = response.json()
        self.auth_token = body["id_token"]
        self.refresh_token = body["refresh_token"]

        # Atualizar headers e cookies
        self.headers["Authorization"] = f"Bearer {self.auth_token}"
        self.cookies["auth_token"] = self.auth_token

        # Salvar nova auth
        self._save_refreshed_auth()

        print("✅ Token renovado automaticamente")

    def _save_refreshed_auth(self) -> None:
        """Salva o token renovado no arquivo de auth"""
        auth_file = Path.home() / ".config" / "lexflow" / "auth.json"
        if auth_file.exists():
            data = json.loads(auth_file.read_text())
            data["token"] = self.auth_token
            data["refresh_token"] = self.refresh_token
            auth_file.write_text(json.dumps(data, indent=2))

    def _ensure_valid_auth(self) -> None:
        """Garante que a autenticação está válida antes de fazer requisição"""
        if self._is_token_expired():
            print("⏳ Token expirado, renovando...")
            self._refresh_firebase_token()

    def execute_workflow(self, workflow_yaml: str) -> Dict[str, Any]:
        """
        Executa um workflow via API

        Args:
            workflow_yaml: String YAML do workflow

        Returns:
            Resultado da execução
        """
        self._ensure_valid_auth()

        url = f"{self.base_url}/v1/workflows/execute"

        payload = {
            "source_yaml": workflow_yaml
        }

        response = requests.post(
            url,
            headers=self.headers,
            cookies=self.cookies,
            json=payload
        )

        if response.status_code != 200:
            print(f"❌ Status: {response.status_code}")
            print(f"Response: {response.text}")

        response.raise_for_status()
        return response.json()

    def execute_workflow_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Lê um arquivo YAML e executa o workflow

        Args:
            file_path: Caminho para arquivo .yaml

        Returns:
            Resultado da execução
        """
        with open(file_path, 'r') as f:
            workflow_yaml = f.read()

        return self.execute_workflow(workflow_yaml)

    def create_workflow_version(
        self,
        workflow_id: str,
        workflow_yaml: str,
        commit_message: str = "Updated from IDE",
        branch_name: str = "main"
    ) -> Dict[str, Any]:
        """
        Cria uma nova versão (commit) de um workflow existente

        Args:
            workflow_id: ID do workflow no LexFlow
            workflow_yaml: String YAML do workflow
            commit_message: Mensagem do commit
            branch_name: Nome da branch (padrão: main)

        Returns:
            Resposta da API com informações da versão criada
        """
        self._ensure_valid_auth()

        url = f"{self.base_url}/v1/workflows/{workflow_id}/versions/"

        payload = {
            "source_yaml": workflow_yaml,
            "commit_message": commit_message,
            "branch_name": branch_name
        }

        response = requests.post(
            url,
            headers=self.headers,
            cookies=self.cookies,
            json=payload
        )

        if response.status_code not in [200, 201]:
            print(f"❌ Status: {response.status_code}")
            print(f"Response: {response.text}")

        response.raise_for_status()
        return response.json()

    def save_workflow(
        self,
        workflow_id: str,
        file_path: str,
        commit_message: str = "Updated from IDE"
    ) -> Dict[str, Any]:
        """
        Salva um workflow no LexFlow a partir de arquivo YAML

        Args:
            workflow_id: ID do workflow no LexFlow
            file_path: Caminho para arquivo .yaml
            commit_message: Mensagem do commit

        Returns:
            Resultado da operação
        """
        with open(file_path, 'r') as f:
            workflow_yaml = f.read()

        return self.create_workflow_version(workflow_id, workflow_yaml, commit_message)

    def create_workflow(
        self,
        name: str,
        app_id: str,
        slug: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cria um workflow completamente novo no LexFlow

        Args:
            name: Nome do workflow
            app_id: ID do app
            slug: Slug do workflow (auto-gerado se não fornecido)
            description: Descrição opcional

        Returns:
            Dados do workflow criado (incluindo ID)
        """
        self._ensure_valid_auth()

        url = f"{self.base_url}/v1/workflows"

        # Auto-gerar slug se não fornecido
        if not slug:
            import re
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

        payload = {
            "name": name,
            "slug": slug
        }

        if description:
            payload["description"] = description

        response = requests.post(
            url,
            headers=self.headers,
            cookies=self.cookies,
            params={"app_id": app_id},
            json=payload
        )

        if response.status_code not in [200, 201]:
            print(f"❌ Status: {response.status_code}")
            print(f"Response: {response.text}")

        response.raise_for_status()
        return response.json()

    def create_workflow_from_file(
        self,
        file_path: str,
        app_id: str,
        name: Optional[str] = None,
        commit_message: str = "Initial version from IDE"
    ) -> Dict[str, Any]:
        """
        Cria um workflow novo do zero a partir de arquivo YAML

        Args:
            file_path: Caminho para arquivo .yaml
            app_id: ID do app onde criar o workflow
            name: Nome do workflow (padrão: nome do arquivo)
            commit_message: Mensagem do primeiro commit

        Returns:
            Dict com 'workflow' e 'version' criados
        """
        from pathlib import Path

        # Auto-gerar nome se não fornecido
        if not name:
            name = Path(file_path).stem.replace('_', ' ').replace('-', ' ').title()

        # 1. Criar workflow vazio
        print(f"📝 Criando workflow '{name}'...")
        workflow = self.create_workflow(name, app_id)
        workflow_id = workflow['id']
        print(f"✅ Workflow criado: {workflow_id}")

        # 2. Fazer primeiro commit com o YAML
        print(f"💾 Salvando versão inicial...")
        with open(file_path, 'r') as f:
            workflow_yaml = f.read()

        version = self.create_workflow_version(
            workflow_id,
            workflow_yaml,
            commit_message
        )
        print(f"✅ Versão criada: {version['id']}")

        return {
            "workflow": workflow,
            "version": version
        }


def get_client() -> LexFlowClient:
    """
    Carrega configuração e retorna cliente pronto com auto-refresh

    Carrega credenciais de ~/.config/lexflow/auth.json criado pelo
    comando 'python lexflow_auth.py login'

    Returns:
        LexFlowClient configurado e pronto para uso

    Raises:
        ValueError: Se não houver autenticação configurada
    """
    auth_file = Path.home() / ".config" / "lexflow" / "auth.json"

    if not auth_file.exists():
        raise ValueError(
            "❌ Autenticação não configurada.\n\n"
            "Execute primeiro:\n"
            "  python lexflow_auth.py login\n\n"
            "Isso abrirá o browser para você fazer login uma única vez.\n"
            "Depois disso, o token será renovado automaticamente."
        )

    try:
        data = json.loads(auth_file.read_text())
        auth_token = data["token"]
        refresh_token = data.get("refresh_token")
        platform_url = data.get("platform_url", "https://lexflow.internal.inspira.legal")
    except (json.JSONDecodeError, KeyError) as e:
        raise ValueError(
            f"❌ Erro ao ler arquivo de autenticação: {e}\n"
            "Execute: python lexflow_auth.py login"
        )

    return LexFlowClient(
        auth_token=auth_token,
        refresh_token=refresh_token,
        base_url=platform_url
    )


if __name__ == "__main__":
    # Exemplo de uso
    import sys

    if len(sys.argv) < 2:
        print("Uso: python lexflow_client.py <arquivo.yaml>")
        print("\nPrimeiro, configure a autenticação:")
        print("  python lexflow_auth.py login")
        sys.exit(1)

    workflow_file = sys.argv[1]

    try:
        client = get_client()
        print(f"📤 Enviando workflow: {workflow_file}")

        result = client.execute_workflow_from_file(workflow_file)

        print("✅ Workflow executado com sucesso!")
        print(json.dumps(result, indent=2))

    except Exception as e:
        print(f"❌ Erro: {e}")
        sys.exit(1)
