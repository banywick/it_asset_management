<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">IT Asset Tracker</div>
      
      <div class="search-container">
        <div class="search-bar">
          <input 
            type="text" 
            v-model="searchQuery" 
            @input="onSearchInput"
            @keyup.enter="goToSearch"
            @focus="showSuggestions = true"
            @blur="handleBlur"
            placeholder="🔍 Поиск по всем сущностям..."
            class="global-search-input"
          >
          <button @click="goToSearch" class="search-btn">🔍</button>
        </div>
        
        <!-- Подсказки поиска -->
        <div v-if="showSuggestions && suggestions.length > 0" class="suggestions-dropdown">
          <div 
            v-for="suggestion in suggestions" 
            :key="suggestion.id"
            class="suggestion-item"
            @mousedown.prevent="selectSuggestion(suggestion)"
          >
            <div class="suggestion-icon">{{ suggestion.icon }}</div>
            <div class="suggestion-content">
              <div class="suggestion-title">{{ suggestion.title }}</div>
              <div class="suggestion-subtitle">{{ suggestion.subtitle }}</div>
            </div>
            <div class="suggestion-type">{{ suggestion.type }}</div>
          </div>
        </div>
      </div>
      
      <div class="nav-right">
        <!-- Кнопка отчета -->
        <button @click="openReportModal" class="report-btn" title="Отчет">
          <i class="fas fa-chart-bar"></i> Отчет
        </button>
        
        <div class="user-menu" @click="toggleUserMenu">
          <div class="user-avatar">
            <i class="fas fa-user-circle"></i>
          </div>
          <span class="user-name">{{ displayUserName }}</span>
          <i class="fas fa-chevron-down" :class="{ 'rotated': userMenuOpen }"></i>
        </div>
        
        <div v-if="userMenuOpen" class="user-dropdown">
          <div class="user-info-header">
            <div class="dropdown-avatar">
              <i class="fas fa-user-circle"></i>
            </div>
            <div class="dropdown-user-details">
              <div class="dropdown-name">{{ currentUser?.first_name }} {{ currentUser?.last_name }}</div>
              <div class="dropdown-username">{{ currentUser?.username }}</div>
              <div class="dropdown-email">{{ currentUser?.email }}</div>
            </div>
          </div>
          <div class="dropdown-divider"></div>
          <button @click="logout" class="logout-btn">
            <i class="fas fa-sign-out-alt"></i>
            Выйти
          </button>
        </div>
      </div>
      
      <div class="nav-links">
        <router-link to="/">Рабочие места</router-link>
        <router-link to="/computers">Компьютеры</router-link>
        <router-link to="/mfps">МФУ</router-link>
        <router-link to="/cartridges">Картриджи</router-link>
        <router-link to="/tvs">Телевизоры</router-link>
        <router-link to="/ups">ИБП</router-link>
        <router-link to="/employees">Сотрудники</router-link>
      </div>
    </nav>
    
    <div class="container">
      <router-view />
    </div>
    
    <!-- Модальное окно отчета -->
    <ReportModal v-model:visible="showReportModal" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { showWarning } from './utils/toast'
import ReportModal from './views/ReportModal.vue'

const router = useRouter()
const route = useRoute()
const API = '/api'

const searchQuery = ref('')
const showSuggestions = ref(false)
const suggestions = ref([])
const userMenuOpen = ref(false)
const currentUser = ref(null)
const showReportModal = ref(false)
let debounceTimer = null

// Вычисляемое свойство для отображения имени пользователя
const displayUserName = computed(() => {
  if (currentUser.value?.first_name && currentUser.value?.last_name) {
    return `${currentUser.value.first_name} ${currentUser.value.last_name}`
  }
  return currentUser.value?.username || 'Гость'
})

// Проверка авторизации
const isAuthenticated = () => {
  return !!currentUser.value
}

// Открытие модального окна отчета с проверкой авторизации
const openReportModal = () => {
  if (!isAuthenticated()) {
    showWarning('Для доступа к отчетам необходимо авторизоваться')
    router.push('/login')
    return
  }
  showReportModal.value = true
}

// Функция для получения подсказок
const fetchSuggestions = async (query) => {
  if (!query.trim()) {
    suggestions.value = []
    return
  }
  
  try {
    const response = await axios.get(`${API}/global-search/suggestions/`, {
      params: { q: query }
    })
    suggestions.value = response.data
  } catch (error) {
    console.error('Ошибка получения подсказок:', error)
    suggestions.value = []
  }
}

// Обработчик ввода с debounce
const onSearchInput = () => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchSuggestions(searchQuery.value)
  }, 300)
}

// Выбор подсказки
const selectSuggestion = (suggestion) => {
  searchQuery.value = suggestion.searchValue
  showSuggestions.value = false
  router.push({ name: 'GlobalSearch', query: { q: suggestion.searchValue } })
}

// Закрытие подсказок
const handleBlur = () => {
  setTimeout(() => {
    showSuggestions.value = false
  }, 200)
}

// Переход к поиску
const goToSearch = () => {
  if (searchQuery.value.trim()) {
    showSuggestions.value = false
    router.push({ name: 'GlobalSearch', query: { q: searchQuery.value } })
  }
}

// Переключение меню пользователя
const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
}

// Закрытие меню при клике вне его
const handleClickOutside = (event) => {
  const userMenu = document.querySelector('.user-menu')
  const dropdown = document.querySelector('.user-dropdown')
  if (userMenu && !userMenu.contains(event.target) && dropdown && !dropdown.contains(event.target)) {
    userMenuOpen.value = false
  }
}

// Выход из системы
const logout = async () => {
  try {
    await axios.post(`${API}/auth/logout/`)
    localStorage.removeItem('user')
    currentUser.value = null
    router.push('/login')
  } catch (error) {
    console.error('Ошибка выхода:', error)
    localStorage.removeItem('user')
    currentUser.value = null
    router.push('/login')
  }
}

// Загрузка текущего пользователя из localStorage
const loadCurrentUser = () => {
  const storedUser = localStorage.getItem('user')
  if (storedUser) {
    currentUser.value = JSON.parse(storedUser)
  } else {
    currentUser.value = null
  }
}

// Событие storage для синхронизации между вкладками
const handleStorageChange = (event) => {
  if (event.key === 'user') {
    loadCurrentUser()
  }
}

// Следим за изменением маршрута
watch(() => route.path, () => {
  loadCurrentUser()
  showSuggestions.value = false
  userMenuOpen.value = false
}, { immediate: true })

onMounted(() => {
  loadCurrentUser()
  document.addEventListener('click', handleClickOutside)
  window.addEventListener('storage', handleStorageChange)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  window.removeEventListener('storage', handleStorageChange)
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
  background: #f5f7fb;
  padding-top: 70px;
}

.navbar {
  background: #2c3e50;
  color: white;
  padding: 1rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
}

.search-container {
  position: relative;
  flex: 1;
  max-width: 500px;
}

.search-bar {
  display: flex;
  gap: 8px;
  width: 100%;
}

.global-search-input {
  flex: 1;
  padding: 8px 15px;
  border: none;
  border-radius: 20px;
  font-size: 0.9rem;
  outline: none;
}

.search-btn {
  background: #1abc9c;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 20px;
  cursor: pointer;
  transition: background 0.2s;
}

.search-btn:hover {
  background: #16a085;
}

/* Стили для подсказок */
.suggestions-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  max-height: 400px;
  overflow-y: auto;
  z-index: 1001;
  margin-top: 8px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 15px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid #eee;
}

.suggestion-item:hover {
  background: #f0f0f0;
}

.suggestion-icon {
  font-size: 1.2rem;
  min-width: 30px;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  font-size: 0.9rem;
  font-weight: 500;
  color: #2c3e50;
}

.suggestion-subtitle {
  font-size: 0.75rem;
  color: #999;
  margin-top: 2px;
}

.suggestion-type {
  font-size: 0.7rem;
  color: #1abc9c;
  background: #e8f5e9;
  padding: 2px 8px;
  border-radius: 12px;
}

/* Стили для правой части навигации */
.nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Кнопка отчета */
.report-btn {
  background: #f39c12;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.report-btn:hover {
  background: #e67e22;
  transform: translateY(-2px);
}

/* Стили для пользовательского меню */
.user-menu {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: 30px;
  background: rgba(255, 255, 255, 0.1);
  transition: background 0.2s;
}

.user-menu:hover {
  background: rgba(255, 255, 255, 0.2);
}

.user-avatar {
  font-size: 1.5rem;
  display: flex;
  align-items: center;
}

.user-name {
  font-size: 0.9rem;
  font-weight: 500;
}

.fa-chevron-down {
  font-size: 0.8rem;
  transition: transform 0.3s;
}

.fa-chevron-down.rotated {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 10px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  min-width: 280px;
  overflow: hidden;
  z-index: 1001;
  animation: fadeInDown 0.2s ease;
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.user-info-header {
  display: flex;
  gap: 15px;
  padding: 20px;
  background: linear-gradient(135deg, #1abc9c, #16a085);
}

.dropdown-avatar {
  font-size: 3rem;
  color: white;
}

.dropdown-user-details {
  flex: 1;
}

.dropdown-name {
  font-weight: bold;
  color: white;
  font-size: 1rem;
}

.dropdown-username {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
  margin-top: 2px;
}

.dropdown-email {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 2px;
}

.dropdown-divider {
  height: 1px;
  background: #eee;
  margin: 0;
}

.logout-btn {
  width: 100%;
  padding: 12px 20px;
  background: none;
  border: none;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: background 0.2s;
  font-size: 0.9rem;
  color: #e74c3c;
}

.logout-btn:hover {
  background: #fef5e7;
}

.nav-links {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: background 0.2s;
}

.nav-links a:hover, 
.nav-links a.router-link-active {
  background: #1abc9c;
}

.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
}

@media (max-width: 768px) {
  body {
    padding-top: 120px;
  }
  
  .navbar {
    flex-direction: column;
    text-align: center;
  }
  
  .search-container {
    max-width: 100%;
    width: 100%;
  }
  
  .nav-right {
    align-self: flex-end;
  }
  
  .user-dropdown {
    right: 0;
    left: auto;
  }
  
  .nav-links {
    justify-content: center;
  }
}
</style>