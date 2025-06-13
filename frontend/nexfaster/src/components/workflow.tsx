import { useEffect, useState } from 'react'
import { InstancesService } from '@/lib/instances'
import { WorkflowService } from '@/lib/workflow'
import type { DatabaseConnectionResponse } from '@/types/connection'
import type { StepOutput } from '@/types/workflow'

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useToast } from '@/components/ui/use-toast'

export function WorkflowPage() {
  type Mode = 'manual' | 'connection'
  const [mode, setMode] = useState<Mode>('manual')
  const { toast } = useToast()

  // Form state
  const [query, setQuery] = useState<string>('')
  const [schemaJson, setSchemaJson] = useState<string>(`{
  "tables": {}
}`)
  const [connections, setConnections] = useState<DatabaseConnectionResponse[]>([])
  const [selectedConnection, setSelectedConnection] = useState<string>('')

  const [loadingConnections, setLoadingConnections] = useState<boolean>(false)
  const [starting, setStarting] = useState<boolean>(false)

  // Workflow state
  const [requestId, setRequestId] = useState<string | null>(null)
  const [steps, setSteps] = useState<StepOutput[]>([])
  const [polling, setPolling] = useState<boolean>(false)

  // Load connections when mode is connection
  useEffect(() => {
    if (mode === 'connection') {
      setLoadingConnections(true)
      InstancesService.list()
        .then((data) => {
          setConnections(data)
          if (data.length > 0) setSelectedConnection(data[0].id)
        })
        .catch(() => toast({ title: 'Error', description: 'Failed to load connections', variant: 'destructive' }))
        .finally(() => setLoadingConnections(false))
    }
  }, [mode, toast])

  const startWorkflow = async () => {
    if (!query.trim()) {
      toast({ title: 'Missing query', description: 'Enter a natural language query' })
      return
    }

    setStarting(true)
    try {
      const resp =
        mode === 'manual'
          ? await WorkflowService.start({ query, schema: JSON.parse(schemaJson) })
          : await WorkflowService.startWithConnection(query, selectedConnection)
      setRequestId(resp.request_id)
      setSteps([])
      setPolling(true)
    } catch (e: any) {
      toast({ title: 'Error', description: e?.message ?? 'Failed to start workflow', variant: 'destructive' })
    } finally {
      setStarting(false)
    }
  }

  // Poll steps
  useEffect(() => {
    if (!requestId || !polling) return

    const interval = setInterval(async () => {
      try {
        const newSteps = await WorkflowService.getSteps(requestId)
        setSteps(newSteps)
        const allDone = newSteps.every((s) => s.status === 'done' || s.status === 'failed')
        if (allDone) {
          setPolling(false)
        }
      } catch (e) {
        console.error(e)
      }
    }, 2000)
    return () => clearInterval(interval)
  }, [requestId, polling])

  const renderStepCard = (step: StepOutput) => {
    const statusVariant =
      step.status === 'done'
        ? 'default'
        : step.status === 'running'
        ? 'secondary'
        : step.status === 'failed'
        ? 'destructive'
        : 'outline'
    return (
      <Card key={step.name} className="border-border">
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg capitalize">{step.name} Agent</CardTitle>
          <Badge variant={statusVariant}>{step.status}</Badge>
        </CardHeader>
        {step.output && (
          <CardContent className="max-h-60 overflow-auto">
            <pre className="text-xs whitespace-pre-wrap font-mono text-muted-foreground">
              {JSON.stringify(step.output, null, 2)}
            </pre>
          </CardContent>
        )}
      </Card>
    )
  }

  // Final SQL extraction
  const composerStep = steps.find((s) => s.name === 'composer' && s.output?.sql_query)
  const finalSql = (composerStep?.output as any)?.sql_query as string | undefined

  const handleOpenInQuery = () => {
    if (!finalSql) return
    localStorage.setItem('prefilledQuery', finalSql)
    window.open('/query', '_blank')
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Agentic Workflow</h1>

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle>Start New Workflow</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Mode toggle */}
          <div className="flex gap-2">
            {(
              [
                { id: 'manual', label: 'Manual Schema' },
                { id: 'connection', label: 'Database Connection' }
              ] as const
            ).map((tab) => (
              <Button key={tab.id} variant={mode === tab.id ? 'default' : 'outline'} onClick={() => setMode(tab.id)}>
                {tab.label}
              </Button>
            ))}
          </div>

          {/* Query input */}
          <div className="flex flex-col gap-2">
            <Label htmlFor="workflow-query">Natural Language Query</Label>
            <Input
              id="workflow-query"
              placeholder="e.g., count all active users where age > 18"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          {mode === 'manual' ? (
            <div className="flex flex-col gap-2">
              <Label htmlFor="schema-json">Database Schema (JSON)</Label>
              <Textarea
                id="schema-json"
                rows={8}
                value={schemaJson}
                onChange={(e) => setSchemaJson(e.target.value)}
                className="font-mono text-xs"
              />
            </div>
          ) : (
            <div className="flex flex-col gap-2 max-w-sm">
              <Label htmlFor="workflow-connection">Database Connection</Label>
              {loadingConnections ? (
                <p>Loading connections...</p>
              ) : connections.length === 0 ? (
                <p className="text-muted-foreground text-sm">No connections available</p>
              ) : (
                <select
                  id="workflow-connection"
                  className="rounded-md border border-input bg-background px-3 py-2 text-base md:text-sm"
                  value={selectedConnection}
                  onChange={(e) => setSelectedConnection(e.target.value)}
                >
                  {connections.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.db_type})
                    </option>
                  ))}
                </select>
              )}
            </div>
          )}
        </CardContent>
        <CardFooter>
          <Button onClick={startWorkflow} disabled={starting}>
            {starting ? 'Starting...' : 'Run Workflow'}
          </Button>
        </CardFooter>
      </Card>

      {/* Workflow Panel */}
      {requestId && (
        <div className="space-y-6">
          <h2 className="text-xl font-semibold">Workflow Progress</h2>
          <ScrollArea className="h-[500px] w-full pr-4">
            <div className="space-y-4">
              {steps.length === 0 ? (
                <p className="text-muted-foreground">Waiting for steps...</p>
              ) : (
                steps.map(renderStepCard)
              )}
            </div>
          </ScrollArea>
        </div>
      )}

      {finalSql && (
        <Card className="border-green-500">
          <CardHeader>
            <CardTitle>Final SQL</CardTitle>
          </CardHeader>
          <CardContent>
            <Textarea readOnly rows={4} value={finalSql} className="font-mono text-sm" />
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button onClick={() => navigator.clipboard.writeText(finalSql)}>Copy</Button>
            <Button variant="secondary" onClick={handleOpenInQuery}>
              Open in Query Tab
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  )
}
