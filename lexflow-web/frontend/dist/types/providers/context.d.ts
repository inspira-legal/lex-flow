import { type ReactNode } from "react";
import type { BackendProvider } from "./types";
interface BackendProviderWrapperProps {
    provider: BackendProvider;
    children: ReactNode;
}
export declare function BackendProviderWrapper({ provider, children, }: BackendProviderWrapperProps): import("react/jsx-runtime").JSX.Element;
export declare function useBackendProvider(): BackendProvider;
export {};
