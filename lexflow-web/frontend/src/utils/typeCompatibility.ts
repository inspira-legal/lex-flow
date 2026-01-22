// Type compatibility checking for orphan-to-reporter drag operations

// Map of compatible types (numeric types can be interchanged)
const NUMERIC_TYPES = new Set(['int', 'float', 'number', 'Integer', 'Float', 'Number'])
const STRING_TYPES = new Set(['str', 'string', 'String'])
const BOOL_TYPES = new Set(['bool', 'boolean', 'Boolean'])

export function checkTypeCompatibility(
  sourceType: string | undefined,
  targetType: string | undefined
): boolean | null {
  // If either type is unknown, return null (can't determine)
  if (!sourceType || !targetType) {
    return null
  }

  // Normalize types (lowercase, strip whitespace)
  const source = sourceType.toLowerCase().trim()
  const target = targetType.toLowerCase().trim()

  // "any" is compatible with everything
  if (source === 'any' || target === 'any') {
    return true
  }

  // Exact match
  if (source === target) {
    return true
  }

  // Numeric types are interchangeable
  if (NUMERIC_TYPES.has(source) && NUMERIC_TYPES.has(target)) {
    return true
  }

  // String types are interchangeable
  if (STRING_TYPES.has(source) && STRING_TYPES.has(target)) {
    return true
  }

  // Bool types are interchangeable
  if (BOOL_TYPES.has(source) && BOOL_TYPES.has(target)) {
    return true
  }

  // Check for Optional[X] format
  const optionalMatch = target.match(/^optional\[(.+)\]$/)
  if (optionalMatch) {
    // If target accepts Optional[X], check if source is compatible with X
    return checkTypeCompatibility(sourceType, optionalMatch[1])
  }

  // Check for Union types (X | Y)
  if (target.includes('|')) {
    const unionTypes = target.split('|').map((t) => t.trim())
    // Compatible if source matches any of the union types
    return unionTypes.some((t) => checkTypeCompatibility(sourceType, t) === true)
  }

  // Types don't match
  return false
}

export function getCompatibilityColor(compatibility: boolean | null): string {
  if (compatibility === true) return '#34D399' // Green
  if (compatibility === false) return '#F87171' // Red
  return '#94A3B8' // Neutral gray (unknown)
}
