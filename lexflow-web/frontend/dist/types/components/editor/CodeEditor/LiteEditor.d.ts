import type { CodeEditorProps } from "./types";
interface LiteEditorProps extends CodeEditorProps {
    value: string;
    onChange: (value: string) => void;
    isParsing?: boolean;
}
export declare function LiteEditor({ className, value, onChange, isParsing }: LiteEditorProps): import("react/jsx-runtime").JSX.Element;
export {};
