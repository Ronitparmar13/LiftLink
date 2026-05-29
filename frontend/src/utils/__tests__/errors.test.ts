import { describe, it, expect } from 'vitest'
import { getApiErrorMessage } from '../errors'

describe('getApiErrorMessage', () => {
  it('returns detail string from axios error', () => {
    const err = {
      isAxiosError: true,
      response: { data: { detail: 'Not found' }, status: 404 },
    }
    expect(getApiErrorMessage(err)).toBe('Not found')
  })

  it('returns joined detail array from axios error', () => {
    const err = {
      isAxiosError: true,
      response: { data: { detail: [{ msg: 'bad' }, { msg: 'wrong' }] }, status: 422 },
    }
    const msg = getApiErrorMessage(err)
    expect(msg).toContain('bad')
    expect(msg).toContain('wrong')
  })

  it('returns session expired for 401', () => {
    const err = { isAxiosError: true, response: { data: {}, status: 401 } }
    expect(getApiErrorMessage(err)).toBe('Session expired. Please sign in again.')
  })

  it('returns domain error for 403', () => {
    const err = { isAxiosError: true, response: { data: {}, status: 403 } }
    expect(getApiErrorMessage(err)).toContain('paruluniversity.ac.in')
  })

  it('returns conflict message for 409', () => {
    const err = { isAxiosError: true, response: { data: {}, status: 409 } }
    expect(getApiErrorMessage(err)).toContain('conflicts')
  })

  it('returns validation message for 422', () => {
    const err = { isAxiosError: true, response: { data: {}, status: 422 } }
    expect(getApiErrorMessage(err)).toContain('check your input')
  })

  it('returns rate limit message for 429', () => {
    const err = { isAxiosError: true, response: { data: {}, status: 429 } }
    expect(getApiErrorMessage(err)).toContain('Too many requests')
  })

  it('returns server error for 500', () => {
    const err = { isAxiosError: true, response: { data: {}, status: 500 } }
    expect(getApiErrorMessage(err)).toContain('Server error')
  })

  it('returns message for non-axios Error', () => {
    expect(getApiErrorMessage(new Error('fail'))).toBe('fail')
  })

  it('returns fallback for unknown error', () => {
    expect(getApiErrorMessage('string')).toBe('Something went wrong')
  })
})
