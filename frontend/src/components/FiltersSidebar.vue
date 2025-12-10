<template>
  <div>
    <!-- Mobile Menu Button -->
    <button
      class="button is-primary sidebar-toggle is-hidden-tablet"
      @click="isOpen = !isOpen"
    >
      <span class="icon">
        <span>{{ isOpen ? '✕' : '☰' }}</span>
      </span>
      <span>Filters</span>
    </button>

    <!-- Overlay for mobile -->
    <div
      v-if="isOpen"
      class="sidebar-overlay is-hidden-tablet"
      @click="isOpen = false"
    ></div>

    <!-- Sidebar -->
    <aside
      class="sidebar-panel"
      :class="{ 'is-open': isOpen, 'is-collapsed': isCollapsed }"
    >

      <div class="sidebar-content">
        <div class="sidebar-header mb-4">
          <h3 class="title is-5 mb-0">
            <span class="icon-text">
              <span class="icon">🔍</span>
              <span>Filters</span>
            </span>
          </h3>
          <button
            class="button is-small sidebar-collapse-btn is-hidden-mobile"
            :class="{ 'is-collapsed': isCollapsed }"
            @click="isCollapsed = !isCollapsed"
            :title="'Collapse sidebar'"
          >
            <span class="icon">
              <span>←</span>
            </span>
          </button>
        </div>

        <!-- Machine Filter -->
        <div class="field mb-5">
          <label class="label">Machine</label>
          <div class="control">
            <div class="select is-fullwidth">
              <select v-model="localMachine">
                <option :value="undefined">All Machines</option>
                <option
                  v-for="machine in machines"
                  :key="machine"
                  :value="machine"
                >
                  {{ getMachineName(machine) }}
                </option>
              </select>
            </div>
          </div>
        </div>

        <!-- Date Range -->
        <div class="field mb-5">
          <label class="label">Start Date</label>
          <div class="control">
            <input
              v-model="localStartDate"
              class="input"
              type="date"
            />
          </div>
        </div>

        <div class="field mb-5">
          <label class="label">End Date</label>
          <div class="control">
            <input
              v-model="localEndDate"
              class="input"
              type="date"
            />
          </div>
        </div>

        <!-- Active Filters Tags -->
        <div class="field mb-5" v-if="hasActiveFilters">
          <label class="label">Active Filters</label>
          <div class="tags">
            <span class="tag is-primary is-medium" v-if="localMachine">
              {{ getMachineName(localMachine) }}
              <button class="delete is-small" @click="clearMachine"></button>
            </span>
            <span class="tag is-info is-medium" v-if="localStartDate">
              From: {{ formatDate(localStartDate) }}
              <button class="delete is-small" @click="clearStartDate"></button>
            </span>
            <span class="tag is-info is-medium" v-if="localEndDate">
              To: {{ formatDate(localEndDate) }}
              <button class="delete is-small" @click="clearEndDate"></button>
            </span>
          </div>
        </div>

        <!-- Actions -->
        <div class="field">
          <button
            class="button is-danger is-light is-fullwidth"
            @click="clearAll"
            :disabled="!hasActiveFilters"
          >
            Clear All Filters
          </button>
        </div>
      </div>
    </aside>

    <button
      v-if="isCollapsed"
      class="button is-small sidebar-expand-btn is-hidden-mobile"
      @click="isCollapsed = false"
      title="Expand sidebar"
    >
      <span class="icon">
        <span>→</span>
      </span>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { fetchMachines } from '@/services/analytics'

interface Filters {
  machine?: string
  startDate: string
  endDate: string
}

interface Props {
  modelValue: Filters
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'update:modelValue': [value: Filters]
  'collapse-change': [collapsed: boolean]
}>()

const isOpen = ref(false)
const isCollapsed = ref(false)

const localMachine = ref(props.modelValue?.machine)
const localStartDate = ref(props.modelValue?.startDate || '')
const localEndDate = ref(props.modelValue?.endDate || '')

const machines = ref<string[]>([])

onMounted(async () => {
  try {
    const data = await fetchMachines()
    machines.value = data.machines
    console.log('Loaded machines:', machines.value)
  } catch (error) {
    console.error('Failed to load machines:', error)
    machines.value = ['molding-machine-1', 'molding-machine-2', 'molding-machine-3']
  }
})

watch([localMachine, localStartDate, localEndDate], () => {
  emit('update:modelValue', {
    machine: localMachine.value,
    startDate: localStartDate.value,
    endDate: localEndDate.value
  })
  if (window.innerWidth < 769) {
    isOpen.value = false
  }
})

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    localMachine.value = newVal.machine
    localStartDate.value = newVal.startDate
    localEndDate.value = newVal.endDate
  }
}, { deep: true })

watch(isCollapsed, (newVal) => {
  emit('collapse-change', newVal)
})

const hasActiveFilters = computed(() => {
  return localMachine.value || localStartDate.value || localEndDate.value
})

function clearMachine() {
  localMachine.value = undefined
}

function clearStartDate() {
  localStartDate.value = ''
}

function clearEndDate() {
  localEndDate.value = ''
}

function clearAll() {
  localMachine.value = undefined
  localStartDate.value = ''
  localEndDate.value = ''
}

function getMachineName(id: string): string {
  return id
    .replace(/[-_]/g, ' ')
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

function formatDate(date: string): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}
</script>

<style scoped>
/* ============================================
   DESKTOP COLLAPSE BUTTON
   ============================================ */
.sidebar-collapse-btn {
  flex-shrink: 0;
  border-radius: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  transition: all 0.2s ease;
}

.sidebar-collapse-btn:hover {
  background-color: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--text-secondary);
}

.sidebar-collapse-btn.is-collapsed {
  left: 1rem;
  background-color: #48c774;
}

.sidebar-collapse-btn.is-collapsed:hover {
  background-color: #3abb67;
}

/* ============================================
   MOBILE TOGGLE BUTTON
   ============================================ */

.sidebar-toggle {
  position: fixed;
  top: 4rem;
  left: 1rem;
  z-index: 200;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

/* ============================================
   MOBILE OVERLAY
   ============================================ */

.sidebar-overlay {
  position: fixed;
  inset: 0;
  top: 3.25rem;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 150;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* ============================================
   SIDEBAR PANEL
   ============================================ */

.sidebar-panel {
  position: fixed;
  left: 0;
  top: 3.25rem;
  bottom: 0;
  width: 17.5rem;
  background-color: var(--bg-primary);
  border-right: 1px solid var(--border-color);
  box-shadow: 0.125rem 0 0.5rem rgba(0, 0, 0, 0.1);
  z-index: 100;
  overflow-y: auto;
  transition: transform 0.3s ease;
}

.sidebar-panel.is-collapsed {
  transform: translateX(-17.5rem);
}

.sidebar-panel.is-collapsed .sidebar-content {
  opacity: 0;
  pointer-events: none;
}

/* ============================================
   SIDEBAR CONTENT
   ============================================ */

.sidebar-content {
  padding: 1.5rem;
  transition: opacity 0.3s ease;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.sidebar-expand-btn {
  position: fixed;
  left: 1rem;
  top: 4.5rem;
  z-index: 101;
  border-radius: 0.5rem;
  padding: 0.75rem;
  background-color: #48c774;
  color: white;
  border: none;
  box-shadow: 0 0.125rem 0.5rem rgba(0, 0, 0, 0.15);
  transition: all 0.2s ease;
}

.sidebar-expand-btn:hover {
  background-color: #3abb67;
  box-shadow: 0 0.25rem 0.75rem rgba(0, 0, 0, 0.25);
  transform: translateY(-0.125rem);
}

/* ============================================
   TAGS STYLING
   ============================================ */

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  margin-bottom: 0;
}

/* ============================================
   SCROLLBAR STYLING
   ============================================ */

.sidebar-panel::-webkit-scrollbar {
  width: 6px;
}

.sidebar-panel::-webkit-scrollbar-track {
  background: var(--bg-secondary);
}

.sidebar-panel::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.sidebar-panel::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* ============================================
   RESPONSIVE: DESKTOP (> 768px)
   ============================================ */

@media screen and (min-width: 64rem) {
  .sidebar-panel:not(.is-collapsed) {
    transform: translateX(0) !important;
  }
}

/* ============================================
   RESPONSIVE: MOBILE (< 768px)
   ============================================ */

@media screen and (max-width: 64rem) {
  .sidebar-panel {
    transform: translateX(-100%);
    z-index: 175;
    width: 16.25rem;
  }

  .sidebar-panel.is-open {
    transform: translateX(0) !important;
  }

  .sidebar-collapse-btn {
    display: none;
  }
}
</style>