@echo off
REM Script de Instalacao Automatica - lex-flow-builder (Windows)
REM Uso: install.bat

echo.
echo ========================================
echo  Instalando lex-flow-builder skill
echo  para Claude Code
echo ========================================
echo.

REM Definir diretorio de skills
set SKILLS_DIR=%USERPROFILE%\.claude\skills

echo Diretorio de skills: %SKILLS_DIR%
echo.

REM Criar diretorio se nao existir
if not exist "%SKILLS_DIR%" (
    echo Criando diretorio de skills...
    mkdir "%SKILLS_DIR%"
    echo [OK] Diretorio criado
) else (
    echo [OK] Diretorio de skills ja existe
)
echo.

REM Verificar se ja esta instalado
if exist "%SKILLS_DIR%\lex-flow-builder" (
    echo [!] lex-flow-builder ja esta instalado
    set /p REINSTALL="Deseja reinstalar? (S/N): "
    if /i not "%REINSTALL%"=="S" (
        echo [X] Instalacao cancelada
        pause
        exit /b 0
    )
    echo Removendo versao antiga...
    rmdir /s /q "%SKILLS_DIR%\lex-flow-builder"
)

REM Verificar se git esta instalado
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [X] Git nao encontrado!
    echo.
    echo Por favor, instale o Git primeiro:
    echo https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [OK] Git encontrado
echo.

REM Clonar o repositorio
echo Clonando repositorio LexFlow...
cd /d "%TEMP%"

set REPO_URL=https://github.com/inspira-legal/lex-flow.git
set TEMP_DIR=%TEMP%\lex-flow-temp-%RANDOM%

git clone "%REPO_URL%" "%TEMP_DIR%"
if %ERRORLEVEL% NEQ 0 (
    echo [X] Erro ao clonar repositorio
    echo.
    echo Verifique se a URL esta correta: %REPO_URL%
    echo Ou se voce tem acesso ao repositorio
    echo.
    pause
    exit /b 1
)

echo [OK] Repositorio clonado com sucesso
echo.

REM Copiar a skill para o diretorio correto
echo Copiando skill para %SKILLS_DIR%\lex-flow-builder...
xcopy /E /I /Y "%TEMP_DIR%\skills\lex-flow-builder" "%SKILLS_DIR%\lex-flow-builder"

REM Limpar arquivos temporarios
echo Limpando arquivos temporarios...
rmdir /s /q "%TEMP_DIR%"
echo.

REM Verificar arquivos essenciais
echo Verificando instalacao...
set ALL_PRESENT=1

if exist "%SKILLS_DIR%\lex-flow-builder\SKILL.md" (
    echo   [OK] SKILL.md
) else (
    echo   [X] SKILL.md ^(FALTANDO!^)
    set ALL_PRESENT=0
)

if exist "%SKILLS_DIR%\lex-flow-builder\reference.md" (
    echo   [OK] reference.md
) else (
    echo   [X] reference.md ^(FALTANDO!^)
    set ALL_PRESENT=0
)

if exist "%SKILLS_DIR%\lex-flow-builder\examples.md" (
    echo   [OK] examples.md
) else (
    echo   [X] examples.md ^(FALTANDO!^)
    set ALL_PRESENT=0
)

echo.

if %ALL_PRESENT%==0 (
    echo [!] Alguns arquivos essenciais estao faltando
    echo     A skill pode nao funcionar corretamente
    echo.
)

REM Sucesso!
echo ========================================
echo  Instalacao concluida com sucesso!
echo ========================================
echo.
echo Proximos passos:
echo.
echo 1. Reinicie o Claude Code ^(se estiver rodando^)
echo.
echo 2. Abra o Claude Code e digite:
echo    "Quero criar um workflow LexFlow"
echo.
echo    Ou force a ativacao:
echo    /skill lex-flow-builder
echo.
echo 3. Leia a documentacao:
echo    type %SKILLS_DIR%\lex-flow-builder\README.md
echo.
echo Pronto para usar! Boa criacao de workflows!
echo.
pause
