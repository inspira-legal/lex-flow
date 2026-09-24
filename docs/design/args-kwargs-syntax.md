# Design note: `args` / `kwargs` node syntax

Status: **phases 1–4 shipped** in PR #128. Phase 5 is open and is the breaking one.
Agreed 2026-09-22, implemented 2026-09-23.

## The problem

`parser.py` read `inputs:` as a dict and **discarded the keys**, building a positional
list from insertion order. Input names were decorative, so this returned **7**:

```yaml
sub:
  opcode: operator_subtract      # (left, right)
  inputs:
    right: { literal: 10 }
    left: { literal: 3 }
```

That is why "make the dict become kwargs" was never an option on its own: the same
file would silently have started returning −7. Any fix had to introduce a *new* way
of writing arguments and leave the old one meaning exactly what it meant.

## Decisions

- `args:` (a list) and `kwargs:` (a mapping) are **sibling node keys**. `inputs:`
  keeps its old meaning; `inputs` together with `args`/`kwargs` on one node is a
  `ParseError`.
- Construct slots are **lowercase**. The list-shaped ones are `args` (fork branches,
  call arguments, return values) and `catch` (try handlers).
- `catch` is a list of `{exception_type, var, body}` — the same inner keys the legacy
  `CATCH1..N` entries used; only the container changed.
- In `workflow_call`, `workflow` is a **reserved** kwarg and every other kwarg binds
  to a parameter of the called workflow. A workflow with a parameter named `workflow`
  can only receive it positionally.
- **No user opcode changes.** Binding lives in the registry wrapper
  (`bind_arguments`); `call(name, args, kwargs=None)` keeps kwargs optional, and
  implementations stored directly in `registry.opcodes` are still called with one
  argument.
- Migration is the explicit `lexflow migrate` command, never automatic.

## What shipped

1. `opcodes/opcodes.py` — `bind_arguments()` replaces the loop duplicated in
   `register()` and `inject()`; `Call`/`Opcode`/`OpStmt` gained `kwargs`; evaluator,
   executor and `WorkflowManager.call` wired through.
2. `parser.py` — `NodeArgs` reads either syntax. Construct slots are checked against
   `get_construct_slots()`, so a misspelled or UPPERCASE slot is rejected instead of
   silently dropped.
3. `engine.py` — `load_program()` validates keyword names against the registered
   signatures, so a typo cannot reach runtime and be swallowed by the workflow's own
   `catch: ValueError`.
4. `lexflow migrate <path> [--diff|--write] [--names]` — ruamel-backed, comment
   preserving. The default rewrite drops input keys (signature-independent, so it
   cannot change behaviour); `--names` keeps them as kwargs only when the keys are
   exactly the signature's first parameters and the opcode is not variadic. A
   misbinding detector flags the rest, and keys the legacy reader never read are
   dropped and reported rather than carried over.
5. Every example migrated, `grammar.json` 1.1 with lowercase slot names, and a
   `DeprecationWarning` (one per workflow) on the legacy path.

## Phase 5: removing `inputs:`

Deleting the legacy branch is a deletion, not a reinterpretation, and needs a **major
bump** of `lexflow-core`. Prerequisites:

- Every consumer repo migrated (`lexflow-opcodes`, `lexflow-automacoes`) and pinned to
  a core that understands `args`/`kwargs`.
- The deprecation warning in place for at least one minor release.

Release order for anything that teaches the new syntax: **core first**, then the
docs, skill and agent, then bump the pins in the consumer repos. Publishing the docs
ahead of the core leaves readers writing workflows the deployed runtime cannot parse.

## Known, deliberately untouched

- `lexflow-web/visualization.py` reads `inputs` directly and does not render migrated
  workflows. The frontend is being discontinued.
- `skills/lex-flow-builder/examples.md` documents a node shape the parser has never
  accepted (`nodes` as a list of `{id, opcode, inputs: {NAME: {type, value}}}`). It
  is pre-existing and wider than this change.
- Three `examples/integrations/hubspot/*.yaml` do not parse, and did not before.
