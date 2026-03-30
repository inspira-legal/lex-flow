---
name: lexflow-extend
description: Cria novos opcodes para LexFlow. Use quando usuário mencionar "criar opcode", "novo opcode", "estender", ou quando lexflow-quick precisar de opcode inexistente
version: 1.0.0
---

# LexFlow Extend - Criador de Opcodes

Crio novos opcodes para estender as capacidades do LexFlow quando necessário.

## O Que Faço

Quando um workflow precisa de funcionalidade que não existe nativamente, eu:

1. **Analiso o requisito** - Entendo o que o opcode precisa fazer
2. **Gero implementação** - Código Python completo e funcional
3. **Crio documentação** - Docs detalhados com exemplos
4. **Gero testes** - Testes automatizados
5. **Preparo PR** - Estrutura pronta para contribuir ao LexFlow

## Tipos de Opcodes

### 🔧 Wrappers (Recomendado)
Encapsulam opcodes existentes para simplificar uso:

**Exemplo: slack_send**
```python
# Wrapper em torno de http_post
# Simplifica envio para Slack
slack_send(webhook_url, message)
  ↓
http_post(url=webhook_url, json={"text": message})
```

**Vantagens:**
- Rápido de criar (< 1 minuto)
- Usa funcionalidade comprovada
- Menos bugs

### ⚙️ Nativos (Quando Necessário)
Implementação completamente nova:

**Exemplo: database_query**
```python
# Implementação do zero
# Conecta e consulta banco de dados
database_query(connection_string, sql)
```

**Quando usar:**
- Funcionalidade completamente nova
- Sem opcode base disponível
- Requer lógica complexa

## Como Trabalho

### Ativação Automática
Sou ativado automaticamente por `lexflow-quick` quando falta um opcode.

**Você nem percebe!**

```
Você: "criar workflow para Slack"
  ↓
lexflow-quick detecta: precisa de slack_send
  ↓
lexflow-extend cria slack_send automaticamente
  ↓
lexflow-quick continua criando workflow
  ↓
Pronto! Workflow funcionando
```

### Ativação Manual
Pode me chamar diretamente:

```
"criar opcode para enviar mensagem no Jira"
"preciso de um opcode que consulte banco PostgreSQL"
"estender LexFlow com suporte a MongoDB"
```

## O Que Gero

### 1. Código Python
```python
class SlackSendOpcode:
    """Envia mensagens para Slack."""

    def execute(self, webhook_url: str, message: str):
        # Implementação completa
        pass
```

### 2. Documentação
```markdown
# slack_send

Envia mensagens para canais Slack usando webhooks.

## Inputs
- webhook_url (string): URL do webhook
- message (string): Mensagem a enviar

## Outputs
- success (boolean): Se enviou com sucesso

## Exemplo
[Exemplo completo de uso]
```

### 3. Testes
```python
def test_slack_send():
    """Testa envio de mensagem."""
    result = slack_send(
        webhook_url="https://...",
        message="Test"
    )
    assert result["success"] == True
```

### 4. Deploy Local
Opcode fica disponível **imediatamente** para uso local enquanto PR é revisado.

## Integração com GitHub

### PR Automático (Simulado)
Preparo estrutura completa para PR:

```
lexflow-opcodes/
├── opcodes/slack_send.py       # Implementação
├── docs/slack_send.md          # Documentação
├── tests/test_slack_send.py    # Testes
└── examples/slack_send.yaml    # Exemplo de uso
```

**Status:** Atualmente simulado, pronto para integração real com GitHub API.

## Opcodes Que Posso Criar

### Comunicação
- Slack, Teams, Discord
- Email (SMTP, SendGrid)
- SMS (Twilio)

### Databases
- PostgreSQL, MySQL
- MongoDB, Redis
- SQLite

### Cloud Services
- AWS (S3, Lambda, SQS)
- GCP (Storage, Pub/Sub)
- Azure (Blob, Queue)

### Project Management
- Jira, Linear
- GitHub Issues
- Trello

### Qualquer outro!
Descreva o que precisa e eu crio.

## Arquitetura Técnica

Detalhes de implementação: [modules/README.md](modules/README.md)

Templates de geração: [templates/](templates/)

## Restrições

**Não crio:**
- ❌ Opcodes maliciosos
- ❌ Operações destrutivas sem confirmação
- ❌ Código que viola privacidade

**Sempre:**
- ✅ Valido inputs
- ✅ Trato erros apropriadamente
- ✅ Documento completamente