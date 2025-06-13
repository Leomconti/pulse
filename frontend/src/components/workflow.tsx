import { useEffect, useState, useCallback } from 'react'
import { InstancesService } from '@/lib/instances'
import { WorkflowService } from '@/lib/workflow'
import type { DatabaseConnectionResponse } from '@/types/connection'
import type { StepOutput } from '@/types/workflow'
import type { DatabaseSchema } from '@/types/query'

import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { ScrollArea } from '@/components/ui/scroll-area'
import { useToast } from '@/components/ui/use-toast'
import { Database, Columns, RefreshCw } from 'lucide-react'

export function WorkflowPage() {
  type Mode = 'manual' | 'connection'
  const [mode, setMode] = useState<Mode>('connection')
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

  // Schema state
  const [schema, setSchema] = useState<DatabaseSchema | null>(null)
  const [loadingSchema, setLoadingSchema] = useState<boolean>(false)

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

  const handleLoadSchema = useCallback(async () => {
    if (!selectedConnection) {
      return
    }

    setLoadingSchema(true)
    try {
      const response = await InstancesService.getSchema(selectedConnection)
      if (response.status === 'ok' && response.schema) {
        setSchema(response.schema)
      } else {
        toast({
          title: 'Schema error',
          description: response.message || 'Failed to load schema',
          variant: 'destructive'
        })
      }
    } catch (e: any) {
      toast({
        title: 'Error',
        description: e?.message ?? 'Failed to load schema',
        variant: 'destructive'
      })
    } finally {
      setLoadingSchema(false)
    }
  }, [selectedConnection, toast])

  // Auto-load schema when connection changes
  useEffect(() => {
    if (mode === 'connection' && selectedConnection) {
      handleLoadSchema()
    } else {
      setSchema(null)
    }
  }, [mode, selectedConnection, handleLoadSchema])

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

      // Initialize steps with expected workflow steps
      const initialSteps: StepOutput[] = [
        { name: 'planner', status: 'pending', output: null },
        { name: 'mapper', status: 'pending', output: null },
        { name: 'composer', status: 'pending', output: null },
        { name: 'validator', status: 'pending', output: null }
      ]
      setSteps(initialSteps)
      setPolling(true)
    } catch (e: any) {
      toast({ title: 'Error', description: e?.message ?? 'Failed to start workflow', variant: 'destructive' })
    } finally {
      setStarting(false)
    }
  }

  // Poll steps - more frequent polling for real-time updates
  useEffect(() => {
    if (!requestId || !polling) return

    // Start polling immediately
    const pollSteps = async () => {
      try {
        const newSteps = await WorkflowService.getSteps(requestId)
        setSteps(newSteps)

        // Check if workflow is complete
        const allDone = newSteps.every((s) => s.status === 'done' || s.status === 'failed')
        const hasRunning = newSteps.some((s) => s.status === 'running')

        if (allDone && !hasRunning) {
          setPolling(false)
        }
      } catch (e) {
        console.error('Error polling steps:', e)
      }
    }

    // Poll immediately, then every 1 second for more responsive updates
    pollSteps()
    const interval = setInterval(pollSteps, 1000)

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

    const statusIcon =
      step.status === 'done' ? '✅' : step.status === 'running' ? '🔄' : step.status === 'failed' ? '❌' : '⏳'

    return (
      <Card
        key={step.name}
        className={`border-border ${step.status === 'running' ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}`}
      >
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-lg capitalize flex items-center gap-2">
            <span>{statusIcon}</span>
            {step.name} Agent
            {step.status === 'running' && <RefreshCw className="w-4 h-4 animate-spin" />}
          </CardTitle>
          <Badge variant={statusVariant}>{step.status}</Badge>
        </CardHeader>
        {step.output && (
          <CardContent className="max-h-60 overflow-auto">
            <pre className="text-xs whitespace-pre-wrap font-mono text-muted-foreground">
              {JSON.stringify(step.output, null, 2)}
            </pre>
          </CardContent>
        )}
        {step.status === 'running' && !step.output && (
          <CardContent>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <RefreshCw className="w-4 h-4 animate-spin" />
              Processing...
            </div>
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

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Form */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <CardTitle>Start New Workflow</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Mode toggle */}
              <div className="flex gap-2">
                {(
                  [
                    { id: 'connection', label: 'Database Connection' },
                    { id: 'manual', label: 'Manual Schema' }
                  ] as const
                ).map((tab) => (
                  <Button
                    key={tab.id}
                    variant={mode === tab.id ? 'default' : 'outline'}
                    onClick={() => setMode(tab.id)}
                  >
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
        </div>

        {/* Schema Preview Sidebar */}
        {mode === 'connection' && (
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="w-5 h-5" />
                  Schema Preview
                </CardTitle>
              </CardHeader>
              <CardContent>
                {loadingSchema ? (
                  <div className="text-center py-8">
                    <RefreshCw className="w-12 h-12 mx-auto text-muted-foreground mb-4 animate-spin" />
                    <p className="text-sm text-muted-foreground">Loading schema...</p>
                  </div>
                ) : !selectedConnection ? (
                  <div className="text-center py-8">
                    <Database className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                    <p className="text-sm text-muted-foreground">Select a connection to view schema</p>
                  </div>
                ) : schema ? (
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {Object.entries(schema.tables).map(([tableName, tableData]) => (
                      <div key={tableName} className="border rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-2">
                          <Database className="w-4 h-4 text-blue-600" />
                          <h4 className="font-medium text-sm">{tableName}</h4>
                        </div>
                        <div className="space-y-1">
                          {tableData.columns.map((column) => (
                            <div key={column.name} className="flex items-center justify-between text-xs">
                              <div className="flex items-center gap-1">
                                <Columns className="w-3 h-3 text-gray-400" />
                                <span className="font-mono">{column.name}</span>
                              </div>
                              <Badge variant="secondary" className="text-xs">
                                {column.type}
                              </Badge>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                    <div className="text-xs text-muted-foreground text-center pt-2 border-t">
                      {Object.keys(schema.tables).length} table(s) found
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground">No schema data available</p>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Workflow Panel */}
      {requestId && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Workflow Progress</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {steps.length === 0 ? (
              <p className="text-muted-foreground col-span-full">Initializing workflow...</p>
            ) : (
              steps.map(renderStepCard)
            )}
          </div>
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
