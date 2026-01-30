# LexFlow Examples

This directory contains organized examples demonstrating LexFlow's features and capabilities.

## Directory Structure

### 📚 basics/
Fundamental examples to get started with LexFlow.

- `hello_world.yaml` / `hello_world.json` - Simple "Hello, World!" program
- `cli_inputs.yaml` - Using command-line inputs with workflows

**Run examples:**
```bash
lexflow examples/basics/hello_world.yaml
lexflow examples/basics/cli_inputs.yaml --input name=Alice --input age=30
```

### 🔀 control_flow/
Examples demonstrating conditional logic and loops.

- `conditionals.yaml` - If/else statements
- `loops_for.yaml` - For loops with range
- `loops_foreach.yaml` - ForEach loops over collections
- `loops_while.json` - While loops

**Run examples:**
```bash
lexflow examples/control_flow/conditionals.yaml
lexflow examples/control_flow/loops_for.yaml
```

### ⚠️ exception_handling/
Exception handling patterns and best practices.

- `comprehensive_examples.yaml` - Complete guide with multiple patterns
- `basic_try_catch.yaml` - Simple try-catch blocks
- `multiple_handlers.yaml` - Multiple exception types
- `finally_blocks.yaml` - Try-catch-finally patterns
- `catch_variables.yaml` - Binding exception messages to variables
- `catch_variables_advanced.yaml` - Advanced variable binding
- `throwing_errors.yaml` - Throwing custom errors

**Run examples:**
```bash
lexflow examples/exception_handling/comprehensive_examples.yaml
lexflow examples/exception_handling/basic_try_catch.yaml
```

### 📦 data_structures/
Working with dictionaries, objects, and lists.

- `dictionaries.yaml` - Dictionary operations (create, get, set, update)
- `objects.yaml` - Object operations (get, set, has, remove)
- `dicts_and_objects.yaml` - Simple examples of both

**Run examples:**
```bash
lexflow examples/data_structures/dictionaries.yaml
lexflow examples/data_structures/objects.yaml
```

### 📂 multi_file/
Multi-file workflow organization.

- `main.yaml` - Main workflow that calls external workflows
- `helpers.yaml` - Helper workflows
- `more_helpers.json` - Additional helpers

**Run example:**
```bash
lexflow examples/multi_file/main.yaml --include examples/multi_file/helpers.yaml examples/multi_file/more_helpers.json
```

### 🔌 integrations/
Integration examples for extending LexFlow.

#### integrations/ai_chat/
AI chat applications with conversation history management.

- `chat_demo.yaml` - Non-interactive demo of chat history opcodes
- `simple_chat.yaml` - Interactive AI chat with multi-turn conversations

**Requirements (for simple_chat.yaml):**
```bash
pip install lexflow[ai]
gcloud auth application-default login
```

**Run examples:**
```bash
lexflow examples/integrations/ai_chat/chat_demo.yaml
lexflow examples/integrations/ai_chat/simple_chat.yaml
```

#### integrations/pydantic_ai/
AI integration using pydantic-ai with Google Vertex AI.

- `vertex_ai_example.yaml` - Complete AI workflow example

**Requirements:**
```bash
uv sync --extra ai
gcloud auth application-default login
```

**Run example:**
```bash
lexflow examples/integrations/pydantic_ai/vertex_ai_example.yaml
```

#### integrations/pygame/
Pygame integration for game development and graphics.

- `hello.yaml` - Simple pygame window
- `simple.yaml` - Basic pygame workflow
- `wave_animation.yaml` - Animated wave pattern
- `custom_opcodes.py` - Custom pygame opcodes
- `run_hello.py` - Python runner for hello example
- `run_wave.py` - Python runner for wave animation

**Requirements:**
```bash
uv sync --extra pygame
```

**Run examples:**
```bash
python examples/integrations/pygame/run_hello.py
python examples/integrations/pygame/run_wave.py
```

#### integrations/http_scraping/
HTTP requests and web scraping examples.

- `fetch_api_data.yaml` - Fetch and parse JSON from a REST API
- `web_scraper.yaml` - Fetch HTML and extract content with CSS selectors

**Requirements:**
```bash
pip install lexflow[http]
```

**Run examples:**
```bash
lexflow examples/integrations/http_scraping/fetch_api_data.yaml
lexflow examples/integrations/http_scraping/web_scraper.yaml
```

#### integrations/custom_opcodes/
Examples of extending LexFlow with custom operations.

- `basics.py` - Creating custom opcodes
- `metrics_usage.py` - Using the metrics system

**Run examples:**
```bash
python examples/integrations/custom_opcodes/basics.py
python examples/integrations/custom_opcodes/metrics_usage.py
```

### 🌟 showcase/
Advanced real-world examples demonstrating LexFlow's capabilities.

#### showcase/ai_code_reviewer/
AI-powered GitHub PR code reviewer.

- `review_pr.yaml` - Review a GitHub PR with AI analysis
- `review.yaml` - Simplified code review workflow

**Requirements:**
```bash
pip install lexflow[ai]
brew install gh && gh auth login  # GitHub CLI
gcloud auth application-default login
```

**Run example:**
```bash
lexflow examples/showcase/ai_code_reviewer/review_pr.yaml \
  --input owner=anthropics --input repo=claude-code \
  --input pr=123 --input project=YOUR_GCP_PROJECT
```

See `examples/showcase/ai_code_reviewer/README.md` for full documentation.

#### showcase/multi_agent_debate/
Multi-agent AI debate system with three specialized agents.

- `debate.yaml` - Full debate workflow with advocate, critic, and judge agents

**Requirements:**
```bash
pip install lexflow[ai]
gcloud auth application-default login
```

**Run example:**
```bash
lexflow examples/showcase/multi_agent_debate/debate.yaml \
  --input topic="AI will replace programmers" \
  --input project=YOUR_GCP_PROJECT
```

See `examples/showcase/multi_agent_debate/README.md` for full documentation.

#### showcase/rag_pipeline/
Complete RAG (Retrieval-Augmented Generation) pipeline with Qdrant.

- `ingest.yaml` - Ingest PDFs into vector database
- `search.yaml` - Semantic search over documents
- `ask.yaml` - Question answering with RAG

**Requirements:**
```bash
pip install lexflow[rag]
docker-compose up -d  # Start Qdrant
gcloud auth application-default login
```

**Run examples:**
```bash
lexflow examples/showcase/rag_pipeline/ingest.yaml \
  --input pdf_dir=./documents --input project=YOUR_GCP_PROJECT

lexflow examples/showcase/rag_pipeline/ask.yaml \
  --input question="What is the main topic?" --input project=YOUR_GCP_PROJECT
```

See `examples/showcase/rag_pipeline/README.md` for full documentation.

## Quick Start

### 1. Start Simple
```bash
lexflow examples/basics/hello_world.yaml
```

### 2. Try Inputs
```bash
lexflow examples/basics/cli_inputs.yaml --input name=YourName --input age=25
```

### 3. Explore Control Flow
```bash
lexflow examples/control_flow/loops_for.yaml
```

### 4. Learn Exception Handling
```bash
lexflow examples/exception_handling/comprehensive_examples.yaml
```

### 5. Work with Data
```bash
lexflow examples/data_structures/dictionaries.yaml
```

## Learning Path

1. **Basics** → Start here to understand workflow structure
2. **Control Flow** → Learn conditional logic and loops
3. **Data Structures** → Work with collections
4. **Exception Handling** → Build robust workflows
5. **Multi-File** → Organize large projects
6. **Integrations** → Extend LexFlow with custom features

## Tips

- Use `--verbose` flag to see execution details
- Use `--validate-only` to check syntax without running
- Use `--metrics` to see performance statistics
- Check `docs/` for detailed language documentation

## More Resources

- [Getting Started Guide](../docs/GETTING_STARTED.md) - Installation and setup
- [Grammar Reference](../docs/GRAMMAR_REFERENCE.md) - Control flow constructs and language specification (auto-generated)
- [Opcode Reference](../docs/OPCODE_REFERENCE.md) - All available operations (auto-generated)

---

**Note:** Test-focused files have been moved to `tests/integration/` to keep examples clean and user-focused.
