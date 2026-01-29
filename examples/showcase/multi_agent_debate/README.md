# Multi-Agent AI Debate

This showcase demonstrates LexFlow's AI capabilities with multiple agents interacting with each other. Two AI agents debate a topic from opposing perspectives, with a third agent serving as judge.

## What This Example Demonstrates

- **Multiple AI Agents**: Three distinct agents with different personas and roles
- **Shared Conversation Context**: Using chat history opcodes to maintain debate history
- **Loop-Based Turn Taking**: Agents take turns in a structured debate format
- **AI-Powered Evaluation**: A judge agent reviews and declares a winner

## How It Works

### The Agents

1. **ADVOCATE** - Argues strongly IN FAVOR of the debate topic
   - Makes compelling arguments supporting the position
   - Counters the opponent's arguments in subsequent rounds
   - Maintains intellectual honesty while being persuasive

2. **CRITIC** - Argues strongly AGAINST the debate topic
   - Presents opposing viewpoints and counterarguments
   - Challenges the advocate's reasoning and evidence
   - Highlights potential flaws and risks

3. **JUDGE** - Impartially evaluates the debate
   - Reviews the full debate transcript
   - Considers logic, evidence, persuasiveness, and rebuttals
   - Declares a winner with detailed reasoning

### The Flow

```
[Setup] Create Model -> Create Agents -> Initialize History
           |
           v
[Round 1] Advocate Opening -> Add to History -> Critic Response -> Add to History
           |
           v
[Round 2] Advocate Rebuttal -> Add to History -> Critic Rebuttal -> Add to History
           |
           v
       ... (repeat for N rounds)
           |
           v
[Judgment] Judge Reviews Full History -> Declares Winner
```

## Running the Example

### Prerequisites

```bash
# Install LexFlow with AI support
pip install lexflow[ai]

# Authenticate with Google Cloud
gcloud auth application-default login
```

### Basic Usage

```bash
lexflow examples/showcase/multi_agent_debate/debate.yaml \
  --input topic="AI will replace programmers" \
  --input project=YOUR_GCP_PROJECT
```

### Options

| Input | Description | Default |
|-------|-------------|---------|
| `topic` | The debate topic | "AI will benefit humanity" |
| `project` | Your GCP project ID | (required) |
| `rounds` | Number of debate rounds | 3 |
| `location` | GCP region | "us-central1" |

### Examples

```bash
# Quick 2-round debate
lexflow examples/showcase/multi_agent_debate/debate.yaml \
  --input topic="Remote work is better than office work" \
  --input project=my-project \
  --input rounds=2

# Extended 5-round debate
lexflow examples/showcase/multi_agent_debate/debate.yaml \
  --input topic="Social media does more harm than good" \
  --input project=my-project \
  --input rounds=5

# Different region
lexflow examples/showcase/multi_agent_debate/debate.yaml \
  --input topic="Electric vehicles will replace gas cars by 2035" \
  --input project=my-project \
  --input location=europe-west1
```

## Sample Output

```
================================================================================
                         MULTI-AGENT AI DEBATE
================================================================================

TOPIC: AI will replace programmers

Rounds: 3

Setting up debate participants...

  [+] ADVOCATE ready (argues IN FAVOR)
  [-] CRITIC ready (argues AGAINST)
  [=] JUDGE ready (will evaluate)

================================================================================
                              LET THE DEBATE BEGIN!
================================================================================

--------------------------------------------------------------------------------
                                   ROUND 1
--------------------------------------------------------------------------------

ADVOCATE [IN FAVOR]:

The trajectory of AI development in software engineering is unmistakable.
Large language models are already writing production-quality code, fixing bugs,
and generating entire applications from natural language descriptions. GitHub
Copilot has demonstrated that AI can boost developer productivity by 55%, and
more advanced systems like GPT-4 can pass coding interviews at top tech companies.

The economic incentives are clear: companies will increasingly adopt AI tools
that can produce code faster and cheaper than human programmers. Just as
automation transformed manufacturing, AI will transform software development.
The question is not if, but when.

CRITIC [AGAINST]:

While AI coding assistants are impressive, they fundamentally lack the creative
problem-solving and contextual understanding that programming truly requires.
Writing code is the easy part - understanding business requirements, designing
system architectures, debugging complex distributed systems, and making ethical
decisions about software impact require human judgment.

AI tools are excellent at pattern matching from training data, but they cannot
innovate or handle truly novel problems. They also produce incorrect code
frequently enough that human oversight remains essential. Programmers will
evolve their roles, but they won't disappear.

...

================================================================================
                              JUDGE'S VERDICT
================================================================================

The judge is reviewing the debate...

--------------------------------------------------------------------------------
                              FINAL VERDICT
--------------------------------------------------------------------------------

WINNER: CRITIC

REASONING: While the Advocate made compelling points about AI's rapid advancement
and economic pressures, the Critic presented stronger arguments about the
fundamental limitations of AI systems. The Critic effectively highlighted that
programming involves much more than code generation - it requires understanding
complex requirements, making architectural decisions, and exercising judgment
that current AI systems cannot replicate.

The Advocate's economic argument was persuasive but oversimplified the nature
of software development. The Critic's point about AI tools requiring human
oversight undermines the replacement thesis. Overall, the Critic demonstrated
more nuanced understanding of both AI capabilities and programming work.

================================================================================
                           DEBATE CONCLUDED
================================================================================
```

## Key Patterns Demonstrated

### 1. Multiple Agents with Different Personas

Each agent has a distinct `instructions` parameter that shapes its behavior:

```yaml
create_advocate:
  opcode: pydantic_ai_create_agent
  inputs:
    model: { variable: "model" }
    instructions:
      literal: |
        You are the ADVOCATE in a formal debate...
        You MUST argue in FAVOR of the topic...
```

### 2. Shared Conversation History

The debate history is maintained using chat opcodes:

```yaml
# Create shared history
create_history:
  opcode: chat_create
  isReporter: true

# Add messages to history
add_advocate_to_history:
  opcode: chat_add_message
  inputs:
    history: { variable: debate_history }
    role: { literal: "user" }
    content: { node: format_advocate_history }

# Convert history to prompt for AI
history_as_prompt:
  opcode: chat_to_prompt
  isReporter: true
  inputs:
    history: { variable: debate_history }
```

### 3. Loop-Based Turn Taking

The debate uses a `control_while` loop with a round counter:

```yaml
debate_loop:
  opcode: control_while
  inputs:
    CONDITION: { node: check_continue }
    BODY: { branch: print_round_header }

check_continue:
  opcode: operator_and
  isReporter: true
  inputs:
    left: { variable: continue_debate }
    right: { node: round_not_exceeded }
```

### 4. Dynamic Prompt Construction

Prompts are built dynamically using string concatenation:

```yaml
build_advocate_prompt:
  opcode: operator_add
  isReporter: true
  inputs:
    left: { literal: "DEBATE TOPIC: " }
    right: { node: advocate_prompt_with_topic }
```

## Customization Ideas

- **Add more agents**: Include a moderator or fact-checker
- **Different debate formats**: Opening statements, cross-examination, closing arguments
- **Audience voting**: Add agents representing different stakeholder perspectives
- **Structured output**: Use Pydantic models to structure agent responses
- **Real-time streaming**: Integrate with WebSocket for live debate viewing

## Related Examples

- `examples/integrations/ai_chat/simple_chat.yaml` - Basic chat with history
- `examples/integrations/pydantic_ai/vertex_ai_example.yaml` - Vertex AI basics
