import axios from 'axios';
import type {
  DefectRateTrendResponse,
  AnalyticsFilters
} from '@/types/analytics';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';


function buildQueryString(filters: AnalyticsFilters): string {
  const params = new URLSearchParams();

  if (filters.start_date) params.append('start_date', filters.start_date + 'T00:00:00');
  if (filters.end_date) params.append('end_date', filters.end_date + 'T23:59:59');
  if (filters.machine_id) params.append('machine_id', filters.machine_id);
  if (filters.interval) params.append('interval', filters.interval);
  if (filters.limit_products !== undefined) {
    params.append('limit_products', filters.limit_products.toString());
  }

  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
}


export async function fetchDefectRateTrend(
  filters: AnalyticsFilters = {}
): Promise<DefectRateTrendResponse> {
  const query = buildQueryString(filters);
  const response = await axios.get<DefectRateTrendResponse>(
    `${API_BASE_URL}/api/v1/analytics/defect-rate-trend${query}`
  );
  return response.data;
}


export async function fetchTopDefects(filters: AnalyticsFilters & { limit?: number } = {}) {
  const params = new URLSearchParams();
  if (filters.machine_id) params.append('machine_id', filters.machine_id);
  if (filters.start_date) params.append('start_date', filters.start_date + 'T00:00:00');
  if (filters.end_date) params.append('end_date', filters.end_date + 'T23:59:59');
  if (filters.limit) params.append('limit', filters.limit.toString());

  const query = params.toString() ? `?${params}` : '';
  const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/top-defects${query}`);
  return response.data;
}


export async function fetchMachineComparison() {
  const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/machine-comparison`);
  return response.data;
}


export async function fetchDefectDistribution(filters: AnalyticsFilters = {}) {
  const query = buildQueryString(filters);
  const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/defect-distribution${query}`);
  return response.data;
}


export async function fetchMachineDefectHeatmap(filters: Omit<AnalyticsFilters, 'machine_id'> = {}) {
  const params = new URLSearchParams();
  if (filters.start_date) params.append('start_date', filters.start_date + 'T00:00:00');
  if (filters.end_date) params.append('end_date', filters.end_date + 'T23:59:59');

  const query = params.toString() ? `?${params}` : '';
  const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/machine-defect-heatmap${query}`);
  return response.data;
}


export async function fetchCycleTimeScatter(filters: AnalyticsFilters & { limit?: number } = {}) {
  const params = new URLSearchParams();
  if (filters.machine_id) params.append('machine_id', filters.machine_id);
  if (filters.start_date) params.append('start_date', filters.start_date + 'T00:00:00');
  if (filters.end_date) params.append('end_date', filters.end_date + 'T23:59:59');
  if (filters.limit) params.append('limit', filters.limit.toString());

  const query = params.toString() ? `?${params}` : '';
  const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/cycle-time-scatter${query}`);
  return response.data;
}


export async function fetchProductDefects(productId: number) {
  const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/product/${productId}/defects`);
  return response.data;
}

export async function fetchMachines(): Promise<{ machines: string[]; count: number }> {
  const response = await axios.get(`${API_BASE_URL}/api/v1/analytics/machines`)
  return response.data
}