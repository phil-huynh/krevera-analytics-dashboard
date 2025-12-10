<template>
  <div class="dashboard-layout">

    <!-- Sidebar Filters -->
    <FiltersSidebar
      v-model="filters"
      @collapse-change="handleSidebarCollapse"
    />

    <!-- Main Content Area -->
    <div
      class="dashboard-content"
      :class="{ 'sidebar-collapsed': sidebarCollapsed }"
    >

      <div class="charts-container">
        <div class="charts-row charts-flow">
          <div class="chart-item">
            <ChartCard
              title="Machine Performance Comparison"
              icon="⚙️"
              @expand="openModal('machineComparison')"
            >
              <MachineComparison />
            </ChartCard>
          </div>
          <div class="chart-item">
            <ChartCard
              title="Defect Count Distribution"
              icon="📉"
              @expand="openModal('defectDistribution')"
            >
              <DefectDistribution
                :machine-id="selectedMachine"
                :start-date="startDate"
                :end-date="endDate"
              />
            </ChartCard>
          </div>
          <div class="chart-item">
            <ChartCard
              title="Cycle Time vs Defect Count"
              icon="⏱️"
              @expand="openModal('cycleTime')"
            >
              <CycleTimeScatter
                :machine-id="selectedMachine"
                :start-date="startDate"
                :end-date="endDate"
              />
            </ChartCard>
          </div>
          <div class="chart-item chart-half">
            <ChartCard
              title="Top Defect Types"
              icon="📊"
              @expand="openModal('topDefects')"
            >
              <TopDefects
                :machine-id="selectedMachine"
                :start-date="startDate"
                :end-date="endDate"
              />
            </ChartCard>
          </div>
          <div class="chart-item chart-half">
            <ChartCard
              title="Machine × Defect Type Analysis"
              icon="🗺️"
              @expand="openModal('machineHeatmap')"
            >
              <MachineDefectHeatmap
                :start-date="startDate"
                :end-date="endDate"
              />
            </ChartCard>
          </div>
        </div>

        <div class="charts-row">
          <div class="chart-item chart-full">
            <ChartCard
              title="Defect Rate Trend"
              icon="📈"
              @expand="openModal('trend')"
            >
              <DefectRateTrend
                :machine-id="selectedMachine"
                :start-date="startDate"
                :end-date="endDate"
              />

            </ChartCard>
          </div>
        </div>

      </div>
    </div>

    <!-- Zoom Modal -->
    <div class="modal" :class="{ 'is-active': zoomModalActive }">
      <div class="modal-background" @click="closeModal"></div>
      <div class="modal-card" style="width: 95vw; max-width: 1600px;">
        <header class="modal-card-head">
          <p class="modal-card-title">
            <span class="icon-text">
              <span class="icon">{{ getChartIcon(activeChart) }}</span>
              <span>{{ getChartTitle(activeChart) }}</span>
            </span>
          </p>
          <button class="delete" aria-label="close" @click="closeModal"></button>
        </header>
        <section class="modal-card-body">
          <div style="min-height: 600px;">
            <DefectRateTrend
              v-if="activeChart === 'trend'"
              :machine-id="selectedMachine"
              :start-date="startDate"
              :end-date="endDate"
            />
            <TopDefects
              v-if="activeChart === 'topDefects'"
              :machine-id="selectedMachine"
              :start-date="startDate"
              :end-date="endDate"
            />
            <MachineDefectHeatmap
              v-if="activeChart === 'machineHeatmap'"
              :start-date="startDate"
              :end-date="endDate"
            />
            <MachineComparison v-if="activeChart === 'machineComparison'" />
            <DefectDistribution
              v-if="activeChart === 'defectDistribution'"
              :machine-id="selectedMachine"
              :start-date="startDate"
              :end-date="endDate"
            />
            <CycleTimeScatter
              v-if="activeChart === 'cycleTime'"
              :machine-id="selectedMachine"
              :start-date="startDate"
              :end-date="endDate"
            />
          </div>
        </section>
        <footer class="modal-card-foot">
          <button class="button" @click="closeModal">Close</button>
        </footer>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import DefectRateTrend from '@/components/DefectRateTrend.vue'
import TopDefects from '@/components/TopDefects.vue'
import MachineComparison from '@/components/MachineComparison.vue'
import DefectDistribution from '@/components/DefectDistribution.vue'
import CycleTimeScatter from '@/components/CycleTimeScatter.vue'
import MachineDefectHeatmap from '@/components/MachineDefectHeatmap.vue'
import ChartCard from '@/components/ChartCard.vue'
import FiltersSidebar from '@/components/FiltersSidebar.vue'


const selectedMachine = ref<string | undefined>(undefined)
const startDate = ref('')
const endDate = ref('')
const sidebarCollapsed = ref(false)

function handleSidebarCollapse(collapsed: boolean) {
  sidebarCollapsed.value = collapsed
}

const filters = computed({
  get: () => ({
    machine: selectedMachine.value,
    startDate: startDate.value,
    endDate: endDate.value
  }),
  set: (value) => {
    selectedMachine.value = value.machine
    startDate.value = value.startDate
    endDate.value = value.endDate
  }
})

const zoomModalActive = ref(false)
const activeChart = ref<string | null>(null)

function openModal(chartType: string) {
  activeChart.value = chartType
  zoomModalActive.value = true
}

function closeModal() {
  zoomModalActive.value = false
  activeChart.value = null
}

function getChartTitle(chartType: string | null): string {
  const titles: Record<string, string> = {
    trend: 'Defect Rate Trend',
    topDefects: 'Top Defect Types',
    machineHeatmap: 'Machine × Defect Analysis',
    machineComparison: 'Machine Performance',
    defectDistribution: 'Defect Distribution',
    cycleTime: 'Cycle Time Correlation'
  }
  return titles[chartType || ''] || 'Chart'
}

function getChartIcon(chartType: string | null): string {
  const icons: Record<string, string> = {
    trend: '📈',
    topDefects: '📊',
    machineHeatmap: '🗺️',
    machineComparison: '⚙️',
    defectDistribution: '📉',
    cycleTime: '⏱️'
  }
  return icons[chartType || ''] || '📊'
}
</script>

<style scoped>
/* ============================================
   DASHBOARD LAYOUT
   ============================================ */

.dashboard-layout {
  display: flex;
  min-height: calc(100vh - 3.25rem);
  background-color: var(--bg-secondary);
}

/* ============================================
   MAIN CONTENT AREA
   ============================================ */

.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 17.5rem;
  transition: margin-left 0.3s ease;
}

.dashboard-content.sidebar-collapsed {
  margin-left: 4rem;
}

/* ============================================
   CHARTS CONTAINER - FLEXBOX APPROACH
   ============================================ */

.charts-container {
  flex: 1;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.charts-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
}

/* ============================================
   CHART ITEMS - FLEXIBLE SIZING
   ============================================ */

.chart-item {
  flex: 1 1 20rem;
  min-height: 24rem;
  max-width: 100%;
}

.chart-full {
  flex: 0 0 100% !important;
  min-height: 25rem;
  width: 100%;
}

.chart-half {
  flex: 1 1 calc(50% - 0.75rem);
  min-height: 25rem;
  max-width: calc(50% - 0.75rem);
}

.charts-flow {
}

.charts-flow .chart-item {
  flex: 1 1 20rem;
  min-height: 24rem;
}

.charts-flow .chart-half {
  flex: 1 1 calc(50% - 0.75rem);
  min-height: 25rem;
}

/* ============================================
   RESPONSIVE BREAKPOINTS
   ============================================ */

@media screen and (min-width: 87.5rem) {
  .charts-flow .chart-item {
    flex: 1 1 calc(33.333% - 1rem);
    max-width: calc(33.333% - 1rem);
  }

  .charts-flow .chart-half {
    flex: 1 1 calc(50% - 0.75rem);
    max-width: calc(50% - 0.75rem);
  }
}

@media screen and (min-width: 68.75rem) and (max-width: 87.5rem) {
  .charts-flow .chart-item,
  .charts-flow .chart-half {
    flex: 1 1 calc(50% - 0.75rem);
    max-width: calc(50% - 0.75rem);
  }
}

@media screen and (max-width: 64rem) {
  .dashboard-content {
    margin-left: 0 !important;
  }

  .dashboard-content.sidebar-collapsed {
    margin-left: 0 !important;
  }
}

@media screen and (min-width: 48rem) and (max-width: 68.75rem) {
  .charts-flow .chart-item,
  .charts-flow .chart-half {
    flex: 1 1 100%;
    max-width: 100%;
  }
}

@media screen and (max-width: 48rem) {
  .dashboard-content {
    margin-left: 0;
    padding: 0;
  }

  .dashboard-content.sidebar-collapsed {
    margin-left: 0;
  }

  .charts-container {
    padding: 0.5rem;
    padding-top: 5rem;
    max-width: 100vw;
    overflow-x: hidden;
  }

  .charts-row {
    gap: 1rem;
  }

  .chart-item,
  .chart-half,
  .chart-full {
    flex: 1 1 100%;
    max-width: 100%;
    width: 100%;
    min-height: 22rem;
  }
}
</style>