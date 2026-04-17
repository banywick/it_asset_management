<template>
  <div id="app">
    <nav class="navbar">
      <div class="nav-brand">IT Asset Tracker</div>
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          @keyup.enter="goToSearch"
          placeholder="🔍 Глобальный поиск..."
          class="global-search-input"
        >
        <button @click="goToSearch" class="search-btn">🔍</button>
      </div>
      <div class="nav-links">
        <router-link to="/">Рабочие места</router-link>
        <router-link to="/computers">Компьютеры</router-link>
        <router-link to="/mfps">МФУ</router-link>
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
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchQuery = ref('')

const goToSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ name: 'GlobalSearch', query: { q: searchQuery.value } })
  }
}
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
}

.nav-brand {
  font-size: 1.5rem;
  font-weight: bold;
}

.search-bar {
  display: flex;
  gap: 8px;
  flex: 1;
  max-width: 400px;
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
  .navbar {
    flex-direction: column;
    text-align: center;
  }
  
  .search-bar {
    max-width: 100%;
    width: 100%;
  }
  
  .nav-links {
    justify-content: center;
  }
}
</style>