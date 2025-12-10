<template>
  <div class="card chart-card-wrapper">
    <header class="card-header">
      <p class="card-header-title">
        <span class="icon mr-2" v-if="icon">{{ icon }}</span>
        {{ title }}
      </p>
      <button
        class="card-header-icon expand-button"
        @click="handleExpand"
        title="Expand chart"
        type="button"
      >
        <span class="icon has-text-grey">
          <span>🔍</span>
        </span>
      </button>
    </header>
    <div class="card-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title: string
  icon?: string
}

defineProps<Props>()
const emit = defineEmits<{
  expand: []
}>()

function handleExpand(e: Event) {
  e.preventDefault()
  e.stopPropagation()
  console.log('Expand button clicked')
  emit('expand')
}
</script>

<style scoped>
.chart-card-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 0.125em 0.25em rgba(10, 10, 10, 0.1);
}

.card-header {
  box-shadow: none;
  border-bottom: 1px solid var(--border-color, #dbdbdb);
  flex-shrink: 0;
}

.card-header-title {
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0.75rem 1rem;
}

.card-header-icon {
  padding: 0.75rem 1rem;
}

.expand-button {
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
  background: transparent;
}

.expand-button:hover {
  background-color: rgba(10, 10, 10, 0.05);
}

.expand-button:hover .icon {
  color: #3273dc !important;
  transform: scale(1.1);
}

.card-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow: hidden;
}

.card-content :deep(.box) {
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-bottom: 0;
  box-shadow: none;
  border: none;
  padding: 1rem;
  background-color: transparent;
}

.card-content :deep(.chart-wrapper) {
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.card-content :deep(.chart-wrapper > div) {
  flex: 1;
  min-height: 0;
}
</style>