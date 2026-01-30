import { forwardRef } from "react"
import { cn } from "@/lib/cn"
import { panelVariants } from "./styles"
import type { PanelProps } from "./types"

export const Panel = forwardRef<HTMLDivElement, PanelProps>(
  ({ className, variant, padding, radius, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(panelVariants({ variant, padding, radius, className }))}
        {...props}
      />
    )
  }
)
Panel.displayName = "Panel"
