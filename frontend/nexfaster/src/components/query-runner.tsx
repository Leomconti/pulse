import { useEffect, useState, useCallback } from 'react'
import { InstancesService } from '@/lib/instances'
import { QueryService } from '@/lib/query'
import type { DatabaseConnectionResponse } from '@/types/connection'
import type { QueryResult, DatabaseSchema } from '@/types/query'

import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { useToast } from '@/components/ui/use-toast'
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell, TableCaption } from '@/components/ui/table'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Eye, Database, Columns, RefreshCw } from 'lucide-react'

export function QueryRunnerPage() {
  const { toast } = useToast()

  const [connections, setConnections] = useState<DatabaseConnectionResponse[]>([])
  const [selectedConnection, setSelectedConnection] = useState<string>('')
  const [sql, setSql] = useState<string>('')
  const [loadingConnections, setLoadingConnections] = useState<boolean>(true)
  const [executing, setExecuting] = useState<boolean>(false)
  const [result, setResult] = useState<QueryResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [schema, setSchema] = useState<DatabaseSchema | null>(null)
  const [loadingSchema, setLoadingSchema] = useState<boolean>(false)
  const [showSchema, setShowSchema] = useState<boolean>(false)

  useEffect(() => {
    InstancesService.list()
      .then((data) => {
        setConnections(data)
        if (data.length > 0) {
          setSelectedConnection(data[0].id)
        }
      })
      .catch(() => toast({ title: 'Error', description: 'Failed to load connections', variant: 'destructive' }))
      .finally(() => setLoadingConnections(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  useEffect(() => {
    // Prefill SQL from workflow
    const prefilled = localStorage.getItem('prefilledQuery')
    if (prefilled) {
      setSql(prefilled)
      localStorage.removeItem('prefilledQuery')
    }
  }, [])

  const handleExecute = async () => {
    if (!selectedConnection || !sql.trim()) {
      toast({ title: 'Missing data', description: 'Please choose a connection and write a SQL query' })
      return
    }

    setExecuting(true)
    setError(null)
    setResult(null)

    try {
      const response = await QueryService.execute({ connection_id: selectedConnection, sql })
      if (response.status === 'ok') {
        setResult(response.data)
        toast({
          title: 'Success',
          description: `Returned ${response.data.row_count} rows in ${response.data.execution_time_ms.toFixed(2)} ms`
        })
      } else {
        setError(response.error)
        toast({ title: 'Query error', description: response.error, variant: 'destructive' })
      }
    } catch (e: any) {
      toast({ title: 'Error', description: e?.message ?? 'Failed to execute query', variant: 'destructive' })
    } finally {
      setExecuting(false)
    }
  }

  const handleClear = () => {
    setSql('')
    setResult(null)
    setError(null)
  }

  const handleLoadSchema = useCallback(async () => {
    if (!selectedConnection) {
      return
    }

    setLoadingSchema(true)
    try {
      const response = await InstancesService.getSchema(selectedConnection)
      if (response.status === 'ok' && response.schema) {
        setSchema(response.schema)
        setShowSchema(true)
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
    if (selectedConnection) {
      handleLoadSchema()
    } else {
      setSchema(null)
      setShowSchema(false)
    }
  }, [selectedConnection, handleLoadSchema])

  const insertSampleQuery = (query: string) => {
    setSql(query)
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">SQL Query Runner</h1>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Query Form */}
        <div className="lg:col-span-3 space-y-6">
          <div className="space-y-4">
            {/* Connection select */}
            <div className="flex flex-col gap-2 max-w-sm">
              <Label htmlFor="connection-select">Database Connection</Label>
              {loadingConnections ? (
                <p>Loading connections...</p>
              ) : connections.length === 0 ? (
                <p className="text-muted-foreground text-sm">No connections found. Create one first.</p>
              ) : (
                <select
                  id="connection-select"
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

            {/* SQL textarea */}
            <div className="flex flex-col gap-2">
              <Label htmlFor="sql-textarea">SQL</Label>
              <Textarea
                id="sql-textarea"
                rows={10}
                placeholder="SELECT * FROM table LIMIT 10;"
                value={sql}
                onChange={(e) => setSql(e.target.value)}
                onKeyDown={(e) => {
                  if (e.ctrlKey && e.key === 'Enter') {
                    e.preventDefault()
                    handleExecute()
                  }
                }}
                className="font-mono text-sm"
              />
            </div>

            {/* Action buttons */}
            <div className="flex items-center gap-4">
              <Button disabled={executing} onClick={handleExecute}>
                {executing ? 'Running...' : 'Run'}
              </Button>
              <Button variant="outline" onClick={handleClear} disabled={executing}>
                Clear
              </Button>
            </div>
          </div>

          {/* Results - moved here to be closer to the form */}
          {error && <p className="text-red-600 font-medium">{error}</p>}

          {result && (
            <div className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Returned {result.row_count} rows in {result.execution_time_ms.toFixed(2)} ms
              </p>
              {result.row_count === 0 ? (
                <p>No rows returned.</p>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      {result.columns.map((col) => (
                        <TableHead key={col}>{col}</TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {result.rows.map((row, i) => (
                      <TableRow key={i}>
                        {row.map((cell, j) => (
                          <TableCell key={j}>{cell as any}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                  <TableCaption>Query Results</TableCaption>
                </Table>
              )}
            </div>
          )}
        </div>

        {/* Schema Sidebar */}
        <div className="lg:col-span-1 space-y-6">
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
                      <div className="mt-2 pt-2 border-t">
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-xs h-6"
                          onClick={() => insertSampleQuery(`SELECT * FROM ${tableName} LIMIT 10;`)}
                        >
                          Insert SELECT
                        </Button>
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

          {/* Quick Reference */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-base">💡 Quick Reference</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Common Queries */}
              <div>
                <h4 className="text-sm font-medium mb-2">Common Queries</h4>
                <div className="space-y-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start text-xs h-8"
                    onClick={() => insertSampleQuery('SHOW TABLES;')}
                  >
                    List tables
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start text-xs h-8"
                    onClick={() => insertSampleQuery("SELECT name FROM sqlite_master WHERE type='table';")}
                  >
                    SQLite tables
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start text-xs h-8"
                    onClick={() => insertSampleQuery('SELECT COUNT(*) as total FROM users;')}
                  >
                    Count records
                  </Button>
                </div>
              </div>

              {/* Keyboard Shortcuts */}
              <div>
                <h4 className="text-sm font-medium mb-2">Shortcuts</h4>
                <div className="text-xs text-muted-foreground space-y-1">
                  <div>
                    <kbd className="bg-muted px-1 rounded">Ctrl+Enter</kbd> Execute
                  </div>
                  <div>
                    <kbd className="bg-muted px-1 rounded">Ctrl+A</kbd> Select All
                  </div>
                  <div>
                    <kbd className="bg-muted px-1 rounded">Tab</kbd> Indent
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
