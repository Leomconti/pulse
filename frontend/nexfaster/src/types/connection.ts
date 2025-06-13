export type DatabaseType = 'postgresql' | 'mysql' | 'sqlite'

export interface DatabaseConnectionResponse {
  id: string
  name: string
  db_type: DatabaseType
  host: string
  port: number
  database: string
  username: string
  created_at: number
  updated_at: number
}

export interface DatabaseConnectionCreate {
  name: string
  db_type: DatabaseType
  host: string
  port: number
  database: string
  username: string
  password: string
}
