import { api } from '@/lib/api'
import type {
  WorkflowRequest,
  WorkflowResponse,
  StepOutput,
  WorkflowStatusResponse,
  WorkflowHistoryItem
} from '@/types/workflow'
import { InstancesService } from '@/lib/instances'

export const WorkflowService = {
  async start(request: WorkflowRequest): Promise<WorkflowResponse> {
    const { data } = await api.post<WorkflowResponse>('/workflows', request)
    return data
  },

  async startWithConnection(query: string, connectionId: string): Promise<WorkflowResponse> {
    // Fetch schema first
    const schemaResp = await InstancesService.getSchema(connectionId)
    if (schemaResp.status !== 'ok') {
      throw new Error('Unable to fetch database schema')
    }
    const payload: WorkflowRequest = {
      query,
      schema: schemaResp.schema
    }
    return this.start(payload)
  },

  async getSteps(requestId: string): Promise<StepOutput[]> {
    const { data } = await api.get<StepOutput[]>(`/workflows/${requestId}/steps`)
    return data
  },

  async getStatus(requestId: string): Promise<WorkflowStatusResponse> {
    const { data } = await api.get<WorkflowStatusResponse>(`/workflows/${requestId}/status`)
    return data
  },

  async history(): Promise<WorkflowHistoryItem[]> {
    const { data } = await api.get<WorkflowHistoryItem[]>('/workflows/history')
    return data
  }
}
