"""Migrate workflow files from the legacy 'inputs' key to 'args'/'kwargs'."""

import inspect
import io
import json
import re
from pathlib import Path
from typing import Any, Optional

from lexflow import Parser, default_registry, get_grammar
from lexflow.grammar import SLOT_ALIASES, get_construct_slots
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq

# Legacy numbered slot families that become a positional 'args' list
SEQUENCE_SLOTS = {
    "control_fork": "BRANCH",
    "workflow_call": "ARG",
    "call": "ARG",
    "workflow_return": "VALUE",
    "return": "VALUE",
}

CATCH_OPCODES = {"control_try", "try_catch"}

# Opcodes whose inputs are named slots rather than positional arguments
NAMED_SLOT_ALIASES = set(SLOT_ALIASES) | {"data_get_variable"}

# Opcodes that read a bare family slot (VALUE) when no numbered one is present
BARE_SLOT_OPCODES = {"workflow_return", "return"}

YAML_SUFFIXES = (".yaml", ".yml")
WORKFLOW_SUFFIXES = YAML_SUFFIXES + (".json",)


def core_supports_kwargs() -> bool:
    """True when the installed core can parse the syntax this migration emits.

    The CLI depends on the core by git URL, which carries no version floor, so
    an older core would accept the rewrite and then reject the rewritten file.
    """
    probe = {
        "workflows": [
            {
                "name": "main",
                "interface": {"inputs": [], "outputs": []},
                "variables": {},
                "nodes": {
                    "start": {"opcode": "workflow_start", "next": "p"},
                    "p": {"opcode": "io_print", "args": [{"literal": "probe"}]},
                },
            }
        ]
    }
    try:
        Parser().parse_dict(probe)
        return True
    except Exception:
        return False


def named_slot_opcodes() -> set[str]:
    """Opcodes whose inputs are named slots: statement constructs plus aliases.

    Constructs that compile to an Opcode (ai_agent_with_tools) bind by position
    like any other opcode, so they are not in this set.
    """
    constructs = {
        c["opcode"]
        for c in get_grammar()["constructs"]
        if c.get("ast_class") not in (None, "Opcode")
    }
    return constructs | NAMED_SLOT_ALIASES


def _represent_none(representer, data):
    """Keep explicit nulls explicit instead of dumping an empty value."""
    return representer.represent_scalar("tag:yaml.org,2002:null", "null")


def _yaml() -> YAML:
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096
    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.representer.add_representer(type(None), _represent_none)
    return yaml


def _numbered(key: str, prefix: str) -> Optional[int]:
    """Index of a numbered slot, matching what the legacy reader looked up.

    NodeArgs.sequence() builds the literal string f"{prefix}{i}" from 1, so a
    zero-padded ARG01 or a non-ASCII digit was never a member of the family.
    """
    match = re.fullmatch(rf"{prefix}([1-9][0-9]*)", key, re.IGNORECASE | re.ASCII)
    return int(match.group(1)) if match else None


def _new_map(source: Any) -> Any:
    """An empty mapping of the same flavour (round-trip or plain) as source."""
    return CommentedMap() if isinstance(source, CommentedMap) else {}


def _new_seq(source: Any) -> Any:
    return CommentedSeq() if isinstance(source, CommentedMap) else []


def _take_family(numbered: dict[int, Any], target: Any) -> None:
    """Read a numbered family the way the legacy reader did: 1, 2, ... to the first gap."""
    index = 1
    while index in numbered:
        target.append(numbered.pop(index))
        index += 1


def _split_construct_inputs(opcode: str, inputs: Any) -> tuple[Any, Any, list[str]]:
    """Split a construct's inputs into a positional list and named slots.

    Returns (args, kwargs, dropped). 'dropped' holds the keys the legacy reader
    never looked at; keeping them would change behaviour, so they are reported
    rather than carried over.
    """
    args = _new_seq(inputs)
    kwargs = _new_map(inputs)
    prefix = SEQUENCE_SLOTS.get(opcode)
    slots = get_construct_slots(opcode)
    numbered_args: dict[int, Any] = {}
    numbered_keys: dict[int, str] = {}
    catches: dict[int, Any] = {}
    catch_keys: dict[int, str] = {}
    bare: Optional[tuple[str, Any]] = None
    dropped: list[str] = []

    for key, value in inputs.items():
        if prefix and (index := _numbered(key, prefix)) is not None:
            numbered_args[index] = value
            numbered_keys[index] = key
        elif opcode in CATCH_OPCODES and (index := _numbered(key, "CATCH")) is not None:
            catches[index] = value
            catch_keys[index] = key
        elif prefix and key.upper() == prefix:
            bare = (key, value)
        elif opcode in CATCH_OPCODES and str(key).lower() == "catch":
            # The legacy reader only ever read the CATCH1..n family
            dropped.append(str(key))
        elif slots is not None and str(key).lower() in slots:
            kwargs[str(key).lower()] = value
        elif slots is None and str(key).lower() == "workflow":
            kwargs["workflow"] = value
        else:
            dropped.append(str(key))

    _take_family(numbered_args, args)
    dropped.extend(numbered_keys[i] for i in sorted(numbered_args))

    # A bare VALUE is read only when the numbered family came back empty
    if bare is not None:
        if opcode in BARE_SLOT_OPCODES and not len(args):
            args.append(bare[1])
        else:
            dropped.append(bare[0])

    catch_list = _new_seq(inputs)
    _take_family(catches, catch_list)
    dropped.extend(catch_keys[i] for i in sorted(catches))
    if len(catch_list):
        kwargs["catch"] = catch_list

    return args, kwargs, sorted(dropped)


def _binds_by_name(opcode: str, inputs: Any) -> bool:
    """True when the input names are exactly the signature's first parameters.

    Only then does binding by name give what binding by position gives today,
    so only then can the migration use 'kwargs' without changing behaviour.
    """
    sig = default_registry.signatures.get(opcode)
    if sig is None:
        return False
    parameters = list(sig.parameters.values())
    # A variadic opcode (*values) rejects keyword arguments at runtime
    if any(p.kind is inspect.Parameter.VAR_POSITIONAL for p in parameters):
        return False
    params = [p.name for p in parameters]
    keys = [str(k).lower() for k in inputs.keys()]
    return bool(keys) and keys == params[: len(keys)]


def _migrate_node(
    node: Any, named_slots: set[str], use_names: bool
) -> tuple[Optional[Any], list[str]]:
    """Return the node rewritten to 'args'/'kwargs' (or None), plus dropped keys."""
    if not isinstance(node, dict) or "inputs" not in node:
        return None, []
    if "args" in node or "kwargs" in node:
        return None, []

    inputs = node.get("inputs") or {}
    if not isinstance(inputs, dict):
        return None, []

    dropped: list[str] = []
    opcode = node.get("opcode", "")
    if opcode in named_slots:
        args, kwargs, dropped = _split_construct_inputs(opcode, inputs)
    elif use_names and _binds_by_name(opcode, inputs):
        args = _new_seq(inputs)
        kwargs = _new_map(inputs)
        for key, value in inputs.items():
            kwargs[str(key).lower()] = value
    else:
        args = _new_seq(inputs)
        for value in inputs.values():
            args.append(value)
        kwargs = _new_map(inputs)

    replacement = []
    if len(args):
        replacement.append(("args", args))
    if len(kwargs):
        replacement.append(("kwargs", kwargs))

    return _replace_key(node, "inputs", replacement), dropped


def _replace_key(node: Any, key: str, replacement: list[tuple[str, Any]]) -> Any:
    """Rebuild a node with `key` swapped for `replacement`, keeping order and comments."""
    new_node = _new_map(node)
    for name, value in node.items():
        if name == key:
            for new_name, new_value in replacement:
                new_node[new_name] = new_value
        else:
            new_node[name] = value

    if isinstance(node, CommentedMap):
        new_node.ca.comment = node.ca.comment
        for name, comment in node.ca.items.items():
            target = name
            if name == key:
                if not replacement:
                    continue
                target = replacement[0][0]
            new_node.ca.items[target] = comment

    return new_node


def _iter_node_tables(data: Any):
    """Yield every workflow's node table in a parsed workflow file."""
    for workflow in data.get("workflows", []) or []:
        nodes = workflow.get("nodes")
        if isinstance(nodes, dict):
            yield workflow.get("name", "?"), nodes


def find_misbindings(data: Any) -> list[str]:
    """Nodes whose legacy input names look intended but bind to other parameters."""
    warnings = []
    named_slots = named_slot_opcodes()

    for workflow_name, nodes in _iter_node_tables(data):
        for node_id, node in nodes.items():
            if not isinstance(node, dict):
                continue
            opcode = node.get("opcode", "")
            inputs = node.get("inputs")
            if opcode in named_slots or not isinstance(inputs, dict) or not inputs:
                continue

            interface = default_registry.get_interface(opcode)
            if "error" in interface:
                continue

            params = [p["name"] for p in interface["parameters"]]
            keys = [str(k).lower() for k in inputs.keys()]
            misbound = [
                (key, params[i])
                for i, key in enumerate(keys)
                if key in params and i < len(params) and params[i] != key
            ]
            if misbound:
                pairs = ", ".join(f"{key} -> {param}" for key, param in misbound)
                warnings.append(
                    f"{workflow_name}.{node_id} ({opcode}): {pairs}. "
                    f"Input names bind by position today; check the values before migrating."
                )

    return warnings


def migrate_data(data: Any, use_names: bool = False) -> tuple[int, list[str]]:
    """Rewrite every node in place. Returns (nodes migrated, dropped-key notes)."""
    named_slots = named_slot_opcodes()
    migrated = 0
    notes = []

    for workflow_name, nodes in _iter_node_tables(data):
        for node_id, node in list(nodes.items()):
            new_node, dropped = _migrate_node(node, named_slots, use_names)
            if new_node is None:
                continue
            nodes[node_id] = new_node
            migrated += 1
            if dropped:
                notes.append(
                    f"{workflow_name}.{node_id} ({node.get('opcode', '?')}): "
                    f"dropped {', '.join(dropped)}, which the legacy reader ignored."
                )

    return migrated, notes


def migrate_text(
    text: str, suffix: str, use_names: bool = False
) -> tuple[str, int, list[str]]:
    """Migrate one workflow document. Returns (new text, nodes migrated, warnings)."""
    if suffix.lower() in YAML_SUFFIXES:
        yaml = _yaml()
        data = yaml.load(text)
    else:
        data = json.loads(text)

    if not isinstance(data, dict) or "workflows" not in data:
        return text, 0, []

    warnings = find_misbindings(data)
    migrated, notes = migrate_data(data, use_names)
    warnings.extend(notes)
    if not migrated:
        return text, 0, warnings

    if suffix.lower() in YAML_SUFFIXES:
        buffer = io.StringIO()
        _yaml().dump(data, buffer)
        return buffer.getvalue(), migrated, warnings

    return json.dumps(data, indent=2, ensure_ascii=False) + "\n", migrated, warnings


# Directories a workflow tree never keeps its own files in
SKIPPED_DIRS = {"node_modules", "__pycache__", ".git", ".venv", "venv", "dist", "build"}


def _is_candidate(path: Path, root: Path) -> bool:
    """True for a workflow file outside vendored and hidden directories."""
    if path.suffix.lower() not in WORKFLOW_SUFFIXES or not path.is_file():
        return False
    parts = path.relative_to(root).parts[:-1]
    return not any(p in SKIPPED_DIRS or p.startswith(".") for p in parts)


def collect_files(paths: list[str]) -> list[Path]:
    """Expand paths into workflow files, recursing into directories."""
    files = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(p for p in path.rglob("*") if _is_candidate(p, path)))
        elif path.is_file():
            files.append(path)
        else:
            raise FileNotFoundError(f"No such file or directory: {raw}")
    return files
