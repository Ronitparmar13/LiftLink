import axios from 'axios'

export function getApiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as { detail?: string | unknown[]; code?: string }
    if (typeof data?.detail === 'string') return data.detail
    if (Array.isArray(data?.detail)) {
      return data.detail.map((d) => JSON.stringify(d)).join('; ')
    }
    if (err.response?.status === 401) return 'Session expired. Please sign in again.'
    if (err.response?.status === 403) {
      return 'Only @paruluniversity.ac.in accounts are allowed.'
    }
    if (err.response?.status === 409) return 'This action conflicts with an existing record.'
    return err.message
  }
  if (err instanceof Error) return err.message
  return 'Something went wrong'
}
