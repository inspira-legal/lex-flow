---
name: lexflow-quick
description: Cria e edita workflows LexFlow rapidamente. Use quando usuário mencionar "criar workflow", "editar workflow", "modificar fluxo", "automatizar", "integrar", ou pedir para criar/modificar automações
version: 2.1.0
---

# LexFlow Quick - Criação e Edição Rápida de Workflows

Crio e edito workflows LexFlow de forma rápida e confiável usando templates validados.

## Minha Abordagem

### 1️⃣ Detecção Automática
Analiso seu pedido e identifico o tipo de workflow instantaneamente:
- **Mensagens**: Slack, Teams, Email
- **APIs**: Buscar dados, enviar requests
- **Processamento**: CSV, JSON, XML
- **Web**: Scraping, webhooks

### 2️⃣ Templates Validados
Uso apenas templates com opcodes comprovadamente funcionais:
- ✅ API REST (http_get, http_post)
- ✅ Processamento de dados (csv_parse, json_parse)
- ✅ Web scraping (html_parse, html_select)
- ✅ Controle de fluxo (control_if_else, control_foreach)

### 3️⃣ Extensão Sob Demanda
Se precisar de algo que não existe:
- Delego para `lexflow-extend` criar o opcode
- Aguardo criação automática
- Continuo criando seu workflow

### 4️⃣ Deploy Automático
Após criar workflow:
- Passo para `lexflow-deploy`
- Deploy via CLI (sempre!)
- Versionamento automático
- Retorno URL de acesso

## Quando Usar Outras Skills

**Não sou eu quem faz:**
- ❌ Criar novos opcodes → Use `lexflow-extend`
- ❌ Deploy manual → Use `lexflow-deploy`
- ❌ Rollback de versões → Use `lexflow-deploy`

## Como Trabalho

**Perguntas Mínimas**: Máximo 2 perguntas para esclarecer requisitos essenciais

**Criação Imediata**: Para casos comuns, crio sem perguntas

**Transparência**: Se algo não existir, aviso e crio automaticamente

---

## Padrões que Reconheço

### Criação de Workflows

#### Mensagens & Notificações
```
"enviar mensagem no Slack"
"notificar equipe no Teams"
"disparar email quando X"
```
→ Template: notification (precisa de extensão se opcode não existir)

#### APIs & Integrações
```
"buscar dados da API"
"chamar endpoint REST"
"integrar com webhook"
```
→ Template: api_integration (opcodes nativos)

#### Processamento de Dados
```
"processar arquivo CSV"
"transformar JSON"
"extrair dados de XML"
```
→ Template: data_processing (opcodes nativos)

#### Web & Scraping
```
"extrair dados de página web"
"fazer scraping de site"
"monitorar mudanças em HTML"
```
→ Template: web_scraper (opcodes nativos)

### Edição de Workflows

#### Adicionar Elementos
```
"adicionar canal #dev ao workflow slack-notifier"
"incluir também o email no fluxo de notificações"
"adicionar validação antes do processamento"
```
→ Busca workflow, adiciona novo elemento, re-deploya

#### Remover Elementos
```
"remover o canal #test do workflow"
"tirar a validação de email"
"deletar o node de logging"
```
→ Busca workflow, remove elemento, re-deploya

#### Alterar Valores
```
"mudar URL da API para https://nova-api.com"
"trocar intervalo de execução para 5 minutos"
"alterar mensagem de erro padrão"
```
→ Busca workflow, atualiza valor, re-deploya

#### Otimizar
```
"otimizar workflow para rodar mais rápido"
"melhorar performance do processamento"
"adicionar cache ao workflow"
```
→ Busca workflow, aplica otimizações, re-deploya

---

## Exemplos de Uso

### Exemplo 1: Criar Workflow

**Você diz:**
> "criar workflow para enviar mensagem no Slack quando API retornar erro"

**Eu faço:**
1. Detecto: notificação Slack + webhook trigger
2. Verifico: opcode `slack_send` não existe
3. Delego para `lexflow-extend` criar opcode
4. Recebo opcode pronto
5. Crio workflow completo
6. Passo para `lexflow-deploy`
7. Retorno: "✅ Workflow deployado em [URL]"

**Perguntas (se necessário):**
- "Qual o webhook URL do Slack?"
- "Qual canal quer notificar?"

### Exemplo 2: Editar Workflow

**Você diz:**
> "editar workflow slack-notifier para enviar também no canal #dev"

**Eu faço:**
1. Busco workflow "slack-notifier"
2. Carrego arquivo YAML
3. Detecto modificação: adicionar canal
4. Identifico node de envio Slack
5. Adiciono "#dev" à lista de canais
6. Salvo versão editada
7. Passo para `lexflow-deploy` (nova versão)
8. Retorno: "✅ Workflow atualizado para v1.2.0 em [URL]"

**Perguntas:** 0 (modificação clara)

### Exemplo 3: Otimizar Workflow

**Você diz:**
> "otimizar workflow csv-processor para processar mais rápido"

**Eu faço:**
1. Busco workflow "csv-processor"
2. Analiso estrutura atual
3. Identifico oportunidades: paralelização, cache
4. Aplico otimizações
5. Passo para `lexflow-deploy`
6. Retorno: "✅ Workflow otimizado - v1.3.0 (30% mais rápido)"

Máximo 2 perguntas quando necessário!

---

## Arquitetura Técnica

Veja detalhes em: [modules/README.md](modules/README.md)

Templates disponíveis: [templates/](templates/)

Protocolo de integração: [../shared/skill_protocol.py](../shared/skill_protocol.py)