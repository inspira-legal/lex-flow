export declare const darkThemeVars: Record<string, string>;
export declare const lightThemeVars: Record<string, string>;
export declare const commonVars: Record<string, string>;
export type ThemePreset = "light" | "dark" | "system";
export declare function getPresetVars(preset: ThemePreset, prefersDark: boolean): Record<string, string>;
