#!/usr/bin/env python3
"""
Script para verificar novos opcodes e sugerir atualizações no reference.md

Uso:
    python sync_opcodes.py

    ou com CI/CD:
    python sync_opcodes.py --check-only  # Apenas reporta, não edita

Este script:
1. Lê OPCODE_REFERENCE.md oficial
2. Compara com reference.md da skill
3. Lista opcodes novos que podem ser adicionados
4. Sugere quais são importantes adicionar
"""

import re
from pathlib import Path
from typing import Set, List, Dict
import sys


def extract_opcodes_from_official(official_path: Path) -> Set[str]:
    """Extrai todos os opcodes do arquivo oficial"""
    opcodes = set()

    if not official_path.exists():
        print(f"❌ Arquivo oficial não encontrado: {official_path}")
        return opcodes

    content = official_path.read_text()

    # Padrão: ### `opcode_name(...)` ou ## opcode_name
    pattern = r'###?\s+`?([a-z_]+)[\(\`]'
    matches = re.findall(pattern, content)

    opcodes.update(matches)
    print(f"✅ Encontrados {len(opcodes)} opcodes no arquivo oficial")

    return opcodes


def extract_opcodes_from_skill(skill_path: Path) -> Set[str]:
    """Extrai opcodes documentados na skill"""
    opcodes = set()

    if not skill_path.exists():
        print(f"❌ reference.md não encontrado: {skill_path}")
        return opcodes

    content = skill_path.read_text()

    # Mesmo padrão
    pattern = r'###?\s+`?([a-z_]+)[\(\`]'
    matches = re.findall(pattern, content)

    opcodes.update(matches)
    print(f"✅ Skill documenta {len(opcodes)} opcodes atualmente")

    return opcodes


def categorize_opcodes(opcodes: List[str]) -> Dict[str, List[str]]:
    """Categoriza opcodes por tipo/importância"""
    categories = {
        "essential": [],      # Muito comuns, devem estar na skill
        "useful": [],         # Úteis, bom ter
        "specialized": [],    # Específicos, opcional
    }

    # Categorias essenciais (muito usadas)
    essential_prefixes = [
        "workflow_", "io_", "operator_", "control_",
        "data_", "dict_", "list_", "http_", "str"
    ]

    # Úteis (integrações comuns)
    useful_prefixes = [
        "slack_", "google_", "github_", "file_",
        "json_", "yaml_", "csv_"
    ]

    for opcode in opcodes:
        # Checar essenciais
        if any(opcode.startswith(prefix) for prefix in essential_prefixes):
            categories["essential"].append(opcode)
        # Checar úteis
        elif any(opcode.startswith(prefix) for prefix in useful_prefixes):
            categories["useful"].append(opcode)
        # Resto é especializado
        else:
            categories["specialized"].append(opcode)

    return categories


def main():
    """Função principal"""
    check_only = "--check-only" in sys.argv

    print("🔍 Verificando sincronização de opcodes...\n")

    # Caminhos
    repo_root = Path(__file__).parent.parent.parent
    official_doc = repo_root / "docs" / "OPCODE_REFERENCE.md"
    skill_ref = Path(__file__).parent / "reference.md"

    print(f"📂 Repo root: {repo_root}")
    print(f"📄 Oficial: {official_doc}")
    print(f"📄 Skill: {skill_ref}\n")

    # Extrair opcodes
    official_opcodes = extract_opcodes_from_official(official_doc)
    skill_opcodes = extract_opcodes_from_skill(skill_ref)

    # Encontrar diferenças
    new_opcodes = official_opcodes - skill_opcodes

    if not new_opcodes:
        print("\n✅ Skill está sincronizada! Nenhum opcode novo.")
        return 0

    print(f"\n📋 Encontrados {len(new_opcodes)} opcodes novos:\n")

    # Categorizar
    categorized = categorize_opcodes(sorted(new_opcodes))

    # Reportar essenciais
    if categorized["essential"]:
        print("⚠️  ESSENCIAIS (devem ser adicionados):")
        for opcode in sorted(categorized["essential"]):
            print(f"   • {opcode}")
        print()

    # Reportar úteis
    if categorized["useful"]:
        print("💡 ÚTEIS (bom adicionar):")
        for opcode in sorted(categorized["useful"]):
            print(f"   • {opcode}")
        print()

    # Reportar especializados
    if categorized["specialized"]:
        print("🔧 ESPECIALIZADOS (opcional):")
        for opcode in sorted(categorized["specialized"]):
            print(f"   • {opcode}")
        print()

    # Sugestão de ação
    print("─" * 50)
    print("📝 AÇÕES RECOMENDADAS:")
    print()

    if categorized["essential"]:
        print(f"1. ⚠️  Adicionar {len(categorized['essential'])} opcodes ESSENCIAIS")
        print("   → Estes são muito usados e devem estar na skill")

    if categorized["useful"]:
        print(f"2. 💡 Considerar {len(categorized['useful'])} opcodes ÚTEIS")
        print("   → Adicione se tiver exemplos práticos")

    if categorized["specialized"]:
        print(f"3. 🔧 Revisar {len(categorized['specialized'])} ESPECIALIZADOS")
        print("   → Apenas se houver demanda específica")

    print()
    print("📖 Para ver detalhes de cada opcode:")
    print(f"   grep -A 20 'opcode_name' {official_doc}")

    # Se não for check-only, poderia adicionar lógica de atualização automática
    if not check_only:
        print("\n💡 Dica: Use --check-only para apenas reportar sem modificar")

    # Retornar código de erro se houver essenciais não documentados
    if categorized["essential"]:
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
