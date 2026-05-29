import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import Button3D from '../Button3D'

describe('Button3D', () => {
  it('renders children text', () => {
    render(<Button3D>Click me</Button3D>)
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument()
  })

  it('calls onClick when clicked', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(<Button3D onClick={onClick}>Go</Button3D>)
    await user.click(screen.getByRole('button'))
    expect(onClick).toHaveBeenCalledOnce()
  })

  it('applies primary variant classes by default', () => {
    render(<Button3D>Primary</Button3D>)
    const btn = screen.getByRole('button')
    expect(btn.className).toContain('bg-primary-600')
  })

  it('applies secondary variant classes', () => {
    render(<Button3D variant="secondary">Secondary</Button3D>)
    const btn = screen.getByRole('button')
    expect(btn.className).toContain('bg-secondary-600')
  })

  it('applies outline variant classes', () => {
    render(<Button3D variant="outline">Outline</Button3D>)
    const btn = screen.getByRole('button')
    expect(btn.className).toContain('border')
  })

  it('applies size classes correctly', () => {
    const { rerender } = render(<Button3D size="sm">Small</Button3D>)
    expect(screen.getByRole('button').className).toContain('h-9')

    rerender(<Button3D size="lg">Large</Button3D>)
    expect(screen.getByRole('button').className).toContain('h-12')
  })

  it('can be disabled', () => {
    render(<Button3D disabled>Disabled</Button3D>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('forwards ref', () => {
    const ref = { current: null }
    render(<Button3D ref={ref}>Ref</Button3D>)
    expect(ref.current).toBeInstanceOf(HTMLButtonElement)
  })
})
