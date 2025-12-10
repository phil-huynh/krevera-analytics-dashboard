import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import Dashboard from '@/views/Dashboard.vue'

// Mock analytics service
vi.mock('@/services/analytics', () => ({
  fetchDefectRateTrend: vi.fn().mockResolvedValue({
    data_points: [],
    stats: { average_rate: 0.742, min_rate: 0.648, max_rate: 0.813, total_products: 3487 }
  }),
  fetchTopDefects: vi.fn().mockResolvedValue({
    defects: [],
    summary: { total_defects: 3400, most_common: 'knit_line_defect', affected_products: 2495 }
  }),
  fetchMachineComparison: vi.fn().mockResolvedValue({ machines: [] }),
  fetchCycleTimeScatter: vi.fn().mockResolvedValue({ points: [], stats: {} }),
  fetchMachines: vi.fn().mockResolvedValue({ machines: [], count: 0 }),
  fetchDefectDistribution: vi.fn().mockResolvedValue({ distribution: [] }),
  fetchMachineDefectHeatmap: vi.fn().mockResolvedValue({ heatmap: [] })
}))

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

describe('Dashboard', () => {
  it('renders dashboard layout', () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          FiltersSidebar: true,
          ChartCard: true,
          DefectRateTrend: true,
          TopDefects: true,
          MachineComparison: true,
          DefectDistribution: true,
          CycleTimeScatter: true,
          MachineDefectHeatmap: true
        }
      }
    })

    expect(wrapper.find('.dashboard-layout').exists()).toBe(true)
    expect(wrapper.find('.dashboard-content').exists()).toBe(true)
  })

  it('handles sidebar collapse', async () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          FiltersSidebar: {
            template: '<div @click="$emit(\'collapse-change\', true)">Sidebar</div>'
          },
          ChartCard: true,
          DefectRateTrend: true,
          TopDefects: true,
          MachineComparison: true,
          DefectDistribution: true,
          CycleTimeScatter: true,
          MachineDefectHeatmap: true
        }
      }
    })

    const vm = wrapper.vm as any
    expect(vm.sidebarCollapsed).toBe(false)

    vm.handleSidebarCollapse(true)
    await wrapper.vm.$nextTick()

    expect(vm.sidebarCollapsed).toBe(true)
    expect(wrapper.find('.dashboard-content').classes()).toContain('sidebar-collapsed')
  })

  it('opens modal when chart is expanded', async () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          FiltersSidebar: true,
          ChartCard: true,
          DefectRateTrend: true,
          TopDefects: true,
          MachineComparison: true,
          DefectDistribution: true,
          CycleTimeScatter: true,
          MachineDefectHeatmap: true
        }
      }
    })

    const vm = wrapper.vm as any

    vm.openModal('trend')
    await wrapper.vm.$nextTick()

    expect(vm.zoomModalActive).toBe(true)
    expect(vm.activeChart).toBe('trend')
    expect(wrapper.find('.modal.is-active').exists()).toBe(true)
  })

  it('closes modal when close button is clicked', async () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          FiltersSidebar: true,
          ChartCard: true,
          DefectRateTrend: true,
          TopDefects: true,
          MachineComparison: true,
          DefectDistribution: true,
          CycleTimeScatter: true,
          MachineDefectHeatmap: true
        }
      }
    })

    const vm = wrapper.vm as any

    vm.openModal('trend')
    await wrapper.vm.$nextTick()
    expect(vm.zoomModalActive).toBe(true)

    vm.closeModal()
    await wrapper.vm.$nextTick()

    expect(vm.zoomModalActive).toBe(false)
    expect(vm.activeChart).toBeNull()
  })

  it('updates filters correctly', async () => {
    const wrapper = mount(Dashboard, {
      global: {
        stubs: {
          FiltersSidebar: true,
          ChartCard: true,
          DefectRateTrend: true,
          TopDefects: true,
          MachineComparison: true,
          DefectDistribution: true,
          CycleTimeScatter: true,
          MachineDefectHeatmap: true
        }
      }
    })

    const vm = wrapper.vm as any

    vm.filters = {
      machine: 'molding-machine-1',
      startDate: '2025-01-01',
      endDate: '2025-01-31'
    }
    await wrapper.vm.$nextTick()

    expect(vm.selectedMachine).toBe('molding-machine-1')
    expect(vm.startDate).toBe('2025-01-01')
    expect(vm.endDate).toBe('2025-01-31')
  })
})