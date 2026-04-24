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
              <!-- Только рабочее место -->
              <div 
                v-if="emp.workplace" 
                class="relation-section"
                @click="openWorkplaceDetails(emp.workplace.id)"
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
            </div>
          </div>
        </div>
      </div>

      <!-- Компьютеры -->
      <div v-if="searchResults.computers?.length" class="result-category">
        <div class="category-header">
          <div class="category-title">
            <span class="category-icon">🖥️</span>
            <h2>Компьютеры</h2>
            <span class="count">{{ searchResults.computers.length }}</span>
          </div>
        </div>
        <div class="cards-grid">
          <div v-for="comp in searchResults.computers" :key="comp.id" class="result-card">
            <div class="card-header">
              <div class="header-icon">💻</div>
              <div class="header-info">
                <div class="title">ОС №{{ comp.asset_number }}</div>
                <div class="subtitle">{{ getComputerTypeText(comp.computer_type) }}</div>
              </div>
              <button @click="openEditModal('computer', comp)" class="edit-icon-btn" title="Редактировать">✏️</button>
            </div>
            <div class="card-content">
              <div class="detail-item">
                <span class="label">Системный блок:</span>
                <span class="value">{{ comp.system_unit || 'Не указан' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Мониторы:</span>
                <span class="value">{{ comp.monitors?.map(m => m.brand).join(', ') || 'нет' }}</span>
              </div>
              <!-- Рабочее место где используется компьютер -->
              <div 
                v-if="comp.workplace" 
                class="relation-section"
                @click="openWorkplaceDetails(comp.workplace.id)"
              >
                <div class="relation-header">
                  <span class="relation-icon">🏢</span>
                  <span class="relation-title">Рабочее место</span>
                  <span class="relation-subtitle">{{ comp.workplace.employee_name || 'Сотрудник не указан' }}</span>
                </div>
                <div class="relation-city">{{ comp.workplace.city || 'Город не указан' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- МФУ -->
      <div v-if="searchResults.mfps?.length" class="result-category">
        <div class="category-header">
          <div class="category-title">
            <span class="category-icon">🖨️</span>
            <h2>МФУ</h2>
            <span class="count">{{ searchResults.mfps.length }}</span>
          </div>
        </div>
        <div class="cards-grid">
          <div v-for="mfp in searchResults.mfps" :key="mfp.id" class="result-card">
            <div class="card-header">
              <div class="header-icon">🖨️</div>
              <div class="header-info">
                <div class="title">ОС №{{ mfp.asset_number }}</div>
                <div class="subtitle">{{ mfp.model }}</div>
              </div>
              <button @click="openEditModal('mfp', mfp)" class="edit-icon-btn" title="Редактировать">✏️</button>
            </div>
            <div class="card-content">
              <div class="detail-item">
                <span class="label">IP адрес:</span>
                <span class="value">{{ mfp.ip_address || 'не указан' }}</span>
              </div>
              <!-- Рабочие места где используется МФУ -->
              <div 
                v-for="wp in mfp.used_in_workplaces" 
                :key="wp.id"
                class="relation-section"
                @click="openWorkplaceDetails(wp.id)"
              >
                <div class="relation-header">
                  <span class="relation-icon">🏢</span>
                  <span class="relation-title">Рабочее место</span>
                  <span class="relation-subtitle">{{ wp.employee_name }}</span>
                </div>
                <div class="relation-city">{{ wp.city || 'Город не указан' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ИБП -->
      <div v-if="searchResults.ups?.length" class="result-category">
        <div class="category-header">
          <div class="category-title">
            <span class="category-icon">🔋</span>
            <h2>ИБП</h2>
            <span class="count">{{ searchResults.ups.length }}</span>
          </div>
        </div>
        <div class="cards-grid">
          <div v-for="ups in searchResults.ups" :key="ups.id" class="result-card">
            <div class="card-header">
              <div class="header-icon">🔋</div>
              <div class="header-info">
                <div class="title">ОС №{{ ups.asset_number }}</div>
                <div class="subtitle">{{ ups.model }}</div>
              </div>
              <div class="card-actions">
                <button @click="openUPSServiceModal(ups)" class="service-icon-btn" title="Обслуживание">🔧</button>
                <button @click="openEditModal('ups', ups)" class="edit-icon-btn" title="Редактировать">✏️</button>
              </div>
            </div>
            <div class="card-content">
              <div class="detail-item">
                <span class="label">Статус:</span>
                <span :class="['status-badge', getUPSStatusClass(ups.status)]">
                  {{ getUPSStatusText(ups.status) }}
                </span>
              </div>
              <div class="detail-item">
                <span class="label">Аккумулятор:</span>
                <span class="value">{{ ups.battery_serial_number || 'не указан' }}</span>
              </div>
              <!-- История замен -->
              <div v-if="ups.battery_history?.length" class="history-preview">
                <div class="history-title">📋 Последние замены АКБ:</div>
                <div v-for="hist in ups.battery_history.slice(0, 2)" :key="hist.id" class="history-mini">
                  {{ formatDate(hist.replaced_at) }}: {{ hist.new_battery_serial }}
                </div>
              </div>
              <!-- Рабочие места где используется ИБП -->
              <div 
                v-for="wp in ups.used_in_workplaces" 
                :key="wp.id"
                class="relation-section"
                @click="openWorkplaceDetails(wp.id)"
              >
                <div class="relation-header">
                  <span class="relation-icon">🏢</span>
                  <span class="relation-title">Рабочее место</span>
                  <span class="relation-subtitle">{{ wp.employee_name }}</span>
                </div>
                <div class="relation-city">{{ wp.city || 'Город не указан' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Телевизоры -->
      <div v-if="searchResults.tvs?.length" class="result-category">
        <div class="category-header">
          <div class="category-title">
            <span class="category-icon">📺</span>
            <h2>Телевизоры</h2>
            <span class="count">{{ searchResults.tvs.length }}</span>
          </div>
        </div>
        <div class="cards-grid">
          <div v-for="tv in searchResults.tvs" :key="tv.id" class="result-card">
            <div class="card-header">
              <div class="header-icon">📺</div>
              <div class="header-info">
                <div class="title">{{ tv.brand }}</div>
                <div class="subtitle">{{ tv.size }}"</div>
              </div>
              <button @click="openEditModal('tv', tv)" class="edit-icon-btn" title="Редактировать">✏️</button>
            </div>
            <div class="card-content">
              <div class="detail-item">
                <span class="label">ОС №:</span>
                <span class="value">{{ tv.asset_number || 'не определен' }}</span>
              </div>
              <div class="detail-item">
                <span class="label">Место:</span>
                <span class="value">{{ tv.location || 'не указано' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальное окно детализации рабочего места -->
    <div v-if="showWorkplaceModal" class="modal" :class="{ 'modal-higher': showEditModal || showUPSServiceModal }">
      <div class="modal-content modal-large">
        <h3>🏢 Детали рабочего места</h3>
        <p class="modal-subtitle">Сотрудник: <strong>{{ workplaceDetails?.employee_name }}</strong></p>
        
        <div class="workplace-details">
          <div class="detail-row">
            <span class="detail-label">👤 Отдел:</span>
            <span class="detail-value">{{ workplaceDetails?.department_name || 'Не указан' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">🏙️ Город:</span>
            <span class="detail-value">{{ workplaceDetails?.city_name || 'Не указан' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">📊 Статус:</span>
            <span :class="['status-badge', getWorkplaceStatusClass(workplaceDetails?.status)]">
              {{ getWorkplaceStatusText(workplaceDetails?.status) }}
            </span>
          </div>
          
          <!-- Компьютер -->
          <div v-if="workplaceDetails?.computer_detail" class="sub-entity" @click.stop="openEditFromWorkplace('computer', workplaceDetails.computer_detail.id)">
            <div class="sub-entity-header">
              <span>🖥️ Компьютер</span>
              <span class="edit-link">✏️</span>
            </div>
            <div class="sub-entity-details">
              <div>ОС №{{ workplaceDetails.computer_detail.asset_number }}</div>
              <div class="small">{{ workplaceDetails.computer_detail.system_unit || 'Системный блок не указан' }}</div>
            </div>
          </div>
          
          <!-- МФУ -->
          <div v-if="workplaceDetails?.mfp_detail" class="sub-entity" @click.stop="openEditFromWorkplace('mfp', workplaceDetails.mfp_detail.id)">
            <div class="sub-entity-header">
              <span>🖨️ МФУ</span>
              <span class="edit-link">✏️</span>
            </div>
            <div class="sub-entity-details">
              <div>{{ workplaceDetails.mfp_detail.model }}</div>
              <div class="small">IP: {{ workplaceDetails.mfp_detail.ip_address || 'не указан' }}</div>
            </div>
          </div>
          
          <!-- ИБП с кнопкой обслуживания -->
          <div v-if="workplaceDetails?.ups_detail" class="sub-entity">
            <div class="sub-entity-header">
              <span>🔋 ИБП</span>
              <div class="sub-entity-actions">
                <button @click.stop="openUPSServiceModal(workplaceDetails.ups_detail)" class="service-small-btn" title="Обслуживание">🔧</button>
                <button @click.stop="openEditFromWorkplace('ups', workplaceDetails.ups_detail.id)" class="edit-link">✏️</button>
              </div>
            </div>
            <div class="sub-entity-details">
              <div>{{ workplaceDetails.ups_detail.model }}</div>
              <!-- <div class="small">АКБ заменён: {{ formatDate(workplaceDetails.ups_detail.battery_replaced_at) || 'не заменялся' }}</div> -->
            </div>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="closeWorkplaceModal" class="cancel-btn">Закрыть</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно обслуживания ИБП -->
    <div v-if="showUPSServiceModal" class="modal" :class="{ 'modal-higher': true }">
      <div class="modal-content modal-large">
        <h3>🔧 Обслуживание ИБП</h3>
        <p class="modal-subtitle">ИБП: <strong>ОС №{{ selectedUPSForService?.asset_number }} - {{ selectedUPSForService?.model }}</strong></p>
        
        <div class="service-form">
          <h4>➕ Замена аккумулятора</h4>
          <div class="form-row">
            <div class="form-group">
              <label>Извлеченный АКБ:</label>
              <input v-model="newBattery.old_battery_serial" placeholder="Серийный номер извлеченного АКБ" class="search-input">
            </div>
            <div class="form-group">
              <label>Установленный АКБ:</label>
              <input v-model="newBattery.new_battery_serial" placeholder="Серийный номер нового АКБ" class="search-input" required>
            </div>
          </div>
          <div class="form-group">
            <label>Кто выполнил замену:</label>
            <input v-model="newBattery.performed_by" placeholder="ФИО сотрудника" class="search-input">
          </div>
          <div class="form-group">
            <label>Комментарий:</label>
            <textarea v-model="newBattery.comment" placeholder="Дополнительная информация о замене..." rows="2" class="textarea-field"></textarea>
          </div>
          <button @click="addUPSBatteryHistory" class="submit-btn small">💾 Добавить запись</button>
        </div>
        
        <div class="history-section">
          <h4>📋 История замен аккумуляторов</h4>
          <div v-if="upsBatteryHistory.length" class="history-list">
            <div v-for="record in upsBatteryHistory" :key="record.id" class="history-item">
              <div class="history-header">
                <span class="history-date">{{ formatDate(record.replaced_at) }}</span>
                <button @click="deleteUPSBatteryHistory(record.id)" class="delete-small" title="Удалить запись">🗑️</button>
              </div>
              <div class="history-details">
                <div>📤 Извлечен: <strong>{{ record.old_battery_serial || 'не указан' }}</strong></div>
                <div>📥 Установлен: <strong>{{ record.new_battery_serial }}</strong></div>
                <div v-if="record.performed_by">👤 Кто: {{ record.performed_by }}</div>
                <div v-if="record.comment">💬 {{ record.comment }}</div>
              </div>
            </div>
          </div>
          <div v-else class="no-data">
            <p>😕 История замен отсутствует</p>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="closeUPSServiceModal" class="cancel-btn">Закрыть</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно для редактирования -->
    <div v-if="showEditModal" class="modal" :class="{ 'modal-higher': showWorkplaceModal || showUPSServiceModal }">
      <div class="modal-content modal-large">
        <h3>✏️ Редактировать {{ getEntityTypeName() }}</h3>
        
        <!-- Сотрудник -->
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
        
        <!-- МФУ -->
        <div v-if="editEntityType === 'mfp'">
          <div class="form-group">
            <label>Номер ОС:</label>
            <input v-model="editData.asset_number" class="main-field">
          </div>
          <div class="form-group">
            <label>Модель:</label>
            <input v-model="editData.model" class="search-input">
          </div>
          <div class="form-group">
            <label>IP адрес:</label>
            <input v-model="editData.ip_address" class="search-input ip-input" placeholder="192.168.1.100">
          </div>
        </div>
        
        <!-- ИБП -->
        <div v-if="editEntityType === 'ups'">
          <div class="form-group">
            <label>Номер ОС:</label>
            <input v-model="editData.asset_number" class="main-field">
          </div>
          <div class="form-group">
            <label>Модель:</label>
            <input v-model="editData.model" class="search-input">
          </div>
          <div class="form-group">
            <label>Статус:</label>
            <select v-model="editData.status" class="search-input">
              <option value="active">✅ Активен</option>
              <option value="repair">🔧 В ремонте</option>
              <option value="replaced">🔄 Заменен временно</option>
            </select>
          </div>
          <div class="form-group">
            <label>Комментарий:</label>
            <textarea v-model="editData.comment" rows="3" class="textarea-field"></textarea>
          </div>
        </div>
        
        <!-- Телевизор -->
        <div v-if="editEntityType === 'tv'">
          <div class="form-group">
            <label>Номер ОС:</label>
            <input v-model="editData.asset_number" class="main-field">
          </div>
          <div class="form-group">
            <label>Марка:</label>
            <input v-model="editData.brand" class="search-input">
          </div>
          <div class="form-group">
            <label>Диагональ:</label>
            <input v-model="editData.size" type="number" step="0.1" class="search-input">
          </div>
          <div class="form-group">
            <label>Место:</label>
            <input v-model="editData.location" class="search-input">
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="saveEdit" class="save-btn">💾 Сохранить</button>
          <button @click="closeEditModal" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { showSuccess, showError, showWarning } from '../utils/toast'
import ConfirmModal from '../components/ConfirmModal.vue'

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

// Данные для рабочего места
const showWorkplaceModal = ref(false)
const workplaceDetails = ref(null)

// Данные для обслуживания ИБП
const showUPSServiceModal = ref(false)
const selectedUPSForService = ref(null)
const upsBatteryHistory = ref([])
const newBattery = ref({
  old_battery_serial: '',
  new_battery_serial: '',
  performed_by: '',
  comment: ''
})

const confirmModal = ref(null)

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

// Загрузка полных данных сущности по ID
const fetchEntityData = async (type, id) => {
  try {
    let response
    switch (type) {
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
      case 'tv':
        response = await axios.get(`${API}/tvs/${id}/`)
        break
      default:
        return null
    }
    return response.data
  } catch (error) {
    console.error(`Ошибка загрузки ${type}:`, error)
    return null
  }
}

// Открытие редактирования из окна деталей рабочего места
const openEditFromWorkplace = async (type, id) => {
  // Закрываем окно детализации
  showWorkplaceModal.value = false
  
  // Загружаем полные данные сущности
  const entityData = await fetchEntityData(type, id)
  
  if (entityData) {
    // Небольшая задержка для плавного перехода
    setTimeout(() => {
      openEditModal(type, entityData)
    }, 100)
  } else {
    showError(`Не удалось загрузить данные для редактирования`)
  }
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

// Открытие деталей рабочего места
const openWorkplaceDetails = async (id) => {
  try {
    const response = await axios.get(`${API}/workplaces/${id}/`)
    workplaceDetails.value = response.data
    showWorkplaceModal.value = true
  } catch (error) {
    console.error('Ошибка загрузки деталей:', error)
    showError('Ошибка загрузки деталей рабочего места')
  }
}

const closeWorkplaceModal = () => {
  showWorkplaceModal.value = false
  workplaceDetails.value = null
}

// Загрузка истории замен для ИБП
const fetchUPSBatteryHistory = async (upsId) => {
  try {
    const response = await axios.get(`${API}/battery-history/?ups=${upsId}`)
    upsBatteryHistory.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки истории:', error)
    showError('Ошибка загрузки истории замен')
  }
}

// Открытие модального окна обслуживания ИБП
const openUPSServiceModal = async (ups) => {
  selectedUPSForService.value = ups
  await fetchUPSBatteryHistory(ups.id)
  newBattery.value = {
    old_battery_serial: '',
    new_battery_serial: '',
    performed_by: '',
    comment: ''
  }
  showUPSServiceModal.value = true
}

const closeUPSServiceModal = () => {
  showUPSServiceModal.value = false
  selectedUPSForService.value = null
  upsBatteryHistory.value = []
}

// Добавление записи о замене АКБ
const addUPSBatteryHistory = async () => {
  if (!newBattery.value.new_battery_serial) {
    showWarning('Пожалуйста, укажите серийный номер установленного аккумулятора')
    return
  }
  
  try {
    const historyData = {
      ups: selectedUPSForService.value.id,
      old_battery_serial: newBattery.value.old_battery_serial || null,
      new_battery_serial: newBattery.value.new_battery_serial,
      performed_by: newBattery.value.performed_by || null,
      comment: newBattery.value.comment || null
    }
    
    await axios.post(`${API}/battery-history/`, historyData)
    await fetchUPSBatteryHistory(selectedUPSForService.value.id)
    
    // Обновляем данные в поиске
    await performSearch()
    
    newBattery.value = {
      old_battery_serial: '',
      new_battery_serial: '',
      performed_by: '',
      comment: ''
    }
    
    showSuccess('Замена аккумулятора зафиксирована!')
  } catch (error) {
    console.error('Ошибка добавления записи:', error)
    showError('Ошибка добавления записи о замене')
  }
}

// Удаление записи об обслуживании
const deleteUPSBatteryHistory = async (id) => {
  const confirmed = await confirmModal.value.open({
    title: 'Удаление записи',
    message: 'Вы уверены, что хотите удалить эту запись о замене аккумулятора?',
    confirmText: 'Да, удалить',
    type: 'danger'
  })
  
  if (confirmed) {
    try {
      await axios.delete(`${API}/battery-history/${id}/`)
      await fetchUPSBatteryHistory(selectedUPSForService.value.id)
      await performSearch()
      showSuccess('Запись удалена!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления записи')
    }
  }
}

// Открытие модального окна редактирования
const openEditModal = (type, entity) => {
  editEntityType.value = type
  editEntityId.value = entity.id
  editData.value = { ...entity }
  
  if (type === 'employee' && entity.department) {
    selectedDepartment.value = allDepartments.value.find(d => d.id === entity.department) || null
  } else {
    selectedDepartment.value = null
  }
  
  departmentSearch.value = ''
  departmentSearchResults.value = []
  showEditModal.value = true
}

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

.card-actions {
  display: flex;
  gap: 5px;
  align-items: center;
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

.service-icon-btn {
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  color: #f39c12;
  transition: all 0.2s;
}

.service-icon-btn:hover {
  background: #f39c12;
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
  z-index: 1000;
}

.modal-higher {
  z-index: 1002 !important;
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

/* Детали рабочего места */
.workplace-details {
  margin-top: 0.5rem;
}

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

.sub-entity-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.edit-link {
  color: #3498db;
  font-size: 0.7rem;
  cursor: pointer;
}

.service-small-btn {
  background: none;
  border: none;
  font-size: 0.85rem;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  color: #f39c12;
  transition: all 0.2s;
}

.service-small-btn:hover {
  background: #f39c12;
  color: white;
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

/* Обслуживание ИБП */
.service-form {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
}

.service-form h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
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

.submit-btn.small {
  width: auto;
  padding: 8px 16px;
  margin-top: 0;
  font-size: 0.9rem;
}

.history-section {
  max-height: 300px;
  overflow-y: auto;
}

.history-section h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.history-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 10px;
  border-left: 3px solid #1abc9c;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  padding-bottom: 5px;
  border-bottom: 1px solid #eee;
}

.history-date {
  font-weight: 600;
  color: #1abc9c;
  font-size: 0.8rem;
}

.delete-small {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  color: #e74c3c;
  padding: 2px 6px;
  border-radius: 4px;
}

.delete-small:hover {
  background: #e74c3c;
  color: white;
}

.history-details {
  font-size: 0.8rem;
  line-height: 1.5;
}

.history-details div {
  margin-bottom: 4px;
}

.no-data {
  color: #999;
  font-style: italic;
  text-align: center;
  padding: 20px;
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
  max-height: 200px;
  overflow-y: auto;
  z-index: 1003;
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
  
  .form-row {
    flex-direction: column;
  }
  
  .form-row .form-group {
    margin-bottom: 1rem;
  }
}
</style>