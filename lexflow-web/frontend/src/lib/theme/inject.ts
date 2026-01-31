// Runtime CSS variable injection for vanilla JS usage

import { getPresetVars, type ThemePreset } from "./presets";
import type { ThemeConfig, ThemeColors } from "../types";

// Style element ID for cleanup
const STYLE_ID_PREFIX = "lexflow-editor-theme-";

// Map user-friendly color names to CSS variable names
function mapColorsToVars(colors: ThemeColors): Record<string, string> {
  const vars: Record<string, string> = {};

  if (colors.accent) {
    vars["--color-accent-blue"] = colors.accent;
  }
  if (colors.background) {
    vars["--color-surface-0"] = colors.background;
  }
  if (colors.surface) {
    vars["--color-surface-1"] = colors.surface;
    vars["--color-surface-2"] = colors.surface;
  }
  if (colors.text) {
    vars["--color-text-primary"] = colors.text;
  }
  if (colors.border) {
    vars["--color-border-default"] = colors.border;
  }

  return vars;
}

// Inject CSS variables into a container element
export function injectThemeVars(
  container: HTMLElement,
  config: ThemeConfig,
  instanceId: string
): void {
  const styleId = `${STYLE_ID_PREFIX}${instanceId}`;

  // Remove existing style if present
  const existing = document.getElementById(styleId);
  if (existing) {
    existing.remove();
  }

  // Determine preset
  const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const preset: ThemePreset = config.preset ?? "dark";

  // Get base vars from preset
  let vars = getPresetVars(preset, prefersDark);

  // Apply color overrides
  if (config.colors) {
    vars = { ...vars, ...mapColorsToVars(config.colors) };
  }

  // Apply custom CSS variables
  if (config.cssVariables) {
    vars = { ...vars, ...config.cssVariables };
  }

  // Create CSS text
  const cssVarText = Object.entries(vars)
    .map(([key, value]) => `${key}: ${value};`)
    .join("\n    ");

  const css = `
    [data-lexflow-instance="${instanceId}"] {
      ${cssVarText}
    }
  `;

  // Create and inject style element
  const style = document.createElement("style");
  style.id = styleId;
  style.textContent = css;
  document.head.appendChild(style);

  // Set data attribute on container
  container.setAttribute("data-lexflow-instance", instanceId);

  // Add/remove light class based on theme
  const isLight = preset === "light" || (preset === "system" && !prefersDark);
  if (isLight) {
    container.classList.add("light");
  } else {
    container.classList.remove("light");
  }
}

// Remove injected styles
export function removeThemeVars(instanceId: string): void {
  const styleId = `${STYLE_ID_PREFIX}${instanceId}`;
  const style = document.getElementById(styleId);
  if (style) {
    style.remove();
  }
}

// Create a scoped CSS string for the editor (for CSS-in-JS scenarios)
export function createScopedCSS(config: ThemeConfig, selector: string): string {
  const prefersDark = typeof window !== "undefined"
    ? window.matchMedia("(prefers-color-scheme: dark)").matches
    : true;

  const preset: ThemePreset = config.preset ?? "dark";
  let vars = getPresetVars(preset, prefersDark);

  if (config.colors) {
    vars = { ...vars, ...mapColorsToVars(config.colors) };
  }

  if (config.cssVariables) {
    vars = { ...vars, ...config.cssVariables };
  }

  const cssVarText = Object.entries(vars)
    .map(([key, value]) => `${key}: ${value};`)
    .join("\n  ");

  return `${selector} {\n  ${cssVarText}\n}`;
}
