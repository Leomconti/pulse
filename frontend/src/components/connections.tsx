import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card'
import { Dialog, DialogTrigger, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { useToast } from '@/components/ui/use-toast'
import { InstancesService } from '@/lib/instances'
import type { DatabaseConnectionResponse, DatabaseConnectionCreate } from '@/types/connection'
import { Badge } from '@/components/ui/badge'

export function ConnectionsPage() {
  const [connections, setConnections] = useState<DatabaseConnectionResponse[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [dialogOpen, setDialogOpen] = useState<boolean>(false)
  const { toast } = useToast()
  const [statusMap, setStatusMap] = useState<Record<string, 'idle' | 'loading' | 'ok' | 'error'>>({})

  const [form, setForm] = useState<DatabaseConnectionCreate>({
    name: '',
    db_type: 'postgresql',
    host: '',
    port: 5432,
    database: '',
    username: '',
    password: ''
  })

  // Fetch connections on mount
  useEffect(() => {
    InstancesService.list()
      .then((data) => {
        setConnections(data)
        setStatusMap(
          Object.fromEntries(data.map((c) => [c.id, 'idle'])) as Record<string, 'idle' | 'loading' | 'ok' | 'error'>
        )
      })
      .catch(() =>
        toast({
          title: 'Error',
          description: 'Unable to fetch connections.',
          variant: 'destructive'
        })
      )
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleChange =
    (field: keyof DatabaseConnectionCreate) => (event: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      setForm((prev) => ({
        ...prev,
        [field]: field === 'port' ? Number(event.target.value) : event.target.value
      }))
    }

  const handleCreate = async () => {
    try {
      const created = await InstancesService.create(form)
      setConnections((prev) => [...prev, created])
      setStatusMap((prev) => ({ ...prev, [created.id]: 'idle' }))
      toast({ title: 'Success', description: 'Connection created successfully!' })
      setDialogOpen(false)
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error?.response?.data?.detail ?? 'Failed to create connection.',
        variant: 'destructive'
      })
    }
  }

  const handleTest = async (id: string) => {
    setStatusMap((prev) => ({ ...prev, [id]: 'loading' }))
    try {
      const res = await InstancesService.test(id)
      setStatusMap((prev) => ({ ...prev, [id]: res.status === 'ok' ? 'ok' : 'error' }))
      toast({ title: res.status === 'ok' ? 'Connection ok' : 'Connection error', description: res.message })
    } catch (e: any) {
      setStatusMap((prev) => ({ ...prev, [id]: 'error' }))
      toast({
        title: 'Error',
        description: e?.response?.data?.detail ?? 'Failed to test connection.',
        variant: 'destructive'
      })
    }
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Database Connections</h1>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>Add Connection</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>New Connection</DialogTitle>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              {[
                { id: 'name', label: 'Name', type: 'text' },
                { id: 'host', label: 'Host', type: 'text' },
                { id: 'port', label: 'Port', type: 'number' },
                { id: 'database', label: 'Database', type: 'text' },
                { id: 'username', label: 'Username', type: 'text' },
                { id: 'password', label: 'Password', type: 'password' }
              ].map(({ id, label, type }) => (
                <div key={id} className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor={id} className="text-right">
                    {label}
                  </Label>
                  <Input
                    id={id}
                    type={type}
                    className="col-span-3"
                    value={(form as any)[id] as string | number}
                    onChange={handleChange(id as keyof DatabaseConnectionCreate)}
                  />
                </div>
              ))}
              {/* DB Type Select */}
              <div className="grid grid-cols-4 items-center gap-4">
                <Label htmlFor="db_type" className="text-right">
                  Type
                </Label>
                <select
                  id="db_type"
                  className="col-span-3 rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none"
                  value={form.db_type}
                  onChange={handleChange('db_type')}
                >
                  <option value="postgresql">PostgreSQL</option>
                  <option value="mysql">MySQL</option>
                  <option value="sqlite">SQLite</option>
                </select>
              </div>
            </div>

            <DialogFooter>
              <Button onClick={handleCreate}>Create Connection</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Connections Grid */}
      {loading ? (
        <p>Loading...</p>
      ) : connections.length === 0 ? (
        <p className="text-muted-foreground">No connections found. Start by adding one.</p>
      ) : (
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {connections.map((conn) => (
            <Card key={conn.id} className="relative group overflow-hidden">
              <CardHeader>
                <CardTitle>{conn.name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1 text-sm">
                <p>
                  <span className="font-medium">Type:</span> {conn.db_type}
                </p>
                <p>
                  <span className="font-medium">Host:</span> {conn.host}:{conn.port}
                </p>
                <p>
                  <span className="font-medium">DB:</span> {conn.database}
                </p>
              </CardContent>
              <CardFooter className="flex items-center justify-between gap-2">
                <Button size="sm" variant="secondary" asChild>
                  <a href={`/connections/${conn.id}`}>Details</a>
                </Button>
                <Button size="sm" variant="outline" onClick={() => handleTest(conn.id)}>
                  Test
                </Button>
                {statusMap[conn.id] && statusMap[conn.id] !== 'idle' && (
                  <Badge
                    variant={
                      statusMap[conn.id] === 'ok'
                        ? 'default'
                        : statusMap[conn.id] === 'loading'
                        ? 'secondary'
                        : 'destructive'
                    }
                  >
                    {statusMap[conn.id] === 'loading' ? 'Testing' : statusMap[conn.id] === 'ok' ? 'OK' : 'Error'}
                  </Badge>
                )}
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}
