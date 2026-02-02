import type { EditorMetadata } from "@/services/metadata";
export interface HeaderProps {
    className?: string;
    onSave?: (source: string, metadata: EditorMetadata) => void | Promise<void>;
    showSaveButton?: boolean;
    saveButtonLabel?: string;
    showExamples?: boolean;
}
export interface ExamplesSelectProps {
    className?: string;
}
