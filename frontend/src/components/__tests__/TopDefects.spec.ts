import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import TopDefects from '@/components/TopDefects.vue'

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
  BarChart: {}
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
  fetchTopDefects: vi.fn()
}))

import { fetchTopDefects } from '@/services/analytics'
import * as echarts from 'echarts/core'

describe('TopDefects', () => {
  const mockData = {
    defects: [
      { defect_type: 'knit_line_defect', count: 1245, percentage: 36.6 },
      { defect_type: 'warpage', count: 892, percentage: 26.2 },
      { defect_type: 'burn_marks', count: 654, percentage: 19.2 },
      { defect_type: 'short_shot', count: 421, percentage: 12.4 },
      { defect_type: 'flow_marks', count: 188, percentage: 5.5 }
    ],
    summary: {
      total_defects: 3400,
      most_common: 'knit_line_defect',
      affected_products: 2495
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders component title', () => {
    vi.mocked(fetchTopDefects).mockResolvedValue(mockData)
    const wrapper = mount(TopDefects)
    expect(wrapper.text()).toContain('Top Defect Types')
  })

  it('loads data on mount', async () => {
    vi.mocked(fetchTopDefects).mockResolvedValue(mockData)
    mount(TopDefects)

    await nextTick()
    await vi.waitFor(() => {
      expect(fetchTopDefects).toHaveBeenCalledWith({
        machine_id: undefined,
        start_date: undefined,
        end_date: undefined,
        limit: 10
      })
    })
  })

  it('displays summary statistics', async () => {
    vi.mocked(fetchTopDefects).mockResolvedValue(mockData)
    const wrapper = mount(TopDefects)

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('3,400')
      expect(wrapper.text()).toContain('Knit Line Defect')
      expect(wrapper.text()).toContain('2,495')
    })
  })

  it('formats defect names correctly', async () => {
    vi.mocked(fetchTopDefects).mockResolvedValue(mockData)
    const wrapper = mount(TopDefects)

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('Knit Line Defect')
      expect(wrapper.text()).not.toContain('knit_line_defect')
    })
  })

  it('allows changing top N value', async () => {
    vi.mocked(fetchTopDefects).mockResolvedValue(mockData)
    const wrapper = mount(TopDefects)

    await vi.waitFor(() => {
      const select = wrapper.find('select')
      expect(select.exists()).toBe(true)
    })

    const select = wrapper.find('select')
    await select.setValue(10)

    await vi.waitFor(() => {
      expect(fetchTopDefects).toHaveBeenCalledWith(
        expect.objectContaining({ limit: 10 })
      )
    })
  })

  it('handles error state', async () => {
    vi.mocked(fetchTopDefects).mockRejectedValue(new Error('API Error'))
    const wrapper = mount(TopDefects)

    await vi.waitFor(() => {
      expect(wrapper.find('.notification.is-danger').exists()).toBe(true)
      expect(wrapper.text()).toContain('Error loading chart')
    })
  })

  it('initializes chart with bar configuration', async () => {
    vi.mocked(fetchTopDefects).mockResolvedValue(mockData)
    mount(TopDefects)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
    })

    await vi.waitFor(() => {
      const mockInstance = vi.mocked(echarts.init).mock.results[0].value
      expect(mockInstance.setOption).toHaveBeenCalled()
    })

    const mockInstance = vi.mocked(echarts.init).mock.results[0].value
    const chartOptions = vi.mocked(mockInstance.setOption).mock.calls[0][0]
    expect(chartOptions.series[0].type).toBe('bar')
  })

  it('reloads chart when props change', async () => {
    vi.mocked(fetchTopDefects).mockResolvedValue(mockData)
    const wrapper = mount(TopDefects, {
      props: {
        machineId: 'machine-1'
      }
    })

    await vi.waitFor(() => {
      expect(fetchTopDefects).toHaveBeenCalledWith({
        machine_id: 'machine-1',
        start_date: undefined,
        end_date: undefined,
        limit: 10
      })
    })

    vi.mocked(fetchTopDefects).mockClear()
    await wrapper.setProps({ machineId: 'machine-2' })

    await vi.waitFor(() => {
      expect(fetchTopDefects).toHaveBeenCalledWith({
        machine_id: 'machine-2',
        start_date: undefined,
        end_date: undefined,
        limit: 10
      })
    })
  })

  it('handles empty data', async () => {
    vi.mocked(fetchTopDefects).mockResolvedValue({
      defects: [],
      summary: mockData.summary
    })
    const wrapper = mount(TopDefects)

    await vi.waitFor(() => {
      expect(wrapper.find('.notification.is-danger').exists()).toBe(true)
    })
  })

  it('disposes chart on unmount', async () => {
    vi.mocked(fetchTopDefects).mockResolvedValue(mockData)
    const wrapper = mount(TopDefects)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
    })

    const mockInstance = vi.mocked(echarts.init).mock.results[0].value
    wrapper.unmount()
    expect(mockInstance.dispose).toHaveBeenCalled()
  })
})