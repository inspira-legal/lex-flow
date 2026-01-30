import { cn } from "@/lib/cn"
import { tooltipVariants } from "./styles"
import type { TooltipProps } from "./types"

export function Tooltip({ content, children, position, className }: TooltipProps) {
  return (
    <div className="relative inline-block group">
      {children}
      <div className={cn(tooltipVariants({ position, className }))}>
        {content}
      </div>
    </div>
  )
}
