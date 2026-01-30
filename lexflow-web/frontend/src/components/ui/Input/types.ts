import type { VariantProps } from "class-variance-authority"
import type { ComponentPropsWithoutRef } from "react"
import type { inputVariants } from "./styles"

export interface InputProps
  extends Omit<ComponentPropsWithoutRef<"input">, "size">,
    VariantProps<typeof inputVariants> {}
