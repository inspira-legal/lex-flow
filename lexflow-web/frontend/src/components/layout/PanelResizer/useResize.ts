import { useState, useEffect, useCallback, useRef } from "react"
import type { UseResizeOptions, UseResizeReturn } from "./types"

export function useResize({
  orientation,
  minSize,
  maxSize,
  defaultSize,
}: UseResizeOptions): UseResizeReturn {
  const [size, setSize] = useState(defaultSize)
  const [isResizing, setIsResizing] = useState(false)
  const containerRef = useRef<HTMLElement | null>(null)

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    containerRef.current = (e.target as HTMLElement).parentElement
    setIsResizing(true)
  }, [])

  useEffect(() => {
    if (!isResizing) return

    const handleMouseMove = (e: MouseEvent) => {
      if (!containerRef.current) return

      const containerRect = containerRef.current.getBoundingClientRect()
      let newSize: number

      if (orientation === "horizontal") {
        newSize = e.clientX - containerRect.left
      } else {
        newSize = containerRect.bottom - e.clientY
      }

      setSize(Math.min(maxSize, Math.max(minSize, newSize)))
    }

    const handleMouseUp = () => {
      setIsResizing(false)
    }

    document.addEventListener("mousemove", handleMouseMove)
    document.addEventListener("mouseup", handleMouseUp)

    return () => {
      document.removeEventListener("mousemove", handleMouseMove)
      document.removeEventListener("mouseup", handleMouseUp)
    }
  }, [isResizing, orientation, minSize, maxSize])

  return { size, isResizing, handleMouseDown }
}
