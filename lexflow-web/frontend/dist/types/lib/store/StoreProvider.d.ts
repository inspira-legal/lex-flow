import { type ReactNode } from "react";
import { type EditorStoreState } from "./createStores";
import type { StoreApi } from "zustand";
export interface StoreProviderProps {
    children: ReactNode;
    instanceId: string;
    initialSource?: string;
    persistSource?: boolean;
}
export declare function StoreProvider({ children, instanceId, initialSource, persistSource, }: StoreProviderProps): import("react/jsx-runtime").JSX.Element;
export declare function useEditorStore<T>(selector: (state: EditorStoreState) => T): T;
export declare function useEditorStoreApi(): StoreApi<EditorStoreState>;
