import { useWorkflowStore } from "@/store"
import { useBackendProvider, supportsExamples } from "@/providers"
import { Select } from "@/components/ui"
import type { ExamplesSelectProps } from "./types"

export function ExamplesSelect({ className }: ExamplesSelectProps) {
  const { examples, setSource } = useWorkflowStore()
  const provider = useBackendProvider()

  const handleSelect = async (e: React.ChangeEvent<HTMLSelectElement>) => {
    const path = e.target.value
    if (!path) return
    try {
      if (supportsExamples(provider)) {
        const example = await provider.getExample(path)
        setSource(example.content)
      }
    } catch (err) {
      console.error("Failed to load example:", err)
    }
    e.target.value = ""
  }

  const grouped = examples.reduce(
    (acc, ex) => {
      if (!acc[ex.category]) acc[ex.category] = []
      acc[ex.category].push(ex)
      return acc
    },
    {} as Record<string, typeof examples>
  )

  return (
    <Select className={className} onChange={handleSelect} defaultValue="">
      <option value="">Load Example...</option>
      {Object.entries(grouped).map(([category, items]) => (
        <optgroup key={category} label={category}>
          {items.map((ex) => (
            <option key={ex.path} value={ex.path}>
              {ex.name}
            </option>
          ))}
        </optgroup>
      ))}
    </Select>
  )
}
