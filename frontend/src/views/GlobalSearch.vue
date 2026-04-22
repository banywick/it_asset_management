<template>
  <div class="page">
    <h1>🔍 Результаты поиска</h1>
    
    <div class="search-info">
      <div class="search-query">
        <span class="query-label">Поиск:</span>
        <span class="query-text">{{ searchQuery }}</span>
        <button @click="clearSearch" class="clear-btn">✖️ Очистить</button>
      </div>
      <div class="results-count">Найдено: {{ totalResults }} результатов</div>
    </div>

    <!-- Результаты поиска -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Поиск...</p>
    </div>

    <div v-else-if="!hasResults && searched" class="no-results">
      <p>😕 Ничего не найдено по запросу "{{ searchQuery }}"</p>
      <p class="hint">Попробуйте изменить поисковый запрос</p>
    </div>

    <div v-else-if="hasResults" class="results">
      <!-- Сотрудники -->
      <div v-if="searchResults.employees && searchResults.employees.length" class="result-category">
        <h2 class="category-title">
          <span class="category-icon">👥</span>
          Сотрудники ({{ searchResults.employees.length }})
        </h2>
        <div class="cards-grid">
          <div v-for="emp in searchResults.employees" :key="emp.id" class="result-card employee-card">
            <div class="card-header">
              <strong>{{ emp.full_name || `${emp.last_name} ${emp.first_name} ${emp.patronymic || ''}` }}</strong>
              <div class="card-actions">
                <span class="badge">Сотрудник</span>
                <button @click="openEditModal('employee', emp)" class="edit-btn-small" title="Редактировать">✏️</button>
              </div>
            </div>
            <div class="card-body">
              <div class="detail-item" @click="openEditModal('employee', emp)">
                <span class="label">📍 Отдел:</span>
                <span class="value clickable-field">{{ emp.department?.name || 'Не указан' }}</span>
                <span class="edit-hint">✏️</span>
              </div>
              
              <!-- Рабочее место -->
              <div v-if="emp.workplace" class="relation-block">
                <div class="relation-title">🏢 Рабочее место</div>
                <div class="detail-item" @click="openEditModal('workplace', { id: emp.workplace.id, employee_name: emp.full_name })">
                  <span class="label">Город:</span>
                  <span class="value clickable-field">{{ emp.workplace.city || 'Не указан' }}</span>
                  <span class="edit-hint">✏️</span>
                </div>
                <div class="detail-item">
                  <span class="label">Статус:</span>
                  <span :class="['status-badge', getWorkplaceStatusClass(emp.workplace.status)]">
                    {{ getWorkplaceStatusText(emp.workplace.status) }}
                  </span>
                </div>
              </div>
              
              <!-- Компьютер -->
              <div v-if="emp.computer" class="relation-block">
                <div class="relation-title">🖥️ Закрепленный компьютер</div>
                <div class="detail-item" @click="openEditModal('computer', { id: emp.computer.id, asset_number: emp.computer.asset_number })">
                  <span class="label">ОС №:</span>
                  <span class="value clickable-field">{{ emp.computer.asset_number }}</span>
                  <span class="edit-hint">✏️</span>
                </div>
                <div class="detail-item">
                  <span class="label">Системный блок:</span>
                  <span class="value">{{ emp.computer.system_unit || 'Не указан' }}</span>
                </div>
                <div class="detail-item">
                  <span class="label">Тип:</span>
                  <span class="value">{{ getComputerTypeText(emp.computer.computer_type) }}</span>
                </div>
              </div>
              
              <!-- ИБП -->
              <div v-if="emp.ups" class="relation-block">
                <div class="relation-title">🔋 Бесперебойник</div>
                <div class="detail-item" @click="openEditModal('ups', { id: emp.ups.id, asset_number: emp.ups.asset_number })">
                  <span class="label">Модель:</span>
                  <span class="value clickable-field">{{ emp.ups.model }}</span>
                  <span class="edit-hint">✏️</span>
                </div>
                <div class="detail-item">
                  <span class="label">Последняя замена АКБ:</span>
                  <span class="value">{{ formatDate(emp.ups.battery_replaced_at) || 'не заменялся' }}</span>
                </div>
                <div v-if="emp.ups.battery_history && emp.ups.battery_history.length" class="history-list">
                  <div class="history-title">📋 История замен АКБ:</div>
                  <div v-for="hist in emp.ups.battery_history" :key="hist.id" class="history-item">
                    <span class="history-date">{{ formatDate(hist.replaced_at) }}</span>
                    <span>📤 {{ hist.old_battery_serial || 'не указан' }} → 📥 {{ hist.new_battery_serial }}</span>
                    <span v-if="hist.performed_by" class="history-performer">👤 {{ hist.performed_by }}</span>
                  </div>
                </div>
              </div>
              
              <!-- МФУ -->
              <div v-if="emp.mfp" class="relation-block">
                <div class="relation-title">🖨️ МФУ</div>
                <div class="detail-item" @click="openEditModal('mfp', { id: emp.mfp.id, asset_number: emp.mfp.asset_number })">
                  <span class="label">Модель:</span>
                  <span class="value clickable-field">{{ emp.mfp.model }}</span>
                  <span class="edit-hint">✏️</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Остальные категории остаются без изменений... -->
    </div>

    <!-- Модальное окно редактирования (остается без изменений) -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { showSuccess, showError, showWarning } from '../utils/toast'

const route = useRoute()
const router = useRouter()
const API = 'http://localhost:8000/api'

const searchQuery = ref('')
const searchResults = ref({})
const loading = ref(false)
const searched = ref(false)

// Данные для редактирования
const showEditModal = ref(false)
const editEntityType = ref('')
const editEntityTitle = ref('')
const editData = ref({})
const editEntityId = ref(null)
const allDepartments = ref([])
const allLocations = ref([])

const hasResults = computed(() => {
  const results = searchResults.value
  return !!(results.employees?.length || 
    results.workplaces?.length || 
    results.computers?.length || 
    results.mfps?.length || 
    results.tvs?.length || 
    results.ups?.length ||
    results.departments?.length ||
    results.locations?.length)
})

const totalResults = computed(() => {
  const results = searchResults.value
  return (results.employees?.length || 0) +
    (results.workplaces?.length || 0) +
    (results.computers?.length || 0) +
    (results.mfps?.length || 0) +
    (results.tvs?.length || 0) +
    (results.ups?.length || 0) +
    (results.departments?.length || 0) +
    (results.locations?.length || 0)
})

// Форматирование даты
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU')
}

// Типы компьютеров
const getComputerTypeText = (type) => {
  const texts = {
    'desktop': 'Стационарный',
    'laptop': 'Ноутбук',
    'all-in-one': 'Моноблок'
  }
  return texts[type] || 'Не указан'
}

// Статусы рабочих мест
const getWorkplaceStatusText = (status) => {
  const statusMap = {
    'active': 'Активно',
    'inactive': 'Неактивно',
    'maintenance': 'На обслуживании',
    'repair': 'Требует ремонта'
  }
  return statusMap[status] || status
}

const getWorkplaceStatusClass = (status) => {
  const classMap = {
    'active': 'status-active',
    'inactive': 'status-inactive',
    'maintenance': 'status-maintenance',
    'repair': 'status-repair'
  }
  return classMap[status] || ''
}

// Статусы ИБП
const getUPSStatusText = (status) => {
  const statusMap = {
    'active': 'Активен',
    'repair': 'В ремонте',
    'replaced': 'Заменен временно'
  }
  return statusMap[status] || status
}

const getUPSStatusClass = (status) => {
  const classMap = {
    'active': 'status-active',
    'repair': 'status-repair',
    'replaced': 'status-replaced'
  }
  return classMap[status] || ''
}

// Загрузка данных для выпадающих списков
const fetchSelectData = async () => {
  try {
    const [depRes, locRes] = await Promise.all([
      axios.get(`${API}/departments/`),
      axios.get(`${API}/locations/`)
    ])
    allDepartments.value = depRes.data
    allLocations.value = locRes.data
  } catch (error) {
    console.error('Ошибка загрузки данных:', error)
  }
}

// Открытие модального окна редактирования
const openEditModal = (type, entity) => {
  editEntityType.value = type
  editEntityId.value = entity.id
  editData.value = { ...entity }
  
  switch (type) {
    case 'employee':
      editEntityTitle.value = `Сотрудника: ${entity.full_name || `${entity.last_name} ${entity.first_name}`}`
      break
    case 'computer':
      editEntityTitle.value = `Компьютер: ОС №${entity.asset_number}`
      break
    case 'ups':
      editEntityTitle.value = `ИБП: ОС №${entity.asset_number}`
      break
    case 'mfp':
      editEntityTitle.value = `МФУ: ОС №${entity.asset_number}`
      break
    case 'tv':
      editEntityTitle.value = `Телевизор: ${entity.brand}`
      break
    case 'workplace':
      editEntityTitle.value = `Рабочее место: ${entity.employee_name}`
      break
    case 'department':
      editEntityTitle.value = `Отдел: ${entity.name}`
      break
    case 'location':
      editEntityTitle.value = `Локация: ${entity.name}`
      break
  }
  
  showEditModal.value = true
}

// Сохранение изменений
const saveEdit = async () => {
  try {
    let response
    let updateData = {}
    
    switch (editEntityType.value) {
      case 'employee':
        updateData = {
          last_name: editData.value.last_name,
          first_name: editData.value.first_name,
          patronymic: editData.value.patronymic || null,
          department: editData.value.department || null
        }
        response = await axios.put(`${API}/employees/${editEntityId.value}/`, updateData)
        break
      case 'computer':
        updateData = {
          asset_number: editData.value.asset_number,
          computer_type: editData.value.computer_type,
          system_unit: editData.value.system_unit
        }
        response = await axios.put(`${API}/computers/${editEntityId.value}/`, updateData)
        break
      case 'ups':
        updateData = {
          asset_number: editData.value.asset_number,
          model: editData.value.model,
          status: editData.value.status,
          comment: editData.value.comment || null
        }
        response = await axios.put(`${API}/ups/${editEntityId.value}/`, updateData)
        break
      case 'mfp':
        updateData = {
          asset_number: editData.value.asset_number,
          model: editData.value.model,
          ip_address: editData.value.ip_address || null
        }
        response = await axios.put(`${API}/mfps/${editEntityId.value}/`, updateData)
        break
      case 'tv':
        updateData = {
          asset_number: editData.value.asset_number,
          brand: editData.value.brand,
          size: editData.value.size,
          location: editData.value.location || null
        }
        response = await axios.put(`${API}/tvs/${editEntityId.value}/`, updateData)
        break
      case 'workplace':
        updateData = {
          city: editData.value.city || null,
          status: editData.value.status
        }
        response = await axios.patch(`${API}/workplaces/${editEntityId.value}/`, updateData)
        break
      case 'department':
        updateData = { name: editData.value.name }
        response = await axios.put(`${API}/departments/${editEntityId.value}/`, updateData)
        break
      case 'location':
        updateData = { name: editData.value.name }
        response = await axios.put(`${API}/locations/${editEntityId.value}/`, updateData)
        break
    }
    
    showEditModal.value = false
    showSuccess(`${editEntityType.value} успешно обновлен!`)
    await performSearch() // Обновляем результаты поиска
  } catch (error) {
    console.error('Ошибка сохранения:', error)
    showError('Ошибка сохранения: ' + (error.response?.data?.detail || error.message))
  }
}

// Глобальный поиск
const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    searched.value = false
    searchResults.value = {}
    return
  }
  
  loading.value = true
  searched.value = true
  
  try {
    const response = await axios.get(`${API}/global-search/search/`, {
      params: { q: searchQuery.value }
    })
    console.log('Результаты поиска:', response.data) // Отладка
    searchResults.value = response.data
  } catch (error) {
    console.error('Ошибка поиска:', error)
    searchResults.value = {}
    showError('Ошибка выполнения поиска')
  } finally {
    loading.value = false
  }
}

// Очистка поиска
const clearSearch = () => {
  searchQuery.value = ''
  searched.value = false
  searchResults.value = {}
  router.push({ path: '/' })
}

// Следим за изменением параметра в URL
watch(() => route.query.q, (newQuery) => {
  if (newQuery) {
    searchQuery.value = newQuery
    performSearch()
  } else {
    searchQuery.value = ''
    searched.value = false
    searchResults.value = {}
  }
})

// Инициализация из URL параметра
onMounted(() => {
  const query = route.query.q
  if (query) {
    searchQuery.value = query
    performSearch()
  }
  fetchSelectData()
})
</script>

<style scoped>
/* Все стили остаются как в предыдущей версии */
.page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
}

h1 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.search-info {
  background: white;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.search-query {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.query-label {
  font-weight: bold;
  color: #666;
}

.query-text {
  background: #e8f5e9;
  padding: 5px 12px;
  border-radius: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.clear-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 5px 12px;
  border-radius: 20px;
  cursor: pointer;
  font-size: 0.85rem;
}

.results-count {
  color: #666;
  font-weight: 500;
}

.loading {
  text-align: center;
  padding: 50px;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #1abc9c;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-results {
  text-align: center;
  padding: 50px;
  background: white;
  border-radius: 12px;
}

.no-results p {
  font-size: 1.2rem;
  color: #666;
}

.hint {
  font-size: 0.9rem;
  color: #999;
}

.results {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.result-category {
  margin-bottom: 1rem;
}

.category-title {
  font-size: 1.3rem;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #1abc9c;
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  font-size: 1.5rem;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1rem;
}

.small-grid {
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
}

.result-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.card-header {
  padding: 12px 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.card-header strong {
  font-size: 1rem;
  color: #2c3e50;
}

.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.badge {
  background: #1abc9c;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.edit-btn-small {
  background: none;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  color: #3498db;
  transition: all 0.2s;
}

.edit-btn-small:hover {
  background: #3498db;
  color: white;
}

.card-body {
  padding: 15px;
}

.detail-item {
  margin-bottom: 8px;
  font-size: 0.85rem;
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.detail-item:hover {
  background: rgba(26, 188, 156, 0.1);
}

.clickable-field {
  cursor: pointer;
}

.edit-hint {
  opacity: 0;
  margin-left: 8px;
  font-size: 0.7rem;
  color: #1abc9c;
  transition: opacity 0.2s;
}

.detail-item:hover .edit-hint {
  opacity: 1;
}

.label {
  font-weight: 600;
  color: #666;
  min-width: 120px;
}

.value {
  color: #333;
  flex: 1;
}

.relation-block {
  margin-top: 12px;
  padding-top: 8px;
  border-top: 1px dashed #ddd;
}

.relation-title {
  font-weight: 600;
  color: #1abc9c;
  margin-bottom: 8px;
  font-size: 0.85rem;
}

.history-list {
  margin-top: 8px;
  padding-left: 10px;
  border-left: 2px solid #1abc9c;
}

.history-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
  margin-bottom: 5px;
}

.history-item {
  font-size: 0.75rem;
  padding: 4px 0;
  border-bottom: 1px solid #eee;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-date {
  color: #1abc9c;
  font-weight: 500;
}

.history-performer {
  color: #999;
}

.status-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.status-active {
  background: #d4edda;
  color: #155724;
}

.status-inactive {
  background: #f8d7da;
  color: #721c24;
}

.status-maintenance {
  background: #fff3cd;
  color: #856404;
}

.status-repair {
  background: #f8d7da;
  color: #721c24;
}

.status-replaced {
  background: #fff3cd;
  color: #856404;
}

/* Модальное окно */
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
  max-width: 600px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.modal-large {
  max-width: 600px !important;
}

.modal-content h3 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.modal-subtitle {
  color: #666;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #2c3e50;
}

.main-field, .search-input, .textarea-field {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
}

.main-field {
  border: 2px solid #1abc9c;
  background: #f8f9fa;
}

.textarea-field {
  resize: vertical;
  font-family: inherit;
}

.modal-buttons {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
}

.save-btn {
  background: #1abc9c;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  cursor: pointer;
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
}

.cancel-btn:hover {
  background: #c0392b;
}

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
  
  .modal-content {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .detail-item {
    flex-direction: column;
  }
  
  .label {
    margin-bottom: 4px;
  }
}
</style>