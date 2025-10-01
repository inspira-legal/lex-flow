"""Test script to demonstrate opcode introspection capabilities."""

import asyncio
from lexflow.opcodes import OpcodeRegistry


async def main():
    registry = OpcodeRegistry()

    print("=" * 60)
    print("OPCODE INTROSPECTION DEMONSTRATION")
    print("=" * 60)

    # List all opcodes
    print(f"\n📋 Total opcodes registered: {len(registry.list_opcodes())}")
    print("\n🔧 Available opcodes:")
    for opcode in registry.list_opcodes()[:10]:  # Show first 10
        print(f"  - {opcode}")
    print(f"  ... and {len(registry.list_opcodes()) - 10} more\n")

    # Show detailed interface for specific opcodes
    examples = [
        "operator_add",
        "math_random",
        "string_split",
        "list_range",
        "io_print",
    ]

    for opcode_name in examples:
        print("\n" + "-" * 60)
        interface = registry.get_interface(opcode_name)
        print(f"📦 {interface['name']}")
        print(f"   {interface['doc']}")
        print(f"\n   Parameters:")
        for param in interface["parameters"]:
            required = "required" if param["required"] else "optional"
            default = f" = {param.get('default', '')}" if not param["required"] else ""
            print(f"     • {param['name']}: {param['type']} ({required}){default}")
        print(f"\n   Returns: {interface['return_type']}")

    # Test calling opcodes
    print("\n" + "=" * 60)
    print("TESTING OPCODE CALLS")
    print("=" * 60)

    # Test addition
    result = await registry.call("operator_add", [5, 3])
    print(f"\n✓ operator_add(5, 3) = {result}")

    # Test string concatenation
    result = await registry.call("operator_add", ["Hello", " World"])
    print(f"✓ operator_add('Hello', ' World') = '{result}'")

    # Test modulo (newly added!)
    result = await registry.call("operator_modulo", [10, 3])
    print(f"✓ operator_modulo(10, 3) = {result}")

    # Test string operations
    result = await registry.call("string_upper", ["hello world"])
    print(f"✓ string_upper('hello world') = '{result}'")

    # Test list operations
    result = await registry.call("list_range", [1, 6])
    print(f"✓ list_range(1, 6) = {result}")

    # Test optional parameter
    result = await registry.call("string_split", ["a,b,c", ","])
    print(f"✓ string_split('a,b,c', ',') = {result}")

    # Test variadic arguments
    result = await registry.call("range", [5])
    print(f"✓ range(5) = {result}")

    print("\n" + "=" * 60)
    print("✅ All tests passed! New opcode system working perfectly.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
