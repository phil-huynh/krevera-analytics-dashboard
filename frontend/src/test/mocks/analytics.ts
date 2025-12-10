import { vi } from 'vitest'

export const mockDefectRateTrendData = {
  data_points: [
    { timestamp: '2025-09-20T00:00:00', defect_rate: 0.75, total_products: 100 },
    { timestamp: '2025-09-21T00:00:00', defect_rate: 0.72, total_products: 105 },
  ],
  stats: {
    average_rate: 0.742,
    min_rate: 0.648,
    max_rate: 0.813,
    total_products: 3487
  }
}

export const mockTopDefectsData = {
  defects: [
    { defect_type: 'knit_line_defect', count: 364, percentage: 10.7 },
    { defect_type: 'contamination', count: 360, percentage: 10.6 },
    { defect_type: 'burn_mark', count: 359, percentage: 10.6 }
  ],
  summary: {
    total_defects: 3400,
    most_common: 'knit_line_defect',
    affected_products: 2495
  }
}

export const mockMachineComparisonData = {
  machines: [
    {
      machine_id: 'molding-machine-1',
      total: 1129,
      rejected: 850,
      accepted: 279,
      defect_rate: 0.7528786536758193
    },
    {
      machine_id: 'molding-machine-2',
      total: 1171,
      rejected: 876,
      accepted: 295,
      defect_rate: 0.7480443544832906
    }
  ]
}

export const mockCycleTimeScatterData = {
  points: [
    { product_id: 1, cycle_time: 24.5, defect_count: 0, is_rejected: false },
    { product_id: 2, cycle_time: 26.3, defect_count: 2, is_rejected: true },
  ],
  stats: {
    correlation: -0.004,
    average_cycle_time: 24.47,
    sample_size: 500
  }
}

export const mockMachinesData = {
  machines: ['molding-machine-1', 'molding-machine-2', 'molding-machine-3'],
  count: 3
}

// Mock API functions
export const mockAnalyticsAPI = {
  fetchDefectRateTrend: vi.fn().mockResolvedValue(mockDefectRateTrendData),
  fetchTopDefects: vi.fn().mockResolvedValue(mockTopDefectsData),
  fetchMachineComparison: vi.fn().mockResolvedValue(mockMachineComparisonData),
  fetchCycleTimeScatter: vi.fn().mockResolvedValue(mockCycleTimeScatterData),
  fetchMachines: vi.fn().mockResolvedValue(mockMachinesData),
  fetchDefectDistribution: vi.fn().mockResolvedValue({ distribution: [] }),
  fetchMachineDefectHeatmap: vi.fn().mockResolvedValue({ heatmap: [] })
}