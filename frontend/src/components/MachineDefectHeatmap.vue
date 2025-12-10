<template>
  <div class="box">
    <div class="level mb-4">
      <div class="level-left">
        <div class="level-item">
          <h3 class="title is-5">Machine × Defect Type Analysis</h3>
        </div>
      </div>
    </div>

    <div v-if="metadata" class="columns is-mobile mb-4">
      <div class="column has-text-centered">
        <p class="heading">Machines</p>
        <p class="title is-6">{{ metadata.machine_count }}</p>
      </div>
      <div class="column has-text-centered">
        <p class="heading">Defect Types</p>
        <p class="title is-6">{{ metadata.defect_type_count }}</p>
      </div>
      <div class="column has-text-centered">
        <p class="heading">Total Defects</p>
        <p class="title is-6">{{ metadata.total_defects.toLocaleString() }}</p>
      </div>
      <div class="column has-text-centered">
        <p class="heading">Max per Cell</p>
        <p class="title is-6 has-text-danger">{{ metadata.max_defects_per_cell }}</p>
      </div>
    </div>

    <div class="chart-wrapper">
      <div ref="chartContainer" class="chart-container"></div>

      <div v-if="loading" class="loading-overlay">
        <progress class="progress is-primary loading-progress" max="100">Loading...</progress>
      </div>

      <div v-if="error" class="notification is-danger is-light error-notification">
        <strong>Error loading heatmap:</strong> {{ error }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts/core'
import { HeatmapChart } from 'echarts/charts'
import {
  TooltipComponent,
  GridComponent,
  VisualMapComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { fetchMachineDefectHeatmap } from '@/services/analytics'

echarts.use([
  HeatmapChart,
  TooltipComponent,
  GridComponent,
  VisualMapComponent,
  CanvasRenderer
])

interface Props {
  startDate?: string
  endDate?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  cellClick: [machineId: string, defectType: string, count: number]
}>()

const chartContainer = ref<HTMLDivElement | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const metadata = ref<any>(null)

let chartInstance: echarts.ECharts | null = null

function formatDefectType(type: string): string {
  return type.replace(/_/g, ' ').replace(/defect/g, '').trim()
    .replace(/\b\w/g, char => char.toUpperCase())
}

async function loadChart() {
  loading.value = true
  error.value = null

  try {
    const data = await fetchMachineDefectHeatmap({
      start_date: props.startDate,
      end_date: props.endDate
    })

    metadata.value = data.metadata

    if (!data.cells || data.cells.length === 0) {
      error.value = 'No defect data available for the selected filters'
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

      chartInstance.on('click', (params: any) => {
        if (params.componentType === 'series') {
          const [machineIndex, defectIndex] = params.value
          const machineId = data.machine_labels[machineIndex]
          const defectType = data.defect_labels[defectIndex]
          const count = params.data[2]

          emit('cellClick', machineId, defectType, count)
        }
      })
    }

    const machineLabels = data.machine_labels
    const defectLabels = data.defect_labels.map(formatDefectType)

    const heatmapData = data.cells.map((cell: number[]) => ({
      value: [cell[0], cell[1], cell[2]]
    }))

    const maxValue = data.metadata.max_defects_per_cell || 100

    const option: echarts.EChartsCoreOption = {
      tooltip: {
        position: 'top',
        formatter: (params: any) => {
          const [machineIndex, defectIndex, count] = params.value
          return `
            <strong>${machineLabels[machineIndex]}</strong><br/>
            ${defectLabels[defectIndex]}<br/>
            Count: <strong>${count}</strong>
          `
        }
      },
      grid: {
        left: '15%',
        right: '12%',
        bottom: '8%',
        top: '5%',
        containLabel: false
      },
      xAxis: {
        type: 'category',
        data: machineLabels,
        splitArea: {
          show: true
        },
        axisLabel: {
          fontSize: 10
        }
      },
      yAxis: {
        type: 'category',
        data: defectLabels,
        splitArea: {
          show: true
        },
        axisLabel: {
          fontSize: 9,
          width: 100,
          overflow: 'truncate'
        }
      },
      visualMap: {
        min: 0,
        max: maxValue,
        calculable: true,
        orient: 'vertical',
        right: '2%',
        top: 'center',
        inRange: {
          color: ['#ffffff', '#ffeb3b', '#ff9800', '#f44336']
        },
        text: ['High', 'Low'],
        textStyle: {
          fontSize: 9
        },
        itemWidth: 12,
        itemHeight: 80
      },
      series: [
        {
          name: 'Defect Count',
          type: 'heatmap',
          data: heatmapData,
          label: {
            show: false
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }

    chartInstance.setOption(option)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Failed to load heatmap'
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

watch([() => props.startDate, () => props.endDate], () => {
  loadChart()
})
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
  height: 15rem;
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
  background: rgba(255, 255, 255, 0.85);
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