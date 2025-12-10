import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import DefectDistribution from '@/components/DefectDistribution.vue'


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


vi.mock('@/services/analytics', () => ({
  fetchDefectDistribution: vi.fn()
}))

import { fetchDefectDistribution } from '@/services/analytics'
import * as echarts from 'echarts/core'

describe('DefectDistribution', () => {
  const mockData = {
    distribution: [
      { defect_count: 0, product_count: 850, percentage: 42.5 },
      { defect_count: 1, product_count: 550, percentage: 27.5 },
      { defect_count: 2, product_count: 350, percentage: 17.5 },
      { defect_count: 3, product_count: 150, percentage: 7.5 },
      { defect_count: 4, product_count: 100, percentage: 5.0 }
    ],
    summary: {
      zero_defects: 850,
      perfect_rate: 42.5,
      total_products: 2000
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })


  it('renders component title', () => {
    vi.mocked(fetchDefectDistribution).mockResolvedValue(mockData)
    const wrapper = mount(DefectDistribution)
    expect(wrapper.text()).toContain('Defect Count Distribution')
  })


  it('loads data on mount', async () => {
    vi.mocked(fetchDefectDistribution).mockResolvedValue(mockData)
    mount(DefectDistribution)

    await nextTick()
    await vi.waitFor(() => {
      expect(fetchDefectDistribution).toHaveBeenCalledWith({
        machine_id: undefined,
        start_date: undefined,
        end_date: undefined
      })
    })
  })


  it('displays summary statistics', async () => {
    vi.mocked(fetchDefectDistribution).mockResolvedValue(mockData)
    const wrapper = mount(DefectDistribution)

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('850')
      expect(wrapper.text()).toContain('42.5%')
      expect(wrapper.text()).toContain('2000')
    })
  })


  it('shows perfect products in green', async () => {
    vi.mocked(fetchDefectDistribution).mockResolvedValue(mockData)
    const wrapper = mount(DefectDistribution)

    await vi.waitFor(() => {
      const successElements = wrapper.findAll('.has-text-success')
      expect(successElements.length).toBeGreaterThan(0)
    })
  })


  it('handles error state', async () => {
    vi.mocked(fetchDefectDistribution).mockRejectedValue(new Error('API Error'))
    const wrapper = mount(DefectDistribution)

    await vi.waitFor(() => {
      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.text()).toContain('Error:')
    })
  })


  it('initializes chart with histogram configuration', async () => {
    vi.mocked(fetchDefectDistribution).mockResolvedValue(mockData)
    mount(DefectDistribution)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
      const mockInstance = vi.mocked(echarts.init).mock.results[0].value
      expect(mockInstance.setOption).toHaveBeenCalled()

      const chartOptions = vi.mocked(mockInstance.setOption).mock.calls[0][0]
      expect(chartOptions.series[0].type).toBe('bar')
      expect(chartOptions.xAxis.data).toEqual(['0 defects', '1 defects', '2 defects', '3 defects', '4 defects'])
    })
  })


  it('reloads chart when props change', async () => {
    vi.mocked(fetchDefectDistribution).mockResolvedValue(mockData)
    const wrapper = mount(DefectDistribution, {
      props: {
        machineId: 'machine-1'
      }
    })

    await vi.waitFor(() => {
      expect(fetchDefectDistribution).toHaveBeenCalledWith({
        machine_id: 'machine-1',
        start_date: undefined,
        end_date: undefined
      })
    })

    vi.mocked(fetchDefectDistribution).mockClear()
    await wrapper.setProps({ machineId: 'machine-2' })

    await vi.waitFor(() => {
      expect(fetchDefectDistribution).toHaveBeenCalledWith({
        machine_id: 'machine-2',
        start_date: undefined,
        end_date: undefined
      })
    })
  })


  it('formats tooltip with percentages', async () => {
    vi.mocked(fetchDefectDistribution).mockResolvedValue(mockData)
    mount(DefectDistribution)

    await vi.waitFor(() => {
      const mockInstance = vi.mocked(echarts.init).mock.results[0].value
      const chartOptions = vi.mocked(mockInstance.setOption).mock.calls[0][0]
      const tooltipFormatter = chartOptions.tooltip.formatter

      const mockParams = [{ dataIndex: 0 }]
      const result = tooltipFormatter(mockParams)

      expect(result).toContain('0 defects')
      expect(result).toContain('850')
      expect(result).toContain('42.5%')
    })
  })


  it('disposes chart on unmount', async () => {
    vi.mocked(fetchDefectDistribution).mockResolvedValue(mockData)
    const wrapper = mount(DefectDistribution)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
    })

    const mockInstance = vi.mocked(echarts.init).mock.results[0].value
    wrapper.unmount()
    expect(mockInstance.dispose).toHaveBeenCalled()
  })
})