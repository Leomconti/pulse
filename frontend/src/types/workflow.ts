export type StepStatus = 'pending' | 'running' | 'done' | 'failed'

export interface WorkflowRequest {
  query: string
  schema: Record<string, unknown>
  user_id?: string
}

export interface WorkflowResponse {
  request_id: string
}

export interface StepOutput {
  name: string // planner, mapper, etc.
  status: StepStatus
  output?: Record<string, unknown> | null
  started_at?: number | null
  finished_at?: number | null
}

export interface WorkflowStatusResponse {
  status: StepStatus | 'completed' | 'retrying' // backend can send completed, retrying
  current?: string | null
}

// ---------------------------------------------------------------------------
// History
// ---------------------------------------------------------------------------

export interface WorkflowHistoryItem {
  request_id: string
  query: string
  status: StepStatus | 'completed' | 'retrying'
  created_at: number
  updated_at: number
}
