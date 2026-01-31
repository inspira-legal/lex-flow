// Enhanced ThemeProvider for embeddable library with CSS variable injection

import {
  createContext,
  useContext,
  useEffect,
  useState,
  useCallback,
  useMemo,
  type ReactNode,
} from "react";
import type { ThemeConfig, ThemeOption, ThemePreset } from "../types";
import { injectThemeVars, removeThemeVars } from "./inject";

interface ThemeContextValue {
  theme: ThemePreset;
  setTheme: (theme: ThemePreset) => void;
  toggleTheme: () => void;
  config: ThemeConfig;
  updateConfig: (config: ThemeConfig) => void;
}

const ThemeContext = createContext<ThemeContextValue | null>(null);

interface LibraryThemeProviderProps {
  children: ReactNode;
  instanceId: string;
  containerRef: React.RefObject<HTMLElement | null>;
  initialTheme?: ThemeOption;
  persist?: boolean;
}

function normalizeThemeOption(theme: ThemeOption | undefined): ThemeConfig {
  if (!theme) {
    return { preset: "dark" };
  }
  if (typeof theme === "string") {
    return { preset: theme };
  }
  return theme;
}

export function LibraryThemeProvider({
  children,
  instanceId,
  containerRef,
  initialTheme,
  persist = false,
}: LibraryThemeProviderProps) {
  const storageKey = `lexflow-theme-${instanceId}`;

  const [config, setConfig] = useState<ThemeConfig>(() => {
    if (persist && typeof window !== "undefined") {
      const stored = localStorage.getItem(storageKey);
      if (stored) {
        try {
          return JSON.parse(stored) as ThemeConfig;
        } catch {
          // Fall through to initial
        }
      }
    }
    return normalizeThemeOption(initialTheme);
  });

  const theme = useMemo<ThemePreset>(() => {
    return config.preset ?? "dark";
  }, [config.preset]);

  const setTheme = useCallback((preset: ThemePreset) => {
    setConfig((prev) => ({ ...prev, preset }));
  }, []);

  const toggleTheme = useCallback(() => {
    setConfig((prev) => {
      const current = prev.preset ?? "dark";
      const next = current === "dark" ? "light" : "dark";
      return { ...prev, preset: next };
    });
  }, []);

  const updateConfig = useCallback((newConfig: ThemeConfig) => {
    setConfig(newConfig);
  }, []);

  // Inject CSS variables when config changes
  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    injectThemeVars(container, config, instanceId);

    if (persist) {
      localStorage.setItem(storageKey, JSON.stringify(config));
    }

    return () => {
      removeThemeVars(instanceId);
    };
  }, [config, containerRef, instanceId, persist, storageKey]);

  // Listen for system theme changes
  useEffect(() => {
    if (config.preset !== "system") return;

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = () => {
      const container = containerRef.current;
      if (container) {
        injectThemeVars(container, config, instanceId);
      }
    };

    mediaQuery.addEventListener("change", handleChange);
    return () => mediaQuery.removeEventListener("change", handleChange);
  }, [config, containerRef, instanceId]);

  const value = useMemo(
    () => ({ theme, setTheme, toggleTheme, config, updateConfig }),
    [theme, setTheme, toggleTheme, config, updateConfig]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useLibraryTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    throw new Error("useLibraryTheme must be used within LibraryThemeProvider");
  }
  return ctx;
}

// Re-export the original ThemeProvider and useTheme for backwards compatibility
// The original theme.ts is at lib/theme.ts (same level as this theme/ directory)
export { ThemeProvider, useTheme, ThemeContext } from "@/lib/theme";
