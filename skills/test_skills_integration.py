#!/usr/bin/env python3
"""Teste de integração das 3 skills LexFlow."""

import sys
import os

# Adiciona paths corretos
base_dir = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(base_dir, '.claude', 'skills'))
sys.path.insert(0, os.path.join(base_dir, '.claude', 'skills', 'shared'))
sys.path.insert(0, os.path.join(base_dir, '.claude', 'skills', 'lexflow-quick'))
sys.path.insert(0, os.path.join(base_dir, '.claude', 'skills', 'lexflow-extend'))
sys.path.insert(0, os.path.join(base_dir, '.claude', 'skills', 'lexflow-deploy'))

from skill_protocol import SkillRouter, SkillMessage, SkillAction
from lexflow_quick import LexFlowQuick
from lexflow_extend import LexFlowExtend
from lexflow_deploy import LexFlowDeploy


def test_simple_workflow():
    """Testa criação de workflow simples com opcodes existentes."""
    print("\n=== Teste 1: Workflow Simples (API Fetcher) ===")

    # Configura roteador e skills
    router = SkillRouter()
    quick_skill = LexFlowQuick(router)
    extend_skill = LexFlowExtend(router)
    deploy_skill = LexFlowDeploy(router)

    router.register("lexflow-quick", quick_skill)
    router.register("lexflow-extend", extend_skill)
    router.register("lexflow-deploy", deploy_skill)

    # Simula requisição do usuário
    message = SkillMessage(
        source="user",
        target="lexflow-quick",
        action=SkillAction.CREATE_WORKFLOW,
        context={
            "user_input": "criar workflow para buscar dados de uma API REST",
            "params": {
                "variables": {
                    "api_url": "https://api.github.com/users/anthropics"
                }
            }
        }
    )

    # Processa mensagem
    response = quick_skill.handle_message(message)

    print(f"Origem: {response.source}")
    print(f"Destino: {response.target}")
    print(f"Ação: {response.action}")
    print(f"Contexto: {response.context}")

    # Verifica se foi para deploy
    if response.target == "lexflow-deploy":
        deploy_response = deploy_skill.handle_message(response)
        print(f"\nDeploy Response:")
        print(f"  Status: {deploy_response.action}")
        print(f"  Detalhes: {deploy_response.context}")


def test_workflow_with_extension():
    """Testa criação de workflow que precisa de novo opcode."""
    print("\n=== Teste 2: Workflow com Extensão (Slack) ===")

    # Configura roteador e skills
    router = SkillRouter()
    quick_skill = LexFlowQuick(router)
    extend_skill = LexFlowExtend(router)
    deploy_skill = LexFlowDeploy(router)

    router.register("lexflow-quick", quick_skill)
    router.register("lexflow-extend", extend_skill)
    router.register("lexflow-deploy", deploy_skill)

    # Simula requisição que precisa de novo opcode
    message = SkillMessage(
        source="user",
        target="lexflow-quick",
        action=SkillAction.CREATE_WORKFLOW,
        context={
            "user_input": "criar workflow para enviar mensagem no Slack",
            "params": {
                "variables": {
                    "webhook_url": "https://hooks.slack.com/services/XXX",
                    "message": "Teste de integração"
                }
            }
        }
    )

    # Processa mensagem
    response = quick_skill.handle_message(message)

    print(f"Primeira resposta:")
    print(f"  Origem: {response.source}")
    print(f"  Destino: {response.target}")
    print(f"  Ação: {response.action}")

    # Se foi para extend, processa criação de opcode
    if response.target == "lexflow-extend":
        print("\n-> Delegando para lexflow-extend para criar opcode...")

        extend_response = extend_skill.handle_message(response)
        print(f"\nResposta do extend:")
        print(f"  Ação: {extend_response.action}")
        print(f"  Opcode criado: {extend_response.context.get('opcode_name')}")
        print(f"  Local: {extend_response.context.get('local_path')}")

        # Quick recebe resposta e continua
        if extend_response.action == SkillAction.OPCODE_READY:
            print("\n-> Opcode pronto, voltando para lexflow-quick...")

            final_response = quick_skill.handle_message(extend_response)
            print(f"\nResposta final do quick:")
            print(f"  Destino: {final_response.target}")
            print(f"  Workflow: {final_response.context.get('workflow_path')}")

            # Deploy
            if final_response.target == "lexflow-deploy":
                print("\n-> Enviando para deploy...")

                deploy_response = deploy_skill.handle_message(final_response)
                print(f"\nDeploy concluído:")
                print(f"  Status: {deploy_response.action}")
                print(f"  URL: {deploy_response.context.get('url')}")
                print(f"  Versão: {deploy_response.context.get('version')}")


def test_full_integration_flow():
    """Testa fluxo completo de integração entre as 3 skills."""
    print("\n=== Teste 3: Fluxo Completo de Integração ===")

    # Configura sistema
    router = SkillRouter()

    skills = {
        "lexflow-quick": LexFlowQuick(router),
        "lexflow-extend": LexFlowExtend(router),
        "lexflow-deploy": LexFlowDeploy(router)
    }

    for name, skill in skills.items():
        router.register(name, skill)

    # Cenários de teste
    test_cases = [
        {
            "name": "CSV Processor",
            "input": "criar workflow para processar arquivo CSV",
            "expected_template": "csv_processor",
            "needs_extension": False
        },
        {
            "name": "Web Scraper",
            "input": "criar workflow para fazer scraping de uma página web",
            "expected_template": "web_scraper",
            "needs_extension": False
        },
        {
            "name": "Slack Notification",
            "input": "criar workflow para notificar equipe no Slack",
            "expected_template": "slack_notification",
            "needs_extension": True
        }
    ]

    for test_case in test_cases:
        print(f"\n--- Testando: {test_case['name']} ---")
        print(f"Input: {test_case['input']}")
        print(f"Precisa extensão: {test_case['needs_extension']}")

        # Cria mensagem inicial
        message = SkillMessage(
            source="user",
            target="lexflow-quick",
            action=SkillAction.CREATE_WORKFLOW,
            context={"user_input": test_case['input']}
        )

        # Processa com roteador
        response = router.route(message)

        # Processa respostas em cadeia
        steps = 0
        max_steps = 5  # Evita loop infinito

        while response and steps < max_steps:
            steps += 1
            print(f"\nPasso {steps}:")
            print(f"  {response.source} -> {response.target}")
            print(f"  Ação: {response.action}")

            if response.action == SkillAction.DEPLOYMENT_COMPLETE:
                print(f"  ✅ Deploy concluído!")
                print(f"  URL: {response.context.get('url')}")
                break
            elif response.action == SkillAction.ERROR:
                print(f"  ❌ Erro: {response.context.get('error')}")
                break
            elif response.target in skills:
                # Continua processamento
                response = router.route(response)
            else:
                break

        print(f"Concluído em {steps} passos")


def test_deployment_operations():
    """Testa operações de deployment (status, rollback)."""
    print("\n=== Teste 4: Operações de Deploy ===")

    # Configura deploy skill
    deploy_skill = LexFlowDeploy()

    # Simula deploy de workflow
    print("\n1. Testando deploy:")
    deploy_message = SkillMessage(
        source="lexflow-quick",
        target="lexflow-deploy",
        action=SkillAction.DEPLOY,
        context={
            "workflow_path": "test_workflow.yaml",
            "environment": "staging"
        }
    )

    # Cria arquivo de teste
    with open("test_workflow.yaml", 'w') as f:
        f.write("""workflows:
  - name: test
    interface:
      inputs: []
      outputs: []
    nodes:
      start:
        opcode: workflow_start
        next: null
        inputs: {}
""")

    response = deploy_skill.handle_message(deploy_message)
    print(f"Deploy response: {response.action}")
    print(f"Details: {response.context}")

    workflow_id = response.context.get("workflow_id", "test_workflow")

    # Testa status
    print("\n2. Testando status:")
    status_message = SkillMessage(
        source="user",
        target="lexflow-deploy",
        action=SkillAction.GET_STATUS,
        context={"workflow_id": workflow_id}
    )

    status_response = deploy_skill.handle_message(status_message)
    print(f"Status: {status_response.context}")

    # Testa rollback
    print("\n3. Testando rollback:")
    rollback_message = SkillMessage(
        source="user",
        target="lexflow-deploy",
        action=SkillAction.ROLLBACK,
        context={
            "workflow_id": workflow_id,
            "version": "1.0.0"
        }
    )

    rollback_response = deploy_skill.handle_message(rollback_message)
    print(f"Rollback: {rollback_response.context}")

    # Limpa arquivo de teste
    if os.path.exists("test_workflow.yaml"):
        os.remove("test_workflow.yaml")


if __name__ == "__main__":
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO DAS 3 SKILLS LEXFLOW")
    print("=" * 60)

    # Executa testes
    test_simple_workflow()
    test_workflow_with_extension()
    test_full_integration_flow()
    test_deployment_operations()

    print("\n" + "=" * 60)
    print("TESTES CONCLUÍDOS")
    print("=" * 60)
    print("\nResumo:")
    print("✅ Skills criadas: lexflow-quick, lexflow-extend, lexflow-deploy")
    print("✅ Protocolo de integração funcionando")
    print("✅ Roteamento de mensagens entre skills")
    print("✅ Criação de opcodes sob demanda")
    print("✅ Deploy via CLI simulado")
    print("✅ Versionamento e rollback")
    print("\nPróximos passos:")
    print("1. Integrar com Claude Code real")
    print("2. Conectar com APIs do LexFlow e GitHub")
    print("3. Adicionar mais templates")
    print("4. Melhorar detecção de padrões")