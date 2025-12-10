import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export type LayoutMode = 'grid' | 'compact' | 'list'

export const usePreferencesStore = defineStore('preferences', () => {
  // State
  const isDarkMode = ref<boolean>(
    localStorage.getItem('darkMode') === 'true'
  )

  const layoutMode = ref<LayoutMode>(
    (localStorage.getItem('layoutMode') as LayoutMode) || 'grid'
  )

  const visibleCharts = ref<string[]>(
    JSON.parse(localStorage.getItem('visibleCharts') || '["trend", "topDefects", "heatmap", "machineComparison", "rejectDistribution", "cycleTime"]')
  )


  watch(isDarkMode, (value) => {
    localStorage.setItem('darkMode', value.toString())
    if (value) {
      document.documentElement.classList.add('dark-mode')
    } else {
      document.documentElement.classList.remove('dark-mode')
    }
  }, { immediate: true })

  watch(layoutMode, (value) => {
    localStorage.setItem('layoutMode', value)
  })

  watch(visibleCharts, (value) => {
    localStorage.setItem('visibleCharts', JSON.stringify(value))
  }, { deep: true })

  // Actions
  function toggleDarkMode() {
    isDarkMode.value = !isDarkMode.value
  }

  function setLayoutMode(mode: LayoutMode) {
    layoutMode.value = mode
  }

  function toggleChart(chartId: string) {
    const index = visibleCharts.value.indexOf(chartId)
    if (index > -1) {
      visibleCharts.value.splice(index, 1)
    } else {
      visibleCharts.value.push(chartId)
    }
  }

  function isChartVisible(chartId: string): boolean {
    return visibleCharts.value.includes(chartId)
  }

  function resetPreferences() {
    isDarkMode.value = false
    layoutMode.value = 'grid'
    visibleCharts.value = ['trend', 'topDefects', 'heatmap', 'machineComparison', 'rejectDistribution', 'cycleTime']
  }

  return {
    // State
    isDarkMode,
    layoutMode,
    visibleCharts,
    // Actions
    toggleDarkMode,
    setLayoutMode,
    toggleChart,
    isChartVisible,
    resetPreferences
  }
})