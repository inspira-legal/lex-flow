// Runtime validation for opcode adapter returns

import type { OpcodeInterface } from "../api/types";

export function validateOpcodes(data: unknown): OpcodeInterface[] {
  if (!Array.isArray(data)) {
    throw new Error(
      `opcodeAdapter must return an array.\n` +
        `Received: ${typeof data}\n\n` +
        `Expected format:\n` +
        `[\n` +
        `  {\n` +
        `    name: "io_print",\n` +
        `    description: "Print to output",\n` +
        `    parameters: [{ name: "MESSAGE", type: "any", required: true }],\n` +
        `    return_type: "void"\n` +
        `  }\n` +
        `]`
    );
  }

  for (let i = 0; i < data.length; i++) {
    const op = data[i];
    if (!op || typeof op !== "object") {
      throw new Error(`opcodeAdapter[${i}] must be an object`);
    }
    if (typeof (op as Record<string, unknown>).name !== "string") {
      throw new Error(`opcodeAdapter[${i}].name must be a string`);
    }
    if (!Array.isArray((op as Record<string, unknown>).parameters)) {
      throw new Error(`opcodeAdapter[${i}].parameters must be an array`);
    }
  }

  return data as OpcodeInterface[];
}
