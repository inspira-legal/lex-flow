import type { VariantProps } from "class-variance-authority";
import type { ReactNode } from "react";
import type { tooltipVariants } from "./styles";
export interface TooltipProps extends VariantProps<typeof tooltipVariants> {
    content: ReactNode;
    children: ReactNode;
    className?: string;
}
