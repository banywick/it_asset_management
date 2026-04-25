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
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const API = 'http://localhost:8000/api'

const searchQuery = ref('')
const showSuggestions = ref(false)
const suggestions = ref([])
let debounceTimer = null

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

// Следим за изменением маршрута
watch(() => router.currentRoute.value.path, () => {
  showSuggestions.value = false
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
  
  .nav-links {
    justify-content: center;
  }
}
</style>