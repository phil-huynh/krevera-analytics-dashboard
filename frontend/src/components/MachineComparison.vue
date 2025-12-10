<template>
  <div class="box">
    <h3 class="title is-5 mb-4">Machine Performance Comparison</h3>

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
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import {
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { fetchMachineComparison } from '@/services/analytics'

echarts.use([BarChart, TooltipComponent, GridComponent, LegendComponent, CanvasRenderer])

const chartContainer = ref<HTMLDivElement | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
let chartInstance: echarts.ECharts | null = null

function formatMachineName(id: string): string {
  return id
    .replace(/[-_]/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

async function loadChart() {
  loading.value = true
  error.value = null

  try {
    const data = await fetchMachineComparison()

    if (!data.machines || data.machines.length === 0) {
      error.value = 'No machine data available'
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

    const machines = data.machines.map((machine: any) => machine.machine_id)
    const totals = data.machines.map((machine: any) => machine.total)
    const rejected = data.machines.map((machine: any) => machine.rejected)
    const accepted = data.machines.map((machine: any) => machine.accepted)
    const rates = data.machines.map((machine: any) => machine.defect_rate * 100)

    const option: echarts.EChartsCoreOption = {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        appendToBody: true,
        formatter: (params: any) => {
          if (!Array.isArray(params)) return ''
          let result = `<strong>${params[0].axisValue}</strong><br/>`
          params.forEach((item: any) => {
            const value = item.seriesName === 'Defect Rate (%)'
              ? item.value.toFixed(2) + '%'
              : item.value.toLocaleString()
            result += `${item.marker} ${item.seriesName}: ${value}<br/>`
          })
          return result
        },
        position: (point: number[], _params: any, _dom: any, _rect: any, size: any) => {
          return [
            point[0] - size.contentSize[0] / 2,
            point[1] - size.contentSize[1] - 20
          ]
        }
      },
      legend: {
        data: ['Total', 'Rejected', 'Accepted', 'Defect Rate (%)'],
        bottom: 0,
        orient: 'horizontal',
        left: 'center',
        itemGap: 15,
        textStyle: {
          fontSize: 11
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        top: '20%',
        bottom: '25%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: machines.map((machine: string) => formatMachineName(machine)),
        axisLabel: {
          interval: 0,
          rotate: 0,
          fontSize: 10,
          formatter: function(value: string) {
            if (value.length > 15) {
              return value.substring(0, 15) + '\n' + value.substring(15)
            }
            return value
          },
          lineHeight: 14
        },
        axisPointer: {
          type: 'shadow'
        }
      },
      yAxis: [
        {
          type: 'value',
          name: 'Count'
        },
        {
          type: 'value',
          name: 'Rate (%)',
          max: 100
        }
      ],
      series: [
        {
          name: 'Total',
          type: 'bar',
          data: totals,
          itemStyle: { color: '#3273dc' }
        },
        {
          name: 'Rejected',
          type: 'bar',
          data: rejected,
          itemStyle: { color: '#f14668' }
        },
        {
          name: 'Accepted',
          type: 'bar',
          data: accepted,
          itemStyle: { color: '#48c774' }
        },
        {
          name: 'Defect Rate (%)',
          type: 'line',
          yAxisIndex: 1,
          data: rates,
          itemStyle: { color: '#ffdd57' },
          lineStyle: { width: 3 }
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
</script>

<style scoped>
.box {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 0.75rem;
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