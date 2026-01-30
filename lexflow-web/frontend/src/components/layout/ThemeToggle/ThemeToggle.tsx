import { useTheme } from "@/lib/theme"
import { IconButton } from "@/components/ui"
import { SunIcon, MoonIcon } from "@/components/icons"
import type { ThemeToggleProps } from "./types"

export function ThemeToggle({ className }: ThemeToggleProps) {
  const { theme, toggleTheme } = useTheme()

  return (
    <IconButton
      className={className}
      icon={theme === "dark" ? <SunIcon /> : <MoonIcon />}
      label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
      onClick={toggleTheme}
    />
  )
}
