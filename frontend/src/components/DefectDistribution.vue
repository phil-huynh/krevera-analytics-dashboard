<template>
  <div class="box">
    <h3 class="title is-5 mb-4">Defect Count Distribution</h3>

    <div v-if="summary" class="columns is-mobile mb-3">
      <div class="column has-text-centered">
        <p class="heading">Perfect Products</p>
        <p class="title is-6 has-text-success">{{ summary.zero_defects }}</p>
      </div>
      <div class="column has-text-centered">
        <p class="heading">Perfect Rate</p>
        <p class="title is-6 has-text-success">{{ summary.perfect_rate.toFixed(1) }}%</p>
      </div>
      <div class="column has-text-centered">
        <p class="heading">Total Products</p>
        <p class="title is-6">{{ summary.total_products }}</p>
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
import { BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { fetchDefectDistribution } from '@/services/analytics'

echarts.use([BarChart, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

interface Props {
  machineId?: string
  startDate?: string
  endDate?: string
}

const props = defineProps<Props>()
const chartContainer = ref<HTMLDivElement | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const summary = ref<any>(null)
let chartInstance: echarts.ECharts | null = null

async function loadChart() {
  loading.value = true
  error.value = null

  try {
    const data = await fetchDefectDistribution({
      machine_id: props.machineId,
      start_date: props.startDate,
      end_date: props.endDate
    })

    summary.value = data.summary

    loading.value = false
    await nextTick()

    if (!chartContainer.value) {
      error.value = 'Failed to initialize chart'
      return
    }

    if (!chartInstance) {
      chartInstance = echarts.init(chartContainer.value)
    }

    const categories = data.distribution.map((item: any) => `${item.defect_count} defects`)
    const counts = data.distribution.map((item: any) => item.product_count)
    const percentages = data.distribution.map((item: any) => item.percentage)

    const option: echarts.EChartsCoreOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        formatter: (params: any) => {
          const index = params[0].dataIndex
          return `${categories[index]}<br/>Products: ${counts[index].toLocaleString()}<br/>Percentage: ${percentages[index].toFixed(1)}%`
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
        data: categories,
        axisLabel: {
          rotate: 0,
          fontSize: 10
        }
      },
      yAxis: {
        type: 'value',
        name: 'Product Count'
      },
      series: [{
        type: 'bar',
        data: counts.map((value: number, index: number) => ({
          value: value,
          itemStyle: {
            color: index === 0 ? '#48c774' :
                   index <= 2 ? '#ffdd57' :
                   index <= 4 ? '#ff9800' :
                   '#f14668'
          }
        })),
        label: {
          show: true,
          position: 'top',
          formatter: '{c}'
        }
      }]
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