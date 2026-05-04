<template>
    <div class="page">
      <h1>📺 Телевизоры</h1>
  
      <!-- Форма добавления телевизора -->
      <div class="form-card">
        <h3>➕ Добавить телевизор</h3>
        
        <div class="form-group">
          <label>Номер основного средства:</label>
          <input 
            v-model="newTV.asset_number" 
            placeholder="Например: ТВ-001"
            class="main-field"
          >
          <small class="field-hint">По умолчанию: "не определен"</small>
        </div>
        
        <div class="form-group">
          <label>Марка телевизора:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="brandSearch" 
              @input="searchBrands" 
              @focus="searchBrands"
              placeholder="Введите марку телевизора для поиска..."
              class="search-input"
            >
            <div v-if="brandSearchResults.length" class="search-results">
              <div 
                v-for="tv in brandSearchResults" 
                :key="tv.id" 
                @click="selectBrand(tv)"
                class="search-result-item"
              >
                {{ tv.brand }}
              </div>
            </div>
          </div>
          <div v-if="selectedBrand" class="selected-tag">
            {{ selectedBrand.brand }}
            <button @click="selectedBrand = null" class="remove-btn">×</button>
          </div>
          <button @click="openAddBrandModal" type="button" class="small-btn">➕ Добавить новую марку</button>
        </div>
  
        <div class="form-group">
          <label>Диагональ (дюймы):</label>
          <input 
            v-model="newTV.size" 
            type="number" 
            step="0.1"
            placeholder="Например: 55"
            class="search-input"
          >
          <small class="field-hint">Введите число (например: 32, 43, 55, 65)</small>
        </div>
  
        <div class="form-group">
          <label>Место расположения (комментарий):</label>
          <textarea 
            v-model="newTV.location" 
            placeholder="Укажите где находится телевизор (кабинет, холл, конференц-зал и т.д.)..."
            rows="3"
            class="textarea-field"
          ></textarea>
          <small class="field-hint">Например: Конференц-зал, 3 этаж, кабинет 305 и т.д.</small>
        </div>
  
        <button @click="addTV" class="submit-btn">💾 Добавить телевизор</button>
      </div>
  
      <!-- Список телевизоров -->
      <div class="list">
        <h3>📋 Список телевизоров</h3>
        <div v-for="tv in tvs" :key="tv.id" class="card">
          <div class="card-header">
            <strong>ОС №{{ tv.asset_number || 'не определен' }}</strong>
            <div class="card-actions">
              <button @click="openEditModal(tv)" class="edit-btn">✏️ Редактировать</button>
              <button @click="deleteTV(tv.id)" class="delete-btn">🗑️ Удалить</button>
            </div>
          </div>
          <div class="card-body">
            <div>📺 Марка: <strong>{{ tv.brand }}</strong></div>
            <div>📏 Диагональ: <strong>{{ tv.size }}"</strong></div>
            <div v-if="tv.location" class="location-info">📍 Место: {{ tv.location }}</div>
            <div v-else class="no-data">📍 Место: не указано</div>
          </div>
        </div>
      </div>
  
      <!-- Модальное окно добавления новой марки -->
      <div v-if="showBrandModal" class="modal">
        <div class="modal-content">
          <h3>➕ Добавить новую марку телевизора</h3>
          <input v-model="newBrandName" placeholder="Марка телевизора">
          <div class="modal-buttons">
            <button @click="addBrand" class="save-btn">Сохранить</button>
            <button @click="showBrandModal = false" class="cancel-btn">Отмена</button>
          </div>
        </div>
      </div>
  
      <!-- Модальное окно редактирования -->
      <div v-if="showEditModal" class="modal">
        <div class="modal-content modal-large">
          <h3>✏️ Редактировать телевизор</h3>
          
          <div class="form-group">
            <label>Номер основного средства:</label>
            <input v-model="editTV.asset_number" class="main-field">
          </div>
          
          <div class="form-group">
            <label>Марка телевизора:</label>
            <select v-model="editTV.brand" class="search-input">
              <option :value="null">Выберите марку</option>
              <option v-for="brand in allBrands" :key="brand.id" :value="brand.brand">
                {{ brand.brand }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Диагональ (дюймы):</label>
            <input 
              v-model="editTV.size" 
              type="number" 
              step="0.1"
              placeholder="Например: 55"
              class="search-input"
            >
          </div>
          
          <div class="form-group">
            <label>Место расположения (комментарий):</label>
            <textarea 
              v-model="editTV.location" 
              placeholder="Укажите где находится телевизор..."
              rows="3"
              class="textarea-field"
            ></textarea>
          </div>
          
          <div class="modal-buttons">
            <button @click="updateTV" class="save-btn">💾 Сохранить</button>
            <button @click="showEditModal = false" class="cancel-btn">Отмена</button>
          </div>
        </div>
      </div>
  
      <!-- Модальное окно подтверждения удаления -->
      <ConfirmModal ref="confirmModal" />
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  import { showSuccess, showError, showWarning } from '../utils/toast'
  import ConfirmModal from '../components/ConfirmModal.vue'
  
  const API = '/api'
  
  // Данные
  const tvs = ref([])
  const allBrands = ref([])
  
  // Выбранные значения для добавления
  const selectedBrand = ref(null)
  
  // Поисковые запросы
  const brandSearch = ref('')
  const brandSearchResults = ref([])
  
  // Модальные окна
  const showBrandModal = ref(false)
  const showEditModal = ref(false)
  
  // Новые данные
  const newBrandName = ref('')
  
  // Данные для нового телевизора
  const newTV = ref({
    asset_number: 'не определен',
    size: '',
    location: ''
  })
  
  // Данные для редактирования
  const editTV = ref({
    id: null,
    asset_number: '',
    brand: null,
    size: '',
    location: ''
  })
  
  // Ref для модального окна подтверждения
  const confirmModal = ref(null)
  
  // Загрузка данных
  const fetchAllData = async () => {
    try {
      const [tvRes] = await Promise.all([
        axios.get(`${API}/tvs/`)
      ])
      tvs.value = tvRes.data
      
      // Извлекаем уникальные марки
      const uniqueBrands = []
      const brandMap = new Map()
      tvRes.data.forEach(tv => {
        if (!brandMap.has(tv.brand)) {
          brandMap.set(tv.brand, { id: tv.id, brand: tv.brand })
          uniqueBrands.push({ id: tv.id, brand: tv.brand })
        }
      })
      allBrands.value = uniqueBrands
    } catch (error) {
      console.error('Ошибка загрузки:', error)
      showError('Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message))
    }
  }
  
  // Поиск марок
  const searchBrands = () => {
    if (!brandSearch.value) {
      brandSearchResults.value = []
      return
    }
    brandSearchResults.value = allBrands.value.filter(b => 
      b.brand.toLowerCase().includes(brandSearch.value.toLowerCase())
    ).slice(0, 10)
  }
  
  // Выбор марки
  const selectBrand = (brand) => {
    selectedBrand.value = brand
    brandSearch.value = ''
    brandSearchResults.value = []
  }
  
  // Добавление телевизора
  const addTV = async () => {
    if (!selectedBrand.value) {
      showWarning('Пожалуйста, выберите или добавьте марку телевизора')
      return
    }
    
    if (!newTV.value.asset_number) {
      showWarning('Пожалуйста, укажите номер основного средства')
      return
    }
    
    if (!newTV.value.size) {
      showWarning('Пожалуйста, укажите диагональ')
      return
    }
    
    if (isNaN(newTV.value.size) || newTV.value.size <= 0) {
      showWarning('Пожалуйста, введите корректную диагональ')
      return
    }
    
    try {
      const tvData = {
        asset_number: newTV.value.asset_number,
        brand: selectedBrand.value.brand,
        size: parseFloat(newTV.value.size),
        location: newTV.value.location || null
      }
      
      await axios.post(`${API}/tvs/`, tvData)
      
      newTV.value = {
        asset_number: 'не определен',
        size: '',
        location: ''
      }
      selectedBrand.value = null
      brandSearch.value = ''
      
      await fetchAllData()
      showSuccess('Телевизор успешно добавлен!')
    } catch (error) {
      console.error('Ошибка добавления:', error)
      showError('Ошибка добавления телевизора: ' + (error.response?.data?.detail || error.message))
    }
  }
  
  // Открытие модального окна добавления марки
  const openAddBrandModal = () => {
    showBrandModal.value = true
    newBrandName.value = brandSearch.value
  }
  
  // Добавление новой марки
  const addBrand = async () => {
    if (!newBrandName.value.trim()) {
      showWarning('Введите марку телевизора')
      return
    }
    
    try {
      const tempTV = {
        asset_number: `TEMP-${Date.now()}`,
        brand: newBrandName.value,
        size: 0,
        location: null
      }
      
      const response = await axios.post(`${API}/tvs/`, tempTV)
      
      allBrands.value.push({ id: response.data.id, brand: newBrandName.value })
      selectedBrand.value = { id: response.data.id, brand: newBrandName.value }
      
      showBrandModal.value = false
      newBrandName.value = ''
      brandSearch.value = ''
      showSuccess('Марка добавлена!')
    } catch (error) {
      console.error('Ошибка добавления марки:', error)
      showError('Ошибка добавления марки')
    }
  }
  
  // Открытие модального окна редактирования
  const openEditModal = (tv) => {
    editTV.value = {
      id: tv.id,
      asset_number: tv.asset_number,
      brand: tv.brand,
      size: tv.size,
      location: tv.location || ''
    }
    showEditModal.value = true
  }
  
  // Обновление телевизора
  const updateTV = async () => {
    if (!editTV.value.brand) {
      showWarning('Пожалуйста, выберите марку телевизора')
      return
    }
    
    if (!editTV.value.size) {
      showWarning('Пожалуйста, укажите диагональ')
      return
    }
    
    if (isNaN(editTV.value.size) || editTV.value.size <= 0) {
      showWarning('Пожалуйста, введите корректную диагональ')
      return
    }
    
    try {
      const tvData = {
        asset_number: editTV.value.asset_number,
        brand: editTV.value.brand,
        size: parseFloat(editTV.value.size),
        location: editTV.value.location || null
      }
      
      await axios.put(`${API}/tvs/${editTV.value.id}/`, tvData)
      showEditModal.value = false
      await fetchAllData()
      showSuccess('Телевизор успешно обновлен!')
    } catch (error) {
      console.error('Ошибка обновления:', error)
      showError('Ошибка обновления телевизора: ' + (error.response?.data?.detail || error.message))
    }
  }
  
  // Удаление телевизора
  const deleteTV = async (id) => {
    const confirmed = await confirmModal.value.open({
      title: 'Удаление телевизора',
      message: 'Вы уверены, что хотите удалить этот телевизор? Это действие нельзя отменить.',
      confirmText: 'Да, удалить',
      type: 'danger'
    })
  
    if (confirmed) {
      try {
        await axios.delete(`${API}/tvs/${id}/`)
        await fetchAllData()
        showSuccess('Телевизор удален!')
      } catch (error) {
        console.error('Ошибка удаления:', error)
        showError('Ошибка удаления телевизора')
      }
    }
  }
  
  onMounted(fetchAllData)
  </script>
  
  <style scoped>
  .page {
    max-width: 1200px;
    margin: 0 auto;
  }
  
  h1 {
    color: #2c3e50;
    margin-bottom: 1.5rem;
  }
  
  .form-card {
    background: white;
    padding: 1.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  
  .form-card h3 {
    margin-bottom: 1rem;
    color: #2c3e50;
  }
  
  .form-group {
    margin-bottom: 1rem;
    position: relative;
  }
  
  .form-group label {
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
    color: #2c3e50;
    font-size: 0.95rem;
  }
  
  .main-field {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #1abc9c;
    border-radius: 8px;
    font-size: 1rem;
    font-weight: 500;
    background: #f8f9fa;
    transition: all 0.2s;
  }
  
  .main-field:focus {
    outline: none;
    background: white;
    border-color: #16a085;
    box-shadow: 0 0 0 3px rgba(26, 188, 156, 0.1);
  }
  
  .textarea-field {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    font-family: inherit;
    resize: vertical;
    transition: border-color 0.2s;
    line-height: 1.5;
  }
  
  .textarea-field:focus {
    outline: none;
    border-color: #1abc9c;
    box-shadow: 0 0 0 3px rgba(26, 188, 156, 0.1);
  }
  
  .field-hint {
    display: block;
    margin-top: 5px;
    font-size: 0.75rem;
    color: #999;
  }
  
  .search-input {
    width: 100%;
    padding: 12px 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
    transition: border-color 0.2s;
  }
  
  .search-input:focus {
    outline: none;
    border-color: #1abc9c;
    box-shadow: 0 0 0 3px rgba(26, 188, 156, 0.1);
  }
  
  .search-wrapper {
    position: relative;
  }
  
  .search-results {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #ddd;
    border-radius: 8px;
    max-height: 250px;
    overflow-y: auto;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }
  
  .search-result-item {
    padding: 12px 15px;
    cursor: pointer;
    border-bottom: 1px solid #eee;
    transition: background 0.2s;
  }
  
  .search-result-item:hover {
    background: #f0f0f0;
  }
  
  .selected-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #e8f5e9;
    padding: 8px 14px;
    border-radius: 20px;
    font-size: 0.95rem;
    font-weight: 500;
    margin-top: 8px;
  }
  
  .remove-btn {
    background: none;
    border: none;
    font-size: 1.3rem;
    cursor: pointer;
    color: #999;
    padding: 0 5px;
    line-height: 1;
  }
  
  .remove-btn:hover {
    color: #e74c3c;
  }
  
  .small-btn {
    background: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
    margin-top: 10px;
    transition: background 0.2s;
    display: inline-block;
  }
  
  .small-btn:hover {
    background: #2980b9;
  }
  
  .submit-btn {
    width: 100%;
    background: #1abc9c;
    color: white;
    border: none;
    padding: 14px;
    border-radius: 12px;
    font-size: 1.05rem;
    font-weight: bold;
    cursor: pointer;
    margin-top: 1rem;
    transition: background 0.2s;
  }
  
  .submit-btn:hover {
    background: #16a085;
  }
  
  .list {
    background: white;
    padding: 1.5rem;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  
  .list h3 {
    margin-bottom: 1.2rem;
    color: #2c3e50;
    font-size: 1.2rem;
  }
  
  .card {
    background: #f8f9fa;
    padding: 1.2rem;
    margin-bottom: 1rem;
    border-radius: 12px;
    border-left: 4px solid #1abc9c;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  
  .card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .card-header strong {
    font-size: 1.15rem;
    color: #2c3e50;
  }
  
  .card-body {
    color: #555;
    line-height: 1.7;
  }
  
  .card-body div {
    margin-bottom: 0.35rem;
  }
  
  .location-info {
    color: #2c3e50;
    background: #e8f5e9;
    padding: 4px 8px;
    border-radius: 6px;
    display: inline-block;
    margin-top: 4px;
  }
  
  .card-actions {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  
  .edit-btn, .delete-btn {
    padding: 5px 10px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: all 0.2s;
  }
  
  .edit-btn {
    background: #3498db;
    color: white;
  }
  
  .edit-btn:hover {
    background: #2980b9;
  }
  
  .delete-btn {
    background: #e74c3c;
    color: white;
  }
  
  .delete-btn:hover {
    background: #c0392b;
  }
  
  .no-data {
    color: #999;
    font-style: italic;
  }
  
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
  }
  
  .modal-content {
    background: white;
    padding: 2rem;
    border-radius: 16px;
    width: 90%;
    max-width: 500px;
    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
  }
  
  .modal-large {
    max-width: 600px !important;
  }
  
  .modal-content h3 {
    margin-bottom: 1.2rem;
    color: #2c3e50;
  }
  
  .modal-content input, .modal-content select, .modal-content textarea {
    width: 100%;
    margin-bottom: 1rem;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 1rem;
  }
  
  .modal-buttons {
    display: flex;
    gap: 1rem;
    justify-content: flex-end;
    margin-top: 1rem;
  }
  
  .save-btn {
    background: #1abc9c;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
  }
  
  .save-btn:hover {
    background: #16a085;
  }
  
  .cancel-btn {
    background: #e74c3c;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
  }
  
  .cancel-btn:hover {
    background: #c0392b;
  }
  
  @media (max-width: 768px) {
    .card-header {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .card-actions {
      width: 100%;
      justify-content: flex-end;
    }
    
    .modal-content {
      padding: 1.5rem;
      margin: 1rem;
    }
  }
  </style>