<template>
  <div class="page">
    <h1>🖨️ МФУ (Многофункциональные устройства)</h1>

    <!-- Форма добавления МФУ -->
    <div class="form-card">
      <h3>➕ Добавить МФУ</h3>
      
      <div class="form-row">
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
          <input 
            v-model="newMFP.model" 
            placeholder="Модель МФУ"
            class="search-input"
          >
        </div>
      </div>

      <div class="form-group">
        <label>IP адрес (необязательно):</label>
        <input 
          v-model="newMFP.ip_address" 
          placeholder="Например: 192.168.1.100"
          class="search-input ip-input"
        >
        <small class="field-hint">Формат: XXX.XXX.XXX.XXX (например: 10.10.29.25)</small>
      </div>

      <button @click="addMFP" class="submit-btn">💾 Добавить МФУ</button>
    </div>

    <!-- Список МФУ -->
    <div class="list">
      <h3>📋 Список МФУ ({{ mfps.length }} шт.)</h3>
      <div class="cards-grid">
        <div v-for="mfp in paginatedMFPs" :key="mfp.id" class="card">
          <div class="card-header">
            <strong>ОС №{{ mfp.asset_number }}</strong>
            <div class="card-actions">
              <button @click="openEditModal(mfp)" class="edit-btn" title="Редактировать">✏️</button>
              <button @click="deleteMFP(mfp.id)" class="delete-btn" title="Удалить">🗑️</button>
            </div>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="label">📠 Модель:</span>
              <span class="value">{{ mfp.model }}</span>
            </div>
            <div class="info-row">
              <span class="label">🌐 IP адрес:</span>
              <span class="value">
                <code class="ip-address">{{ mfp.ip_address || 'не указан' }}</code>
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Пагинация -->
      <div v-if="totalPages > 1" class="pagination">
        <button @click="prevPage" :disabled="currentPage === 1" class="page-btn">◀ Предыдущая</button>
        <span class="page-info">Страница {{ currentPage }} из {{ totalPages }}</span>
        <button @click="nextPage" :disabled="currentPage === totalPages" class="page-btn">Следующая ▶</button>
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
        
        <!-- Модель МФУ с поиском -->
        <div class="form-group">
          <label>Модель МФУ:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="modelSearch" 
              @input="searchModels" 
              @focus="searchModels"
              placeholder="Введите модель МФУ..."
              class="search-input"
            >
            <div v-if="modelSearchResults.length" class="search-results">
              <div 
                v-for="m in modelSearchResults" 
                :key="m.id" 
                @click="selectModel(m)"
                class="search-result-item"
              >
                {{ m.model }}
              </div>
            </div>
          </div>
          <div v-if="selectedModel" class="selected-tag">
            {{ selectedModel.model }}
            <button @click="selectedModel = null" class="remove-btn">×</button>
          </div>
        </div>
        
        <div class="form-group">
          <label>IP адрес:</label>
          <input 
            v-model="editMFP.ip_address" 
            placeholder="192.168.1.100"
            class="search-input ip-input"
          >
        </div>
        
        <div class="modal-buttons">
          <button @click="updateMFP" class="save-btn">💾 Сохранить</button>
          <button @click="closeEditModal" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно подтверждения удаления -->
    <ConfirmModal ref="confirmModal" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { showSuccess, showError, showWarning } from '../utils/toast'
import ConfirmModal from '../components/ConfirmModal.vue'

const API = 'http://localhost:8000/api'

const mfps = ref([])

// Пагинация
const currentPage = ref(1)
const itemsPerPage = 6

// Модальные окна
const showEditModal = ref(false)

// Данные для нового МФУ
const newMFP = ref({
  asset_number: 'не определен',
  model: '',
  ip_address: ''
})

// Данные для редактирования
const editMFP = ref({
  id: null,
  asset_number: '',
  model: '',
  ip_address: ''
})

// Поиск моделей
const modelSearch = ref('')
const modelSearchResults = ref([])
const selectedModel = ref(null)

// Список всех уникальных моделей для поиска
const allModels = computed(() => {
  const uniqueModels = []
  const modelMap = new Map()
  mfps.value.forEach(mfp => {
    if (!modelMap.has(mfp.model)) {
      modelMap.set(mfp.model, { id: mfp.id, model: mfp.model })
      uniqueModels.push({ id: mfp.id, model: mfp.model })
    }
  })
  return uniqueModels
})

// Пагинированные МФУ
const paginatedMFPs = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return mfps.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(mfps.value.length / itemsPerPage)
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

// Пагинация
const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

// Загрузка данных
const fetchAllData = async () => {
  try {
    const mfpRes = await axios.get(`${API}/mfps/`)
    mfps.value = mfpRes.data
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    showError('Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message))
  }
}

// Поиск моделей для редактирования
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
  editMFP.value.model = model.model
  modelSearch.value = ''
  modelSearchResults.value = []
}

// Добавление МФУ
const addMFP = async () => {
  if (!newMFP.value.model) {
    showWarning('Пожалуйста, укажите модель МФУ')
    return
  }
  
  if (newMFP.value.ip_address && !isValidIP(newMFP.value.ip_address)) {
    showWarning('Пожалуйста, введите корректный IP адрес (формат: 192.168.1.100)')
    return
  }
  
  try {
    const mfpData = {
      asset_number: newMFP.value.asset_number || 'не определен',
      model: newMFP.value.model,
      ip_address: newMFP.value.ip_address || null
    }
    
    await axios.post(`${API}/mfps/`, mfpData)
    
    newMFP.value = {
      asset_number: 'не определен',
      model: '',
      ip_address: ''
    }
    
    await fetchAllData()
    currentPage.value = Math.ceil(mfps.value.length / itemsPerPage)
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
    ip_address: mfp.ip_address || ''
  }
  selectedModel.value = { id: mfp.id, model: mfp.model }
  modelSearch.value = ''
  modelSearchResults.value = []
  showEditModal.value = true
}

// Закрытие модального окна редактирования
const closeEditModal = () => {
  showEditModal.value = false
  editMFP.value = {
    id: null,
    asset_number: '',
    model: '',
    ip_address: ''
  }
  selectedModel.value = null
  modelSearch.value = ''
  modelSearchResults.value = []
}

// Обновление МФУ
const updateMFP = async () => {
  if (!editMFP.value.model) {
    showWarning('Пожалуйста, укажите модель МФУ')
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
      ip_address: editMFP.value.ip_address || null
    }
    
    await axios.put(`${API}/mfps/${editMFP.value.id}/`, mfpData)
    closeEditModal()
    await fetchAllData()
    showSuccess('МФУ успешно обновлено!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления МФУ: ' + (error.response?.data?.detail || error.message))
  }
}

// Удаление МФУ
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
      if (paginatedMFPs.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
      showSuccess('МФУ удалено!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления МФУ')
    }
  }
}

onMounted(() => {
  fetchAllData()
})
</script>

<style scoped>
.page {
  max-width: 1400px;
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

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.form-row .form-group {
  flex: 1;
  margin-bottom: 0;
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

.ip-input {
  font-family: 'Courier New', monospace;
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

.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

@media (max-width: 1000px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}

.card {
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #1abc9c;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 15px;
  background: rgba(26, 188, 156, 0.1);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.card-header strong {
  font-size: 1rem;
  color: #2c3e50;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.edit-btn, .delete-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 5px;
  border-radius: 6px;
  transition: all 0.2s;
}

.edit-btn {
  color: #3498db;
}

.edit-btn:hover {
  background: #3498db;
  color: white;
}

.delete-btn {
  color: #e74c3c;
}

.delete-btn:hover {
  background: #e74c3c;
  color: white;
}

.card-body {
  padding: 12px 15px;
}

.info-row {
  margin-bottom: 8px;
  font-size: 0.85rem;
  line-height: 1.4;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
}

.label {
  font-weight: 600;
  color: #666;
  min-width: 80px;
  flex-shrink: 0;
}

.value {
  color: #333;
}

.ip-address {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.page-btn {
  background: #3498db;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #2980b9;
}

.page-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 0.9rem;
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
  .form-row {
    flex-direction: column;
  }
  
  .form-row .form-group {
    margin-bottom: 1rem;
  }
  
  .modal-content {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .pagination {
    flex-wrap: wrap;
  }
}
</style>