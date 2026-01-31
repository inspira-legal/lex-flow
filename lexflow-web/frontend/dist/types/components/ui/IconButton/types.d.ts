import type { VariantProps } from "class-variance-authority";
import type { ComponentPropsWithoutRef, ReactNode } from "react";
import type { iconButtonVariants } from "./styles";
export interface IconButtonProps extends ComponentPropsWithoutRef<"button">, VariantProps<typeof iconButtonVariants> {
    icon: ReactNode;
    label: string;
}
