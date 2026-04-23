<template>
  <div class="page">
    <div class="search-header">
      <h1>🔍 Глобальный поиск</h1>
      <div class="search-stats" v-if="hasResults">
        <span class="stat-badge">📊 Найдено: {{ totalResults }}</span>
      </div>
    </div>

    <!-- Результаты поиска -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Поиск...</p>
    </div>

    <div v-else-if="!hasResults && searched" class="no-results">
      <div class="no-results-icon">🔍</div>
      <p>Ничего не найдено по запросу "{{ searchQuery }}"</p>
      <p class="hint">Попробуйте изменить поисковый запрос</p>
    </div>

    <div v-else-if="hasResults" class="results">
      <!-- Сотрудники -->
      <div v-if="searchResults.employees?.length" class="result-category">
        <div class="category-header">
          <div class="category-title">
            <span class="category-icon">👥</span>
            <h2>Сотрудники</h2>
            <span class="count">{{ searchResults.employees.length }}</span>
          </div>
        </div>
        <div class="cards-grid">
          <div v-for="emp in searchResults.employees" :key="emp.id" class="result-card">
            <div class="card-header">
              <div class="header-icon">👤</div>
              <div class="header-info">
                <div class="title">{{ emp.full_name }}</div>
                <div class="subtitle">{{ emp.department?.name || 'Отдел не указан' }}</div>
              </div>
              <button @click="openEditModal('employee', emp)" class="edit-icon-btn" title="Редактировать">✏️</button>
            </div>
            
            <div class="card-content">
              <!-- Рабочее место -->
              <div 
                v-if="emp.workplace" 
                class="relation-section"
                @click="openDetailsModal('workplace', emp.workplace.id)"
              >
                <div class="relation-header">
                  <span class="relation-icon">🏢</span>
                  <span class="relation-title">Рабочее место</span>
                  <span class="relation-city">{{ emp.workplace.city || 'Город не указан' }}</span>
                </div>
                <div class="relation-status">
                  <span :class="['status-badge', getWorkplaceStatusClass(emp.workplace.status)]">
                    {{ getWorkplaceStatusText(emp.workplace.status) }}
                  </span>
                </div>
              </div>
              
              <!-- Компьютер -->
              <div 
                v-if="emp.computer" 
                class="relation-section"
                @click="openDetailsModal('computer', emp.computer.id)"
              >
                <div class="relation-header">
                  <span class="relation-icon">🖥️</span>
                  <span class="relation-title">Закрепленный компьютер</span>
                  <span class="relation-subtitle">ОС №{{ emp.computer.asset_number }}</span>
                </div>
                <div class="relation-type">{{ getComputerTypeText(emp.computer.computer_type) }}</div>
              </div>
              
              <!-- ИБП -->
              <div 
                v-if="emp.ups" 
                class="relation-section"
                @click="openDetailsModal('ups', emp.ups.id)"
              >
                <div class="relation-header">
                  <span class="relation-icon">🔋</span>
                  <span class="relation-title">Бесперебойник</span>
                  <span class="relation-subtitle">{{ emp.ups.model }}</span>
                </div>
                <div class="relation-date">
                  🔋 АКБ: {{ formatDate(emp.ups.battery_replaced_at) || 'не заменялся' }}
                </div>
              </div>
              
              <!-- МФУ -->
              <div 
                v-if="emp.mfp" 
                class="relation-section"
                @click="openDetailsModal('mfp', emp.mfp.id)"
              >
                <div class="relation-header">
                  <span class="relation-icon">🖨️</span>
                  <span class="relation-title">МФУ</span>
                  <span class="relation-subtitle">{{ emp.mfp.model }}</span>
                </div>
                <div class="relation-ip">IP: {{ emp.mfp.ip_address || 'не указан' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Остальные категории (компьютеры, МФУ, ИБП, телевизоры) остаются без изменений -->
      <!-- ... -->
    </div>

    <!-- Модальное окно для редактирования (с поиском отдела) -->
    <div v-if="showEditModal" class="modal" :class="{ 'modal-higher': showDetailsModal }">
      <div class="modal-content modal-large">
        <h3>✏️ Редактировать {{ getEntityTypeName() }}</h3>
        
        <!-- Сотрудник с поиском отдела -->
        <div v-if="editEntityType === 'employee'">
          <div class="form-group">
            <label>Фамилия:</label>
            <input v-model="editData.last_name" class="search-input">
          </div>
          <div class="form-group">
            <label>Имя:</label>
            <input v-model="editData.first_name" class="search-input">
          </div>
          <div class="form-group">
            <label>Отчество:</label>
            <input v-model="editData.patronymic" class="search-input">
          </div>
          
          <!-- Отдел с поиском -->
          <div class="form-group">
            <label>Отдел:</label>
            <div class="search-wrapper">
              <input 
                type="text" 
                v-model="departmentSearch" 
                @input="searchDepartments"
                @focus="searchDepartments"
                placeholder="Поиск отдела..."
                class="search-input"
              >
              <div v-if="departmentSearchResults.length" class="search-results">
                <div 
                  v-for="dep in departmentSearchResults" 
                  :key="dep.id" 
                  @click="selectDepartment(dep)"
                  class="search-result-item"
                >
                  {{ dep.name }}
                </div>
              </div>
            </div>
            <div v-if="selectedDepartment" class="selected-tag">
              {{ selectedDepartment.name }}
              <button @click="selectedDepartment = null" class="remove-btn">×</button>
            </div>
          </div>
        </div>
        
        <!-- Компьютер -->
        <div v-if="editEntityType === 'computer'">
          <div class="form-group">
            <label>Номер ОС:</label>
            <input v-model="editData.asset_number" class="main-field">
          </div>
          <div class="form-group">
            <label>Тип:</label>
            <select v-model="editData.computer_type" class="search-input">
              <option value="desktop">🖥️ Стационарный</option>
              <option value="laptop">💻 Ноутбук</option>
              <option value="all-in-one">🖥️ Моноблок</option>
            </select>
          </div>
          <div class="form-group">
            <label>Системный блок:</label>
            <textarea v-model="editData.system_unit" rows="3" class="textarea-field"></textarea>
          </div>
          <div class="form-group">
            <label>Статус обслуживания:</label>
            <select v-model="editData.service_status" class="search-input">
              <option value="operational">✅ В эксплуатации</option>
              <option value="repair">🔧 В ремонте</option>
              <option value="upgrade">⚡ На модернизации</option>
            </select>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editData.has_keyboard"> Клавиатура
            </label>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="editData.has_mouse"> Мышь
            </label>
          </div>
        </div>
        
        <!-- Остальные типы (МФУ, ИБП, телевизор, рабочее место) -->
        <!-- ... -->
        
        <div class="modal-buttons">
          <button @click="saveEdit" class="save-btn">💾 Сохранить</button>
          <button @click="closeEditModal" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно для детализации -->
    <div v-if="showDetailsModal" class="modal" :class="{ 'modal-higher': showEditModal }">
      <div class="modal-content modal-large">
        <h3>📋 {{ detailsTitle }}</h3>
        
        <!-- Детали рабочего места -->
        <div v-if="detailsType === 'workplace' && detailsData" class="workplace-details">
          <div class="detail-row">
            <span class="detail-label">👤 Сотрудник:</span>
            <span class="detail-value">{{ detailsData.employee_name }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">🏙️ Город:</span>
            <span class="detail-value">{{ detailsData.city_name || 'Не указан' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">📊 Статус:</span>
            <span :class="['status-badge', getWorkplaceStatusClass(detailsData.status)]">
              {{ getWorkplaceStatusText(detailsData.status) }}
            </span>
          </div>
          
          <!-- Компьютер в рабочем месте -->
          <div v-if="detailsData.computer_detail" class="sub-entity" @click.stop="openEditFromDetails('computer', detailsData.computer_detail)">
            <div class="sub-entity-header">
              <span>🖥️ Компьютер</span>
              <span class="edit-link">✏️</span>
            </div>
            <div class="sub-entity-details">
              <div>ОС №{{ detailsData.computer_detail.asset_number }}</div>
              <div class="small">{{ detailsData.computer_detail.system_unit || 'Системный блок не указан' }}</div>
            </div>
          </div>
          
          <!-- МФУ в рабочем месте -->
          <div v-if="detailsData.mfp_detail" class="sub-entity" @click.stop="openEditFromDetails('mfp', detailsData.mfp_detail)">
            <div class="sub-entity-header">
              <span>🖨️ МФУ</span>
              <span class="edit-link">✏️</span>
            </div>
            <div class="sub-entity-details">
              <div>{{ detailsData.mfp_detail.model }}</div>
              <div class="small">IP: {{ detailsData.mfp_detail.ip_address || 'не указан' }}</div>
            </div>
          </div>
          
          <!-- ИБП в рабочем месте -->
          <div v-if="detailsData.ups_detail" class="sub-entity" @click.stop="openEditFromDetails('ups', detailsData.ups_detail)">
            <div class="sub-entity-header">
              <span>🔋 ИБП</span>
              <span class="edit-link">✏️</span>
            </div>
            <div class="sub-entity-details">
              <div>{{ detailsData.ups_detail.model }}</div>
              <div class="small">АКБ заменён: {{ formatDate(detailsData.ups_detail.battery_replaced_at) || 'не заменялся' }}</div>
            </div>
          </div>
        </div>
        
        <!-- Остальные типы детализации -->
        <!-- ... -->
        
        <div class="modal-buttons">
          <button v-if="detailsData" @click="openEditFromDetails(detailsType, detailsData)" class="save-btn">✏️ Редактировать</button>
          <button @click="closeDetailsModal" class="cancel-btn">Закрыть</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { showSuccess, showError } from '../utils/toast'

const route = useRoute()
const API = 'http://localhost:8000/api'

const searchQuery = ref('')
const searchResults = ref({})
const loading = ref(false)
const searched = ref(false)

// Данные для редактирования
const showEditModal = ref(false)
const editEntityType = ref('')
const editData = ref({})
const editEntityId = ref(null)
const allDepartments = ref([])
const allLocations = ref([])

// Поиск отдела
const departmentSearch = ref('')
const departmentSearchResults = ref([])
const selectedDepartment = ref(null)

// Данные для детализации
const showDetailsModal = ref(false)
const detailsType = ref('')
const detailsData = ref(null)
const detailsId = ref(null)

const hasResults = computed(() => {
  const results = searchResults.value
  return !!(results.employees?.length || 
    results.workplaces?.length || 
    results.computers?.length || 
    results.mfps?.length || 
    results.tvs?.length || 
    results.ups?.length)
})

const totalResults = computed(() => {
  const results = searchResults.value
  return (results.employees?.length || 0) +
    (results.workplaces?.length || 0) +
    (results.computers?.length || 0) +
    (results.mfps?.length || 0) +
    (results.tvs?.length || 0) +
    (results.ups?.length || 0)
})

const detailsTitle = computed(() => {
  const titles = {
    'workplace': 'Детали рабочего места',
    'computer': 'Детали компьютера',
    'ups': 'Детали ИБП',
    'mfp': 'Детали МФУ',
    'employee': 'Детали сотрудника'
  }
  return titles[detailsType.value] || 'Детали'
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

// Получение названия типа сущности
const getEntityTypeName = () => {
  const names = {
    'employee': 'сотрудника',
    'computer': 'компьютер',
    'ups': 'ИБП',
    'mfp': 'МФУ',
    'tv': 'телевизор',
    'workplace': 'рабочее место'
  }
  return names[editEntityType.value] || ''
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

// Поиск отделов
const searchDepartments = () => {
  if (!departmentSearch.value) {
    departmentSearchResults.value = []
    return
  }
  departmentSearchResults.value = allDepartments.value.filter(d => 
    d.name.toLowerCase().includes(departmentSearch.value.toLowerCase())
  ).slice(0, 10)
}

const selectDepartment = (department) => {
  selectedDepartment.value = department
  editData.value.department = department.id
  departmentSearch.value = ''
  departmentSearchResults.value = []
}

// Открытие модального окна детализации
const openDetailsModal = async (type, id) => {
  try {
    let response
    switch (type) {
      case 'workplace':
        response = await axios.get(`${API}/workplaces/${id}/`)
        break
      case 'computer':
        response = await axios.get(`${API}/computers/${id}/`)
        break
      case 'ups':
        response = await axios.get(`${API}/ups/${id}/`)
        break
      case 'mfp':
        response = await axios.get(`${API}/mfps/${id}/`)
        break
      case 'employee':
        response = await axios.get(`${API}/employees/${id}/`)
        break
    }
    detailsType.value = type
    detailsData.value = response.data
    detailsId.value = id
    showDetailsModal.value = true
  } catch (error) {
    console.error('Ошибка загрузки деталей:', error)
    showError('Ошибка загрузки деталей')
  }
}

// Открытие редактирования из деталей (закрывает окно деталей и открывает редактирование)
const openEditFromDetails = (type, data) => {
  // Закрываем окно детализации
  showDetailsModal.value = false
  
  // Небольшая задержка для плавного перехода
  setTimeout(() => {
    openEditModal(type, data)
  }, 100)
}

// Закрытие окна детализации
const closeDetailsModal = () => {
  showDetailsModal.value = false
  detailsType.value = ''
  detailsData.value = null
  detailsId.value = null
}

// Открытие модального окна редактирования
const openEditModal = (type, entity) => {
  editEntityType.value = type
  editEntityId.value = entity.id
  editData.value = { ...entity }
  
  // Для сотрудника восстанавливаем выбранный отдел
  if (type === 'employee' && entity.department) {
    selectedDepartment.value = allDepartments.value.find(d => d.id === entity.department) || null
  } else {
    selectedDepartment.value = null
  }
  
  departmentSearch.value = ''
  departmentSearchResults.value = []
  showEditModal.value = true
}

// Закрытие окна редактирования
const closeEditModal = () => {
  showEditModal.value = false
  editEntityType.value = ''
  editData.value = {}
  editEntityId.value = null
  selectedDepartment.value = null
  departmentSearch.value = ''
  departmentSearchResults.value = []
}

// Сохранение изменений
const saveEdit = async () => {
  try {
    let updateData = {}
    
    switch (editEntityType.value) {
      case 'employee':
        updateData = {
          last_name: editData.value.last_name,
          first_name: editData.value.first_name,
          patronymic: editData.value.patronymic || null,
          department: editData.value.department || null
        }
        await axios.put(`${API}/employees/${editEntityId.value}/`, updateData)
        break
      case 'computer':
        updateData = {
          asset_number: editData.value.asset_number,
          computer_type: editData.value.computer_type,
          system_unit: editData.value.system_unit,
          service_status: editData.value.service_status,
          has_keyboard: editData.value.has_keyboard,
          has_mouse: editData.value.has_mouse
        }
        await axios.put(`${API}/computers/${editEntityId.value}/`, updateData)
        break
      case 'ups':
        updateData = {
          asset_number: editData.value.asset_number,
          model: editData.value.model,
          status: editData.value.status,
          comment: editData.value.comment || null
        }
        await axios.put(`${API}/ups/${editEntityId.value}/`, updateData)
        break
      case 'mfp':
        updateData = {
          asset_number: editData.value.asset_number,
          model: editData.value.model,
          ip_address: editData.value.ip_address || null
        }
        await axios.put(`${API}/mfps/${editEntityId.value}/`, updateData)
        break
      case 'tv':
        updateData = {
          asset_number: editData.value.asset_number,
          brand: editData.value.brand,
          size: editData.value.size,
          location: editData.value.location || null
        }
        await axios.put(`${API}/tvs/${editEntityId.value}/`, updateData)
        break
      case 'workplace':
        updateData = {
          city: editData.value.city || null,
          status: editData.value.status
        }
        await axios.patch(`${API}/workplaces/${editEntityId.value}/`, updateData)
        break
    }
    
    closeEditModal()
    await performSearch()
    showSuccess(`${getEntityTypeName()} успешно обновлен!`)
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
    searchResults.value = response.data
  } catch (error) {
    console.error('Ошибка поиска:', error)
    searchResults.value = {}
    showError('Ошибка выполнения поиска')
  } finally {
    loading.value = false
  }
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
/* Все предыдущие стили остаются, добавляем новые */

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
  max-height: 200px;
  overflow-y: auto;
  z-index: 1002;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.search-result-item {
  padding: 10px 12px;
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
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
  margin-top: 8px;
}

.remove-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #999;
  padding: 0 5px;
  line-height: 1;
}

.remove-btn:hover {
  color: #e74c3c;
}

/* Стили для z-index модальных окон */
.modal {
  z-index: 1000;
}

.modal-higher {
  z-index: 1002 !important;
}

.page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1rem;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.search-header h1 {
  color: #2c3e50;
  margin: 0;
}

.search-stats {
  display: flex;
  gap: 0.5rem;
}

.stat-badge {
  background: #e8f5e9;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  color: #2c3e50;
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
  padding: 60px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.no-results-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.no-results p {
  font-size: 1.2rem;
  color: #666;
}

.hint {
  font-size: 0.9rem;
  color: #999;
  margin-top: 0.5rem;
}

.results {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.result-category {
  margin-bottom: 0.5rem;
}

.category-header {
  margin-bottom: 1rem;
}

.category-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.category-icon {
  font-size: 1.5rem;
}

.category-title h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin: 0;
}

.count {
  background: #e0e0e0;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  font-size: 0.8rem;
  color: #555;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 1rem;
}

.result-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
}

.result-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
  border-bottom: 1px solid #eee;
}

.header-icon {
  width: 40px;
  height: 40px;
  background: #e8f5e9;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
}

.header-info {
  flex: 1;
}

.title {
  font-weight: 600;
  font-size: 1rem;
  color: #2c3e50;
}

.subtitle {
  font-size: 0.75rem;
  color: #999;
  margin-top: 2px;
}

.edit-icon-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  color: #3498db;
  transition: all 0.2s;
}

.edit-icon-btn:hover {
  background: #3498db;
  color: white;
}

.card-content {
  padding: 16px;
}

.relation-section {
  margin-bottom: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.relation-section:hover {
  background: #fff9e6;
  transform: translateX(4px);
}

.relation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
  flex-wrap: wrap;
}

.relation-icon {
  font-size: 1rem;
}

.relation-title {
  font-weight: 600;
  font-size: 0.85rem;
  color: #1abc9c;
}

.relation-subtitle {
  font-size: 0.8rem;
  color: #666;
  margin-left: auto;
}

.relation-city {
  font-size: 0.7rem;
  color: #999;
  margin-left: auto;
}

.relation-type {
  font-size: 0.75rem;
  color: #666;
  padding-left: 24px;
}

.relation-date {
  font-size: 0.7rem;
  color: #27ae60;
  padding-left: 24px;
}

.relation-ip {
  font-size: 0.7rem;
  color: #3498db;
  padding-left: 24px;
}

.relation-status {
  padding-left: 24px;
}

.detail-item {
  display: flex;
  align-items: baseline;
  margin-bottom: 8px;
  font-size: 0.8rem;
  flex-wrap: wrap;
  gap: 4px;
}

.detail-item .label {
  font-weight: 500;
  color: #666;
  min-width: 85px;
}

.detail-item .value {
  color: #333;
}

.history-preview {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px dashed #ddd;
}

.history-title {
  font-size: 0.7rem;
  font-weight: 600;
  color: #666;
  margin-bottom: 4px;
}

.history-mini {
  font-size: 0.7rem;
  color: #999;
  padding: 2px 0;
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

/* Модальные окна */
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
  z-index: 1001;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 20px;
  width: 90%;
  max-width: 550px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.2);
  max-height: 80vh;
  overflow-y: auto;
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
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 0.9rem;
}

.main-field {
  border: 2px solid #1abc9c;
  background: #f8f9fa;
}

.textarea-field {
  resize: vertical;
  font-family: inherit;
}

.ip-input {
  font-family: 'Courier New', monospace;
}

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
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
  border-radius: 10px;
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
  border-radius: 10px;
  cursor: pointer;
}

.cancel-btn:hover {
  background: #c0392b;
}

/* Детали */
.detail-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  font-size: 0.85rem;
  flex-wrap: wrap;
  padding: 6px 0;
}

.detail-label {
  font-weight: 600;
  color: #555;
  min-width: 110px;
}

.detail-value {
  color: #333;
  flex: 1;
}

.sub-entity {
  margin-top: 12px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.sub-entity:hover {
  background: #e8f5e9;
}

.sub-entity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-weight: 600;
  font-size: 0.8rem;
  color: #1abc9c;
}

.edit-link {
  color: #3498db;
  font-size: 0.7rem;
}

.sub-entity-details {
  font-size: 0.75rem;
  color: #666;
  padding-left: 8px;
}

.small {
  font-size: 0.65rem;
  color: #999;
  margin-top: 2px;
}

.history-list {
  margin-top: 12px;
}

.history-item {
  padding: 8px;
  margin: 5px 0;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid #1abc9c;
}

.history-date {
  font-weight: 600;
  color: #1abc9c;
  font-size: 0.7rem;
  margin-bottom: 4px;
}

.history-performer {
  font-size: 0.65rem;
  color: #999;
  margin-top: 4px;
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
  
  .detail-item .label {
    margin-bottom: 2px;
  }
  
  .relation-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .relation-subtitle, .relation-city {
    margin-left: 0;
  }
  
  .detail-row {
    flex-direction: column;
  }
  
  .detail-label {
    margin-bottom: 4px;
  }
}
</style>