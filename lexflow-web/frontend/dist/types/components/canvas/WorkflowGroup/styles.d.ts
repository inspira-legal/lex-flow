import type { CSSProperties } from "react";
export declare function getGroupLayout(x: number, y: number, width: number, height: number): {
    padding: number;
    labelHeight: number;
    rect: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
    header: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
    label: {
        x: number;
        y: number;
    };
    dragIcon: {
        x: number;
        y: number;
    };
};
export declare function getBorderStyle(isMain: boolean): CSSProperties;
export declare function getLabelBgStyle(isMain: boolean): CSSProperties;
export declare function getLabelStyle(isMain: boolean): CSSProperties;
export declare const dragHandleStyle: CSSProperties;
export declare const dragIconStyle: CSSProperties;
