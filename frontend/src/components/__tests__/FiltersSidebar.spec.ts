import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import FiltersSidebar from '../FiltersSidebar.vue'

vi.mock('@/services/analytics', () => ({
  fetchMachines: vi.fn().mockResolvedValue({
    machines: ['molding-machine-1', 'molding-machine-2', 'molding-machine-3'],
    count: 3
  })
}))

describe('FiltersSidebar', () => {
  const defaultProps = {
    modelValue: {
      machine: undefined,
      startDate: '',
      endDate: ''
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders filters title', () => {
    const wrapper = mount(FiltersSidebar, { props: defaultProps })
    expect(wrapper.text()).toContain('Filters')
  })

it('loads machines on mount', async () => {
    const { fetchMachines } = await import('@/services/analytics')

    mount(FiltersSidebar, { props: defaultProps })

    await vi.waitFor(() => {
      expect(fetchMachines).toHaveBeenCalled()
    })
  })

it('emits update when machine is selected', async () => {
    const wrapper = mount(FiltersSidebar, { props: defaultProps })

    await vi.waitFor(() => {
      expect(wrapper.find('select option').exists()).toBe(true)
    })

    const vm = wrapper.vm as any
    vm.localMachine = 'molding-machine-1'
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    const emittedValue = wrapper.emitted('update:modelValue')?.[0]?.[0] as any
    expect(emittedValue.machine).toBe('molding-machine-1')
  })

  it('emits collapse-change when collapse button is clicked', async () => {
    const wrapper = mount(FiltersSidebar, { props: defaultProps })

    const collapseBtn = wrapper.find('.sidebar-collapse-btn')
    if (collapseBtn.exists()) {
      await collapseBtn.trigger('click')
      expect(wrapper.emitted('collapse-change')).toBeTruthy()
    }
  })

  it('clears all filters when clear button is clicked', async () => {
    const wrapper = mount(FiltersSidebar, {
      props: {
        modelValue: {
          machine: 'molding-machine-1',
          startDate: '2025-01-01',
          endDate: '2025-01-31'
        }
      }
    })

    const clearBtn = wrapper.find('.button.is-danger')
    await clearBtn.trigger('click')

    const emittedValue = wrapper.emitted('update:modelValue')?.slice(-1)[0]?.[0] as any
    expect(emittedValue.machine).toBeUndefined()
    expect(emittedValue.startDate).toBe('')
    expect(emittedValue.endDate).toBe('')
  })

  it('formats machine names correctly', () => {
    const wrapper = mount(FiltersSidebar, { props: defaultProps })
    const vm = wrapper.vm as any

    expect(vm.getMachineName('molding-machine-1')).toBe('Molding Machine 1')
    expect(vm.getMachineName('test_machine_name')).toBe('Test Machine Name')
  })

it('formats dates correctly', () => {
    const wrapper = mount(FiltersSidebar, { props: defaultProps })
    const vm = wrapper.vm as any

    expect(vm.formatDate('2025-06-15')).toMatch(/Jun \d{1,2}, 2025/)
    expect(vm.formatDate('')).toBe('')
  })
})