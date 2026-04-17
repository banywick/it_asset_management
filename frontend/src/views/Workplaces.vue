<template>
  <div class="page">
    <h1>📌 Перемещения сотрудников и рабочие места</h1>
    <p class="note">У одного сотрудника может быть несколько рабочих мест</p>

    <div class="form-card">
      <h3>➕ Создать рабочее место</h3>
      
      <!-- Поиск сотрудника -->
      <div class="form-group">
        <label>Выберите сотрудника:</label>
        <div class="search-wrapper">
          <input 
            type="text" 
            v-model="employeeSearch" 
            @input="searchEmployees" 
            @focus="searchEmployees"
            placeholder="Введите фамилию или имя сотрудника..."
            class="search-input"
          >
          <div v-if="employeeSearchResults.length" class="search-results">
            <div 
              v-for="emp in employeeSearchResults" 
              :key="emp.id" 
              @click="selectEmployee(emp)"
              class="search-result-item"
            >
              {{ emp.last_name }} {{ emp.first_name }} {{ emp.patronymic || '' }} - {{ emp.department_name || 'нет отдела' }}
            </div>
          </div>
        </div>
        <div v-if="selectedEmployee" class="selected-tag">
          {{ selectedEmployee.last_name }} {{ selectedEmployee.first_name }} {{ selectedEmployee.patronymic || '' }}
          <span v-if="selectedEmployee.department_name" class="department-tag">
            📍 {{ selectedEmployee.department_name }}
          </span>
          <button @click="selectedEmployee = null" class="remove-btn">×</button>
        </div>
      </div>

      <!-- Город/Локация -->
      <div class="form-group">
        <label>Город/Локация:</label>
        <select v-model="form.city" class="search-input">
          <option :value="null">Выберите город</option>
          <option v-for="city in locations" :key="city.id" :value="city.id">
            {{ city.name }}
          </option>
        </select>
      </div>

      <!-- МФУ -->
      <div class="form-group">
        <label>МФУ (необязательно):</label>
        <div class="search-wrapper">
          <input 
            type="text" 
            v-model="mfpSearch" 
            @input="searchMFP" 
            @focus="searchMFP"
            placeholder="Введите модель или номер ОС МФУ..."
            class="search-input"
          >
          <div v-if="mfpSearchResults.length" class="search-results">
            <div 
              v-for="mfp in mfpSearchResults" 
              :key="mfp.id" 
              @click="selectMFP(mfp)"
              class="search-result-item"
            >
              ОС №{{ mfp.asset_number }} - {{ mfp.model }}
            </div>
          </div>
        </div>
        <div v-if="selectedMFP" class="selected-tag">
          ОС №{{ selectedMFP.asset_number }} - {{ selectedMFP.model }}
          <button @click="selectedMFP = null" class="remove-btn">×</button>
        </div>
      </div>

      <!-- Бесперебойник -->
      <div class="form-group">
        <label>Бесперебойник (необязательно):</label>
        <div class="search-wrapper">
          <input 
            type="text" 
            v-model="upsSearch" 
            @input="searchUPS" 
            @focus="searchUPS"
            placeholder="Введите модель или номер ОС ИБП..."
            class="search-input"
          >
          <div v-if="upsSearchResults.length" class="search-results">
            <div 
              v-for="ups in upsSearchResults" 
              :key="ups.id" 
              @click="selectUPS(ups)"
              class="search-result-item"
            >
              ОС №{{ ups.asset_number }} - {{ ups.model }}
              <span v-if="ups.battery_replaced_at" class="battery-info">
                🔋 Замена АКБ: {{ formatDate(ups.battery_replaced_at) }}
              </span>
            </div>
          </div>
        </div>
        <div v-if="selectedUPS" class="selected-tag">
          ОС №{{ selectedUPS.asset_number }} - {{ selectedUPS.model }}
          <span v-if="selectedUPS.battery_replaced_at" class="battery-date">
            🔋 АКБ заменён: {{ formatDate(selectedUPS.battery_replaced_at) }}
          </span>
          <button @click="selectedUPS = null" class="remove-btn">×</button>
        </div>
      </div>

      <!-- Статус -->
      <div class="form-group">
        <label>Статус:</label>
        <select v-model="form.status" class="search-input">
          <option value="active">✅ Активно</option>
          <option value="inactive">❌ Неактивно</option>
          <option value="maintenance">🔧 На обслуживании</option>
          <option value="repair">⚠️ Требует ремонта</option>
        </select>
      </div>

      <button @click="createWorkplace" class="submit-btn">➕ Создать рабочее место</button>
    </div>

    <!-- Список рабочих мест -->
    <div class="list">
      <h3>📋 Рабочие места</h3>
      <div class="cards-grid">
        <div v-for="wp in workplaces" :key="wp.id" class="card">
          <div class="card-header">
            <div class="employee-info">
              <strong>{{ wp.employee_name }}</strong>
              <span v-if="wp.department_name" class="department-badge">
                📍 {{ wp.department_name }}
              </span>
            </div>
            <button @click="deleteWorkplace(wp.id)" class="delete-btn" title="Удалить">🗑️</button>
          </div>
          <div class="card-body">
            <!-- Город -->
            <div class="info-row clickable" @click="openCityEdit(wp)">
              <span class="label">🏙️ Город:</span>
              <span class="value">{{ wp.city_name || 'Не указан' }}</span>
              <span class="edit-hint">✏️ нажмите для редактирования</span>
            </div>
            
            <!-- МФУ -->
            <div class="info-row clickable" @click="openMFPEdit(wp)">
              <span class="label">🖨️ МФУ:</span>
              <span class="value">{{ wp.mfp_detail?.model || 'Не указан' }}</span>
              <span class="edit-hint">✏️ нажмите для редактирования</span>
            </div>
            
            <!-- ИБП -->
            <div class="info-row clickable" @click="openUPSEdit(wp)">
              <span class="label">🔋 ИБП:</span>
              <span class="value">
                {{ wp.ups_detail?.model || 'Не указан' }}
                <span v-if="wp.ups_detail?.battery_replaced_at" class="battery-date">
                  (АКБ заменён: {{ formatDate(wp.ups_detail.battery_replaced_at) }})
                </span>
              </span>
              <span class="edit-hint">✏️ нажмите для редактирования</span>
            </div>
            
            <!-- Комментарий ИБП -->
            <div v-if="wp.ups_detail?.comment" class="info-row comment-row">
              <span class="label">💬 Комментарий ИБП:</span>
              <span class="value comment">{{ wp.ups_detail.comment }}</span>
            </div>
            
            <!-- Статус -->
            <div class="info-row clickable" @click="openStatusEdit(wp)">
              <span class="label">📊 Статус:</span>
              <span :class="['status-badge', getStatusClass(wp.status)]">
                {{ getStatusText(wp.status) }}
              </span>
              <span class="edit-hint">✏️ нажмите для редактирования</span>
            </div>
            
            <!-- Дата создания -->
            <div class="info-row">
              <span class="label">📅 Создано:</span>
              <span class="value">{{ formatDate(wp.created_at) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Модальные окна для редактирования (остаются без изменений) -->
    <!-- Город -->
    <div v-if="showCityModal" class="modal">
      <div class="modal-content">
        <h3>✏️ Изменить город</h3>
        <p class="modal-subtitle">Для рабочего места: <strong>{{ editWorkplace.employee_name }}</strong></p>
        <select v-model="editCityValue" class="search-input">
          <option :value="null">Выберите город</option>
          <option v-for="city in locations" :key="city.id" :value="city.id">
            {{ city.name }}
          </option>
        </select>
        <div class="modal-buttons">
          <button @click="updateCity" class="save-btn">💾 Сохранить</button>
          <button @click="showCityModal = false" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- МФУ с поиском -->
    <div v-if="showMFPModal" class="modal">
      <div class="modal-content modal-large">
        <h3>✏️ Изменить МФУ</h3>
        <p class="modal-subtitle">Для рабочего места: <strong>{{ editWorkplace.employee_name }}</strong></p>
        
        <div class="form-group">
          <label>Поиск МФУ:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="editMFPSearch" 
              @input="searchEditMFP" 
              @focus="searchEditMFP"
              placeholder="Введите модель или номер ОС..."
              class="search-input"
            >
            <div v-if="editMFPSearchResults.length" class="search-results">
              <div 
                v-for="mfp in editMFPSearchResults" 
                :key="mfp.id" 
                @click="selectEditMFP(mfp)"
                class="search-result-item"
              >
                ОС №{{ mfp.asset_number }} - {{ mfp.model }}
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label>Или выберите из списка:</label>
          <div class="selected-items-list">
            <div 
              v-for="mfp in allMFPs" 
              :key="mfp.id" 
              @click="selectEditMFP(mfp)"
              class="selectable-item"
              :class="{ selected: editMFPValue === mfp.id }"
            >
              ОС №{{ mfp.asset_number }} - {{ mfp.model }}
            </div>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateMFP" class="save-btn">💾 Сохранить</button>
          <button @click="closeMFPModal" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- ИБП с поиском -->
    <div v-if="showUPSModal" class="modal">
      <div class="modal-content modal-large">
        <h3>✏️ Изменить ИБП</h3>
        <p class="modal-subtitle">Для рабочего места: <strong>{{ editWorkplace.employee_name }}</strong></p>
        
        <div class="form-group">
          <label>Поиск ИБП:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="editUPSSearch" 
              @input="searchEditUPS" 
              @focus="searchEditUPS"
              placeholder="Введите модель или номер ОС..."
              class="search-input"
            >
            <div v-if="editUPSSearchResults.length" class="search-results">
              <div 
                v-for="ups in editUPSSearchResults" 
                :key="ups.id" 
                @click="selectEditUPS(ups)"
                class="search-result-item"
              >
                ОС №{{ ups.asset_number }} - {{ ups.model }}
                <span v-if="ups.battery_replaced_at" class="battery-info">
                  🔋 АКБ заменён: {{ formatDate(ups.battery_replaced_at) }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label>Или выберите из списка:</label>
          <div class="selected-items-list">
            <div 
              v-for="ups in allUPS" 
              :key="ups.id" 
              @click="selectEditUPS(ups)"
              class="selectable-item"
              :class="{ selected: editUPSValue === ups.id }"
            >
              ОС №{{ ups.asset_number }} - {{ ups.model }}
              <span v-if="ups.battery_replaced_at" class="battery-date">
                (АКБ заменён: {{ formatDate(ups.battery_replaced_at) }})
              </span>
            </div>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateUPS" class="save-btn">💾 Сохранить</button>
          <button @click="closeUPSModal" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Статус -->
    <div v-if="showStatusModal" class="modal">
      <div class="modal-content">
        <h3>✏️ Изменить статус</h3>
        <p class="modal-subtitle">Для рабочего места: <strong>{{ editWorkplace.employee_name }}</strong></p>
        <select v-model="editStatusValue" class="search-input">
          <option value="active">✅ Активно</option>
          <option value="inactive">❌ Неактивно</option>
          <option value="maintenance">🔧 На обслуживании</option>
          <option value="repair">⚠️ Требует ремонта</option>
        </select>
        <div class="modal-buttons">
          <button @click="updateStatus" class="save-btn">💾 Сохранить</button>
          <button @click="showStatusModal = false" class="cancel-btn">Отмена</button>
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

const employees = ref([])
const workplaces = ref([])
const locations = ref([])
const allMFPs = ref([])
const allUPS = ref([])

const selectedEmployee = ref(null)
const selectedMFP = ref(null)
const selectedUPS = ref(null)

const employeeSearch = ref('')
const employeeSearchResults = ref([])
const mfpSearch = ref('')
const mfpSearchResults = ref([])
const upsSearch = ref('')
const upsSearchResults = ref([])

const form = ref({
  city: null,
  status: 'active',
  mfp: null,
  ups: null
})

// Модальные окна для редактирования
const showCityModal = ref(false)
const showMFPModal = ref(false)
const showUPSModal = ref(false)
const showStatusModal = ref(false)

// Данные для редактирования
const editWorkplace = ref({
  id: null,
  employee_name: '',
  city: null,
  mfp: null,
  ups: null,
  status: 'active'
})
const editCityValue = ref(null)
const editMFPValue = ref(null)
const editUPSValue = ref(null)
const editStatusValue = ref('active')

// Поиск для модальных окон МФУ и ИБП
const editMFPSearch = ref('')
const editMFPSearchResults = ref([])
const editUPSSearch = ref('')
const editUPSSearchResults = ref([])

const confirmModal = ref(null)

// Форматирование даты
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU')
}

// Статусы
const getStatusText = (status) => {
  const statusMap = {
    'active': 'Активно',
    'inactive': 'Неактивно',
    'maintenance': 'На обслуживании',
    'repair': 'Требует ремонта'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const classMap = {
    'active': 'status-active',
    'inactive': 'status-inactive',
    'maintenance': 'status-maintenance',
    'repair': 'status-repair'
  }
  return classMap[status] || ''
}

// Загрузка данных
const fetchData = async () => {
  try {
    const [empRes, wpRes, locRes, mfpRes, upsRes] = await Promise.all([
      axios.get(`${API}/employees/`),
      axios.get(`${API}/workplaces/`),
      axios.get(`${API}/locations/`),
      axios.get(`${API}/mfps/`),
      axios.get(`${API}/ups/`)
    ])
    employees.value = empRes.data
    workplaces.value = wpRes.data
    locations.value = locRes.data
    allMFPs.value = mfpRes.data
    allUPS.value = upsRes.data
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    showError('Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message))
  }
}

// Поиск сотрудников
const searchEmployees = () => {
  if (!employeeSearch.value) {
    employeeSearchResults.value = []
    return
  }
  employeeSearchResults.value = employees.value.filter(emp => {
    const fullName = `${emp.last_name} ${emp.first_name} ${emp.patronymic || ''}`.toLowerCase()
    return fullName.includes(employeeSearch.value.toLowerCase())
  }).slice(0, 10)
}

const selectEmployee = (employee) => {
  selectedEmployee.value = employee
  employeeSearch.value = ''
  employeeSearchResults.value = []
}

// Поиск МФУ для формы добавления
const searchMFP = () => {
  if (!mfpSearch.value) {
    mfpSearchResults.value = []
    return
  }
  mfpSearchResults.value = allMFPs.value.filter(mfp => 
    mfp.asset_number.toLowerCase().includes(mfpSearch.value.toLowerCase()) ||
    mfp.model.toLowerCase().includes(mfpSearch.value.toLowerCase())
  ).slice(0, 10)
}

const selectMFP = (mfp) => {
  selectedMFP.value = mfp
  form.value.mfp = mfp.id
  mfpSearch.value = ''
  mfpSearchResults.value = []
}

// Поиск ИБП для формы добавления
const searchUPS = () => {
  if (!upsSearch.value) {
    upsSearchResults.value = []
    return
  }
  upsSearchResults.value = allUPS.value.filter(ups => 
    ups.asset_number.toLowerCase().includes(upsSearch.value.toLowerCase()) ||
    ups.model.toLowerCase().includes(upsSearch.value.toLowerCase())
  ).slice(0, 10)
}

const selectUPS = (ups) => {
  selectedUPS.value = ups
  form.value.ups = ups.id
  upsSearch.value = ''
  upsSearchResults.value = []
}

// Поиск МФУ для модального окна редактирования
const searchEditMFP = () => {
  if (!editMFPSearch.value) {
    editMFPSearchResults.value = []
    return
  }
  editMFPSearchResults.value = allMFPs.value.filter(mfp => 
    mfp.asset_number.toLowerCase().includes(editMFPSearch.value.toLowerCase()) ||
    mfp.model.toLowerCase().includes(editMFPSearch.value.toLowerCase())
  ).slice(0, 10)
}

const selectEditMFP = (mfp) => {
  editMFPValue.value = mfp.id
  editMFPSearch.value = ''
  editMFPSearchResults.value = []
}

// Поиск ИБП для модального окна редактирования
const searchEditUPS = () => {
  if (!editUPSSearch.value) {
    editUPSSearchResults.value = []
    return
  }
  editUPSSearchResults.value = allUPS.value.filter(ups => 
    ups.asset_number.toLowerCase().includes(editUPSSearch.value.toLowerCase()) ||
    ups.model.toLowerCase().includes(editUPSSearch.value.toLowerCase())
  ).slice(0, 10)
}

const selectEditUPS = (ups) => {
  editUPSValue.value = ups.id
  editUPSSearch.value = ''
  editUPSSearchResults.value = []
}

// Создание рабочего места
const createWorkplace = async () => {
  if (!selectedEmployee.value) {
    showWarning('Пожалуйста, выберите сотрудника')
    return
  }
  
  try {
    const workplaceData = {
      employee: selectedEmployee.value.id,
      location: 'Рабочее место',
      city: form.value.city || null,
      status: form.value.status,
      mfp: form.value.mfp || null,
      ups: form.value.ups || null,
      is_active: form.value.status === 'active'
    }
    
    await axios.post(`${API}/workplaces/`, workplaceData)
    
    form.value = { city: null, status: 'active', mfp: null, ups: null }
    selectedEmployee.value = null
    selectedMFP.value = null
    selectedUPS.value = null
    employeeSearch.value = ''
    mfpSearch.value = ''
    upsSearch.value = ''
    
    await fetchData()
    showSuccess('Рабочее место успешно создано!')
  } catch (error) {
    console.error('Ошибка создания:', error)
    showError('Ошибка создания рабочего места: ' + (error.response?.data?.detail || error.message))
  }
}

// Открытие модальных окон для редактирования
const openCityEdit = (workplace) => {
  editWorkplace.value = {
    id: workplace.id,
    employee_name: workplace.employee_name,
    city: workplace.city
  }
  editCityValue.value = workplace.city
  showCityModal.value = true
}

const openMFPEdit = (workplace) => {
  editWorkplace.value = {
    id: workplace.id,
    employee_name: workplace.employee_name,
    mfp: workplace.mfp
  }
  editMFPValue.value = workplace.mfp
  editMFPSearch.value = ''
  editMFPSearchResults.value = []
  showMFPModal.value = true
}

const openUPSEdit = (workplace) => {
  editWorkplace.value = {
    id: workplace.id,
    employee_name: workplace.employee_name,
    ups: workplace.ups
  }
  editUPSValue.value = workplace.ups
  editUPSSearch.value = ''
  editUPSSearchResults.value = []
  showUPSModal.value = true
}

const openStatusEdit = (workplace) => {
  editWorkplace.value = {
    id: workplace.id,
    employee_name: workplace.employee_name,
    status: workplace.status
  }
  editStatusValue.value = workplace.status
  showStatusModal.value = true
}

// Закрытие модальных окон
const closeMFPModal = () => {
  showMFPModal.value = false
  editMFPSearch.value = ''
  editMFPSearchResults.value = []
}

const closeUPSModal = () => {
  showUPSModal.value = false
  editUPSSearch.value = ''
  editUPSSearchResults.value = []
}

// Обновление города
const updateCity = async () => {
  try {
    await axios.patch(`${API}/workplaces/${editWorkplace.value.id}/`, {
      city: editCityValue.value
    })
    showCityModal.value = false
    await fetchData()
    showSuccess('Город успешно обновлен!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления города')
  }
}

// Обновление МФУ
const updateMFP = async () => {
  try {
    await axios.patch(`${API}/workplaces/${editWorkplace.value.id}/`, {
      mfp: editMFPValue.value
    })
    closeMFPModal()
    await fetchData()
    showSuccess('МФУ успешно обновлено!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления МФУ')
  }
}

// Обновление ИБП
const updateUPS = async () => {
  try {
    await axios.patch(`${API}/workplaces/${editWorkplace.value.id}/`, {
      ups: editUPSValue.value
    })
    closeUPSModal()
    await fetchData()
    showSuccess('ИБП успешно обновлен!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления ИБП')
  }
}

// Обновление статуса
const updateStatus = async () => {
  try {
    await axios.patch(`${API}/workplaces/${editWorkplace.value.id}/`, {
      status: editStatusValue.value,
      is_active: editStatusValue.value === 'active'
    })
    showStatusModal.value = false
    await fetchData()
    showSuccess('Статус успешно обновлен!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления статуса')
  }
}

// Удаление рабочего места
const deleteWorkplace = async (id) => {
  const confirmed = await confirmModal.value.open({
    title: 'Удаление рабочего места',
    message: 'Вы уверены, что хотите удалить это рабочее место? Это действие нельзя отменить.',
    confirmText: 'Да, удалить',
    type: 'danger'
  })
  
  if (confirmed) {
    try {
      await axios.delete(`${API}/workplaces/${id}/`)
      await fetchData()
      showSuccess('Рабочее место удалено!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления рабочего места')
    }
  }
}

onMounted(fetchData)
</script>

<style scoped>
/* ... все предыдущие стили ... */

/* Новые стили для отдела */
.employee-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.employee-info strong {
  font-size: 1rem;
  color: #2c3e50;
}

.department-badge {
  display: inline-block;
  background: #e8f5e9;
  color: #2c3e50;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: normal;
  width: fit-content;
}

.department-tag {
  display: inline-block;
  background: #e8f5e9;
  color: #2c3e50;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: normal;
  margin-left: 8px;
}

/* Остальные стили из предыдущей версии */
.page {
  max-width: 1400px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.note {
  color: #e67e22;
  margin-bottom: 1.5rem;
  padding: 10px;
  background: #fef5e7;
  border-radius: 8px;
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
  flex-wrap: wrap;
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
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

@media (max-width: 900px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}

.card {
  background: #f8f9fa;
  border-radius: 16px;
  border-left: 5px solid #1abc9c;
  transition: transform 0.2s, box-shadow 0.2s;
  overflow: hidden;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(26, 188, 156, 0.1) 0%, rgba(26, 188, 156, 0.05) 100%);
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.delete-btn {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  color: #e74c3c;
  padding: 5px 10px;
  border-radius: 8px;
  transition: all 0.2s;
}

.delete-btn:hover {
  background: #e74c3c;
  color: white;
}

.card-body {
  padding: 16px 20px;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  font-size: 0.9rem;
  line-height: 1.4;
  padding: 8px 12px;
  border-radius: 10px;
  transition: all 0.2s;
}

.info-row.clickable {
  cursor: pointer;
  background: #ffffff;
  border: 1px solid #e0e0e0;
  transition: all 0.2s;
}

.info-row.clickable:hover {
  background: #fff9e6;
  border-color: #1abc9c;
  transform: translateX(4px);
}

.comment-row {
  background: #fef5e7;
  border-left: 3px solid #f39c12;
}

.label {
  font-weight: 600;
  color: #555;
  min-width: 100px;
  flex-shrink: 0;
}

.value {
  color: #333;
  flex: 1;
}

.value.comment {
  font-style: italic;
  color: #e67e22;
}

.edit-hint {
  font-size: 0.7rem;
  color: #1abc9c;
  opacity: 0;
  transition: opacity 0.2s;
  margin-left: 8px;
  white-space: nowrap;
}

.info-row.clickable:hover .edit-hint {
  opacity: 1;
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
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

.battery-date {
  font-size: 0.7rem;
  color: #27ae60;
  margin-left: 5px;
}

.battery-info {
  font-size: 0.7rem;
  color: #27ae60;
  margin-left: 8px;
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
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.modal-subtitle {
  color: #666;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.modal-content select {
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

.selected-items-list {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-top: 8px;
}

.selectable-item {
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  transition: all 0.2s;
}

.selectable-item:hover {
  background: #f0f0f0;
}

.selectable-item.selected {
  background: #e8f5e9;
  border-left: 3px solid #1abc9c;
}

.selectable-item:last-child {
  border-bottom: none;
}

@media (max-width: 768px) {
  .info-row {
    flex-wrap: wrap;
  }
  
  .label {
    width: 100%;
    margin-bottom: 6px;
  }
  
  .edit-hint {
    white-space: normal;
  }
  
  .modal-content {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .selected-items-list {
    max-height: 200px;
  }
  
  .card-header {
    flex-direction: column;
    gap: 8px;
  }
  
  .delete-btn {
    align-self: flex-end;
  }
}
</style>