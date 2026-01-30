import type { VariantProps } from "class-variance-authority"
import type { ComponentPropsWithoutRef } from "react"
import type { selectVariants } from "./styles"

export interface SelectProps
  extends Omit<ComponentPropsWithoutRef<"select">, "size">,
    VariantProps<typeof selectVariants> {}
