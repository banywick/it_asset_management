
<template>
  <div class="page">
    <h1>🖥️ Компьютеры (Основные средства)</h1>

    <!-- Форма добавления компьютера -->
    <div class="form-card">
      <h3>➕ Добавить компьютер</h3>
      
      <div class="form-row">
        <div class="form-group">
          <label>Номер основного средства:</label>
          <input 
            v-model="newComputer.asset_number" 
            placeholder="Например: ПК-001"
            class="main-field"
          >
          <small class="field-hint">По умолчанию: "не определен"</small>
        </div>
        
        <div class="form-group">
          <label>Системный блок:</label>
          <textarea 
            v-model="newComputer.system_unit" 
            placeholder="Введите модель, характеристики и комплектацию системного блока..."
            rows="4"
            class="textarea-field"
          ></textarea>
          <small class="field-hint">Укажите полные характеристики системного блока</small>
        </div>
      </div>

      <!-- Мониторы с поиском (множественный выбор) -->
      <div class="form-group">
        <label>Мониторы (можно выбрать несколько):</label>
        <div class="search-wrapper">
          <input 
            type="text" 
            v-model="monitorSearch" 
            @input="searchMonitors" 
            @focus="searchMonitors"
            placeholder="Введите марку монитора для поиска..."
            class="search-input"
          >
          <div v-if="monitorSearchResults.length" class="search-results">
            <div 
              v-for="mon in monitorSearchResults" 
              :key="mon.id" 
              @click="addMonitorToSelection(mon)"
              class="search-result-item"
            >
              {{ mon.brand }}
            </div>
          </div>
        </div>
        <div class="selected-items">
          <div v-for="mon in selectedMonitors" :key="mon.id" class="selected-tag">
            {{ mon.brand }}
            <button @click="removeMonitor(mon.id)" class="remove-btn">×</button>
          </div>
        </div>
        <button @click="openAddMonitorModal" type="button" class="small-btn">➕ Добавить новый монитор</button>
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
        <button @click="openAddDepartmentModal" type="button" class="small-btn">➕ Добавить новый отдел</button>
      </div>

      <!-- Сотрудник с поиском -->
      <div class="form-group">
        <label>Закрепить за сотрудником:</label>
        <div class="search-wrapper">
          <input 
            type="text" 
            v-model="employeeSearch" 
            @input="searchEmployees" 
            @focus="searchEmployees"
            placeholder="Введите фамилию сотрудника..."
            class="search-input"
          >
          <div v-if="employeeSearchResults.length" class="search-results">
            <div 
              v-for="emp in employeeSearchResults" 
              :key="emp.id" 
              @click="selectEmployee(emp)"
              class="search-result-item"
            >
              {{ emp.last_name }} {{ emp.first_name }} {{ emp.patronymic || '' }}
            </div>
          </div>
        </div>
        <div v-if="selectedEmployee" class="selected-tag">
          {{ selectedEmployee.last_name }} {{ selectedEmployee.first_name }}
          <button @click="selectedEmployee = null" class="remove-btn">×</button>
        </div>
        <button @click="openAddEmployeeModal" type="button" class="small-btn">➕ Добавить нового сотрудника</button>
      </div>

      <!-- Периферия -->
      <div class="form-row">
        <label class="checkbox-label">
          <input type="checkbox" v-model="newComputer.has_keyboard"> Клавиатура
        </label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="newComputer.has_mouse"> Мышь
        </label>
      </div>

      <!-- Модернизация -->
      <label class="checkbox-label">
        <input type="checkbox" v-model="newComputer.needs_upgrade"> ⚠️ Требует модернизации
      </label>

      <button @click="addComputer" class="submit-btn">💾 Добавить компьютер</button>
    </div>

    <!-- Список компьютеров -->
    <div class="list">
      <h3>📋 Список компьютеров</h3>
      <div v-for="comp in computers" :key="comp.id" class="card">
        <div class="card-header">
          <strong>ОС №{{ comp.asset_number }}</strong>
          <div class="card-actions">
            <span v-if="comp.needs_upgrade" class="upgrade-badge">Требует модернизации</span>
            <button @click="openEditModal(comp)" class="edit-btn">✏️ Редактировать</button>
            <button @click="deleteComputer(comp.id)" class="delete-btn">🗑️ Удалить</button>
          </div>
        </div>
        <div class="card-body">
          <div class="system-unit">💻 Системный блок: <span>{{ comp.system_unit || 'Не указан' }}</span></div>
          <div>🖥️ Мониторы: 
            <span v-if="comp.monitors_detail && comp.monitors_detail.length">
              <span v-for="(mon, idx) in comp.monitors_detail" :key="mon.id">
                {{ mon.brand }}<span v-if="idx < comp.monitors_detail.length - 1">, </span>
              </span>
            </span>
            <span v-else class="no-data">нет</span>
          </div>
          <div>⌨️ Клавиатура: {{ comp.has_keyboard ? '✅ есть' : '❌ нет' }}</div>
          <div>🖱️ Мышь: {{ comp.has_mouse ? '✅ есть' : '❌ нет' }}</div>
          <div>📍 Отдел: {{ comp.department_name || 'Не указан' }}</div>
          <div>👤 Закреплен за: {{ comp.assigned_to_name || 'Не закреплен' }}</div>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content modal-large">
        <h3>✏️ Редактировать компьютер</h3>
        
        <div class="form-group">
          <label>Номер основного средства:</label>
          <input v-model="editComputer.asset_number" class="main-field">
        </div>
        
        <div class="form-group">
          <label>Системный блок:</label>
          <textarea v-model="editComputer.system_unit" rows="3" class="textarea-field"></textarea>
        </div>
        
        <div class="form-group">
          <label>Мониторы:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="editMonitorSearch" 
              @input="searchEditMonitors" 
              placeholder="Поиск мониторов..."
              class="search-input"
            >
            <div v-if="editMonitorSearchResults.length" class="search-results">
              <div 
                v-for="mon in editMonitorSearchResults" 
                :key="mon.id" 
                @click="addEditMonitor(mon)"
                class="search-result-item"
              >
                {{ mon.brand }}
              </div>
            </div>
          </div>
          <div class="selected-items">
            <div v-for="mon in editSelectedMonitors" :key="mon.id" class="selected-tag">
              {{ mon.brand }}
              <button @click="removeEditMonitor(mon.id)" class="remove-btn">×</button>
            </div>
          </div>
        </div>
        
        <div class="form-group">
          <label>Отдел:</label>
          <select v-model="editComputer.department" class="search-input">
            <option :value="null">Без отдела</option>
            <option v-for="dep in allDepartments" :key="dep.id" :value="dep.id">{{ dep.name }}</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Закрепить за сотрудником:</label>
          <select v-model="editComputer.assigned_to" class="search-input">
            <option :value="null">Не закреплен</option>
            <option v-for="emp in allEmployees" :key="emp.id" :value="emp.id">
              {{ emp.last_name }} {{ emp.first_name }} {{ emp.patronymic || '' }}
            </option>
          </select>
        </div>
        
        <div class="form-row">
          <label class="checkbox-label">
            <input type="checkbox" v-model="editComputer.has_keyboard"> Клавиатура
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="editComputer.has_mouse"> Мышь
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="editComputer.needs_upgrade"> ⚠️ Требует модернизации
          </label>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateComputer" class="save-btn">💾 Сохранить</button>
          <button @click="showEditModal = false" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальные окна для добавления (остаются без изменений) -->
    <div v-if="showMonitorModal" class="modal">
      <div class="modal-content">
        <h3>Добавить новый монитор</h3>
        <input v-model="newMonitorBrand" placeholder="Марка монитора">
        <div class="modal-buttons">
          <button @click="addMonitor" class="save-btn">Сохранить</button>
          <button @click="showMonitorModal = false" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <div v-if="showDepartmentModal" class="modal">
      <div class="modal-content">
        <h3>Добавить новый отдел</h3>
        <input v-model="newDepartmentName" placeholder="Название отдела">
        <div class="modal-buttons">
          <button @click="addDepartment" class="save-btn">Сохранить</button>
          <button @click="showDepartmentModal = false" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <div v-if="showEmployeeModal" class="modal">
      <div class="modal-content">
        <h3>Добавить нового сотрудника</h3>
        <input v-model="newEmployee.last_name" placeholder="Фамилия">
        <input v-model="newEmployee.first_name" placeholder="Имя">
        <input v-model="newEmployee.patronymic" placeholder="Отчество (необязательно)">
        <div class="modal-buttons">
          <button @click="addEmployee" class="save-btn">Сохранить</button>
          <button @click="showEmployeeModal = false" class="cancel-btn">Отмена</button>
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
import ConfirmModal from '../components/ConfirmModal.vue'

const API = 'http://localhost:8000/api'

// Данные
const computers = ref([])
const allMonitors = ref([])
const allDepartments = ref([])
const allEmployees = ref([])

// Выбранные значения для добавления
const selectedMonitors = ref([])
const selectedDepartment = ref(null)
const selectedEmployee = ref(null)

// Поисковые запросы
const monitorSearch = ref('')
const monitorSearchResults = ref([])
const departmentSearch = ref('')
const departmentSearchResults = ref([])
const employeeSearch = ref('')
const employeeSearchResults = ref([])

// Модальные окна
const showMonitorModal = ref(false)
const showDepartmentModal = ref(false)
const showEmployeeModal = ref(false)
const showEditModal = ref(false)

// Новые данные
const newMonitorBrand = ref('')
const newDepartmentName = ref('')
const newEmployee = ref({ last_name: '', first_name: '', patronymic: '' })

// Данные для редактирования
const editComputer = ref({
  id: null,
  asset_number: '',
  system_unit: '',
  monitors: [],
  has_keyboard: false,
  has_mouse: false,
  department: null,
  needs_upgrade: false,
  assigned_to: null
})
const editSelectedMonitors = ref([])
const editMonitorSearch = ref('')
const editMonitorSearchResults = ref([])

// Форма нового компьютера
const newComputer = ref({
  asset_number: 'не определен',
  system_unit: '',
  has_keyboard: false,
  has_mouse: false,
  needs_upgrade: false
})

// Загрузка данных
const fetchAllData = async () => {
  try {
    const [compRes, monRes, depRes, empRes] = await Promise.all([
      axios.get(`${API}/computers/`),
      axios.get(`${API}/monitors/`),
      axios.get(`${API}/departments/`),
      axios.get(`${API}/employees/`)
    ])
    computers.value = compRes.data
    allMonitors.value = monRes.data
    allDepartments.value = depRes.data
    allEmployees.value = empRes.data
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    showError('Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message))
  }
}

// Поиск мониторов для добавления
const searchMonitors = () => {
  if (!monitorSearch.value) {
    monitorSearchResults.value = []
    return
  }
  monitorSearchResults.value = allMonitors.value.filter(m => 
    m.brand.toLowerCase().includes(monitorSearch.value.toLowerCase())
  ).slice(0, 10)
}

// Добавление монитора в выбранные
const addMonitorToSelection = (monitor) => {
  if (!selectedMonitors.value.find(m => m.id === monitor.id)) {
    selectedMonitors.value.push(monitor)
  }
  monitorSearch.value = ''
  monitorSearchResults.value = []
}

// Удаление монитора
const removeMonitor = (monitorId) => {
  selectedMonitors.value = selectedMonitors.value.filter(m => m.id !== monitorId)
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

// Выбор отдела
const selectDepartment = (department) => {
  selectedDepartment.value = department
  departmentSearch.value = ''
  departmentSearchResults.value = []
}

// Поиск сотрудников
const searchEmployees = () => {
  if (!employeeSearch.value) {
    employeeSearchResults.value = []
    return
  }
  employeeSearchResults.value = allEmployees.value.filter(e => 
    `${e.last_name} ${e.first_name}`.toLowerCase().includes(employeeSearch.value.toLowerCase())
  ).slice(0, 10)
}

// Выбор сотрудника
const selectEmployee = (employee) => {
  selectedEmployee.value = employee
  employeeSearch.value = ''
  employeeSearchResults.value = []
}

// Добавление компьютера
const addComputer = async () => {
  if (!newComputer.value.asset_number) {
    showWarning('Пожалуйста, укажите номер основного средства')
    return
  }
  
  try {
    const computerData = {
      ...newComputer.value,
      monitors: selectedMonitors.value.map(m => m.id),
      department: selectedDepartment.value?.id || null,
      assigned_to: selectedEmployee.value?.id || null
    }
    
    await axios.post(`${API}/computers/`, computerData)
    
    newComputer.value = {
      asset_number: 'не определен',
      system_unit: '',
      has_keyboard: false,
      has_mouse: false,
      needs_upgrade: false
    }
    selectedMonitors.value = []
    selectedDepartment.value = null
    selectedEmployee.value = null
    
    await fetchAllData()
    showSuccess('Компьютер успешно добавлен!')
  } catch (error) {
    console.error('Ошибка добавления:', error)
    showError('Ошибка добавления компьютера: ' + (error.response?.data?.detail || error.message))
  }
}

// Открытие модального окна редактирования
const openEditModal = (computer) => {
  editComputer.value = {
    id: computer.id,
    asset_number: computer.asset_number,
    system_unit: computer.system_unit || '',
    has_keyboard: computer.has_keyboard,
    has_mouse: computer.has_mouse,
    department: computer.department,
    needs_upgrade: computer.needs_upgrade,
    assigned_to: computer.assigned_to
  }
  editSelectedMonitors.value = [...(computer.monitors_detail || [])]
  showEditModal.value = true
}

// Поиск мониторов для редактирования
const searchEditMonitors = () => {
  if (!editMonitorSearch.value) {
    editMonitorSearchResults.value = []
    return
  }
  editMonitorSearchResults.value = allMonitors.value.filter(m => 
    m.brand.toLowerCase().includes(editMonitorSearch.value.toLowerCase()) &&
    !editSelectedMonitors.value.find(sm => sm.id === m.id)
  ).slice(0, 10)
}

// Добавление монитора при редактировании
const addEditMonitor = (monitor) => {
  if (!editSelectedMonitors.value.find(m => m.id === monitor.id)) {
    editSelectedMonitors.value.push(monitor)
  }
  editMonitorSearch.value = ''
  editMonitorSearchResults.value = []
}

// Удаление монитора при редактировании
const removeEditMonitor = (monitorId) => {
  editSelectedMonitors.value = editSelectedMonitors.value.filter(m => m.id !== monitorId)
}

// Обновление компьютера
const updateComputer = async () => {
  try {
    const computerData = {
      asset_number: editComputer.value.asset_number,
      system_unit: editComputer.value.system_unit,
      monitors: editSelectedMonitors.value.map(m => m.id),
      has_keyboard: editComputer.value.has_keyboard,
      has_mouse: editComputer.value.has_mouse,
      department: editComputer.value.department,
      needs_upgrade: editComputer.value.needs_upgrade,
      assigned_to: editComputer.value.assigned_to
    }
    
    await axios.put(`${API}/computers/${editComputer.value.id}/`, computerData)
    showEditModal.value = false
    await fetchAllData()
    showSuccess('Компьютер успешно обновлен!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления компьютера: ' + (error.response?.data?.detail || error.message))
  }
}



// Добавление монитора
const addMonitor = async () => {
  if (!newMonitorBrand.value.trim()) {
    showWarning('Введите марку монитора')
    return
  }
  
  try {
    const response = await axios.post(`${API}/monitors/`, { brand: newMonitorBrand.value })
    await fetchAllData()
    selectedMonitors.value.push(response.data)
    showMonitorModal.value = false
    newMonitorBrand.value = ''
    showSuccess('Монитор добавлен!')
  } catch (error) {
    console.error('Ошибка добавления монитора:', error)
    showError('Ошибка добавления монитора')
  }
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
    selectedDepartment.value = response.data
    showDepartmentModal.value = false
    newDepartmentName.value = ''
    showSuccess('Отдел добавлен!')
  } catch (error) {
    console.error('Ошибка добавления отдела:', error)
    showError('Ошибка добавления отдела')
  }
}

// Добавление сотрудника
const addEmployee = async () => {
  if (!newEmployee.value.last_name || !newEmployee.value.first_name) {
    showWarning('Введите фамилию и имя сотрудника')
    return
  }
  
  try {
    const response = await axios.post(`${API}/employees/`, newEmployee.value)
    await fetchAllData()
    selectedEmployee.value = response.data
    showEmployeeModal.value = false
    newEmployee.value = { last_name: '', first_name: '', patronymic: '' }
    showSuccess('Сотрудник добавлен!')
  } catch (error) {
    console.error('Ошибка добавления сотрудника:', error)
    showError('Ошибка добавления сотрудника')
  }
}

// Открытие модальных окон
const openAddMonitorModal = () => {
  showMonitorModal.value = true
  newMonitorBrand.value = monitorSearch.value
}

const openAddDepartmentModal = () => {
  showDepartmentModal.value = true
  newDepartmentName.value = departmentSearch.value
}

const openAddEmployeeModal = () => {
  showEmployeeModal.value = true
}
const confirmModal = ref(null)

// Удаление компьютера с подтверждением
const deleteComputer = async (id) => {
  const confirmed = await confirmModal.value.open({
    title: 'Удаление компьютера',
    message: 'Вы уверены, что хотите удалить этот компьютер? Это действие нельзя отменить.',
    confirmText: 'Да, удалить',
    type: 'danger'
  })
  
  if (confirmed) {
    try {
      await axios.delete(`${API}/computers/${id}/`)
      await fetchAllData()
      showSuccess('Компьютер удален!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления компьютера')
    }
  }
}

onMounted(fetchAllData)

</script>

<style scoped>
/* ... все предыдущие стили остаются ... */

/* Добавляем новые стили для кнопок редактирования и удаления */
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

/* Модальное окно большего размера */
.modal-large {
  max-width: 700px !important;
  width: 90%;
}

/* Остальные стили из предыдущей версии */
.form-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
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

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 10px 0;
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

.checkbox-label {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-right: 1.5rem;
  cursor: pointer;
  padding: 5px 0;
  font-size: 1rem;
}

.checkbox-label input {
  width: 18px;
  height: 18px;
  cursor: pointer;
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
  margin-top: 1.5rem;
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

.system-unit {
  margin-bottom: 0.5rem;
  padding: 8px;
  background: #fff;
  border-radius: 8px;
}

.system-unit span {
  font-weight: 500;
  color: #2c3e50;
}

.upgrade-badge {
  background: #e67e22;
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
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
    gap: 1rem;
  }
  
  .search-results {
    position: relative;
    max-height: 200px;
  }
  
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