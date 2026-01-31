import type { VariantProps } from "class-variance-authority";
import type { ComponentPropsWithoutRef } from "react";
import type { panelVariants } from "./styles";
export interface PanelProps extends ComponentPropsWithoutRef<"div">, VariantProps<typeof panelVariants> {
}
