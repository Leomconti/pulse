import { useEffect, useState } from 'react'
import { InstancesService } from '@/lib/instances'
import { QueryService } from '@/lib/query'
import type { DatabaseConnectionResponse } from '@/types/connection'
import type { QueryResult } from '@/types/query'

import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { useToast } from '@/components/ui/use-toast'
import { Table, TableHeader, TableBody, TableHead, TableRow, TableCell, TableCaption } from '@/components/ui/table'

export function QueryRunnerPage() {
  const { toast } = useToast()

  const [connections, setConnections] = useState<DatabaseConnectionResponse[]>([])
  const [selectedConnection, setSelectedConnection] = useState<string>('')
  const [sql, setSql] = useState<string>('')
  const [loadingConnections, setLoadingConnections] = useState<boolean>(true)
  const [executing, setExecuting] = useState<boolean>(false)
  const [result, setResult] = useState<QueryResult | null>(null)
  const [error, setError] = useState<string | null>(null)

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

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">SQL Query Runner</h1>

      {/* Form */}
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

      {/* Results */}
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
  )
}
