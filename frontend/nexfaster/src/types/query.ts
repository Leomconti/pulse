export interface QueryRequest {
  connection_id: string
  sql: string
}

export interface QueryResult {
  columns: string[]
  rows: Array<Array<string | number | null>>
  row_count: number
  execution_time_ms: number
}

export interface QueryResponseOk {
  status: 'ok'
  data: QueryResult
  error: null
}

export interface QueryResponseError {
  status: 'error'
  data: null
  error: string
}

export type QueryResponse = QueryResponseOk | QueryResponseError

// Schema types
export interface SchemaColumn {
  name: string
  type: string
  nullable?: boolean
  default?: string | null
}

export interface SchemaTable {
  columns: SchemaColumn[]
}

export interface DatabaseSchema {
  tables: Record<string, SchemaTable>
}

export interface SchemaResponse {
  status: 'ok' | 'error'
  schema?: DatabaseSchema
  message?: string
}
