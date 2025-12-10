import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import CycleTimeScatter from '@/components/CycleTimeScatter.vue'

// Mock ECharts
vi.mock('echarts/core', () => ({
  use: vi.fn(),
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn()
  })),
  graphic: {
    LinearGradient: vi.fn()
  }
}))

vi.mock('echarts/charts', () => ({
  ScatterChart: {}
}))

vi.mock('echarts/components', () => ({
  TooltipComponent: {},
  GridComponent: {}
}))

vi.mock('echarts/renderers', () => ({
  CanvasRenderer: {}
}))

// Mock analytics service
vi.mock('@/services/analytics', () => ({
  fetchCycleTimeScatter: vi.fn()
}))

import { fetchCycleTimeScatter } from '@/services/analytics'
import * as echarts from 'echarts/core'

describe('CycleTimeScatter', () => {
  const mockData = {
    points: [
      { cycle_time: 28.5, defect_count: 0, product_id: 1, is_rejected: false },
      { cycle_time: 31.2, defect_count: 1, product_id: 2, is_rejected: false },
      { cycle_time: 35.8, defect_count: 3, product_id: 3, is_rejected: true },
      { cycle_time: 26.8, defect_count: 2, product_id: 4, is_rejected: false }
    ],
    stats: {
      correlation: -0.45,
      average_cycle_time: 29.4,
      sample_size: 4
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders component title', () => {
    vi.mocked(fetchCycleTimeScatter).mockResolvedValue(mockData)
    const wrapper = mount(CycleTimeScatter)
    expect(wrapper.text()).toContain('Cycle Time vs Defect Count')
  })

  it('loads data on mount', async () => {
    vi.mocked(fetchCycleTimeScatter).mockResolvedValue(mockData)
    mount(CycleTimeScatter)

    await nextTick()
    await vi.waitFor(() => {
      expect(fetchCycleTimeScatter).toHaveBeenCalledWith({
        machine_id: undefined,
        start_date: undefined,
        end_date: undefined
      })
    })
  })

  it('displays summary statistics', async () => {
    vi.mocked(fetchCycleTimeScatter).mockResolvedValue(mockData)
    const wrapper = mount(CycleTimeScatter)

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('-0.450')
      expect(wrapper.text()).toContain('29.4s')
      expect(wrapper.text()).toContain('4')
    })
  })

  it('applies correct correlation color for medium correlation', async () => {
    vi.mocked(fetchCycleTimeScatter).mockResolvedValue(mockData)
    const wrapper = mount(CycleTimeScatter)

    await vi.waitFor(() => {
      const correlationElements = wrapper.findAll('.title.is-6')
      const correlationValue = correlationElements[0]
      expect(correlationValue.classes()).toContain('has-text-warning')
    })
  })

  it('handles error state', async () => {
    vi.mocked(fetchCycleTimeScatter).mockRejectedValue(new Error('API Error'))
    const wrapper = mount(CycleTimeScatter)

    await vi.waitFor(() => {
      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.text()).toContain('Error:')
    })
  })

  it('initializes chart with correct series', async () => {
    vi.mocked(fetchCycleTimeScatter).mockResolvedValue(mockData)
    mount(CycleTimeScatter)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
      const mockInstance = vi.mocked(echarts.init).mock.results[0].value
      expect(mockInstance.setOption).toHaveBeenCalled()

      const chartOptions = vi.mocked(mockInstance.setOption).mock.calls[0][0]
      expect(chartOptions.series).toHaveLength(2)
      expect(chartOptions.series[0].name).toBe('Accepted')
      expect(chartOptions.series[1].name).toBe('Rejected')
    })
  })

  it('separates accepted and rejected products', async () => {
    vi.mocked(fetchCycleTimeScatter).mockResolvedValue(mockData)
    mount(CycleTimeScatter)

    await vi.waitFor(() => {
      const mockInstance = vi.mocked(echarts.init).mock.results[0].value
      const chartOptions = vi.mocked(mockInstance.setOption).mock.calls[0][0]
      const acceptedSeries = chartOptions.series[0]
      const rejectedSeries = chartOptions.series[1]

      expect(acceptedSeries.data).toHaveLength(3)
      expect(rejectedSeries.data).toHaveLength(1)
    })
  })

  it('reloads chart when props change', async () => {
    vi.mocked(fetchCycleTimeScatter).mockResolvedValue(mockData)
    const wrapper = mount(CycleTimeScatter, {
      props: {
        machineId: 'machine-1'
      }
    })

    await vi.waitFor(() => {
      expect(fetchCycleTimeScatter).toHaveBeenCalledWith({
        machine_id: 'machine-1',
        start_date: undefined,
        end_date: undefined
      })
    })

    vi.mocked(fetchCycleTimeScatter).mockClear()
    await wrapper.setProps({ machineId: 'machine-2' })

    await vi.waitFor(() => {
      expect(fetchCycleTimeScatter).toHaveBeenCalledWith({
        machine_id: 'machine-2',
        start_date: undefined,
        end_date: undefined
      })
    })
  })

  it('handles empty data gracefully', async () => {
    vi.mocked(fetchCycleTimeScatter).mockResolvedValue({
      points: [],
      stats: mockData.stats
    })
    const wrapper = mount(CycleTimeScatter)

    await vi.waitFor(() => {
      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.text()).toContain('No data available')
    })
  })

  it('disposes chart on unmount', async () => {
    vi.mocked(fetchCycleTimeScatter).mockResolvedValue(mockData)
    const wrapper = mount(CycleTimeScatter)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
    })

    const mockInstance = vi.mocked(echarts.init).mock.results[0].value
    wrapper.unmount()
    expect(mockInstance.dispose).toHaveBeenCalled()
  })
})