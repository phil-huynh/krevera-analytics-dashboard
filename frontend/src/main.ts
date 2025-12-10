import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

import 'bulma/css/bulma.css'
import './assets/styles/themes.css'
import './assets/styles/global.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')