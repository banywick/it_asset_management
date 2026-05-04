import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Vue3Toastify from 'vue3-toastify'
import 'vue3-toastify/dist/index.css'

const app = createApp(App)

app.use(router)
app.use(Vue3Toastify, {
    autoClose: 3000,
    position: "top-right",
    theme: "light",
    transition: "flip",
    pauseOnHover: true,
    pauseOnFocusLoss: false
})

app.mount('#app')

// Экспортируем API URL для использования в других компонентах
export const API_URL = '/api';