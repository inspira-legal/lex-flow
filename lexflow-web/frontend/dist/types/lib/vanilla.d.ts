import type { MountOptions, EditorInstance } from "./types";
import "../styles/variables.css";
import "../styles/index.css";
export declare function mount(container: HTMLElement | string, options?: Omit<MountOptions, "container">): EditorInstance;
export declare function unmountAll(): void;
export declare function getMountedCount(): number;
declare const _default: {
    mount: typeof mount;
    unmountAll: typeof unmountAll;
    getMountedCount: typeof getMountedCount;
};
export default _default;
