import { type ReactNode } from "react";
import type { ThemeConfig, ThemeOption, ThemePreset } from "../types";
interface ThemeContextValue {
    theme: ThemePreset;
    setTheme: (theme: ThemePreset) => void;
    toggleTheme: () => void;
    config: ThemeConfig;
    updateConfig: (config: ThemeConfig) => void;
}
interface LibraryThemeProviderProps {
    children: ReactNode;
    instanceId: string;
    containerRef: React.RefObject<HTMLElement | null>;
    initialTheme?: ThemeOption;
    persist?: boolean;
}
export declare function LibraryThemeProvider({ children, instanceId, containerRef, initialTheme, persist, }: LibraryThemeProviderProps): import("react/jsx-runtime").JSX.Element;
export declare function useLibraryTheme(): ThemeContextValue;
export { ThemeProvider, useTheme, ThemeContext } from "@/lib/theme";
