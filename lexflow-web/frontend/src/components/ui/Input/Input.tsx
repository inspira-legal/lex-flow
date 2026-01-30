import { forwardRef } from "react"
import { cn } from "@/lib/cn"
import { inputVariants } from "./styles"
import type { InputProps } from "./types"

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ className, size, type = "text", ...props }, ref) => {
    return (
      <input
        ref={ref}
        type={type}
        className={cn(inputVariants({ size, className }))}
        {...props}
      />
    )
  }
)
Input.displayName = "Input"
