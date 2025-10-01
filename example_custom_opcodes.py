"""Example of adding custom opcodes to LexFlow."""

import asyncio
from typing import Any
from lexflow.opcodes import OpcodeRegistry


# Example 1: Extend the built-in registry
async def example_extend_builtins():
    registry = OpcodeRegistry()

    # Add a custom Fibonacci opcode
    @registry.register()
    async def fibonacci(n: int) -> int:
        """Calculate nth Fibonacci number."""
        if n <= 1:
            return n
        a, b = 0, 1
        for _ in range(2, int(n) + 1):
            a, b = b, a + b
        return b

    # Add a custom text formatting opcode
    @registry.register("format_name")
    async def format_full_name(first: str, last: str, title: str = "Mr.") -> str:
        """Format a full name with optional title."""
        return f"{title} {first} {last}"

    # Add a validation opcode
    @registry.register()
    async def is_valid_email(email: str) -> bool:
        """Simple email validation."""
        return "@" in email and "." in email.split("@")[1]

    # Test the custom opcodes
    print("=" * 60)
    print("CUSTOM OPCODE EXAMPLES")
    print("=" * 60)

    # Fibonacci
    result = await registry.call("fibonacci", [10])
    print(f"\n✓ fibonacci(10) = {result}")

    # Format name with default title
    result = await registry.call("format_name", ["John", "Doe"])
    print(f"✓ format_name('John', 'Doe') = '{result}'")

    # Format name with custom title
    result = await registry.call("format_name", ["Jane", "Smith", "Dr."])
    print(f"✓ format_name('Jane', 'Smith', 'Dr.') = '{result}'")

    # Email validation
    result = await registry.call("is_valid_email", ["user@example.com"])
    print(f"✓ is_valid_email('user@example.com') = {result}")

    result = await registry.call("is_valid_email", ["invalid-email"])
    print(f"✓ is_valid_email('invalid-email') = {result}")

    # Show interface
    print("\n" + "-" * 60)
    interface = registry.get_interface("format_name")
    print(f"📦 {interface['name']}")
    print(f"   {interface['doc']}")
    print("\n   Parameters:")
    for param in interface["parameters"]:
        required = "required" if param["required"] else "optional"
        default = f" = {param.get('default', '')}" if not param["required"] else ""
        print(f"     • {param['name']}: {param['type']} ({required}){default}")
    print(f"\n   Returns: {interface['return_type']}")
    print("=" * 60)


# Example 2: Domain-specific opcodes (AI workflows)
async def example_ai_opcodes():
    """Example of domain-specific AI workflow opcodes."""
    registry = OpcodeRegistry()

    @registry.register()
    async def ai_sentiment(text: str) -> str:
        """Analyze sentiment of text (mock implementation)."""
        # In a real implementation, this would call an AI service
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

    @registry.register()
    async def ai_summarize(text: str, max_length: int = 50) -> str:
        """Summarize text to max length (mock implementation)."""
        # In a real implementation, this would call an AI service
        if len(text) <= max_length:
            return text
        return text[: max_length - 3] + "..."

    @registry.register()
    async def ai_translate(text: str, target_lang: str = "es") -> str:
        """Translate text to target language (mock implementation)."""
        # Mock translation
        translations = {
            "es": {"hello": "hola", "world": "mundo", "good": "bueno"},
            "fr": {"hello": "bonjour", "world": "monde", "good": "bon"},
        }

        text_lower = text.lower()
        lang_dict = translations.get(target_lang, {})

        for eng, foreign in lang_dict.items():
            text_lower = text_lower.replace(eng, foreign)

        return text_lower

    # Test AI opcodes
    print("\n" + "=" * 60)
    print("AI WORKFLOW OPCODES")
    print("=" * 60)

    result = await registry.call("ai_sentiment", ["This is awesome and great!"])
    print(f"\n✓ ai_sentiment('This is awesome and great!') = {result}")

    result = await registry.call("ai_sentiment", ["This is terrible and awful!"])
    print(f"✓ ai_sentiment('This is terrible and awful!') = {result}")

    long_text = "This is a very long piece of text that needs to be summarized."
    result = await registry.call("ai_summarize", [long_text, 30])
    print(f"✓ ai_summarize('{long_text}', 30)")
    print(f"  = '{result}'")

    result = await registry.call("ai_translate", ["hello world", "es"])
    print(f"✓ ai_translate('hello world', 'es') = '{result}'")

    print("=" * 60)


# Example 3: Data processing opcodes
async def example_data_opcodes():
    """Example of data processing opcodes."""
    registry = OpcodeRegistry()

    @registry.register()
    async def json_parse(json_string: str) -> dict:
        """Parse JSON string to dictionary."""
        import json

        return json.loads(json_string)

    @registry.register()
    async def json_stringify(data: dict) -> str:
        """Convert dictionary to JSON string."""
        import json

        return json.dumps(data)

    @registry.register()
    async def csv_parse(csv_string: str, delimiter: str = ",") -> list[list[str]]:
        """Parse CSV string to list of rows."""
        lines = csv_string.strip().split("\n")
        return [line.split(delimiter) for line in lines]

    @registry.register()
    async def dict_get(data: dict, key: str, default: Any = None) -> Any:
        """Get value from dictionary with default."""
        return data.get(key, default)

    # Test data opcodes
    print("\n" + "=" * 60)
    print("DATA PROCESSING OPCODES")
    print("=" * 60)

    json_str = '{"name": "Alice", "age": 30}'
    result = await registry.call("json_parse", [json_str])
    print(f"\n✓ json_parse('{json_str}')")
    print(f"  = {result}")

    result = await registry.call("json_stringify", [{"x": 1, "y": 2}])
    print(f"✓ json_stringify({{'x': 1, 'y': 2}}) = '{result}'")

    csv = "name,age\nAlice,30\nBob,25"
    result = await registry.call("csv_parse", [csv])
    print(f"✓ csv_parse('{csv.replace(chr(10), ' | ')}')")
    print(f"  = {result}")

    result = await registry.call("dict_get", [{"x": 10}, "x"])
    print(f"✓ dict_get({{'x': 10}}, 'x') = {result}")

    result = await registry.call("dict_get", [{"x": 10}, "y", "default"])
    print(f"✓ dict_get({{'x': 10}}, 'y', 'default') = {result}")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(example_extend_builtins())
    asyncio.run(example_ai_opcodes())
    asyncio.run(example_data_opcodes())

    print("\n✅ All custom opcode examples completed!")
    print("\n💡 Key takeaways:")
    print("   • Adding opcodes is as easy as decorating a function")
    print("   • Type hints provide automatic documentation")
    print("   • Optional parameters work seamlessly")
    print("   • Variadic arguments (*args) are supported")
    print("   • Introspection enables tooling and documentation")
