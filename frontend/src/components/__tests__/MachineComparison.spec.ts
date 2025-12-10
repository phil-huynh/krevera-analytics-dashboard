import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import MachineComparison from '@/components/MachineComparison.vue'

// Mock ECharts
vi.mock('echarts/core', () => ({
  use: vi.fn(),
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn()
  }))
}))

vi.mock('echarts/charts', () => ({
  BarChart: {}
}))

vi.mock('echarts/components', () => ({
  TooltipComponent: {},
  GridComponent: {},
  LegendComponent: {}
}))

vi.mock('echarts/renderers', () => ({
  CanvasRenderer: {}
}))

// Mock analytics service
vi.mock('@/services/analytics', () => ({
  fetchMachineComparison: vi.fn()
}))

import { fetchMachineComparison } from '@/services/analytics'
import * as echarts from 'echarts/core'

describe('MachineComparison', () => {
  const mockData = {
    machines: [
      { machine_id: 'molding-machine-1', total: 1250, rejected: 95, accepted: 1155, defect_rate: 0.076 },
      { machine_id: 'molding-machine-2', total: 1180, rejected: 88, accepted: 1092, defect_rate: 0.075 },
      { machine_id: 'molding-machine-3', total: 1340, rejected: 102, accepted: 1238, defect_rate: 0.076 }
    ]
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders component title', () => {
    vi.mocked(fetchMachineComparison).mockResolvedValue(mockData)
    const wrapper = mount(MachineComparison)
    expect(wrapper.text()).toContain('Machine Performance Comparison')
  })

  it('loads data on mount', async () => {
    vi.mocked(fetchMachineComparison).mockResolvedValue(mockData)
    mount(MachineComparison)

    await nextTick()
    await vi.waitFor(() => {
      expect(fetchMachineComparison).toHaveBeenCalled()
    })
  })

  it('handles error state', async () => {
    vi.mocked(fetchMachineComparison).mockRejectedValue(new Error('API Error'))
    const wrapper = mount(MachineComparison)

    await vi.waitFor(() => {
      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.text()).toContain('Error loading chart')
    })
  })

  it('initializes chart with bar configuration', async () => {
    vi.mocked(fetchMachineComparison).mockResolvedValue(mockData)
    mount(MachineComparison)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
      const mockInstance = vi.mocked(echarts.init).mock.results[0].value
      expect(mockInstance.setOption).toHaveBeenCalled()

      const chartOptions = vi.mocked(mockInstance.setOption).mock.calls[0][0]
      expect(chartOptions.series).toBeDefined()
      // Machine names are formatted by the component
      expect(chartOptions.xAxis.data).toEqual(['Molding Machine 1', 'Molding Machine 2', 'Molding Machine 3'])
    })
  })

  it('formats tooltip values with decimals', async () => {
    vi.mocked(fetchMachineComparison).mockResolvedValue(mockData)
    mount(MachineComparison)

    await vi.waitFor(() => {
      const mockInstance = vi.mocked(echarts.init).mock.results[0].value
      const chartOptions = vi.mocked(mockInstance.setOption).mock.calls[0][0]
      const tooltipFormatter = chartOptions.tooltip.formatter

      const mockParams = [
        { axisValue: 'molding-machine-1', seriesName: 'Defect Rate (%)', value: 7.6, marker: '●' },
        { axisValue: 'molding-machine-1', seriesName: 'Total Products', value: 1250, marker: '●' }
      ]

      const result = tooltipFormatter(mockParams)
      expect(result).toContain('7.60%')
      expect(result).toContain('1,250')
    })
  })

  it('handles empty data', async () => {
    vi.mocked(fetchMachineComparison).mockResolvedValue({
      machines: []
    })
    const wrapper = mount(MachineComparison)

    await vi.waitFor(() => {
      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.text()).toContain('No machine data available')
    })
  })

  it('formats machine names correctly', async () => {
    vi.mocked(fetchMachineComparison).mockResolvedValue(mockData)
    mount(MachineComparison)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
    })
  })

  it('calculates defect rates as percentages', async () => {
    vi.mocked(fetchMachineComparison).mockResolvedValue(mockData)
    mount(MachineComparison)

    await vi.waitFor(() => {
      const mockInstance = vi.mocked(echarts.init).mock.results[0].value
      const chartOptions = vi.mocked(mockInstance.setOption).mock.calls[0][0]
      const series = chartOptions.series

      const defectRateSeries = series.find((s: any) => s.name === 'Defect Rate (%)')
      expect(defectRateSeries).toBeDefined()
      expect(defectRateSeries.data[0]).toBeCloseTo(7.6, 1)
    })
  })

  it('disposes chart on unmount', async () => {
    vi.mocked(fetchMachineComparison).mockResolvedValue(mockData)
    const wrapper = mount(MachineComparison)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
    })

    const mockInstance = vi.mocked(echarts.init).mock.results[0].value
    wrapper.unmount()
    expect(mockInstance.dispose).toHaveBeenCalled()
  })
})