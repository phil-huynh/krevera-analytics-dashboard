import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import MachineDefectHeatmap from '@/components/MachineDefectHeatmap.vue'


vi.mock('echarts/core', () => ({
  use: vi.fn(),
  init: vi.fn(() => ({
    setOption: vi.fn(),
    resize: vi.fn(),
    dispose: vi.fn(),
    on: vi.fn()
  }))
}))

vi.mock('echarts/charts', () => ({
  HeatmapChart: {}
}))

vi.mock('echarts/components', () => ({
  TooltipComponent: {},
  GridComponent: {},
  VisualMapComponent: {}
}))

vi.mock('echarts/renderers', () => ({
  CanvasRenderer: {}
}))

vi.mock('@/services/analytics', () => ({
  fetchMachineDefectHeatmap: vi.fn()
}))

import { fetchMachineDefectHeatmap } from '@/services/analytics'
import * as echarts from 'echarts/core'

describe('MachineDefectHeatmap', () => {
  const mockData = {
    cells: [
      { machine_index: 0, defect_index: 0, count: 45, machine_id: 'molding-machine-1', defect_type: 'knit_line_defect' },
      { machine_index: 0, defect_index: 1, count: 32, machine_id: 'molding-machine-1', defect_type: 'warpage' },
      { machine_index: 1, defect_index: 0, count: 38, machine_id: 'molding-machine-2', defect_type: 'knit_line_defect' },
      { machine_index: 1, defect_index: 1, count: 28, machine_id: 'molding-machine-2', defect_type: 'warpage' }
    ],
    machines: ['molding-machine-1', 'molding-machine-2'],
    defect_types: ['knit_line_defect', 'warpage'],
    metadata: {
      machine_count: 2,
      defect_type_count: 2,
      total_defects: 143,
      max_defects_per_cell: 45
    }
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })


  it('renders component title', () => {
    vi.mocked(fetchMachineDefectHeatmap).mockResolvedValue(mockData)
    const wrapper = mount(MachineDefectHeatmap)
    expect(wrapper.text()).toContain('Machine × Defect Type Analysis')
  })


  it('loads data on mount', async () => {
    vi.mocked(fetchMachineDefectHeatmap).mockResolvedValue(mockData)
    mount(MachineDefectHeatmap)

    await nextTick()
    await vi.waitFor(() => {
      expect(fetchMachineDefectHeatmap).toHaveBeenCalledWith({
        start_date: undefined,
        end_date: undefined
      })
    })
  })


  it('displays metadata statistics', async () => {
    vi.mocked(fetchMachineDefectHeatmap).mockResolvedValue(mockData)
    const wrapper = mount(MachineDefectHeatmap)

    await vi.waitFor(() => {
      expect(wrapper.text()).toContain('2')
      expect(wrapper.text()).toContain('143')
      expect(wrapper.text()).toContain('45')
    })
  })


  it('handles error state', async () => {
    vi.mocked(fetchMachineDefectHeatmap).mockRejectedValue(new Error('API Error'))
    const wrapper = mount(MachineDefectHeatmap)

    await vi.waitFor(() => {
      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.text()).toContain('Error loading heatmap')
    })
  })


  it('reloads chart when props change', async () => {
    vi.mocked(fetchMachineDefectHeatmap).mockResolvedValue(mockData)
    const wrapper = mount(MachineDefectHeatmap, {
      props: {
        startDate: '2024-01-01'
      }
    })

    await vi.waitFor(() => {
      expect(fetchMachineDefectHeatmap).toHaveBeenCalledWith({
        start_date: '2024-01-01',
        end_date: undefined
      })
    })

    vi.mocked(fetchMachineDefectHeatmap).mockClear()
    await wrapper.setProps({ startDate: '2024-02-01' })

    await vi.waitFor(() => {
      expect(fetchMachineDefectHeatmap).toHaveBeenCalledWith({
        start_date: '2024-02-01',
        end_date: undefined
      })
    })
  })


  it('handles empty data', async () => {
    vi.mocked(fetchMachineDefectHeatmap).mockResolvedValue({
      cells: [],
      machines: [],
      defect_types: [],
      metadata: mockData.metadata
    })
    const wrapper = mount(MachineDefectHeatmap)

    await vi.waitFor(() => {
      expect(wrapper.find('.error-notification').exists()).toBe(true)
      expect(wrapper.text()).toContain('No defect data available')
    })
  })


  it('disposes chart on unmount', async () => {
    vi.mocked(fetchMachineDefectHeatmap).mockResolvedValue(mockData)
    const wrapper = mount(MachineDefectHeatmap)

    await vi.waitFor(() => {
      expect(echarts.init).toHaveBeenCalled()
    })

    const mockInstance = vi.mocked(echarts.init).mock.results[0].value
    wrapper.unmount()
    expect(mockInstance.dispose).toHaveBeenCalled()
  })
})