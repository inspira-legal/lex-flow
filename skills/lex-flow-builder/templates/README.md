# LexFlow Templates

Esta pasta contém templates de arquivos Python que a skill `lex-flow-builder` copia automaticamente para os projetos dos usuários.

## Arquivos

### `lexflow_auth.py`
Sistema de autenticação com login via browser e auto-refresh de token.

**Funcionalidades:**
- Login interativo via browser (comando: `python lexflow_auth.py login`)
- Salva credenciais em `~/.config/lexflow/auth.json`
- Renovação automática de token Firebase
- Comandos: `login`, `status`, `logout`

**Quando a skill usa:**
- Na primeira vez que o usuário pede para criar um workflow
- Apenas se `~/.config/lexflow/auth.json` não existir

### `lexflow_client.py`
Cliente Python para API do LexFlow com auto-refresh integrado.

**Funcionalidades:**
- Carrega credenciais automaticamente de `~/.config/lexflow/auth.json`
- Renova token automaticamente quando expira
- Métodos para criar, editar e executar workflows
- Função `get_client()` para uso simples

**Quando a skill usa:**
- Sempre que criar um novo projeto
- Template para usuários chamarem nos seus scripts

### `requirements.txt`
Dependências Python necessárias.

**Conteúdo:**
- `requests` - Para chamadas HTTP à API
- `pyyaml` - Para parsing de workflows YAML

## Como a Skill Usa os Templates

### Fluxo de Setup Automático

1. **Usuário pede**: "Crie um workflow para enviar emails"

2. **Skill verifica**: `~/.config/lexflow/auth.json` existe?
   - ✅ SIM: Pula setup, vai direto para discovery
   - ❌ NÃO: Inicia setup abaixo

3. **Skill copia templates** para pasta do usuário:
   ```
   Write lexflow_auth.py (do template)
   Write lexflow_client.py (do template)
   Write requirements.txt (do template)
   ```

4. **Skill guia login**:
   ```
   "Execute: python lexflow_auth.py login"
   [Aguarda confirmação do usuário]
   ```

5. **Skill cria workflow**:
   - Faz discovery
   - Gera YAML
   - Salva no LexFlow usando `lexflow_client.py`

## Vantagens desta Abordagem

✅ **Zero configuração manual** - Usuário não precisa criar arquivos
✅ **Pasta vazia funciona** - Skill providencia tudo
✅ **Login uma vez só** - Token renova automaticamente
✅ **Reutilizável** - Mesma auth serve para vários projetos
✅ **Sem tokens manuais** - Nunca mais copiar do DevTools

## Customização

Se precisar alterar os templates:

1. Edite os arquivos nesta pasta
2. A skill vai copiar a versão atualizada em novos projetos
3. Projetos existentes continuam com a versão antiga (a menos que o usuário delete e recrie)

## Troubleshooting

### "Template não encontrado"
Verifique se os arquivos existem em `skills/lex-flow-builder/templates/`

### "Erro ao copiar template"
Verifique permissões de escrita na pasta do usuário

### "Token não renova"
Verifique se `FIREBASE_API_KEY` está correto no `lexflow_auth.py`
