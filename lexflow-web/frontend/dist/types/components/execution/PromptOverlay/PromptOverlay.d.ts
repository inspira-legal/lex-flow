import type { PendingPrompt } from "@/store/executionStore";
interface PromptOverlayProps {
    prompt: PendingPrompt;
    onSubmit: (value: unknown) => void;
}
export declare function PromptOverlay({ prompt, onSubmit }: PromptOverlayProps): import("react/jsx-runtime").JSX.Element;
export {};
