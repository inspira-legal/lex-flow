import { forwardRef } from "react"
import { cn } from "@/lib/cn"
import { iconButtonVariants } from "./styles"
import type { IconButtonProps } from "./types"

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(
  ({ className, variant, size, icon, label, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(iconButtonVariants({ variant, size, className }))}
        aria-label={label}
        title={label}
        {...props}
      >
        {icon}
      </button>
    )
  }
)
IconButton.displayName = "IconButton"
