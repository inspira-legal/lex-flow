#!/usr/bin/env python3
"""
Sistema de autenticação LexFlow com auto-refresh de token

Uso:
    python lexflow_auth.py login    # Fazer login via browser
    python lexflow_auth.py status   # Ver status da autenticação
    python lexflow_auth.py logout   # Remover credenciais

Após o login, suas credenciais são salvas em ~/.config/lexflow/auth.json
e o token é renovado automaticamente quando necessário.
"""

import json
import base64
import time
import webbrowser
import socket
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from urllib.parse import quote
from typing import Optional, Dict
import requests


# Configurações
AUTH_DIR = Path.home() / ".config" / "lexflow"
AUTH_FILE = AUTH_DIR / "auth.json"
FIREBASE_API_KEY = "AIzaSyBCm6Puaap_bRh_TMeb0LupseAabrx2p6I"
DEFAULT_PLATFORM_URL = "https://lexflow.internal.inspira.legal"


class LexFlowAuth:
    """Gerenciador de autenticação do LexFlow"""

    def __init__(self, platform_url: str = DEFAULT_PLATFORM_URL):
        self.platform_url = platform_url

    def _is_token_expired(self, token: str, margin_seconds: int = 60) -> bool:
        """Verifica se o token JWT está expirado

        Args:
            token: Token JWT do Firebase
            margin_seconds: Margem de segurança em segundos

        Returns:
            True se o token está expirado ou vai expirar em breve
        """
        try:
            payload_b64 = token.split(".")[1]
            padding = 4 - len(payload_b64) % 4
            payload_b64 += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))
            exp = payload.get("exp", 0)
            return time.time() >= (exp - margin_seconds)
        except Exception:
            return True

    def _refresh_token(self, refresh_token: str) -> Dict[str, str]:
        """Renova o token usando o refresh_token

        Args:
            refresh_token: Refresh token do Firebase

        Returns:
            Dict com 'id_token' e 'refresh_token' novos

        Raises:
            RuntimeError: Se falhar ao renovar
        """
        response = requests.post(
            f"https://securetoken.googleapis.com/v1/token?key={FIREBASE_API_KEY}",
            data={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10.0,
        )

        if response.status_code != 200:
            raise RuntimeError(
                "Falha ao renovar token. Execute 'python lexflow_auth.py login' novamente."
            )

        body = response.json()
        return {
            "id_token": body["id_token"],
            "refresh_token": body["refresh_token"]
        }

    def save_auth(self, token: str, refresh_token: str) -> None:
        """Salva credenciais no arquivo

        Args:
            token: Token JWT do Firebase
            refresh_token: Refresh token do Firebase
        """
        AUTH_DIR.mkdir(parents=True, exist_ok=True)
        data = {
            "platform_url": self.platform_url,
            "token": token,
            "refresh_token": refresh_token,
        }
        AUTH_FILE.write_text(json.dumps(data, indent=2))
        print(f"✅ Credenciais salvas em: {AUTH_FILE}")

    def load_auth(self) -> Optional[Dict[str, str]]:
        """Carrega credenciais do arquivo, renovando se necessário

        Returns:
            Dict com 'token' e 'refresh_token' válidos, ou None
        """
        if not AUTH_FILE.exists():
            return None

        try:
            data = json.loads(AUTH_FILE.read_text())
            token = data["token"]
            refresh_token = data.get("refresh_token")
        except (json.JSONDecodeError, KeyError):
            return None

        # Se token expirado, tentar renovar
        if self._is_token_expired(token):
            if not refresh_token:
                return None

            try:
                print("⏳ Token expirado, renovando automaticamente...")
                renewed = self._refresh_token(refresh_token)
                token = renewed["id_token"]
                refresh_token = renewed["refresh_token"]
                self.save_auth(token, refresh_token)
                print("✅ Token renovado com sucesso!")
            except RuntimeError as e:
                print(f"❌ {e}")
                return None

        return {
            "token": token,
            "refresh_token": refresh_token
        }

    def clear_auth(self) -> None:
        """Remove credenciais salvas"""
        if AUTH_FILE.exists():
            AUTH_FILE.unlink()
            print("✅ Credenciais removidas")
        else:
            print("ℹ️  Nenhuma credencial salva")

    def _find_free_port(self) -> int:
        """Encontra uma porta TCP livre"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", 0))
            return s.getsockname()[1]

    def login_interactive(self) -> str:
        """Executa login via browser com callback local

        Returns:
            Token JWT do Firebase

        Raises:
            RuntimeError: Se o login falhar ou timeout
        """
        port = self._find_free_port()
        token_holder = []
        callback_path = "/callback"

        class CallbackHandler(BaseHTTPRequestHandler):
            """Handler para receber o token do browser"""

            def _send_cors_headers(self):
                self.send_header("Access-Control-Allow-Origin", self.server.platform_url.rstrip("/"))
                self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")

            def do_OPTIONS(self):
                """CORS preflight"""
                self.send_response(204)
                self._send_cors_headers()
                self.end_headers()

            def do_POST(self):
                """Recebe token do callback"""
                if self.path != callback_path:
                    self.send_response(404)
                    self.end_headers()
                    return

                length = int(self.headers.get("Content-Length", 0))
                body = json.loads(self.rfile.read(length))
                token_holder.append(body)

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(b'{"ok": true}')

            def log_message(self, format, *args):
                pass  # Silenciar logs

        server = HTTPServer(("127.0.0.1", port), CallbackHandler)
        server.platform_url = self.platform_url

        def serve():
            while not token_holder:
                server.handle_request()

        thread = Thread(target=serve, daemon=True)
        thread.start()

        callback_url = f"http://localhost:{port}{callback_path}"
        login_url = f"{self.platform_url}/login?logout=1&cli_callback={quote(callback_url, safe='')}"

        print(f"🌐 Abrindo browser para login em: {self.platform_url}")
        print("   Se o browser não abrir, copie e cole esta URL:")
        print(f"   {login_url}")
        print()
        print("⏳ Aguardando login... (timeout em 120 segundos)")

        webbrowser.open(login_url)

        # Aguardar até 120 segundos
        for _ in range(240):
            if token_holder:
                break
            time.sleep(0.5)

        server.server_close()

        if not token_holder:
            raise RuntimeError("⏰ Timeout - nenhum token recebido em 120 segundos")

        callback_data = token_holder[0]
        token = callback_data["token"]
        refresh_token = callback_data.get("refreshToken")

        # Verificar se o token funciona
        print("🔍 Verificando token...")
        response = requests.get(
            f"{self.platform_url}/v1/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"❌ Token inválido (HTTP {response.status_code}). "
                "Tente novamente."
            )

        user_data = response.json()
        print(f"✅ Login bem-sucedido! Olá, {user_data.get('display_name', 'usuário')}!")

        self.save_auth(token, refresh_token)
        return token

    def status(self) -> None:
        """Mostra status da autenticação"""
        auth = self.load_auth()

        if not auth:
            print("❌ Não autenticado")
            print("   Execute: python lexflow_auth.py login")
            return

        token = auth["token"]

        # Decodificar token para mostrar info
        try:
            payload_b64 = token.split(".")[1]
            padding = 4 - len(payload_b64) % 4
            payload_b64 += "=" * padding
            payload = json.loads(base64.urlsafe_b64decode(payload_b64))

            import datetime
            exp_timestamp = payload.get("exp", 0)
            exp_date = datetime.datetime.fromtimestamp(exp_timestamp)
            remaining = exp_date - datetime.datetime.now()

            print("✅ Autenticado")
            print(f"   Email: {payload.get('email', 'N/A')}")
            print(f"   Nome: {payload.get('name', 'N/A')}")
            print(f"   Expira em: {exp_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   Tempo restante: {remaining.total_seconds() / 3600:.1f} horas")
            print(f"   Arquivo: {AUTH_FILE}")
            print()
            print("ℹ️  O token será renovado automaticamente quando necessário")

        except Exception:
            print("✅ Autenticado (erro ao decodificar detalhes)")


def main():
    """CLI principal"""
    import sys

    auth = LexFlowAuth()

    if len(sys.argv) < 2:
        print("🔐 LexFlow Authentication Manager")
        print()
        print("Uso:")
        print("  python lexflow_auth.py login    # Fazer login via browser")
        print("  python lexflow_auth.py status   # Ver status da autenticação")
        print("  python lexflow_auth.py logout   # Remover credenciais")
        print()
        print("Após o login, seus scripts Python usarão automaticamente")
        print("as credenciais salvas com renovação automática do token.")
        return

    command = sys.argv[1].lower()

    if command == "login":
        try:
            auth.login_interactive()
            print()
            print("🎉 Pronto! Agora você pode criar workflows sem se preocupar com tokens")
        except Exception as e:
            print(f"❌ Erro no login: {e}")
            sys.exit(1)

    elif command == "status":
        auth.status()

    elif command == "logout":
        auth.clear_auth()

    else:
        print(f"❌ Comando desconhecido: {command}")
        print("   Comandos válidos: login, status, logout")
        sys.exit(1)


if __name__ == "__main__":
    main()
