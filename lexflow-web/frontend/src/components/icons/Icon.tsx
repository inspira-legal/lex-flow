import type { SVGProps } from "react"

export interface IconProps extends SVGProps<SVGSVGElement> {
  size?: number | string
}

export function createIcon(
  path: React.ReactNode,
  displayName: string,
  defaultSize = 18
) {
  const Icon = ({ size = defaultSize, className, ...props }: IconProps) => (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={2}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
      {...props}
    >
      {path}
    </svg>
  )
  Icon.displayName = displayName
  return Icon
}
