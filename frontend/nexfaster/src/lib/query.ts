import { api } from '@/lib/api'
import type { QueryRequest, QueryResponse } from '@/types/query'

export const QueryService = {
  async execute(request: QueryRequest): Promise<QueryResponse> {
    const { data } = await api.post<QueryResponse>('/query', request)
    return data
  },
  async executeByConnection(connectionId: string, sql: string): Promise<QueryResponse> {
    const { data } = await api.post<QueryResponse>(`/instances/${connectionId}/query`, { sql })
    return data
  }
}
