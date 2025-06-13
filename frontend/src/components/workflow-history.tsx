import { useEffect, useState } from 'react'
import { WorkflowService } from '@/lib/workflow'
import type { WorkflowHistoryItem, StepOutput } from '@/types/workflow'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { RefreshCw } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'

export function WorkflowHistoryPage() {
  const [history, setHistory] = useState<WorkflowHistoryItem[]>([])
  const [loading, setLoading] = useState<boolean>(false)
  const [stepsMap, setStepsMap] = useState<Record<string, StepOutput[]>>({})

  useEffect(() => {
    setLoading(true)
    WorkflowService.history()
      .then(async (items) => {
        setHistory(items)

        // Fetch steps for each item in parallel
        const entries = await Promise.all(
          items.map(async (it) => {
            try {
              const steps = await WorkflowService.getSteps(it.request_id)
              return [it.request_id, steps] as const
            } catch {
              return [it.request_id, []] as const
            }
          })
        )

        setStepsMap(Object.fromEntries(entries))
      })
      .finally(() => setLoading(false))
  }, [])

  const statusVariant = (status: string) => {
    switch (status) {
      case 'completed':
      case 'done':
        return 'default'
      case 'running':
      case 'retrying':
        return 'secondary'
      case 'failed':
        return 'destructive'
      default:
        return 'outline'
    }
  }

  if (loading) {
    return (
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <RefreshCw className="w-4 h-4 animate-spin" /> Loading history...
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Workflow History</h1>

      {history.length === 0 ? (
        <p className="text-muted-foreground">No workflows found.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {history.map((item) => {
            const steps = stepsMap[item.request_id] ?? []

            return (
              <Card key={item.request_id}>
                <CardHeader>
                  <CardTitle className="flex items-center justify-between gap-2 text-base">
                    <span className="truncate max-w-[60%]" title={item.query}>
                      {item.query}
                    </span>
                    <Badge variant={statusVariant(item.status)}>{item.status}</Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="text-xs text-muted-foreground space-y-2">
                  <div>
                    <strong>ID:</strong> {item.request_id}
                  </div>
                  <div>
                    <strong>Created:</strong>{' '}
                    {formatDistanceToNow(new Date(item.created_at * 1000), { addSuffix: true })}
                  </div>
                  <div>
                    <strong>Updated:</strong>{' '}
                    {formatDistanceToNow(new Date(item.updated_at * 1000), { addSuffix: true })}
                  </div>

                  {/* Step details */}
                  {steps.length > 0 && (
                    <div className="pt-2 space-y-2">
                      {steps.map((step) => (
                        <div key={step.name} className="border rounded p-2 bg-muted/50">
                          <div className="flex items-center justify-between">
                            <span className="capitalize font-medium">{step.name}</span>
                            <Badge variant={statusVariant(step.status)}>{step.status}</Badge>
                          </div>
                          {step.output && (
                            <pre className="mt-1 whitespace-pre-wrap break-all text-[10px]">
                              {JSON.stringify(step.output, null, 2)}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
