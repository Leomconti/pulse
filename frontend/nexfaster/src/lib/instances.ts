import { api } from '@/lib/api'
import type { DatabaseConnectionResponse, DatabaseConnectionCreate } from '@/types/connection'
import type { SchemaResponse } from '@/types/query'

export const InstancesService = {
  async list(): Promise<DatabaseConnectionResponse[]> {
    const { data } = await api.get<DatabaseConnectionResponse[]>('/instances')
    return data
  },
  async create(payload: DatabaseConnectionCreate): Promise<DatabaseConnectionResponse> {
    const { data } = await api.post<DatabaseConnectionResponse>('/instances', payload)
    return data
  },
  async get(id: string): Promise<DatabaseConnectionResponse> {
    const { data } = await api.get<DatabaseConnectionResponse>(`/instances/${id}`)
    return data
  },
  async update(id: string, payload: Partial<DatabaseConnectionCreate>): Promise<DatabaseConnectionResponse> {
    const { data } = await api.put<DatabaseConnectionResponse>(`/instances/${id}`, payload)
    return data
  },
  async remove(id: string): Promise<void> {
    await api.delete(`/instances/${id}`)
  },
  async test(id: string): Promise<{ status: string; message: string }> {
    const { data } = await api.post<{ status: string; message: string }>(`/instances/${id}/test`)
    return data
  },
  async getSchema(id: string): Promise<SchemaResponse> {
    const { data } = await api.get<SchemaResponse>(`/instances/${id}/schema`)
    return data
  }
}
