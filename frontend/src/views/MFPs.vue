<template>
    <div class="page">
      <h1>🖨️ МФУ (Многофункциональные устройства)</h1>
  
      <!-- Форма добавления МФУ -->
      <div class="form-card">
        <h3>➕ Добавить МФУ</h3>
        
        <div class="form-group">
          <label>Номер основного средства:</label>
          <input 
            v-model="newMFP.asset_number" 
            placeholder="Например: МФУ-001"
            class="main-field"
          >
          <small class="field-hint">По умолчанию: "не определен"</small>
        </div>
        
        <div class="form-group">
          <label>Модель МФУ:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="modelSearch" 
              @input="searchModels" 
              @focus="searchModels"
              placeholder="Введите модель МФУ для поиска..."
              class="search-input"
            >
            <div v-if="modelSearchResults.length" class="search-results">
              <div 
                v-for="mfp in modelSearchResults" 
                :key="mfp.id" 
                @click="selectModel(mfp)"
                class="search-result-item"
              >
                {{ mfp.model }}
              </div>
            </div>
          </div>
          <div v-if="selectedModel" class="selected-tag">
            {{ selectedModel.model }}
            <button @click="selectedModel = null" class="remove-btn">×</button>
          </div>
          <button @click="openAddModelModal" type="button" class="small-btn">➕ Добавить новую модель</button>
        </div>
  
        <!-- Отдел - выпадающий список из базы -->
        <div class="form-group">
          <label>Отдел:</label>
          <select v-model="newMFP.department" class="search-input">
            <option :value="null">Без отдела</option>
            <option v-for="dep in allDepartments" :key="dep.id" :value="dep.id">
              {{ dep.name }}
            </option>
          </select>
          <button @click="openAddDepartmentModal" type="button" class="small-btn">➕ Добавить новый отдел</button>
        </div>
  
        <!-- IP адрес - без маски, с простым вводом -->
        <div class="form-group">
          <label>IP адрес (необязательно):</label>
          <input 
            v-model="newMFP.ip_address" 
            placeholder="192.168.1.100"
            class="search-input ip-input"
            @input="validateIP"
          >
          <small class="field-hint">Формат: XXX.XXX.XXX.XXX (например: 10.10.29.25)</small>
          <div v-if="ipError" class="error-message">{{ ipError }}</div>
        </div>
  
        <button @click="addMFP" class="submit-btn">💾 Добавить МФУ</button>
      </div>
  
      <!-- Список МФУ -->
      <div class="list">
        <h3>📋 Список МФУ</h3>
        <div v-for="mfp in mfps" :key="mfp.id" class="card">
          <div class="card-header">
            <strong>ОС №{{ mfp.asset_number }}</strong>
            <div class="card-actions">
              <button @click="openEditModal(mfp)" class="edit-btn">✏️ Редактировать</button>
              <button @click="deleteMFP(mfp.id)" class="delete-btn">🗑️ Удалить</button>
            </div>
          </div>
          <div class="card-body">
            <div>📠 Модель: <strong>{{ mfp.model }}</strong></div>
            <div>📍 Отдел: {{ mfp.department_name || 'Не указан' }}</div>
            <div>🌐 IP адрес: <code class="ip-address">{{ mfp.ip_address || 'не указан' }}</code></div>
          </div>
        </div>
      </div>
  
      <!-- Модальные окна (остаются без изменений) -->
      <div v-if="showModelModal" class="modal">
        <div class="modal-content">
          <h3>➕ Добавить новую модель МФУ</h3>
          <input v-model="newModelName" placeholder="Модель МФУ">
          <div class="modal-buttons">
            <button @click="addModel" class="save-btn">Сохранить</button>
            <button @click="showModelModal = false" class="cancel-btn">Отмена</button>
          </div>
        </div>
      </div>
  
      <div v-if="showDepartmentModal" class="modal">
        <div class="modal-content">
          <h3>➕ Добавить новый отдел</h3>
          <input v-model="newDepartmentName" placeholder="Название отдела">
          <div class="modal-buttons">
            <button @click="addDepartment" class="save-btn">Сохранить</button>
            <button @click="showDepartmentModal = false" class="cancel-btn">Отмена</button>
          </div>
        </div>
      </div>
  
      <!-- Модальное окно редактирования -->
      <div v-if="showEditModal" class="modal">
        <div class="modal-content modal-large">
          <h3>✏️ Редактировать МФУ</h3>
          
          <div class="form-group">
            <label>Номер основного средства:</label>
            <input v-model="editMFP.asset_number" class="main-field">
          </div>
          
          <div class="form-group">
            <label>Модель МФУ:</label>
            <select v-model="editMFP.model" class="search-input">
              <option :value="null">Выберите модель</option>
              <option v-for="model in allModels" :key="model.id" :value="model.model">
                {{ model.model }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Отдел:</label>
            <select v-model="editMFP.department" class="search-input">
              <option :value="null">Без отдела</option>
              <option v-for="dep in allDepartments" :key="dep.id" :value="dep.id">
                {{ dep.name }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label>IP адрес:</label>
            <input 
              v-model="editMFP.ip_address" 
              placeholder="192.168.1.100"
              class="search-input ip-input"
              @input="validateEditIP"
            >
            <div v-if="editIpError" class="error-message">{{ editIpError }}</div>
          </div>
          
          <div class="modal-buttons">
            <button @click="updateMFP" class="save-btn">💾 Сохранить</button>
            <button @click="showEditModal = false" class="cancel-btn">Отмена</button>
          </div>
        </div>
      </div>
    </div>
    <!-- Модальное окно подтверждения удаления -->
    <ConfirmModal ref="confirmModal" />
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  import { showSuccess, showError, showWarning } from '../utils/toast'
  
  const API = 'http://localhost:8000/api'
  
  // Данные
  const mfps = ref([])
  const allModels = ref([])
  const allDepartments = ref([])
  
  // Выбранные значения для добавления
  const selectedModel = ref(null)
  
  // Поисковые запросы
  const modelSearch = ref('')
  const modelSearchResults = ref([])
  
  // Модальные окна
  const showModelModal = ref(false)
  const showDepartmentModal = ref(false)
  const showEditModal = ref(false)
  
  // Новые данные
  const newModelName = ref('')
  const newDepartmentName = ref('')
  
  // Ошибки IP
  const ipError = ref('')
  const editIpError = ref('')
  
  // Данные для нового МФУ
  const newMFP = ref({
    asset_number: 'не определен',
    department: null,
    ip_address: ''
  })
  
  // Данные для редактирования
  const editMFP = ref({
    id: null,
    asset_number: '',
    model: null,
    department: null,
    ip_address: ''
  })
  
  // Валидация IP адреса
  const isValidIP = (ip) => {
    if (!ip) return true
    const ipRegex = /^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$/
    if (!ipRegex.test(ip)) return false
    const parts = ip.split('.')
    for (let part of parts) {
      const num = parseInt(part, 10)
      if (isNaN(num) || num < 0 || num > 255) return false
    }
    return true
  }
  
  const validateIP = () => {
    if (newMFP.value.ip_address && !isValidIP(newMFP.value.ip_address)) {
      ipError.value = 'Неверный формат IP адреса. Используйте формат: 192.168.1.100'
    } else {
      ipError.value = ''
    }
  }
  
  const validateEditIP = () => {
    if (editMFP.value.ip_address && !isValidIP(editMFP.value.ip_address)) {
      editIpError.value = 'Неверный формат IP адреса. Используйте формат: 192.168.1.100'
    } else {
      editIpError.value = ''
    }
  }
  
  // Загрузка данных
  const fetchAllData = async () => {
    try {
      const [mfpRes, depRes] = await Promise.all([
        axios.get(`${API}/mfps/`),
        axios.get(`${API}/departments/`)
      ])
      mfps.value = mfpRes.data
      allDepartments.value = depRes.data
      
      // Извлекаем уникальные модели
      const uniqueModels = []
      const modelMap = new Map()
      mfpRes.data.forEach(mfp => {
        if (!modelMap.has(mfp.model)) {
          modelMap.set(mfp.model, { id: mfp.id, model: mfp.model })
          uniqueModels.push({ id: mfp.id, model: mfp.model })
        }
      })
      allModels.value = uniqueModels
    } catch (error) {
      console.error('Ошибка загрузки:', error)
      showError('Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message))
    }
  }
  
  // Поиск моделей
  const searchModels = () => {
    if (!modelSearch.value) {
      modelSearchResults.value = []
      return
    }
    modelSearchResults.value = allModels.value.filter(m => 
      m.model.toLowerCase().includes(modelSearch.value.toLowerCase())
    ).slice(0, 10)
  }
  
  // Выбор модели
  const selectModel = (model) => {
    selectedModel.value = model
    modelSearch.value = ''
    modelSearchResults.value = []
  }
  
  // Добавление МФУ
  const addMFP = async () => {
    if (!selectedModel.value) {
      showWarning('Пожалуйста, выберите или добавьте модель МФУ')
      return
    }
    
    if (!newMFP.value.asset_number) {
      showWarning('Пожалуйста, укажите номер основного средства')
      return
    }
    
    if (newMFP.value.ip_address && !isValidIP(newMFP.value.ip_address)) {
      showWarning('Пожалуйста, введите корректный IP адрес (формат: 192.168.1.100)')
      return
    }
    
    try {
      const mfpData = {
        asset_number: newMFP.value.asset_number,
        model: selectedModel.value.model,
        department: newMFP.value.department || null,
        ip_address: newMFP.value.ip_address || null
      }
      
      await axios.post(`${API}/mfps/`, mfpData)
      
      newMFP.value = {
        asset_number: 'не определен',
        department: null,
        ip_address: ''
      }
      selectedModel.value = null
      modelSearch.value = ''
      ipError.value = ''
      
      await fetchAllData()
      showSuccess('МФУ успешно добавлено!')
    } catch (error) {
      console.error('Ошибка добавления:', error)
      showError('Ошибка добавления МФУ: ' + (error.response?.data?.detail || error.message))
    }
  }
  
  // Открытие модального окна редактирования
  const openEditModal = (mfp) => {
    editMFP.value = {
      id: mfp.id,
      asset_number: mfp.asset_number,
      model: mfp.model,
      department: mfp.department,
      ip_address: mfp.ip_address || ''
    }
    editIpError.value = ''
    showEditModal.value = true
  }
  
  // Обновление МФУ
  const updateMFP = async () => {
    if (!editMFP.value.model) {
      showWarning('Пожалуйста, выберите модель МФУ')
      return
    }
    
    if (editMFP.value.ip_address && !isValidIP(editMFP.value.ip_address)) {
      showWarning('Пожалуйста, введите корректный IP адрес (формат: 192.168.1.100)')
      return
    }
    
    try {
      const mfpData = {
        asset_number: editMFP.value.asset_number,
        model: editMFP.value.model,
        department: editMFP.value.department,
        ip_address: editMFP.value.ip_address || null
      }
      
      await axios.put(`${API}/mfps/${editMFP.value.id}/`, mfpData)
      showEditModal.value = false
      await fetchAllData()
      showSuccess('МФУ успешно обновлено!')
    } catch (error) {
      console.error('Ошибка обновления:', error)
      showError('Ошибка обновления МФУ: ' + (error.response?.data?.detail || error.message))
    }
  }
  

  
  // Добавление модели
  const openAddModelModal = () => {
    showModelModal.value = true
    newModelName.value = modelSearch.value
  }
  
  const addModel = async () => {
    if (!newModelName.value.trim()) {
      showWarning('Введите модель МФУ')
      return
    }
    
    try {
      const tempMFP = {
        asset_number: `TEMP-${Date.now()}`,
        model: newModelName.value,
        department: null,
        ip_address: null
      }
      
      const response = await axios.post(`${API}/mfps/`, tempMFP)
      allModels.value.push({ id: response.data.id, model: newModelName.value })
      selectedModel.value = { id: response.data.id, model: newModelName.value }
      
      showModelModal.value = false
      newModelName.value = ''
      modelSearch.value = ''
      showSuccess('Модель добавлена!')
    } catch (error) {
      console.error('Ошибка добавления модели:', error)
      showError('Ошибка добавления модели')
    }
  }
  
  // Добавление отдела
  const openAddDepartmentModal = () => {
    showDepartmentModal.value = true
    newDepartmentName.value = ''
  }
  
  const addDepartment = async () => {
    if (!newDepartmentName.value.trim()) {
      showWarning('Введите название отдела')
      return
    }
    
    try {
      const response = await axios.post(`${API}/departments/`, { name: newDepartmentName.value })
      await fetchAllData()
      newMFP.value.department = response.data.id
      showDepartmentModal.value = false
      newDepartmentName.value = ''
      showSuccess('Отдел добавлен!')
    } catch (error) {
      console.error('Ошибка добавления отдела:', error)
      showError('Ошибка добавления отдела')
    }
  }

  import ConfirmModal from '../components/ConfirmModal.vue'

const confirmModal = ref(null)

const deleteMFP = async (id) => {
  const confirmed = await confirmModal.value.open({
    title: 'Удаление МФУ',
    message: 'Вы уверены, что хотите удалить это МФУ? Это действие нельзя отменить.',
    confirmText: 'Да, удалить',
    type: 'danger'
  })
  
  if (confirmed) {
    try {
      await axios.delete(`${API}/mfps/${id}/`)
      await fetchAllData()
      showSuccess('МФУ удалено!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления МФУ')
    }
  }
}
  
  



  onMounted(fetchAllData)
  </script>
  
  <style scoped>
  /* Все стили остаются как в предыдущей версии, добавляем только ошибки */
  .error-message {
    color: #e74c3c;
    font-size: 0.75rem;
    margin-top: 5px;
  }
  
  /* Остальные стили из предыдущей версии */
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
  
  .ip-input {
    font-family: 'Courier New', monospace;
    font-size: 1rem;
    letter-spacing: 0.5px;
  }
  
  .ip-address {
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
    color: #2c3e50;
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
  
  .modal-content input, .modal-content select {
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