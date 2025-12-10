<template>
  <div class="box">
    <div class="level mb-4">
      <div class="level-left">
        <div class="level-item">
          <h3 class="title is-5">Defect Rate Trend</h3>
        </div>
      </div>
      <div class="level-right">
        <div class="level-item">
          <div class="field has-addons">
            <p class="control">
              <button
                class="button is-small"
                :class="{ 'is-primary': interval === 'hour' }"
                @click="interval = 'hour'"
              >
                Hourly
              </button>
            </p>
            <p class="control">
              <button
                class="button is-small"
                :class="{ 'is-primary': interval === 'day' }"
                @click="interval = 'day'"
              >
                Daily
              </button>
            </p>
            <p class="control">
              <button
                class="button is-small"
                :class="{ 'is-primary': interval === 'week' }"
                @click="interval = 'week'"
              >
                Weekly
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="summary" class="columns is-mobile">
      <div class="column">
        <div class="has-text-centered">
          <p class="heading">Avg Rate</p>
          <p class="title is-6" :class="getRateColor(summary.avg_rate)">
            {{ (summary.avg_rate * 100).toFixed(1) }}%
          </p>
        </div>
      </div>
      <div class="column">
        <div class="has-text-centered">
          <p class="heading">Min Rate</p>
          <p class="title is-6" :class="getRateColor(summary.min_rate)">
            {{ (summary.min_rate * 100).toFixed(1) }}%
          </p>
        </div>
      </div>
      <div class="column">
        <div class="has-text-centered">
          <p class="heading">Max Rate</p>
          <p class="title is-6" :class="getRateColor(summary.max_rate)">
            {{ (summary.max_rate * 100).toFixed(1) }}%
          </p>
        </div>
      </div>
      <div class="column">
        <div class="has-text-centered">
          <p class="heading">Total Products</p>
          <p class="title is-6">{{ summary.total_products.toLocaleString() }}</p>
        </div>
      </div>
    </div>

    <div class="chart-wrapper">
      <div ref="chartContainer" class="chart-container"></div>

      <div v-if="loading" class="loading-overlay">
        <progress class="progress is-primary loading-progress" max="100">Loading...</progress>
      </div>

      <div v-if="error" class="notification is-danger is-light error-notification">
        <strong>Error loading chart:</strong> {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { fetchDefectRateTrend } from '@/services/analytics'
import type { DefectRateTrendResponse } from '@/types/analytics'

echarts.use([
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  CanvasRenderer
])

interface Props {
  machineId?: string
  startDate?: string
  endDate?: string
}

const props = defineProps<Props>()

const chartContainer = ref<HTMLDivElement | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const interval = ref<'hour' | 'day' | 'week'>('day')
const summary = ref<DefectRateTrendResponse['summary'] | null>(null)

let chartInstance: echarts.ECharts | null = null

watch(interval, () => {
  loadChart()
})

function getRateColor(rate: number): string {
  if (rate >= 0.8) return 'has-text-danger'
  if (rate >= 0.5) return 'has-text-warning'
  return 'has-text-success'
}

async function loadChart() {
  loading.value = true
  error.value = null

  try {
    const data = await fetchDefectRateTrend({
      machine_id: props.machineId,
      start_date: props.startDate,
      end_date: props.endDate,
      interval: interval.value
    })

    summary.value = data.summary

    if (!data.data_points || data.data_points.length === 0) {
      error.value = 'No data available for the selected filters'
      loading.value = false
      return
    }

    loading.value = false
    await nextTick()

    if (!chartContainer.value) {
      error.value = 'Failed to initialize chart container'
      return
    }

    if (!chartInstance) {
      chartInstance = echarts.init(chartContainer.value)
    }

    const timestamps = data.data_points.map(dataPoint => dataPoint.timestamp)
    const defectRates = data.data_points.map(dataPoint => (dataPoint.defect_rate * 100))
    const rejectedCounts = data.data_points.map(dataPoint => dataPoint.rejected_products)
    const totalCounts = data.data_points.map(dataPoint => dataPoint.total_products)

    const option: echarts.EChartsCoreOption = {
      tooltip: {
        trigger: 'axis',
        formatter: (params: any) => {
          const index = params[0].dataIndex
          return `
            <strong>${new Date(timestamps[index]).toLocaleString()}</strong><br/>
            Defect Rate: <strong>${defectRates[index].toFixed(1)}%</strong><br/>
            Rejected: ${rejectedCounts[index]} / ${totalCounts[index]}
          `
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: timestamps.map(timestamp => new Date(timestamp).toLocaleDateString()),
        boundaryGap: false
      },
      yAxis: {
        type: 'value',
        name: 'Defect Rate (%)',
        min: 0,
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [
        {
          name: 'Defect Rate',
          type: 'line',
          data: defectRates,
          smooth: true,
          lineStyle: {
            width: 3,
            color: '#f14668'
          },
          itemStyle: {
            color: '#f14668'
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(241, 70, 104, 0.3)' },
              { offset: 1, color: 'rgba(241, 70, 104, 0.05)' }
            ])
          }
        }
      ]
    }

    chartInstance.setOption(option, {
      notMerge: false,
      lazyUpdate: false
    })
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load chart'
    loading.value = false
  }
}

function handleResize() {
  chartInstance?.resize()
}

onMounted(() => {
  loadChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})

watch([() => props.machineId, () => props.startDate, () => props.endDate], () => {
  loadChart()
}, { deep: true })
</script>

<style scoped>
.heading {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #7a7a7a;
}

.box {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 1rem;
}

.chart-wrapper {
  position: relative;
  flex: 1;
  min-height: 0;
  width: 100%;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.8);
}

.loading-progress {
  width: 50%;
}

.error-notification {
  position: absolute;
  inset: 0;
  margin: 1rem;
}
</style>