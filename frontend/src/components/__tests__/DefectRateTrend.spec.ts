import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import DefectRateTrend from '@/components/DefectRateTrend.vue'

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
  LineChart: {}
}))

vi.mock('echarts/components', () => ({
  TitleComponent: {},
  TooltipComponent: {},
  GridComponent: {},
  LegendComponent: {}
}))

vi.mock('echarts/renderers', () => ({
  CanvasRenderer: {}
}))

// Mock analytics service
vi.mock('@/services/analytics', () => ({
  fetchDefectRateTrend: vi.fn()
}))

import { fetchDefectRateTrend } from '@/services/analytics'
import * as echarts from 'echarts/core'

describe('DefectRateTrend', () => {
  const mockData = {
    data_points: [
      { timestamp: '2024-01-01T00:00:00Z', defect_rate: 0.742, rejected_products: 45, total_products: 250 },
      { timestamp: '2024-01-02T00:00:00Z', defect_rate: 0.688, rejected_products: 42, total_products: 245 },
      { timestamp: '2024-01-03T00:00:00Z', defect_rate: 0.813, rejected_products: 51, total_products: 260 }
    ],
    summary: {
      avg_rate: 0.748,
      min_rate: 0.688,
      max_rate: 0.813,
      total_products: 755
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders component title', () => {
    vi.mocked(fetchDefectRateTrend).mockResolvedValue(mockData)
    const wrapper = mount(DefectRateTrend)
    expect(wrapper.text()).toContain('Defect Rate Trend')
  })

  it('loads data on mount', async () => {
    vi.mocked(fetchDefectRateTrend).mockResolvedValue(mockData)
    mount(DefectRateTrend)

    await nextTick()
    await vi.waitFor(() => {
      expect(fetchDefectRateTrend).toHaveBeenCalledWith({
        machine_id: undefined,
        start_date: undefined,
        end_date: undefined,
        interval: 'day'
      })
    })
  })

  it('displays summary statistics', async () => {
    vi.mocked(fetchDefectRateTrend).mockResolvedValue(mockData)
    const wrapper = mount(DefectRateTrend)

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('74.8%')
      expect(wrapper.text()).toContain('68.8%')
      expect(wrapper.text()).toContain('81.3%')
      expect(wrapper.text()).toContain('755')
    })
  })

  it('allows changing interval', async () => {
    vi.mocked(fetchDefectRateTrend).mockResolvedValue(mockData)
    const wrapper = mount(DefectRateTrend)

    await vi.waitFor(() => {
      const hourlyButton = wrapper.findAll('button').find(btn => btn.text() === 'Hourly')
      expect(hourlyButton).toBeDefined()
    })

    const hourlyButton = wrapper.findAll('button').find(btn => btn.text() === 'Hourly')
    await hourlyButton!.trigger('click')

    await vi.waitFor(() => {
      expect(fetchDefectRateTrend).toHaveBeenCalledWith(
        expect.objectContaining({ interval: 'hour' })
      )
    })
  })

  it('applies correct rate color classes', async () => {
    vi.mocked(fetchDefectRateTrend).mockResolvedValue(mockData)
    const wrapper = mount(DefectRateTrend)

    await vi.waitFor(() => {
      const rateElements = wrapper.findAll('.title.is-6')
      const avgRateElement = rateElements[0]
      expect(avgRateElement.classes()).toContain('has-text-warning')
    })
  })

  it('handles error state', async () => {
    vi.mocked(fetchDefectRateTrend).mockRejectedValue(new Error('API Error'))
    const wrapper = mount(DefectRateTrend)

    await vi.waitFor(() => {
      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.text()).toContain('Error loading chart')
    })
  })

  it('initializes chart with line configuration', async () => {
    vi.mocked(fetchDefectRateTrend).mockResolvedValue(mockData)
    mount(DefectRateTrend)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
      const mockInstance = vi.mocked(echarts.init).mock.results[0].value
      expect(mockInstance.setOption).toHaveBeenCalled()

      const chartOptions = vi.mocked(mockInstance.setOption).mock.calls[0][0]
      expect(chartOptions.series[0].type).toBe('line')
      expect(chartOptions.yAxis.name).toContain('Defect Rate')
    })
  })

  it('reloads chart when props change', async () => {
    vi.mocked(fetchDefectRateTrend).mockResolvedValue(mockData)
    const wrapper = mount(DefectRateTrend, {
      props: {
        machineId: 'machine-1'
      }
    })

    await vi.waitFor(() => {
      expect(fetchDefectRateTrend).toHaveBeenCalledWith({
        machine_id: 'machine-1',
        start_date: undefined,
        end_date: undefined,
        interval: 'day'
      })
    })

    vi.mocked(fetchDefectRateTrend).mockClear()
    await wrapper.setProps({ machineId: 'machine-2' })

    await vi.waitFor(() => {
      expect(fetchDefectRateTrend).toHaveBeenCalledWith({
        machine_id: 'machine-2',
        start_date: undefined,
        end_date: undefined,
        interval: 'day'
      })
    })
  })

  it('handles empty data', async () => {
    vi.mocked(fetchDefectRateTrend).mockResolvedValue({
      data_points: [],
      summary: mockData.summary
    })
    const wrapper = mount(DefectRateTrend)

    await vi.waitFor(() => {
      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.text()).toContain('No data available')
    })
  })

  it('disposes chart on unmount', async () => {
    vi.mocked(fetchDefectRateTrend).mockResolvedValue(mockData)
    const wrapper = mount(DefectRateTrend)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
    })

    const mockInstance = vi.mocked(echarts.init).mock.results[0].value
    wrapper.unmount()
    expect(mockInstance.dispose).toHaveBeenCalled()
  })
})