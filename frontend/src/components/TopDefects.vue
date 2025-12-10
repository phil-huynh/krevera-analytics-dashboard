<template>
  <div class="box">
    <div class="level mb-4">
      <div class="level-left">
        <div class="level-item">
          <h3 class="title is-5">Top Defect Types</h3>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <div class="field">
            <label class="label is-small">Show Top</label>
            <div class="control">
              <div class="select is-small">
                <select v-model.number="topN" @change="loadChart">
                  <option :value="5">Top 5</option>
                  <option :value="10">Top 10</option>
                  <option :value="13">All Types</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Stats -->
    <div v-if="summary" class="columns is-mobile mb-4">
      <div class="column">
        <div class="has-text-centered">
          <p class="heading">Total Defects</p>
          <p class="title is-6">{{ summary.total_defects.toLocaleString() }}</p>
        </div>
      </div>
      <div class="column">
        <div class="has-text-centered">
          <p class="heading">Most Common</p>
          <p class="title is-6">{{formatDefectName(summary.most_common)}}</p>
        </div>
      </div>
      <div class="column">
        <div class="has-text-centered">
          <p class="heading">Affected Products</p>
          <p class="title is-6">{{ summary.affected_products.toLocaleString() }}</p>
        </div>
      </div>
    </div>

    <!-- Chart Container -->
    <div class="chart-wrapper" style="position: relative; width: 100%; height: 280px;">
      <div ref="chartContainer" style="width: 100%; height: 100%;"></div>

      <div
        v-if="loading"
        class="has-text-centered"
        style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(255, 255, 255, 0.8);"
      >
        <progress class="progress is-primary" style="width: 50%;" max="100">Loading...</progress>
      </div>

      <div
        v-if="error"
        class="notification is-danger is-light"
        style="position: absolute; inset: 0; margin: 1rem;"
      >
        <strong>Error loading chart:</strong> {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts/core';
import { BarChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';
import { fetchTopDefects } from '@/services/analytics';

echarts.use([
  BarChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  CanvasRenderer
]);

interface Props {
  machineId?: string;
  startDate?: string;
  endDate?: string;
}

const props = defineProps<Props>();

const chartContainer = ref<HTMLDivElement | null>(null);
const loading = ref(false);
const error = ref<string | null>(null);
const topN = ref(10);
const summary = ref<any>(null);

let chartInstance: echarts.ECharts | null = null;


function formatDefectType(type: string): string {
  return type.replace(/_/g, ' ').replace(/defect/g, '').trim()
    .replace(/\b\w/g, c => c.toUpperCase());
}

function formatDefectName(name: string): string {
  if (!name) return ''
  return name
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ')
}


async function loadChart() {
  loading.value = true;
  error.value = null;

  try {
    const data = await fetchTopDefects({
      machine_id: props.machineId,
      start_date: props.startDate,
      end_date: props.endDate,
      limit: topN.value
    });

    summary.value = data.summary;

    if (!data.defects || data.defects.length === 0) {
      error.value = 'No defect data available';
      loading.value = false;
      return;
    }

    loading.value = false;

    await nextTick();

    if (!chartContainer.value) {
      console.error('Chart container not found');
      error.value = 'Failed to initialize chart container';
      return;
    }

    if (!chartInstance) {
      chartInstance = echarts.init(chartContainer.value);
    }

    const defectTypes = data.defects.map((d: any) => formatDefectType(d.defect_type)).reverse();
    const counts = data.defects.map((d: any) => d.count).reverse();
    const percentages = data.defects.map((d: any) => d.percentage);

    const option: echarts.EChartsCoreOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        },
        formatter: (params: any) => {
          const idx = params[0].dataIndex;
          return `
            <strong>${defectTypes[idx]}</strong><br/>
            Count: <strong>${counts[idx].toLocaleString()}</strong><br/>
            Percentage: <strong>${percentages[idx].toFixed(1)}%</strong>
          `;
        }
      },
      grid: {
        left: '5%',
        right: '10%',
        bottom: '3%',
        top: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: 'Count'
      },
      yAxis: {
        type: 'category',
        data: defectTypes,
        axisLabel: {
          fontSize: 11,
          width: 140,
          overflow: 'truncate',
          ellipsis: '...'
        }
      },
      series: [
        {
          name: 'Defect Count',
          type: 'bar',
          data: counts,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
              { offset: 0, color: '#f14668' },
              { offset: 1, color: '#ff6b9d' }
            ])
          },
          label: {
            show: true,
            position: 'right',
            formatter: '{c}'
          }
        }
      ]
    };

    chartInstance.setOption(option);
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load chart';
    console.error('Chart error:', err);
    loading.value = false;
  }
}

function handleResize() {
  chartInstance?.resize();
}

onMounted(() => {
  loadChart();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  chartInstance?.dispose();
});

watch([() => props.machineId, () => props.startDate, () => props.endDate], () => {
  loadChart();
});
</script>

<style scoped>
.heading {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #7a7a7a;
}
</style>