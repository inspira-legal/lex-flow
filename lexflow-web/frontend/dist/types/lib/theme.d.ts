import { type ReactNode } from "react";
type Theme = "dark" | "light";
interface ThemeContextValue {
    theme: Theme;
    setTheme: (theme: Theme) => void;
    toggleTheme: () => void;
}
export declare const ThemeContext: import("react").Context<ThemeContextValue | null>;
export declare function ThemeProvider({ children }: {
    children: ReactNode;
}): import("react").FunctionComponentElement<import("react").ProviderProps<ThemeContextValue | null>>;
export declare function useTheme(): ThemeContextValue;
export {};
