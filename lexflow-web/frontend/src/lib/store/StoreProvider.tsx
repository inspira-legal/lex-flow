// Scoped store provider for isolated editor instances

import { createContext, useContext, useMemo, type ReactNode } from "react";
import {
  createEditorStore,
  type EditorStoreState,
  type CreateStoresOptions,
} from "./createStores";
import type { StoreApi } from "zustand";
import { useStore } from "zustand";

// Context for the store
const EditorStoreContext = createContext<StoreApi<EditorStoreState> | null>(null);

// Store provider props
export interface StoreProviderProps {
  children: ReactNode;
  instanceId: string;
  initialSource?: string;
  persistSource?: boolean;
}

// Provider component that creates and provides an isolated store
export function StoreProvider({
  children,
  instanceId,
  initialSource,
  persistSource = false,
}: StoreProviderProps) {
  const store = useMemo(() => {
    const options: CreateStoresOptions = {
      instanceId,
      initialSource,
      persistSource,
    };
    return createEditorStore(options);
  }, [instanceId, initialSource, persistSource]);

  return (
    <EditorStoreContext.Provider value={store}>
      {children}
    </EditorStoreContext.Provider>
  );
}

// Hook to get the store
function useEditorStoreContext() {
  const store = useContext(EditorStoreContext);
  if (!store) {
    throw new Error("useEditorStore must be used within a StoreProvider");
  }
  return store;
}

// Hook to select state from the store
export function useEditorStore<T>(selector: (state: EditorStoreState) => T): T {
  const store = useEditorStoreContext();
  return useStore(store, selector);
}

// Hook to get the entire store API (for advanced usage)
export function useEditorStoreApi() {
  return useEditorStoreContext();
}
