<template>
  <div id="app">
    <nav class="navbar is-dark" role="navigation">
      <div class="navbar-brand">
        <a class="navbar-item" href="/">
          <span class="icon-text">
            <span class="icon">📊</span>
            <span><strong>Manufacturing Analytics</strong></span>
          </span>
        </a>
      </div>
    </nav>
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>