import type { ThemeConfig } from "../types";
export declare function injectThemeVars(container: HTMLElement, config: ThemeConfig, instanceId: string): void;
export declare function removeThemeVars(instanceId: string): void;
export declare function createScopedCSS(config: ThemeConfig, selector: string): string;
