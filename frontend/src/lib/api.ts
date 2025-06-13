import axios from 'axios'

/**
 * Axios instance pre-configured with the backend base URL.
 *
 * Set the NEXT_PUBLIC_API_BASE_URL env variable to override the default.
 */
export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Optional helper to attach bearer tokens etc.
export function setAuthToken(token?: string) {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common['Authorization']
  }
}
