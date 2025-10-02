"""Example of adding custom opcodes to LexFlow."""

import asyncio
from typing import Any
from lexflow import opcode, default_registry, OpcodeRegistry


# Example 1: Simple registration using global registry
@opcode()
async def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, int(n) + 1):
        a, b = b, a + b
    return b


@opcode("format_name")
async def format_full_name(first: str, last: str, title: str = "Mr.") -> str:
    """Format a full name with optional title."""
    return f"{title} {first} {last}"


@opcode()
async def is_valid_email(email: str) -> bool:
    """Simple email validation."""
    return "@" in email and "." in email.split("@")[1]


async def example_simple_registration():
    """Example using the simple global registry pattern."""
    print("=" * 60)
    print("SIMPLE REGISTRATION (Global Registry)")
    print("=" * 60)

    # Opcodes registered above are available to all engines automatically
    result = await default_registry.call("fibonacci", [10])
    print(f"\n✓ fibonacci(10) = {result}")

    result = await default_registry.call("format_name", ["John", "Doe"])
    print(f"✓ format_name('John', 'Doe') = '{result}'")

    result = await default_registry.call("format_name", ["Jane", "Smith", "Dr."])
    print(f"✓ format_name('Jane', 'Smith', 'Dr.') = '{result}'")

    result = await default_registry.call("is_valid_email", ["user@example.com"])
    print(f"✓ is_valid_email('user@example.com') = {result}")

    result = await default_registry.call("is_valid_email", ["invalid-email"])
    print(f"✓ is_valid_email('invalid-email') = {result}")

    print("\n" + "-" * 60)
    interface = default_registry.get_interface("format_name")
    print(f"📦 {interface['name']}")
    print(f"   {interface['doc']}")
    print("\n   Parameters:")
    for param in interface["parameters"]:
        required = "required" if param["required"] else "optional"
        default = f" = {param.get('default', '')}" if not param["required"] else ""
        print(f"     • {param['name']}: {param['type']} ({required}){default}")
    print(f"\n   Returns: {interface['return_type']}")
    print("=" * 60)


# Example 2: Advanced - Custom isolated registry
async def example_custom_registry():
    """Example of using a custom registry for isolation."""
    print("\n" + "=" * 60)
    print("ADVANCED: Custom Isolated Registry")
    print("=" * 60)

    # Create a custom registry (doesn't include global opcodes)
    custom_registry = OpcodeRegistry()

    @custom_registry.register()
    async def custom_multiply(x: int, y: int) -> int:
        """Multiply two numbers."""
        return x * y * 100  # Custom behavior

    # Custom registry only has builtins + custom opcodes
    result = await custom_registry.call("custom_multiply", [5, 3])
    print(f"\n✓ custom_multiply(5, 3) = {result}")

    # Fibonacci not available in custom registry
    try:
        await custom_registry.call("fibonacci", [10])
    except ValueError as e:
        print(f"✓ Expected error: {e}")

    print("\n" + "=" * 60)


# Example 3: Domain-specific opcodes (AI workflows)
@opcode()
async def ai_sentiment(text: str) -> str:
    """Analyze sentiment of text (mock implementation)."""
    positive_words = ["good", "great", "awesome", "love"]
    negative_words = ["bad", "terrible", "hate", "awful"]

    text_lower = text.lower()
    pos_count = sum(1 for word in positive_words if word in text_lower)
    neg_count = sum(1 for word in negative_words if word in text_lower)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"


@opcode()
async def ai_summarize(text: str, max_length: int = 50) -> str:
    """Summarize text to max length (mock implementation)."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


@opcode()
async def ai_translate(text: str, target_lang: str = "es") -> str:
    """Translate text to target language (mock implementation)."""
    translations = {
        "es": {"hello": "hola", "world": "mundo", "good": "bueno"},
        "fr": {"hello": "bonjour", "world": "monde", "good": "bon"},
    }

    text_lower = text.lower()
    lang_dict = translations.get(target_lang, {})

    for eng, foreign in lang_dict.items():
        text_lower = text_lower.replace(eng, foreign)

    return text_lower


async def example_ai_opcodes():
    """Example of domain-specific AI workflow opcodes."""
    print("\n" + "=" * 60)
    print("AI WORKFLOW OPCODES")
    print("=" * 60)

    result = await default_registry.call("ai_sentiment", ["This is awesome and great!"])
    print(f"\n✓ ai_sentiment('This is awesome and great!') = {result}")

    result = await default_registry.call("ai_sentiment", ["This is terrible and awful!"])
    print(f"✓ ai_sentiment('This is terrible and awful!') = {result}")

    long_text = "This is a very long piece of text that needs to be summarized."
    result = await default_registry.call("ai_summarize", [long_text, 30])
    print(f"✓ ai_summarize('{long_text}', 30)")
    print(f"  = '{result}'")

    result = await default_registry.call("ai_translate", ["hello world", "es"])
    print(f"✓ ai_translate('hello world', 'es') = '{result}'")

    print("=" * 60)


# Example 4: Data processing opcodes
@opcode()
async def json_parse(json_string: str) -> dict:
    """Parse JSON string to dictionary."""
    import json

    return json.loads(json_string)


@opcode()
async def json_stringify(data: dict) -> str:
    """Convert dictionary to JSON string."""
    import json

    return json.dumps(data)


@opcode()
async def csv_parse(csv_string: str, delimiter: str = ",") -> list[list[str]]:
    """Parse CSV string to list of rows."""
    lines = csv_string.strip().split("\n")
    return [line.split(delimiter) for line in lines]


@opcode()
async def dict_get(data: dict, key: str, default: Any = None) -> Any:
    """Get value from dictionary with default."""
    return data.get(key, default)


async def example_data_opcodes():
    """Example of data processing opcodes."""
    print("\n" + "=" * 60)
    print("DATA PROCESSING OPCODES")
    print("=" * 60)

    json_str = '{"name": "Alice", "age": 30}'
    result = await default_registry.call("json_parse", [json_str])
    print(f"\n✓ json_parse('{json_str}')")
    print(f"  = {result}")

    result = await default_registry.call("json_stringify", [{"x": 1, "y": 2}])
    print(f"✓ json_stringify({{'x': 1, 'y': 2}}) = '{result}'")

    csv = "name,age\nAlice,30\nBob,25"
    result = await default_registry.call("csv_parse", [csv])
    print(f"✓ csv_parse('{csv.replace(chr(10), ' | ')}')")
    print(f"  = {result}")

    result = await default_registry.call("dict_get", [{"x": 10}, "x"])
    print(f"✓ dict_get({{'x': 10}}, 'x') = {result}")

    result = await default_registry.call("dict_get", [{"x": 10}, "y", "default"])
    print(f"✓ dict_get({{'x': 10}}, 'y', 'default') = {result}")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(example_simple_registration())
    asyncio.run(example_custom_registry())
    asyncio.run(example_ai_opcodes())
    asyncio.run(example_data_opcodes())

    print("\n✅ All custom opcode examples completed!")
    print("\n💡 Key takeaways:")
    print("   • Use @opcode() decorator for simple registration")
    print("   • No need to create registries manually")
    print("   • All engines share the global registry by default")
    print("   • Advanced users can create custom registries for isolation")
    print("   • Type hints provide automatic documentation")
