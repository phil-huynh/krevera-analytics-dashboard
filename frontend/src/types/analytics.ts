// ============================================================================
// TIME SERIES TYPES (Line Chart)
// ============================================================================

export interface DefectRateDataPoint {
  timestamp: string; // ISO datetime string
  total_products: number;
  rejected_products: number;
  defect_rate: number; // 0-1 decimal
}

export interface DefectRateTrendResponse {
  data_points: DefectRateDataPoint[];
  summary: {
    avg_rate: number;
    min_rate: number;
    max_rate: number;
    total_products: number;
  };
}

// ============================================================================
// HEATMAP TYPES (Product × Defect Grid)
// ============================================================================

export interface HeatmapCell {
  product_id: string;
  defect_type: string;
  count: number;
}

export interface DefectHeatmapResponse {
  cells: HeatmapCell[];
  product_labels: string[]; // Y-axis
  defect_labels: string[]; // X-axis
  metadata: {
    total_products: number;
    total_defects: number;
    max_defects_per_product: number;
  };
}

// ============================================================================
// QUERY PARAMETERS
// ============================================================================

export interface AnalyticsFilters {
  start_date?: string; // ISO datetime
  end_date?: string;
  machine_id?: string;
  interval?: 'hour' | 'day' | 'week';
  limit_products?: number;
}
