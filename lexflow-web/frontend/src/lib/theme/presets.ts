// Theme presets extracted from index.css

// Dark theme (default)
export const darkThemeVars: Record<string, string> = {
  "--color-surface-0": "oklch(0.18 0.008 250)",
  "--color-surface-1": "oklch(0.21 0.008 250)",
  "--color-surface-2": "oklch(0.24 0.008 250)",
  "--color-surface-3": "oklch(0.28 0.008 250)",
  "--color-surface-4": "oklch(0.34 0.008 250)",
  "--color-border-subtle": "oklch(0.28 0.008 250)",
  "--color-border-default": "oklch(0.35 0.008 250)",
  "--color-border-strong": "oklch(0.48 0.008 250)",
  "--color-text-muted": "oklch(0.52 0.008 250)",
  "--color-text-secondary": "oklch(0.68 0.005 250)",
  "--color-text-primary": "oklch(0.90 0.005 250)",
  "--color-accent-blue": "oklch(0.65 0.18 240)",
  "--color-accent-green": "oklch(0.72 0.16 145)",
  "--color-accent-amber": "oklch(0.75 0.15 75)",
  "--color-accent-red": "oklch(0.65 0.20 25)",
  "--color-accent-violet": "oklch(0.55 0.18 290)",
  "--color-node-control": "oklch(0.55 0.12 240)",
  "--color-node-data": "oklch(0.55 0.12 145)",
  "--color-node-io": "oklch(0.55 0.12 75)",
  "--color-node-logic": "oklch(0.55 0.12 290)",
  "--color-node-math": "oklch(0.55 0.12 25)",
  "--color-node-string": "oklch(0.55 0.12 180)",
};

// Light theme
export const lightThemeVars: Record<string, string> = {
  "--color-surface-0": "oklch(0.97 0.005 250)",
  "--color-surface-1": "oklch(0.95 0.005 250)",
  "--color-surface-2": "oklch(0.92 0.006 250)",
  "--color-surface-3": "oklch(0.88 0.008 250)",
  "--color-surface-4": "oklch(0.82 0.010 250)",
  "--color-border-subtle": "oklch(0.88 0.006 250)",
  "--color-border-default": "oklch(0.80 0.008 250)",
  "--color-border-strong": "oklch(0.68 0.010 250)",
  "--color-text-muted": "oklch(0.52 0.008 250)",
  "--color-text-secondary": "oklch(0.38 0.008 250)",
  "--color-text-primary": "oklch(0.18 0.010 250)",
  // Accent colors stay the same for light theme
  "--color-accent-blue": "oklch(0.65 0.18 240)",
  "--color-accent-green": "oklch(0.72 0.16 145)",
  "--color-accent-amber": "oklch(0.75 0.15 75)",
  "--color-accent-red": "oklch(0.65 0.20 25)",
  "--color-accent-violet": "oklch(0.55 0.18 290)",
  "--color-node-control": "oklch(0.55 0.12 240)",
  "--color-node-data": "oklch(0.55 0.12 145)",
  "--color-node-io": "oklch(0.55 0.12 75)",
  "--color-node-logic": "oklch(0.55 0.12 290)",
  "--color-node-math": "oklch(0.55 0.12 25)",
  "--color-node-string": "oklch(0.55 0.12 180)",
};

// Common variables for both themes
export const commonVars: Record<string, string> = {
  "--font-sans": "'Inter', 'Plus Jakarta Sans', system-ui, sans-serif",
  "--font-mono": "'JetBrains Mono', monospace",
  "--radius-sm": "2px",
  "--radius-md": "3px",
  "--radius-lg": "4px",
};

export type ThemePreset = "light" | "dark" | "system";

export function getPresetVars(preset: ThemePreset, prefersDark: boolean): Record<string, string> {
  const isDark = preset === "system" ? prefersDark : preset === "dark";
  return {
    ...commonVars,
    ...(isDark ? darkThemeVars : lightThemeVars),
  };
}
