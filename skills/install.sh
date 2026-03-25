#!/bin/bash

# ============================================================
# LexFlow Skills - Instalador Automático
# ============================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cores
print_color() {
    color=$1
    message=$2
    echo -e "${color}${message}${NC}"
}

# Banner
clear
print_color "$BLUE" "============================================================"
print_color "$BLUE" "          LexFlow Skills para Claude Code"
print_color "$BLUE" "          Instalador Automático v1.0.0"
print_color "$BLUE" "============================================================"
echo

# 1. Verificar pré-requisitos
print_color "$YELLOW" "📋 Verificando pré-requisitos..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_color "$RED" "❌ Python 3 não encontrado. Por favor, instale Python 3.9+"
    exit 1
fi
print_color "$GREEN" "✅ Python encontrado: $(python3 --version)"

# Verificar uv
if ! command -v uv &> /dev/null; then
    print_color "$YELLOW" "⚠️  uv não encontrado. Instalando..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
print_color "$GREEN" "✅ uv encontrado"

# 2. Detectar diretório de destino
print_color "$YELLOW" "\n📁 Onde você quer instalar as skills?"
echo "1) Diretório atual: $(pwd)"
echo "2) Outro diretório"
read -p "Escolha (1 ou 2): " choice

if [ "$choice" = "2" ]; then
    read -p "Digite o caminho completo: " TARGET_DIR
else
    TARGET_DIR=$(pwd)
fi

# Criar estrutura de diretórios
print_color "$YELLOW" "\n🔧 Criando estrutura de diretórios..."
mkdir -p "$TARGET_DIR/.claude/skills"

# 3. Copiar arquivos das skills
print_color "$YELLOW" "📦 Copiando skills..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copiar cada skill
for skill in lexflow-quick lexflow-extend lexflow-deploy shared; do
    if [ -d "$SCRIPT_DIR/$skill" ]; then
        cp -r "$SCRIPT_DIR/$skill" "$TARGET_DIR/.claude/skills/"
        print_color "$GREEN" "✅ Skill $skill copiada"
    else
        print_color "$YELLOW" "⚠️  Skill $skill não encontrada em $SCRIPT_DIR"
    fi
done

# 4. Copiar arquivos de suporte
print_color "$YELLOW" "\n📄 Copiando arquivos de suporte..."

# Copiar README
if [ -f "$SCRIPT_DIR/README.md" ]; then
    cp "$SCRIPT_DIR/README.md" "$TARGET_DIR/.claude/skills/"
fi

# Copiar guia de integração
if [ -f "$SCRIPT_DIR/INTEGRATION_GUIDE.md" ]; then
    cp "$SCRIPT_DIR/INTEGRATION_GUIDE.md" "$TARGET_DIR/.claude/skills/"
fi

# 5. Criar arquivo de configuração
print_color "$YELLOW" "\n⚙️  Configurando ambiente..."

ENV_FILE="$TARGET_DIR/.env.lexflow"

if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" << 'EOF'
# ============================================================
# Configuração LexFlow Skills
# ============================================================

# API LexFlow
LEXFLOW_API_URL=https://api.lexflow.com
LEXFLOW_API_KEY=seu_token_aqui

# GitHub (para PRs de opcodes customizados)
GITHUB_TOKEN=ghp_seu_token_aqui
GITHUB_REPO=seu-org/lexflow-opcodes

# Configurações de ambiente
DEFAULT_ENVIRONMENT=production
AUTO_DEPLOY=false
VERBOSE_LOGGING=false

# Diretórios
WORKFLOWS_DIR=./workflows
CUSTOM_OPCODES_DIR=./.lexflow/custom_opcodes
EOF
    print_color "$GREEN" "✅ Arquivo de configuração criado: $ENV_FILE"
    print_color "$YELLOW" "   ⚠️  Não esqueça de adicionar suas credenciais!"
else
    print_color "$BLUE" "ℹ️  Arquivo de configuração já existe"
fi

# 6. Criar diretórios de trabalho
print_color "$YELLOW" "\n📂 Criando diretórios de trabalho..."

mkdir -p "$TARGET_DIR/workflows/development"
mkdir -p "$TARGET_DIR/workflows/staging"
mkdir -p "$TARGET_DIR/workflows/production"
mkdir -p "$TARGET_DIR/workflows/archive"
mkdir -p "$TARGET_DIR/.lexflow/custom_opcodes"

print_color "$GREEN" "✅ Diretórios criados"

# 7. Instalar dependências Python (se houver requirements)
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    print_color "$YELLOW" "\n📦 Instalando dependências Python..."
    cd "$TARGET_DIR"
    uv pip install -r "$SCRIPT_DIR/requirements.txt"
    print_color "$GREEN" "✅ Dependências instaladas"
fi

# 8. Executar testes
print_color "$YELLOW" "\n🧪 Executando testes de integração..."

# Copiar arquivo de teste
if [ -f "$SCRIPT_DIR/test_skills_integration.py" ]; then
    cp "$SCRIPT_DIR/test_skills_integration.py" "$TARGET_DIR/"

    cd "$TARGET_DIR"
    if python3 test_skills_integration.py > /dev/null 2>&1; then
        print_color "$GREEN" "✅ Testes passaram com sucesso!"
    else
        print_color "$YELLOW" "⚠️  Alguns testes falharam. Execute manualmente para ver detalhes:"
        print_color "$YELLOW" "   python3 test_skills_integration.py"
    fi
fi

# 9. Criar comando de atalho (opcional)
print_color "$YELLOW" "\n🎯 Deseja criar um comando 'lexflow' para acesso rápido? (s/n)"
read -p "> " create_alias

if [ "$create_alias" = "s" ] || [ "$create_alias" = "S" ]; then
    SHELL_RC=""

    # Detectar shell
    if [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    fi

    if [ -n "$SHELL_RC" ]; then
        echo "" >> "$SHELL_RC"
        echo "# LexFlow Skills" >> "$SHELL_RC"
        echo "alias lexflow='cd $TARGET_DIR && python3 -m lexflow_cli'" >> "$SHELL_RC"
        print_color "$GREEN" "✅ Comando 'lexflow' adicionado ao $SHELL_RC"
        print_color "$YELLOW" "   Execute: source $SHELL_RC"
    fi
fi

# 10. Instruções finais
echo
print_color "$BLUE" "============================================================"
print_color "$GREEN" "🎉 Instalação Concluída!"
print_color "$BLUE" "============================================================"
echo
print_color "$YELLOW" "📝 Próximos passos:"
echo
echo "1. Configure suas credenciais em: $ENV_FILE"
echo "2. Teste a instalação:"
echo "   cd $TARGET_DIR"
echo "   python3 test_skills_integration.py"
echo "3. Use com Claude Code:"
echo "   - As skills serão detectadas automaticamente"
echo "   - Fale naturalmente: 'criar workflow para...'"
echo
print_color "$BLUE" "📚 Documentação completa em:"
print_color "$BLUE" "   $TARGET_DIR/.claude/skills/README.md"
echo
print_color "$GREEN" "⭐ Não esqueça de dar uma estrela no GitHub!"
print_color "$BLUE" "   https://github.com/seu-usuario/lexflow-skills"
echo
print_color "$BLUE" "============================================================"