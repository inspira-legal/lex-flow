import type { VariantProps } from "class-variance-authority"
import type { ComponentPropsWithoutRef } from "react"
import type { badgeVariants } from "./styles"

export interface BadgeProps
  extends ComponentPropsWithoutRef<"span">,
    VariantProps<typeof badgeVariants> {}
