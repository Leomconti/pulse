import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { useToast } from '@/components/ui/use-toast'
import { InstancesService } from '@/lib/instances'
import type { DatabaseConnectionResponse } from '@/types/connection'

export function ConnectionDetailsPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { toast } = useToast()

  const [connection, setConnection] = useState<DatabaseConnectionResponse | null>(null)
  const [status, setStatus] = useState<'idle' | 'loading' | 'ok' | 'error'>('idle')
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    if (!id) return
    InstancesService.get(id)
      .then(setConnection)
      .catch(() => {
        toast({ title: 'Error', description: 'Connection not found', variant: 'destructive' })
        navigate('/connections')
      })
      .finally(() => setLoading(false))
  }, [id, navigate, toast])

  const handleTest = async () => {
    if (!id) return
    setStatus('loading')
    try {
      const res = await InstancesService.test(id)
      setStatus(res.status === 'ok' ? 'ok' : 'error')
      toast({ title: res.status === 'ok' ? 'Connection ok' : 'Connection error', description: res.message })
    } catch (e: any) {
      setStatus('error')
      toast({
        title: 'Error',
        description: e?.response?.data?.detail ?? 'Failed to test connection.',
        variant: 'destructive'
      })
    }
  }

  if (loading) return <p>Loading...</p>
  if (!connection) return null

  const fieldRows: Array<{ label: string; value: string | number }> = [
    { label: 'Name', value: connection.name },
    { label: 'Type', value: connection.db_type },
    { label: 'Host', value: `${connection.host}:${connection.port}` },
    { label: 'Database', value: connection.database },
    { label: 'Username', value: connection.username }
  ]

  return (
    <Card className="max-w-xl mx-auto">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle>Connection Details</CardTitle>
        {status !== 'idle' && (
          <Badge variant={status === 'ok' ? 'default' : status === 'loading' ? 'secondary' : 'destructive'}>
            {status === 'loading' ? 'Testing' : status === 'ok' ? 'OK' : 'Error'}
          </Badge>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        {fieldRows.map((row) => (
          <div key={row.label} className="flex items-center justify-between">
            <Label className="font-medium">{row.label}</Label>
            <span className="text-muted-foreground text-sm">{row.value}</span>
          </div>
        ))}
      </CardContent>
      <CardFooter className="justify-between space-x-2">
        <Button variant="outline" onClick={() => navigate('/connections')}>
          Back
        </Button>
        <Button onClick={handleTest}>Test Connection</Button>
      </CardFooter>
    </Card>
  )
}
