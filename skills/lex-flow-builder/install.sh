#!/bin/bash

# Script de Instalação Automática - lex-flow-builder
# Uso: bash install.sh

set -e  # Parar se houver erro

echo "🚀 Instalando lex-flow-builder skill para Claude Code..."
echo ""

# Detectar sistema operacional
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Cygwin;;
    MINGW*)     MACHINE=MinGw;;
    MSYS*)      MACHINE=Msys;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

echo "Sistema detectado: ${MACHINE}"
echo ""

# Definir diretório de skills baseado no OS
if [[ "$MACHINE" == "Mac" || "$MACHINE" == "Linux" ]]; then
    SKILLS_DIR="$HOME/.claude/skills"
elif [[ "$MACHINE" == "MinGw" || "$MACHINE" == "Msys" || "$MACHINE" == "Cygwin" ]]; then
    SKILLS_DIR="$USERPROFILE/.claude/skills"
else
    echo "❌ Sistema operacional não suportado: ${MACHINE}"
    exit 1
fi

echo "📁 Diretório de skills: $SKILLS_DIR"
echo ""

# Criar diretório se não existir
if [ ! -d "$SKILLS_DIR" ]; then
    echo "📁 Criando diretório de skills..."
    mkdir -p "$SKILLS_DIR"
    echo "✅ Diretório criado"
else
    echo "✅ Diretório de skills já existe"
fi
echo ""

# Verificar se já está instalado
if [ -d "$SKILLS_DIR/lex-flow-builder" ]; then
    echo "⚠️  lex-flow-builder já está instalado"
    read -p "Deseja reinstalar? (s/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
        echo "❌ Instalação cancelada"
        exit 0
    fi
    echo "🗑️  Removendo versão antiga..."
    rm -rf "$SKILLS_DIR/lex-flow-builder"
fi

# Verificar se git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Git não encontrado. Por favor, instale o Git primeiro."
    echo "   Mac: brew install git"
    echo "   Linux: apt-get install git ou yum install git"
    echo "   Windows: https://git-scm.com/download/win"
    exit 1
fi

echo "✅ Git encontrado"
echo ""

# Clonar o repositório
echo "📦 Clonando repositório LexFlow..."

REPO_URL="https://github.com/inspira-legal/lex-flow.git"
# Use mktemp for secure temporary directory creation
TEMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/lex-flow-temp.XXXXXX")

if git clone "$REPO_URL" "$TEMP_DIR"; then
    echo "✅ Repositório clonado com sucesso"
else
    echo "❌ Erro ao clonar repositório"
    echo "   Verifique se a URL está correta: $REPO_URL"
    echo "   Ou se você tem acesso ao repositório"
    exit 1
fi
echo ""

# Copiar a skill para o diretório correto
echo "📁 Copiando skill para $SKILLS_DIR/lex-flow-builder..."
cp -r "$TEMP_DIR/skills/lex-flow-builder" "$SKILLS_DIR/"

# Limpar arquivos temporários
echo "🗑️  Limpando arquivos temporários..."
rm -rf "$TEMP_DIR"
echo ""

# Verificar arquivos essenciais
echo "🔍 Verificando instalação..."
ESSENTIAL_FILES=("SKILL.md" "reference.md" "examples.md")
ALL_PRESENT=true

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$SKILLS_DIR/lex-flow-builder/$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (FALTANDO!)"
        ALL_PRESENT=false
    fi
done
echo ""

if [ "$ALL_PRESENT" = false ]; then
    echo "⚠️  Alguns arquivos essenciais estão faltando"
    echo "   A skill pode não funcionar corretamente"
    echo ""
fi

# Sucesso!
echo "🎉 Instalação concluída com sucesso!"
echo ""
echo "📋 Próximos passos:"
echo ""
echo "1. Reinicie o Claude Code (se estiver rodando)"
echo ""
echo "2. Abra o Claude Code e digite:"
echo "   \"Quero criar um workflow LexFlow\""
echo ""
echo "   Ou force a ativação:"
echo "   /skill lex-flow-builder"
echo ""
echo "3. Leia a documentação:"
echo "   cat $SKILLS_DIR/lex-flow-builder/README.md"
echo ""
echo "✨ Pronto para usar! Boa criação de workflows!"
