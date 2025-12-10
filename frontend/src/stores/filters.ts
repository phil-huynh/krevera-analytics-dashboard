import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useFiltersStore = defineStore('filters', () => {
  // State
  const selectedMachine = ref<string | undefined>(undefined)
  const startDate = ref<string>('')
  const endDate = ref<string>('')

  // Computed
  const apiFilters = computed(() => ({
    machine_id: selectedMachine.value,
    start_date: startDate.value,
    end_date: endDate.value
  }))

  // Actions
  function setMachine(machineId: string | undefined) {
    selectedMachine.value = machineId
  }

  function setDateRange(start: string, end: string) {
    startDate.value = start
    endDate.value = end
  }

  function clearFilters() {
    selectedMachine.value = undefined
    startDate.value = ''
    endDate.value = ''
  }

  function setPreset(preset: 'today' | 'week' | 'month') {
    const now = new Date()
    const end = now.toISOString().split('T')[0]

    let start: Date
    switch (preset) {
      case 'today':
        start = now
        break
      case 'week':
        start = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
        break
      case 'month':
        start = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
        break
    }

    startDate.value = start.toISOString().split('T')[0]
    endDate.value = end
  }

  return {
    // State
    selectedMachine,
    startDate,
    endDate,
    // Computed
    apiFilters,
    // Actions
    setMachine,
    setDateRange,
    clearFilters,
    setPreset
  }
})