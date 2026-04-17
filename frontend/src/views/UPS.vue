<template>
  <div class="page">
    <h1>🔋 ИБП (бесперебойники)</h1>

    <!-- Форма добавления ИБП -->
    <div class="form-card">
      <h3>➕ Добавить ИБП</h3>
      
      <div class="form-group">
        <label>Номер основного средства:</label>
        <input 
          v-model="newUPS.asset_number" 
          placeholder="Например: ИБП-001"
          class="main-field"
        >
        <small class="field-hint">По умолчанию: "не определен"</small>
      </div>
      
      <div class="form-group">
        <label>Модель ИБП:</label>
        <div class="search-wrapper">
          <input 
            type="text" 
            v-model="modelSearch" 
            @input="searchModels" 
            @focus="searchModels"
            placeholder="Введите модель ИБП для поиска..."
            class="search-input"
          >
          <div v-if="modelSearchResults.length" class="search-results">
            <div 
              v-for="ups in modelSearchResults" 
              :key="ups.id" 
              @click="selectModel(ups)"
              class="search-result-item"
            >
              {{ ups.model }}
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
        <select v-model="newUPS.department" class="search-input">
          <option :value="null">Без отдела</option>
          <option v-for="dep in allDepartments" :key="dep.id" :value="dep.id">
            {{ dep.name }}
          </option>
        </select>
        <button @click="openAddDepartmentModal" type="button" class="small-btn">➕ Добавить новый отдел</button>
      </div>

      <div class="form-group">
        <label>Серийный номер аккумулятора (необязательно):</label>
        <input 
          v-model="newUPS.battery_serial_number" 
          placeholder="Например: BAT-2024-001"
          class="search-input"
        >
      </div>

      <div class="form-group">
        <label>Дата замены аккумулятора:</label>
        <input 
          v-model="newUPS.battery_replaced_at" 
          type="date"
          class="search-input"
        >
        <small class="field-hint">Укажите дату последней замены аккумулятора</small>
      </div>

      <div class="form-group">
        <label>Комментарий:</label>
        <textarea 
          v-model="newUPS.comment" 
          placeholder="Дополнительная информация о ИБП..."
          rows="3"
          class="textarea-field"
        ></textarea>
        <small class="field-hint">Место расположения, особенности и т.д.</small>
      </div>

      <button @click="addUPS" class="submit-btn">💾 Добавить ИБП</button>
    </div>

    <!-- Список ИБП -->
    <div class="list">
      <h3>📋 Список ИБП</h3>
      <div v-for="ups in upsList" :key="ups.id" class="card">
        <div class="card-header">
          <strong>ОС №{{ ups.asset_number }}</strong>
          <div class="card-actions">
            <button @click="openEditModal(ups)" class="edit-btn">✏️ Редактировать</button>
            <button @click="deleteUPS(ups.id)" class="delete-btn">🗑️ Удалить</button>
          </div>
        </div>
        <div class="card-body">
          <div>🔋 Модель: <strong>{{ ups.model }}</strong></div>
          <div>📍 Отдел: {{ ups.department_name || 'Не указан' }}</div>
          <div v-if="ups.battery_serial_number">🔧 Аккумулятор: {{ ups.battery_serial_number }}</div>
          <div v-if="ups.battery_replaced_at">📅 Замена аккумулятора: {{ formatDate(ups.battery_replaced_at) }}</div>
          <div v-if="ups.comment" class="comment-info">💬 {{ ups.comment }}</div>
        </div>
      </div>
    </div>

    <!-- Модальное окно добавления новой модели -->
    <div v-if="showModelModal" class="modal">
      <div class="modal-content">
        <h3>➕ Добавить новую модель ИБП</h3>
        <input v-model="newModelName" placeholder="Модель ИБП">
        <div class="modal-buttons">
          <button @click="addModel" class="save-btn">Сохранить</button>
          <button @click="showModelModal = false" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно добавления отдела -->
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
        <h3>✏️ Редактировать ИБП</h3>
        
        <div class="form-group">
          <label>Номер основного средства:</label>
          <input v-model="editUPS.asset_number" class="main-field">
        </div>
        
        <div class="form-group">
          <label>Модель ИБП:</label>
          <select v-model="editUPS.model" class="search-input">
            <option :value="null">Выберите модель</option>
            <option v-for="model in allModels" :key="model.id" :value="model.model">
              {{ model.model }}
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Отдел:</label>
          <select v-model="editUPS.department" class="search-input">
            <option :value="null">Без отдела</option>
            <option v-for="dep in allDepartments" :key="dep.id" :value="dep.id">
              {{ dep.name }}
            </option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Серийный номер аккумулятора:</label>
          <input v-model="editUPS.battery_serial_number" class="search-input">
        </div>
        
        <div class="form-group">
          <label>Дата замены аккумулятора:</label>
          <input v-model="editUPS.battery_replaced_at" type="date" class="search-input">
        </div>
        
        <div class="form-group">
          <label>Комментарий:</label>
          <textarea 
            v-model="editUPS.comment" 
            placeholder="Дополнительная информация..."
            rows="3"
            class="textarea-field"
          ></textarea>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateUPS" class="save-btn">💾 Сохранить</button>
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

const API = 'http://localhost:8000/api'

// Данные
const upsList = ref([])
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

// Данные для нового ИБП
const newUPS = ref({
  asset_number: 'не определен',
  department: null,
  battery_serial_number: '',
  battery_replaced_at: '',
  comment: ''
})

// Данные для редактирования
const editUPS = ref({
  id: null,
  asset_number: '',
  model: null,
  department: null,
  battery_serial_number: '',
  battery_replaced_at: '',
  comment: ''
})

// Ref для модального окна подтверждения
const confirmModal = ref(null)

// Форматирование даты
const formatDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  return d.toLocaleDateString('ru-RU')
}

// Загрузка данных
const fetchAllData = async () => {
  try {
    const [upsRes, depRes] = await Promise.all([
      axios.get(`${API}/ups/`),
      axios.get(`${API}/departments/`)
    ])
    upsList.value = upsRes.data
    allDepartments.value = depRes.data
    
    // Извлекаем уникальные модели из существующих ИБП
    const uniqueModels = []
    const modelMap = new Map()
    upsRes.data.forEach(ups => {
      if (!modelMap.has(ups.model)) {
        modelMap.set(ups.model, { id: ups.id, model: ups.model })
        uniqueModels.push({ id: ups.id, model: ups.model })
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

// Добавление ИБП
const addUPS = async () => {
  if (!selectedModel.value) {
    showWarning('Пожалуйста, выберите или добавьте модель ИБП')
    return
  }
  
  if (!newUPS.value.asset_number) {
    showWarning('Пожалуйста, укажите номер основного средства')
    return
  }
  
  try {
    const upsData = {
      asset_number: newUPS.value.asset_number,
      model: selectedModel.value.model,
      department: newUPS.value.department || null,
      battery_serial_number: newUPS.value.battery_serial_number || null,
      battery_replaced_at: newUPS.value.battery_replaced_at || null,
      comment: newUPS.value.comment || null
    }
    
    await axios.post(`${API}/ups/`, upsData)
    
    // Сброс формы
    newUPS.value = {
      asset_number: 'не определен',
      department: null,
      battery_serial_number: '',
      battery_replaced_at: '',
      comment: ''
    }
    selectedModel.value = null
    modelSearch.value = ''
    
    await fetchAllData()
    showSuccess('ИБП успешно добавлен!')
  } catch (error) {
    console.error('Ошибка добавления:', error)
    showError('Ошибка добавления ИБП: ' + (error.response?.data?.detail || error.message))
  }
}

// Открытие модального окна добавления модели
const openAddModelModal = () => {
  showModelModal.value = true
  newModelName.value = modelSearch.value
}

// Добавление новой модели
const addModel = async () => {
  if (!newModelName.value.trim()) {
    showWarning('Введите модель ИБП')
    return
  }
  
  try {
    const tempUPS = {
      asset_number: `TEMP-${Date.now()}`,
      model: newModelName.value,
      department: null,
      battery_serial_number: null,
      battery_replaced_at: null,
      comment: null
    }
    
    const response = await axios.post(`${API}/ups/`, tempUPS)
    
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

// Открытие модального окна добавления отдела
const openAddDepartmentModal = () => {
  showDepartmentModal.value = true
  newDepartmentName.value = ''
}

// Добавление отдела
const addDepartment = async () => {
  if (!newDepartmentName.value.trim()) {
    showWarning('Введите название отдела')
    return
  }
  
  try {
    const response = await axios.post(`${API}/departments/`, { name: newDepartmentName.value })
    await fetchAllData()
    newUPS.value.department = response.data.id
    showDepartmentModal.value = false
    newDepartmentName.value = ''
    showSuccess('Отдел добавлен!')
  } catch (error) {
    console.error('Ошибка добавления отдела:', error)
    showError('Ошибка добавления отдела')
  }
}

// Открытие модального окна редактирования
const openEditModal = (ups) => {
  editUPS.value = {
    id: ups.id,
    asset_number: ups.asset_number,
    model: ups.model,
    department: ups.department,
    battery_serial_number: ups.battery_serial_number || '',
    battery_replaced_at: ups.battery_replaced_at || '',
    comment: ups.comment || ''
  }
  showEditModal.value = true
}

// Обновление ИБП
const updateUPS = async () => {
  if (!editUPS.value.model) {
    showWarning('Пожалуйста, выберите модель ИБП')
    return
  }
  
  try {
    const upsData = {
      asset_number: editUPS.value.asset_number,
      model: editUPS.value.model,
      department: editUPS.value.department,
      battery_serial_number: editUPS.value.battery_serial_number || null,
      battery_replaced_at: editUPS.value.battery_replaced_at || null,
      comment: editUPS.value.comment || null
    }
    
    await axios.put(`${API}/ups/${editUPS.value.id}/`, upsData)
    showEditModal.value = false
    await fetchAllData()
    showSuccess('ИБП успешно обновлен!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления ИБП: ' + (error.response?.data?.detail || error.message))
  }
}

// Удаление ИБП с подтверждением
const deleteUPS = async (id) => {
  const confirmed = await confirmModal.value.open({
    title: 'Удаление ИБП',
    message: 'Вы уверены, что хотите удалить этот ИБП? Это действие нельзя отменить.',
    confirmText: 'Да, удалить',
    type: 'danger'
  })

  if (confirmed) {
    try {
      await axios.delete(`${API}/ups/${id}/`)
      await fetchAllData()
      showSuccess('ИБП удален!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления ИБП')
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

.comment-info {
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