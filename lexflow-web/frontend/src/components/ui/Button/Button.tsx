import { forwardRef } from "react"
import { cn } from "@/lib/cn"
import { buttonVariants } from "./styles"
import type { ButtonProps } from "./types"

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(buttonVariants({ variant, size, className }))}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"
