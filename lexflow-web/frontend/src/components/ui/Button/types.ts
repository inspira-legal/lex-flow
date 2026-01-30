import type { VariantProps } from "class-variance-authority"
import type { ComponentPropsWithoutRef } from "react"
import type { buttonVariants } from "./styles"

export interface ButtonProps
  extends ComponentPropsWithoutRef<"button">,
    VariantProps<typeof buttonVariants> {}
