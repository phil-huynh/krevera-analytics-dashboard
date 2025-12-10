<template>
  <div class="box">
    <h3 class="title is-5 mb-4">Cycle Time vs Defect Count</h3>

    <div v-if="stats" class="columns is-mobile mb-3">
      <div class="column has-text-centered">
        <p class="heading">Correlation</p>
        <p class="title is-6" :class="getCorrelationColor(stats.correlation)">
          {{ stats.correlation.toFixed(3) }}
        </p>
      </div>
      <div class="column has-text-centered">
        <p class="heading">Avg Cycle Time</p>
        <p class="title is-6">{{ stats.average_cycle_time }}s</p>
      </div>
      <div class="column has-text-centered">
        <p class="heading">Sample Size</p>
        <p class="title is-6">{{ stats.sample_size }}</p>
      </div>
    </div>

    <div class="chart-wrapper">
      <div ref="chartContainer" class="chart-container"></div>

      <div v-if="loading" class="loading-overlay">
        <progress class="progress is-primary loading-progress" max="100">Loading...</progress>
      </div>

      <div v-if="error" class="notification is-danger is-light error-notification">
        <strong>Error:</strong> {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts/core'
import { ScatterChart } from 'echarts/charts'
import { TooltipComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { fetchCycleTimeScatter } from '@/services/analytics'

echarts.use([ScatterChart, TooltipComponent, GridComponent, CanvasRenderer])

interface Props {
  machineId?: string
  startDate?: string
  endDate?: string
}

const props = defineProps<Props>()
const chartContainer = ref<HTMLDivElement | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const stats = ref<any>(null)
let chartInstance: echarts.ECharts | null = null

function getCorrelationColor(correlation: number): string {
  if (Math.abs(correlation) > 0.7) return 'has-text-danger'
  if (Math.abs(correlation) > 0.4) return 'has-text-warning'
  return 'has-text-success'
}

async function loadChart() {
  loading.value = true
  error.value = null

  try {
    const data = await fetchCycleTimeScatter({
      machine_id: props.machineId,
      start_date: props.startDate,
      end_date: props.endDate
    })

    stats.value = data.stats

    if (!data.points || data.points.length === 0) {
      error.value = 'No data available'
      loading.value = false
      return
    }

    loading.value = false
    await nextTick()

    if (!chartContainer.value) {
      error.value = 'Failed to initialize chart'
      return
    }

    if (!chartInstance) {
      chartInstance = echarts.init(chartContainer.value)
    }

    const acceptedData = data.points
      .filter((point: any) => !point.is_rejected)
      .map((point: any) => ({
        value: [point.cycle_time, point.defect_count],
        product_id: point.product_id,
        cycle_time: point.cycle_time,
        defect_count: point.defect_count,
        is_rejected: false
      }))

    const rejectedData = data.points
      .filter((point: any) => point.is_rejected)
      .map((point: any) => ({
        value: [point.cycle_time, point.defect_count],
        product_id: point.product_id,
        cycle_time: point.cycle_time,
        defect_count: point.defect_count,
        is_rejected: true
      }))

    const option: echarts.EChartsCoreOption = {
      tooltip: {
        trigger: 'item',
        formatter: (params: any) => {
          const point = params.data
          return `
            <strong>Product ${point.product_id}</strong><br/>
            Cycle Time: ${point.cycle_time}s<br/>
            Defect Count: ${point.defect_count}<br/>
            Status: ${point.is_rejected ? 'Rejected' : 'Accepted'}
          `
        }
      },
      legend: {
        data: ['Accepted', 'Rejected'],
        top: '2%',
        textStyle: {
          fontSize: 10
        }
      },
      grid: {
        left: '10%',
        right: '8%',
        bottom: '12%',
        top: '12%',
        containLabel: true
      },
      xAxis: {
        type: 'value',
        name: 'Cycle Time (seconds)',
        nameLocation: 'middle',
        nameGap: 25,
        axisLabel: {
          fontSize: 10
        }
      },
      yAxis: {
        type: 'value',
        name: 'Defect Count',
        nameLocation: 'middle',
        nameGap: 30,
        axisLabel: {
          fontSize: 10
        }
      },
      series: [
        {
          name: 'Accepted',
          type: 'scatter',
          data: acceptedData,
          symbolSize: 6,
          itemStyle: {
            color: '#48c774'
          }
        },
        {
          name: 'Rejected',
          type: 'scatter',
          data: rejectedData,
          symbolSize: 6,
          itemStyle: {
            color: '#f14668'
          }
        }
      ]
    }

    chartInstance.setOption(option)
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

watch([() => props.machineId, () => props.startDate, () => props.endDate], loadChart)
</script>

<style scoped>
.heading {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #7a7a7a;
}

.chart-wrapper {
  position: relative;
  width: 100%;
  height: 16.25rem;
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