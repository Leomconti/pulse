import { api } from '@/lib/api'
import type { QueryRequest, QueryResponse, SchemaResponse } from '@/types/query'

export const QueryService = {
  async execute(request: QueryRequest): Promise<QueryResponse> {
    const { data } = await api.post<QueryResponse>('/query', request)
    return data
  },
  async executeByConnection(connectionId: string, sql: string): Promise<QueryResponse> {
    const { data } = await api.post<QueryResponse>(`/instances/${connectionId}/query`, { sql })
    return data
  },
  async getSchema(connectionId: string): Promise<SchemaResponse> {
    const { data } = await api.get<SchemaResponse>(`/instances/${connectionId}/schema`)
    return data
  }
}
