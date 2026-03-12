---
name: lex-flow-builder
description: Guia desenvolvedores na criacao de workflows LexFlow desde discovery ate deploy. Cobre coleta de requisitos, design de fluxo, implementacao YAML, validacao e instrucoes de deploy. Use quando usuario mencionar "criar workflow", "lex-flow", "fluxo", "automacao", "n8n", "workflow visual" ou solicitar construcao de processos automatizados.
---

# LexFlow Workflow Builder

Guide users through creating LexFlow workflows - a visual, stack-based programming tool for process automation (similar to N8N).

## Tech Stack do LexFlow

- **Backend**: Python (lexflow-core, lexflow-cli)
- **Frontend**: TypeScript (lexflow-web editor visual)
- **Formato**: Workflows em YAML/JSON
- **Arquitetura**: Node-based graph com opcodes

## 0. SETUP INICIAL (Executar UMA VEZ por projeto)

Antes de criar workflows, verificar se o projeto está configurado com autenticação.

### Verificar autenticação existente

```bash
ls ~/.config/lexflow/auth.json
```

**Se o arquivo EXISTE**: Pular para seção 1 (DISCOVERY)

**Se o arquivo NÃO EXISTE**: Executar setup abaixo

### Setup do projeto (pasta vazia ou sem configuração)

**PASSO 1: Criar arquivos base do projeto**

Use o Write tool para criar estes 3 arquivos na pasta do usuário:

1. **lexflow_auth.py** - Copiar de `templates/lexflow_auth.py`
2. **lexflow_client.py** - Copiar de `templates/lexflow_client.py`
3. **requirements.txt** - Copiar de `templates/requirements.txt`

**PASSO 2: Instalar dependências**

```bash
pip install -r requirements.txt
```

**PASSO 3: Fazer login (UMA VEZ)**

Guiar o usuário:

```
Para criar workflows no LexFlow, você precisa fazer login uma única vez.

Execute este comando:
  python lexflow_auth.py login

Isso vai:
1. Abrir o browser
2. Você faz login com sua conta Inspira
3. As credenciais são salvas em ~/.config/lexflow/auth.json
4. O token é renovado AUTOMATICAMENTE quando necessário

Após o login, você nunca mais precisa se preocupar com tokens!
```

**PASSO 4: Aguardar confirmação**

Pergunte ao usuário: "Conseguiu fazer o login com sucesso?"

- ✅ Se SIM: Continuar para seção 1 (DISCOVERY)
- ❌ Se NÃO: Ajudar com troubleshooting:
  - Verificar se o browser abriu
  - Verificar mensagem de erro
  - Sugerir: `python lexflow_auth.py status`

### Verificar configuração

Para confirmar que está tudo OK:

```bash
python lexflow_auth.py status
```

Deve mostrar email do usuário e tempo restante do token.

**IMPORTANTE**:
- Este setup é feito UMA VEZ por máquina (não por projeto)
- O token é compartilhado entre todos os projetos
- Renovação é automática - usuário não precisa fazer nada

## Processo de Criação (Ciclo Completo)

### 1. DISCOVERY (Entender o Contexto)

Antes de criar qualquer workflow, SEMPRE faça discovery através de perguntas **SIMPLES e INTUITIVAS**.

**PRINCÍPIOS DE COMUNICAÇÃO**:
- ❌ Evite jargão técnico desnecessário
- ✅ Use linguagem do dia-a-dia
- ❌ Não pergunte "Qual opcode usar?"
- ✅ Pergunte "O que você quer fazer com os dados?"
- ❌ Não pergunte sobre "branches" ou "nodes"
- ✅ Pergunte "E se acontecer um erro, o que deve fazer?"

**Exemplos de perguntas INTUITIVAS**:

```
❌ RUIM (muito técnico):
"Você precisa de um control_foreach ou control_for?"

✅ BOM (intuitivo):
"Você tem uma lista de itens para processar?
- Sim, processar cada item da lista
- Sim, repetir X vezes
- Não, executar apenas uma vez"
```

```
❌ RUIM:
"Precisa de http_post com headers customizados?"

✅ BOM:
"Você vai se conectar com algum sistema externo?
- Sim, Slack
- Sim, Jira
- Sim, outra API (qual?)
- Não, apenas processar dados internos"
```

**Perguntas essenciais (em linguagem simples)**:

Use o AskUserQuestion tool:

1. **Objetivo**: "O que esse fluxo deve fazer no final?"
   - Ex: "Enviar notificação", "Processar arquivo", "Criar relatório"

2. **Entrada de dados**: "De onde vêm as informações?"
   - Ex: "Usuário digita", "Arquivo", "Sistema externo"

3. **Saída esperada**: "O que deve acontecer ao final?"
   - Ex: "Enviar email", "Salvar em arquivo", "Mostrar resultado"

4. **Condições**: "Tem alguma situação especial?"
   - Ex: "Se valor for maior que 100, fazer X"

5. **Repetições**: "Precisa fazer algo várias vezes?"
   - Ex: "Para cada cliente", "Repetir 10 vezes"

6. **Sistemas externos**: "Vai conectar com algum sistema?"
   - Ex: "Slack", "Jira", "Planilhas Google", "Email"

**IMPORTANTE**:
- Não assuma nada. Sempre confirme com o usuário.
- Use exemplos concretos do contexto do usuário
- Se usuário usar termo técnico, pode usar termos técnicos de volta
- Se usuário usar linguagem simples, mantenha simples

### 2. DESIGN (Planejar o Fluxo)

Use o TodoWrite tool para criar um plano estruturado:

```
Exemplo de plano:
1. Definir inputs/outputs do workflow
2. Mapear nodes principais (ex: leitura → processamento → saída)
3. Identificar opcodes necessários (ver reference.md)
4. Planejar variáveis de estado
5. Definir controle de fluxo (loops, branches)
```

Apresente o design textual ou visual para aprovação.

**IMPORTANTE**: Adapte visualização ao perfil do usuário!

#### Para usuários NÃO TÉCNICOS - Use linguagem simples:

```
📋 FLUXO: Enviar Alerta de Vendas

1. 📥 RECEBER
   └─ Valor da venda

2. 🔍 VERIFICAR
   └─ O valor é maior que R$ 1000?

   ┌─ SIM → 3. Enviar alerta
   └─ NÃO → 4. Apenas registrar

3. 📢 ENVIAR ALERTA
   └─ Mensagem no Slack: "Venda grande: R$ [valor]"

4. ✅ FINALIZAR
   └─ Mostrar "Processado com sucesso"
```

#### Para usuários TÉCNICOS - Pode incluir detalhes:

```
WORKFLOW: sales_alert_flow

START
  ↓
GET_INPUT (variable: sale_value)
  ↓
COMPARE (operator_greater_than)
  ├─ sale_value > 1000
  ↓
IF_ELSE (control_if_else)
  ├─ TRUE  → SEND_SLACK (http_post)
  └─ FALSE → LOG_ONLY (io_print)
  ↓
END

Opcodes: workflow_start, operator_greater_than,
         control_if_else, http_post, io_print
Variables: sale_value, alert_sent
```

#### Para AMBOS - Após aprovação, mostrar resumo:

```
✅ Fluxo planejado!

O que vai fazer:
- Recebe valor de venda
- Se > R$ 1000: envia alerta no Slack
- Se ≤ R$ 1000: apenas registra
- Mostra confirmação final

Próximo passo: Criar o código YAML
Você aprova? (sim/não/mudar algo)
```

### 3. IMPLEMENTAÇÃO (Escrever o YAML)

Siga a estrutura padrão do LexFlow (consulte reference.md e examples.md):

```yaml
workflows:
  - name: main
    interface:
      inputs: ["input_var"]  # Lista de nomes de inputs
      outputs: []

    variables:
      temp_var: initial_value  # Declaração direta: nome: valor
      result: null

    nodes:
      start:
        opcode: workflow_start  # ⚠️ SEMPRE o primeiro node!
        next: node1
        inputs: {}

      node1:
        opcode: io_print
        next: node2
        inputs:
          STRING:  # ⚠️ Parâmetros em MAIÚSCULAS quando necessário
            literal: "Hello"

      compute:
        opcode: operator_add
        isReporter: true  # ⚠️ Necessário para nodes que retornam valores
        inputs:
          left:
            literal: 10
          right:
            variable: temp_var

      node2:
        opcode: data_set_variable_to
        next: null
        inputs:
          VARIABLE:
            literal: "result"
          VALUE:
            node: compute  # Usa resultado de outro node
```

**Padrões Importantes** (validados com exemplos oficiais):
- ⚠️ **SEMPRE comece com `workflow_start`** como primeiro node
- Nodes são **objetos** (não arrays): `nodes: { start: {}, node1: {} }`
- Inputs usam **3 formas**: `literal:`, `variable:`, `node:`
- Alguns parâmetros usam **MAIÚSCULAS** (ex: `STRING`, `CONDITION`, `VARIABLE`)
- **Reporter nodes** precisam de `isReporter: true`
- Control flow usa `branch:` não `node:` (ex: `THEN: { branch: nome_branch }`)

### 4. VALIDAÇÃO (Testar o Workflow)

Antes de finalizar:

1. **Validar YAML**: Verificar sintaxe e estrutura
2. **Testar execução**: Usar lexflow-cli se disponível
3. **Review de opcodes**: Confirmar que todos os opcodes existem (ver reference.md)
4. **Checklist de qualidade**:
   - [ ] Todos os nodes têm IDs únicos?
   - [ ] Inputs/outputs estão definidos corretamente?
   - [ ] Controle de fluxo está correto (next/branches)?
   - [ ] Variáveis declaradas antes do uso?
   - [ ] Error handling considerado?

### 5. DOCUMENTAÇÃO (Explicar o Workflow)

Gere uma documentação clara e de fácil entendimento em Markdown para o flow construído, contendo:
- **Objetivo**: O que o flow faz.
- **Pré-requisitos**: Configurações ou credenciais necessárias.
- **Estrutura**: Explicação simples de cada etapa/node do fluxo.
- **Utilização**: Como executar ou importar o workflow.

### 6. DEPLOY (Disponibilizar o Workflow)

**ANTES DE QUALQUER COISA**: Verificar ambiente do usuário automaticamente:

```bash
# Checar se existe infraestrutura de API
ls lexflow_client.py 2>/dev/null
ls .env 2>/dev/null
```

**Se arquivos existirem** → Deploy automático (Opção A)
**Se NÃO existirem** → Perguntar preferência do usuário

### 6. DEPLOY (Entregar o Workflow)

Opções de deploy:

**Opção A - CLI Local**:
```bash
lexflow workflow.yaml
```

**Opção B - Programático**:
```python
from lexflow import Parser, Engine

async def run():
    parser = Parser()
    program = parser.parse_file("workflow.yaml")
    engine = Engine(program)
    result = await engine.run()
    return result
```

**Opção C - Web Editor**:
- Importar o YAML no editor visual
- Testar visualmente
- Publicar

**Opção D - API (Criar/Atualizar Workflows Remotamente)** ⭐ RECOMENDADO:

Se o usuário tem o ambiente configurado com `lexflow_client.py` e `.env`:

```bash
# Criar workflow novo do zero
python create_workflow.py workflow.yaml "Nome do Workflow"

# Atualizar workflow existente
python save_workflow.py <workflow_id> workflow.yaml "Mensagem de commit"

# Testar temporariamente (não salva)
python lexflow_client.py workflow.yaml
```

**IMPORTANTE**: Sempre que criar um workflow, **execute automaticamente** o deploy via `create_workflow.py` ao final, para que o workflow já fique disponível no LexFlow dashboard!

## Lidando com Funcionalidades Não Disponíveis

Quando o usuário pedir algo que não tem opcode direto:

### 1. **Identificar alternativas viáveis**

**Cenário comum**: "Quero buscar dados do Jira"

❌ **NÃO diga**: "Não existe opcode jira_get_issue"

✅ **DIGA**: "Posso fazer isso de 2 formas:
- **Opção 1**: Conectar com a API do Jira (mais completo, precisa de token)
- **Opção 2**: Você já tem os dados em arquivo? Posso ler e processar

Qual faz mais sentido para você?"

### 2. **Usar AskUserQuestion para explorar soluções**

```
Exemplo de pergunta intuitiva:

"Para conectar com [Sistema X], preciso fazer uma chamada de API.
Você tem:
- Token/senha de acesso? (posso configurar agora)
- Alguém que pode fornecer? (te mostro o que precisa)
- Prefere outro jeito? (podemos pensar em alternativa)"
```

### 3. **Explicar limitações de forma clara**

Se algo realmente não for possível:

❌ **NÃO diga**: "LexFlow não suporta esse opcode de machine learning"

✅ **DIGA**: "Entendi! Você quer [fazer previsão com IA].
Atualmente o LexFlow faz bem:
- Conectar com APIs de IA (Google, OpenAI)
- Processar dados antes/depois da IA
- Tomar decisões baseadas no resultado

Posso criar um fluxo que:
1. Prepara seus dados
2. Envia para [API de IA]
3. Processa o resultado

Faz sentido?"

### 4. **Soluções alternativas comuns**

| Usuário quer | Solução |
|-------------|---------|
| "Conectar com [Sistema]" | → Usar `http_post`/`http_get` com API |
| "Fazer cálculo complexo" | → Combinar operadores (`operator_add`, `operator_multiply`) |
| "Processar cada item" | → Loop com `control_foreach` |
| "Enviar notificação" | → API do Slack/Email via HTTP |
| "Ler arquivo" | → `io_read` ou processar via HTTP se for GCS/S3 |

## Boas Práticas

1. **Modularidade**: Crie workflows pequenos e reutilizáveis
2. **Nomenclatura**: Use IDs descritivos (ex: `fetch_data`, `process_items`)
3. **Documentação**: Adicione comentários no YAML quando necessário
4. **Versionamento**: Sugira salvar versões do workflow
5. **Error Handling**: Sempre considere casos de erro
6. **Performance**: Evite loops desnecessários ou nodes redundantes
7. **Comunicação Clara**: Adapte linguagem ao nível técnico do usuário

## Integração com Recursos

Durante o desenvolvimento, consulte:

- `reference.md`: Catálogo completo de opcodes disponíveis
- `examples.md`: Templates de workflows comuns
- Repositório: https://github.com/inspira-legal/lex-flow

## Workflow de Trabalho Recomendado

```
1. User descreve necessidade
   ↓
2. Discovery via AskUserQuestion (coletar requisitos)
   ↓
3. Criar TodoList com plano estruturado
   ↓
4. Apresentar design textual/visual para aprovação
   ↓
5. Implementar YAML do workflow
   ↓
6. Validar e revisar
   ↓
7. Ajustar com base em feedback
   ↓
8. Gerar documentação explicativa do fluxo
   ↓
9. Entregar workflow + documentação + instruções de deploy
```

## Adaptação ao Nível do Usuário

**Detectar automaticamente o perfil técnico**:

### Sinais de usuário NÃO TÉCNICO:
- Usa termos como "mandar mensagem", "puxar dados", "fazer conta"
- Foca no resultado final, não no processo
- Pergunta "pode fazer X?" sem mencionar tecnologias

**Como comunicar**:
- ✅ Use metáforas do dia-a-dia
- ✅ Explique o "o quê" antes do "como"
- ✅ Mostre exemplos visuais do fluxo
- ✅ Evite termos: opcode, node, branch, reporter
- ✅ Use: etapa, passo, se/então, repetir

**Exemplo**:
```
"Vou criar um fluxo com 3 etapas:
1. Buscar dados do sistema
2. Verificar se valor > 100
3. Se sim: enviar alerta no Slack"
```

### Sinais de usuário TÉCNICO:
- Menciona: "API", "endpoint", "JSON", "loop", "condicional"
- Pergunta sobre estrutura, performance, error handling
- Já usou ferramentas similares (n8n, Zapier, código)

**Como comunicar**:
- ✅ Pode usar termos técnicos
- ✅ Mostrar estrutura YAML desde cedo
- ✅ Explicar opcodes e arquitetura
- ✅ Oferecer otimizações e boas práticas

**Exemplo**:
```
"Vou usar http_post com headers de auth para o endpoint do Jira.
O response vem como dict com {status, json}, então vou extrair
o campo 'issues' com dict_get e iterar com control_foreach."
```

### Quando em dúvida:
- Comece SIMPLES
- Se usuário pedir mais detalhes técnicos → aumente complexidade
- Se usuário parecer confuso → simplifique

## Quando NÃO Usar Esta Skill

- Para bugs ou debugging de workflows existentes (use problem-solver skill)
- Para explicar conceitos gerais de programação (use conversa normal)
- Para tarefas não relacionadas a workflows

## Exemplo de Uso

```
User: "Quero criar um workflow que lê arquivos CSV e envia por email"