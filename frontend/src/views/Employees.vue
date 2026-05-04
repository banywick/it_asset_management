<template>
  <div class="page">
    <h1>👥 Сотрудники</h1>

    <!-- Форма добавления сотрудника -->
    <div class="form-card">
      <h3>➕ Добавить нового сотрудника</h3>

      <div class="form-row">
        <div class="form-group">
          <label>Фамилия:</label>
          <input 
            v-model="newEmployee.last_name" 
            placeholder="Фамилия"
            class="search-input"
            required
          >
        </div>
        
        <div class="form-group">
          <label>Имя:</label>
          <input 
            v-model="newEmployee.first_name" 
            placeholder="Имя"
            class="search-input"
            required
          >
        </div>
        
        <div class="form-group">
          <label>Отчество:</label>
          <input 
            v-model="newEmployee.patronymic" 
            placeholder="Отчество (необязательно)"
            class="search-input"
          >
        </div>
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
            placeholder="Введите название отдела..."
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

      <button @click="addEmployee" class="submit-btn">💾 Создать сотрудника</button>
    </div>

    <!-- Список сотрудников с пагинацией -->
    <div class="list">
      <h3>📋 Список сотрудников</h3>
      
      <div class="cards-grid">
        <div v-for="emp in paginatedEmployees" :key="emp.id" class="card">
          <div class="card-header">
            <div class="employee-name">
              <strong>{{ emp.last_name }} {{ emp.first_name }} {{ emp.patronymic || '' }}</strong>
            </div>
            <div class="card-actions">
              <button @click="openEditModal(emp)" class="edit-btn" title="Редактировать">✏️</button>
              <button @click="deleteEmployee(emp.id)" class="delete-btn" title="Удалить">🗑️</button>
            </div>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="label">📍 Отдел:</span>
              <span class="value">{{ emp.department_name || 'Не указан' }}</span>
            </div>
            
            <!-- Ссылка на рабочее место -->
            <div v-if="getEmployeeWorkplace(emp.id)" class="info-row workplace-link" @click="openWorkplaceModal(emp)">
              <span class="label">🏢 Рабочее место:</span>
              <span class="value link">Подробнее →</span>
            </div>
            <div v-else class="info-row no-workplace">
              <span class="label">🏢 Рабочее место:</span>
              <span class="value">Не создано</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Пагинация -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="currentPage--" 
          :disabled="currentPage === 1"
          class="page-btn"
        >
          ◀ Предыдущая
        </button>
        <span class="page-info">
          Страница {{ currentPage }} из {{ totalPages }}
        </span>
        <button 
          @click="currentPage++" 
          :disabled="currentPage === totalPages"
          class="page-btn"
        >
          Следующая ▶
        </button>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content modal-large">
        <h3>✏️ Редактировать сотрудника</h3>
        
        <div class="form-group">
          <label>Фамилия:</label>
          <input v-model="editEmployee.last_name" class="search-input">
        </div>
        
        <div class="form-group">
          <label>Имя:</label>
          <input v-model="editEmployee.first_name" class="search-input">
        </div>
        
        <div class="form-group">
          <label>Отчество:</label>
          <input v-model="editEmployee.patronymic" class="search-input">
        </div>
        
        <!-- Отдел с поиском в модальном окне -->
        <div class="form-group">
          <label>Отдел:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="editDepartmentSearch" 
              @input="searchEditDepartments" 
              @focus="searchEditDepartments"
              placeholder="Введите название отдела..."
              class="search-input"
            >
            <div v-if="editDepartmentSearchResults.length" class="search-results">
              <div 
                v-for="dep in editDepartmentSearchResults" 
                :key="dep.id" 
                @click="selectEditDepartment(dep)"
                class="search-result-item"
              >
                {{ dep.name }}
              </div>
            </div>
          </div>
          <div v-if="editSelectedDepartment" class="selected-tag">
            {{ editSelectedDepartment.name }}
            <button @click="editSelectedDepartment = null" class="remove-btn">×</button>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateEmployee" class="save-btn">💾 Сохранить</button>
          <button @click="showEditModal = false" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно детализации рабочего места -->
    <div v-if="showWorkplaceModal" class="modal">
      <div class="modal-content modal-large">
        <h3>🏢 Детали рабочего места</h3>
        <p class="modal-subtitle">Сотрудник: <strong>{{ selectedEmployeeForWorkplace?.full_name }}</strong></p>
        
        <div v-if="selectedWorkplace" class="workplace-details">
          <!-- Рабочее место -->
          <div class="detail-section">
            <div class="section-title">📍 Информация о рабочем месте</div>
            <div class="detail-row">
              <span class="detail-label">🏙️ Город:</span>
              <span class="detail-value">{{ selectedWorkplace.city_name || 'Не указан' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">🖨️ МФУ:</span>
              <span class="detail-value">{{ selectedWorkplace.mfp_detail?.model || 'Не указан' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">🔋 ИБП:</span>
              <span class="detail-value">
                {{ selectedWorkplace.ups_detail?.model || 'Не указан' }}
                <span v-if="selectedWorkplace.ups_detail?.battery_replaced_at" class="battery-date">
                  (АКБ заменён: {{ formatDate(selectedWorkplace.ups_detail.battery_replaced_at) }})
                </span>
              </span>
            </div>
            <div v-if="selectedWorkplace.ups_detail?.comment" class="detail-row">
              <span class="detail-label">💬 Комментарий ИБП:</span>
              <span class="detail-value">{{ selectedWorkplace.ups_detail.comment }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">📊 Статус:</span>
              <span :class="['status-badge', getStatusClass(selectedWorkplace.status)]">
                {{ getStatusText(selectedWorkplace.status) }}
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">📅 Создано:</span>
              <span class="detail-value">{{ formatDate(selectedWorkplace.created_at) }}</span>
            </div>
          </div>

          <!-- Компьютер -->
          <div v-if="selectedComputer" class="detail-section">
            <div class="section-title">🖥️ Закрепленный компьютер</div>
            <div class="detail-row">
              <span class="detail-label">🆔 Номер ОС:</span>
              <span class="detail-value">{{ selectedComputer.asset_number || 'Не указан' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">💻 Системный блок:</span>
              <span class="detail-value">{{ selectedComputer.system_unit || 'Не указан' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">🖥️ Мониторы:</span>
              <span class="detail-value">
                <span v-if="selectedComputer.monitors_detail && selectedComputer.monitors_detail.length">
                  {{ selectedComputer.monitors_detail.map(m => m.brand).join(', ') }}
                </span>
                <span v-else class="no-data">нет</span>
              </span>
            </div>
            <div class="detail-row">
              <span class="detail-label">⌨️ Клавиатура:</span>
              <span class="detail-value">{{ selectedComputer.has_keyboard ? '✅ есть' : '❌ нет' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">🖱️ Мышь:</span>
              <span class="detail-value">{{ selectedComputer.has_mouse ? '✅ есть' : '❌ нет' }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-label">📍 Отдел:</span>
              <span class="detail-value">{{ selectedComputer.department_name || 'Не указан' }}</span>
            </div>
            <div v-if="selectedComputer.needs_upgrade" class="detail-row warning-row">
              <span class="detail-label">⚠️ Модернизация:</span>
              <span class="detail-value">Требуется модернизация</span>
            </div>
          </div>
          <div v-else class="detail-section no-data-section">
            <div class="section-title">🖥️ Закрепленный компьютер</div>
            <p class="no-data">Компьютер не закреплен</p>
          </div>
        </div>
        <div v-else class="no-workplace-details">
          <p>😕 Рабочее место не найдено</p>
        </div>
        
        <div class="modal-buttons">
          <button @click="showWorkplaceModal = false" class="cancel-btn">Закрыть</button>
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

const API = '/api'

// Данные
const employees = ref([])
const workplaces = ref([])
const computers = ref([])
const allDepartments = ref([])

// Поиск отделов для формы добавления
const departmentSearch = ref('')
const departmentSearchResults = ref([])

// Выбранные значения для добавления
const selectedDepartment = ref(null)

// Пагинация
const currentPage = ref(1)
const itemsPerPage = 9 // 3x3 сетка

// Модальные окна
const showEditModal = ref(false)
const showWorkplaceModal = ref(false)

// Данные для нового сотрудника
const newEmployee = ref({
  last_name: '',
  first_name: '',
  patronymic: '',
  department: null
})

// Данные для редактирования
const editEmployee = ref({
  id: null,
  last_name: '',
  first_name: '',
  patronymic: '',
  department: null
})

// Поиск для модального окна
const editDepartmentSearch = ref('')
const editDepartmentSearchResults = ref([])
const editSelectedDepartment = ref(null)

// Данные для модального окна рабочего места
const selectedEmployeeForWorkplace = ref(null)
const selectedWorkplace = ref(null)
const selectedComputer = ref(null)

const confirmModal = ref(null)

// Пагинированные сотрудники
const paginatedEmployees = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return employees.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(employees.value.length / itemsPerPage)
})

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

// Получение рабочего места сотрудника
const getEmployeeWorkplace = (employeeId) => {
  return workplaces.value.find(wp => wp.employee === employeeId)
}

// Получение компьютера закрепленного за сотрудником
const getEmployeeComputer = (employeeId) => {
  return computers.value.find(comp => comp.assigned_to === employeeId)
}

// Загрузка данных
const fetchAllData = async () => {
  try {
    const [empRes, depRes, wpRes, compRes] = await Promise.all([
      axios.get(`${API}/employees/`),
      axios.get(`${API}/departments/`),
      axios.get(`${API}/workplaces/`),
      axios.get(`${API}/computers/`)
    ])
    employees.value = empRes.data
    allDepartments.value = depRes.data
    workplaces.value = wpRes.data
    computers.value = compRes.data
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    showError('Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message))
  }
}

// Поиск отделов для формы добавления
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
  newEmployee.value.department = department.id
  departmentSearch.value = ''
  departmentSearchResults.value = []
}

// Добавление сотрудника
const addEmployee = async () => {
  if (!newEmployee.value.last_name) {
    showWarning('Пожалуйста, укажите фамилию сотрудника')
    return
  }
  
  if (!newEmployee.value.first_name) {
    showWarning('Пожалуйста, укажите имя сотрудника')
    return
  }
  
  // Проверка на дубликат
  const existingEmployee = employees.value.find(emp => 
    emp.last_name.toLowerCase() === newEmployee.value.last_name.toLowerCase() &&
    emp.first_name.toLowerCase() === newEmployee.value.first_name.toLowerCase()
  )
  
  if (existingEmployee) {
    showWarning('Такой сотрудник уже существует!')
    return
  }
  
  try {
    const employeeData = {
      last_name: newEmployee.value.last_name,
      first_name: newEmployee.value.first_name,
      patronymic: newEmployee.value.patronymic || null,
      department: newEmployee.value.department || null
    }
    
    await axios.post(`${API}/employees/`, employeeData)
    
    // Сброс формы
    newEmployee.value = {
      last_name: '',
      first_name: '',
      patronymic: '',
      department: null
    }
    selectedDepartment.value = null
    departmentSearch.value = ''
    
    await fetchAllData()
    // Сбрасываем пагинацию на первую страницу
    currentPage.value = 1
    showSuccess('Сотрудник успешно добавлен!')
  } catch (error) {
    console.error('Ошибка добавления:', error)
    showError('Ошибка добавления сотрудника: ' + (error.response?.data?.detail || error.message))
  }
}

// Поиск для модального окна (отделы)
const searchEditDepartments = () => {
  if (!editDepartmentSearch.value) {
    editDepartmentSearchResults.value = []
    return
  }
  editDepartmentSearchResults.value = allDepartments.value.filter(d => 
    d.name.toLowerCase().includes(editDepartmentSearch.value.toLowerCase())
  ).slice(0, 10)
}

const selectEditDepartment = (department) => {
  editSelectedDepartment.value = department
  editEmployee.value.department = department.id
  editDepartmentSearch.value = ''
  editDepartmentSearchResults.value = []
}

// Открытие модального окна редактирования
const openEditModal = (employee) => {
  editEmployee.value = {
    id: employee.id,
    last_name: employee.last_name,
    first_name: employee.first_name,
    patronymic: employee.patronymic || '',
    department: employee.department
  }
  editSelectedDepartment.value = allDepartments.value.find(d => d.id === employee.department) || null
  editDepartmentSearch.value = ''
  editDepartmentSearchResults.value = []
  showEditModal.value = true
}

// Обновление сотрудника
const updateEmployee = async () => {
  if (!editEmployee.value.last_name) {
    showWarning('Пожалуйста, укажите фамилию сотрудника')
    return
  }
  
  if (!editEmployee.value.first_name) {
    showWarning('Пожалуйста, укажите имя сотрудника')
    return
  }
  
  try {
    const employeeData = {
      last_name: editEmployee.value.last_name,
      first_name: editEmployee.value.first_name,
      patronymic: editEmployee.value.patronymic || null,
      department: editEmployee.value.department || null
    }
    
    await axios.put(`${API}/employees/${editEmployee.value.id}/`, employeeData)
    showEditModal.value = false
    await fetchAllData()
    showSuccess('Сотрудник успешно обновлен!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления сотрудника: ' + (error.response?.data?.detail || error.message))
  }
}

// Открытие модального окна с деталями рабочего места
const openWorkplaceModal = async (employee) => {
  const workplace = getEmployeeWorkplace(employee.id)
  if (workplace) {
    try {
      // Получаем полные данные рабочего места с деталями МФУ и ИБП
      const [workplaceRes, computerRes] = await Promise.all([
        axios.get(`${API}/workplaces/${workplace.id}/`),
        axios.get(`${API}/computers/?assigned_to=${employee.id}`)
      ])
      selectedWorkplace.value = workplaceRes.data
      selectedComputer.value = computerRes.data[0] || null
      selectedEmployeeForWorkplace.value = employee
      showWorkplaceModal.value = true
    } catch (error) {
      console.error('Ошибка загрузки деталей:', error)
      showError('Ошибка загрузки деталей рабочего места')
    }
  }
}

// Удаление сотрудника
const deleteEmployee = async (id) => {
  // Проверяем, есть ли у сотрудника рабочее место
  const hasWorkplace = workplaces.value.some(wp => wp.employee === id)
  let message = 'Вы уверены, что хотите удалить этого сотрудника?'
  if (hasWorkplace) {
    message = 'У этого сотрудника есть рабочее место. При удалении сотрудника рабочее место также будет удалено. Продолжить?'
  }
  
  const confirmed = await confirmModal.value.open({
    title: 'Удаление сотрудника',
    message: message,
    confirmText: 'Да, удалить',
    type: 'danger'
  })

  if (confirmed) {
    try {
      await axios.delete(`${API}/employees/${id}/`)
      await fetchAllData()
      // Если после удаления на странице не осталось элементов, переходим на предыдущую
      if (paginatedEmployees.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
      showSuccess('Сотрудник удален!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления сотрудника')
    }
  }
}

onMounted(fetchAllData)
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

.employee-name strong {
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
  min-width: 100px;
  flex-shrink: 0;
}

.value {
  color: #333;
}

.workplace-link {
  cursor: pointer;
  transition: all 0.2s;
  padding: 4px 8px;
  margin: -4px -8px;
  border-radius: 6px;
}

.workplace-link:hover {
  background: rgba(26, 188, 156, 0.1);
}

.workplace-link .link {
  color: #1abc9c;
  font-weight: 500;
}

.no-workplace .value {
  color: #999;
  font-style: italic;
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

/* Модальное окно деталей рабочего места */
.workplace-details {
  margin: 1rem 0;
  max-height: 60vh;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 1.5rem;
  padding: 0.5rem;
  border-radius: 12px;
  background: #f9f9f9;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #1abc9c;
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #1abc9c;
  display: inline-block;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
  padding: 6px 8px;
  border-bottom: 1px solid #eee;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-weight: 600;
  color: #555;
  min-width: 130px;
  flex-shrink: 0;
}

.detail-value {
  color: #333;
  flex: 1;
}

.warning-row {
  background: #fff3cd;
  border-radius: 6px;
}

.warning-row .detail-label,
.warning-row .detail-value {
  color: #856404;
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

.no-data {
  color: #999;
  font-style: italic;
}

.no-data-section {
  text-align: center;
  padding: 1rem;
}

.no-data-section .no-data {
  margin-top: 0.5rem;
}

.no-workplace-details {
  text-align: center;
  padding: 2rem;
  color: #999;
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
  max-width: 650px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
}

.modal-large {
  max-width: 650px !important;
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
  
  .detail-row {
    flex-direction: column;
  }
  
  .detail-label {
    margin-bottom: 4px;
  }
  
  .section-title {
    font-size: 0.9rem;
  }
}
</style>