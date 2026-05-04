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
          <label>Тип компьютера:</label>
          <select v-model="newComputer.computer_type" class="search-input">
            <option value="desktop">🖥️ Стационарный</option>
            <option value="laptop">💻 Ноутбук</option>
            <option value="all-in-one">🖥️ Моноблок</option>
          </select>
        </div>
      </div>

      <div class="form-row">
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

      <!-- Мониторы с поиском -->
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

      <!-- Периферия -->
      <div class="form-row">
        <label class="checkbox-label">
          <input type="checkbox" v-model="newComputer.has_keyboard"> ⌨️ Клавиатура
        </label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="newComputer.has_mouse"> 🖱️ Мышь
        </label>
      </div>

      <!-- Статус обслуживания -->
      <div class="form-group">
        <label>Статус обслуживания:</label>
        <select v-model="newComputer.service_status" class="search-input">
          <option value="operational">✅ В эксплуатации</option>
          <option value="repair">🔧 В ремонте</option>
          <option value="upgrade">⚡ На модернизации</option>
        </select>
      </div>

      <button @click="addComputer" class="submit-btn">💾 Добавить компьютер</button>
    </div>

    <!-- Список компьютеров -->
    <div class="list">
      <h3>📋 Список компьютеров ({{ computers.length }} шт.)</h3>
      <div class="cards-grid">
        <div v-for="comp in paginatedComputers" :key="comp.id" class="card">
          <div class="card-header">
            <div class="header-left">
              <!-- Номер ОС теперь кликабельный -->
              <div class="clickable-asset" @click="openEditModal(comp, 'asset_number')" title="Кликните чтобы изменить номер ОС">
                <strong>ОС №{{ comp.asset_number }}</strong>
                <span class="edit-hint-small">✏️</span>
              </div>
            </div>
            <div class="card-actions">
              <span :class="['service-badge', getServiceStatusClass(comp.service_status)]">
                {{ getServiceStatusText(comp.service_status) }}
              </span>
              <button @click="deleteComputer(comp.id)" class="delete-btn" title="Удалить">🗑️</button>
            </div>
          </div>
          <div class="card-body">
            <!-- Тип компьютера -->
            <div class="info-row clickable" @click="openEditModal(comp, 'computer_type')">
              <span class="label">{{ getComputerTypeIcon(comp.computer_type) }} Тип:</span>
              <span class="value">{{ getComputerTypeText(comp.computer_type) }}</span>
              <span class="edit-hint">✏️</span>
            </div>
            
            <!-- Системный блок -->
            <div class="info-row clickable" @click="openEditModal(comp, 'system_unit')">
              <span class="label">💻 Системный блок:</span>
              <span class="value">{{ comp.system_unit || 'Не указан' }}</span>
              <span class="edit-hint">✏️</span>
            </div>
            
            <!-- Мониторы -->
            <div class="info-row clickable" @click="openEditModal(comp, 'monitors')">
              <span class="label">🖥️ Мониторы:</span>
              <span class="value">
                <span v-if="comp.monitors_detail && comp.monitors_detail.length">
                  {{ comp.monitors_detail.map(m => m.brand).join(', ') }}
                </span>
                <span v-else class="no-data">нет</span>
              </span>
              <span class="edit-hint">✏️</span>
            </div>
            
            <!-- Периферия -->
            <div class="info-row clickable" @click="openEditModal(comp, 'peripherals')">
              <span class="label">⌨️ Периферия:</span>
              <span class="value">
                <span v-if="comp.has_keyboard && comp.has_mouse">⌨️ Клавиатура, 🖱️ Мышь</span>
                <span v-else-if="comp.has_keyboard">⌨️ Клавиатура</span>
                <span v-else-if="comp.has_mouse">🖱️ Мышь</span>
                <span v-else class="no-data">нет</span>
              </span>
              <span class="edit-hint">✏️</span>
            </div>
            
            <!-- Статус обслуживания -->
            <div class="info-row clickable" @click="openEditModal(comp, 'service_status')">
              <span class="label">🔧 Статус:</span>
              <span :class="['service-badge', getServiceStatusClass(comp.service_status)]">
                {{ getServiceStatusText(comp.service_status) }}
              </span>
              <span class="edit-hint">✏️</span>
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

    <!-- Модальное окно добавления монитора -->
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

    <!-- Модальное окно редактирования -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content modal-large">
        <h3>✏️ Редактировать компьютер</h3>
        <p class="modal-subtitle">Текущий ОС №{{ editComputer.asset_number }}</p>
        
        <!-- Номер основного средства -->
        <div v-if="editField === 'asset_number'">
          <div class="form-group">
            <label>Номер основного средства:</label>
            <input v-model="editComputer.asset_number" class="main-field" placeholder="Например: ПК-001">
            <small class="field-hint">Уникальный идентификатор компьютера</small>
          </div>
        </div>
        
        <!-- Тип компьютера -->
        <div v-if="editField === 'computer_type'">
          <div class="form-group">
            <label>Тип компьютера:</label>
            <select v-model="editComputer.computer_type" class="search-input">
              <option value="desktop">🖥️ Стационарный</option>
              <option value="laptop">💻 Ноутбук</option>
              <option value="all-in-one">🖥️ Моноблок</option>
            </select>
          </div>
        </div>
        
        <!-- Системный блок -->
        <div v-if="editField === 'system_unit'">
          <div class="form-group">
            <label>Системный блок:</label>
            <textarea v-model="editComputer.system_unit" rows="4" class="textarea-field" placeholder="Введите характеристики системного блока"></textarea>
          </div>
        </div>
        
        <!-- Мониторы -->
        <div v-if="editField === 'monitors'">
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
        </div>
        
        <!-- Периферия -->
        <div v-if="editField === 'peripherals'">
          <div class="form-group">
            <label>Периферия:</label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="editComputer.has_keyboard"> ⌨️ Клавиатура
            </label>
            <label class="checkbox-label">
              <input type="checkbox" v-model="editComputer.has_mouse"> 🖱️ Мышь
            </label>
          </div>
        </div>
        
        <!-- Статус обслуживания -->
        <div v-if="editField === 'service_status'">
          <div class="form-group">
            <label>Статус обслуживания:</label>
            <select v-model="editComputer.service_status" class="search-input">
              <option value="operational">✅ В эксплуатации</option>
              <option value="repair">🔧 В ремонте</option>
              <option value="upgrade">⚡ На модернизации</option>
            </select>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateComputerField" class="save-btn">💾 Сохранить</button>
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

const API = '/api'

const computers = ref([])
const allMonitors = ref([])

// Пагинация
const currentPage = ref(1)
const itemsPerPage = 4

// Выбранные значения для добавления
const selectedMonitors = ref([])

// Поисковые запросы
const monitorSearch = ref('')
const monitorSearchResults = ref([])

// Модальные окна
const showMonitorModal = ref(false)
const showEditModal = ref(false)

// Новые данные
const newMonitorBrand = ref('')

// Данные для редактирования
const editComputer = ref({
  id: null,
  asset_number: '',
  computer_type: 'desktop',
  system_unit: '',
  monitors: [],
  has_keyboard: false,
  has_mouse: false,
  service_status: 'operational',
  needs_upgrade: false
})
const editField = ref('')
const editSelectedMonitors = ref([])
const editMonitorSearch = ref('')
const editMonitorSearchResults = ref([])

// Форма нового компьютера
const newComputer = ref({
  asset_number: 'не определен',
  computer_type: 'desktop',
  system_unit: '',
  has_keyboard: false,
  has_mouse: false,
  service_status: 'operational',
  needs_upgrade: false
})

const confirmModal = ref(null)

// Пагинированные компьютеры
const paginatedComputers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return computers.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(computers.value.length / itemsPerPage)
})

// Иконки типов компьютеров
const getComputerTypeIcon = (type) => {
  const icons = {
    'desktop': '🖥️',
    'laptop': '💻',
    'all-in-one': '🖥️'
  }
  return icons[type] || '🖥️'
}

// Текстовое название типа компьютера
const getComputerTypeText = (type) => {
  const texts = {
    'desktop': 'Стационарный',
    'laptop': 'Ноутбук',
    'all-in-one': 'Моноблок'
  }
  return texts[type] || 'Не указан'
}

// Статусы обслуживания
const getServiceStatusText = (status) => {
  const statusMap = {
    'operational': 'В эксплуатации',
    'repair': 'В ремонте',
    'upgrade': 'На модернизации'
  }
  return statusMap[status] || status
}

const getServiceStatusClass = (status) => {
  const classMap = {
    'operational': 'status-operational',
    'repair': 'status-repair',
    'upgrade': 'status-upgrade'
  }
  return classMap[status] || ''
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
    const [compRes, monRes] = await Promise.all([
      axios.get(`${API}/computers/`),
      axios.get(`${API}/monitors/`)
    ])
    computers.value = compRes.data
    allMonitors.value = monRes.data
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

// Добавление компьютера
const addComputer = async () => {
  if (!newComputer.value.asset_number) {
    showWarning('Пожалуйста, укажите номер основного средства')
    return
  }
  
  try {
    const computerData = {
      ...newComputer.value,
      monitors: selectedMonitors.value.map(m => m.id)
    }
    
    await axios.post(`${API}/computers/`, computerData)
    
    newComputer.value = {
      asset_number: 'не определен',
      computer_type: 'desktop',
      system_unit: '',
      has_keyboard: false,
      has_mouse: false,
      service_status: 'operational',
      needs_upgrade: false
    }
    selectedMonitors.value = []
    
    await fetchAllData()
    currentPage.value = Math.ceil(computers.value.length / itemsPerPage)
    showSuccess('Компьютер успешно добавлен!')
  } catch (error) {
    console.error('Ошибка добавления:', error)
    showError('Ошибка добавления компьютера: ' + (error.response?.data?.detail || error.message))
  }
}

// Открытие модального окна редактирования
const openEditModal = (computer, field) => {
  editComputer.value = {
    id: computer.id,
    asset_number: computer.asset_number,
    computer_type: computer.computer_type || 'desktop',
    system_unit: computer.system_unit || '',
    has_keyboard: computer.has_keyboard,
    has_mouse: computer.has_mouse,
    service_status: computer.service_status || 'operational',
    needs_upgrade: computer.needs_upgrade
  }
  editSelectedMonitors.value = [...(computer.monitors_detail || [])]
  editField.value = field
  editMonitorSearch.value = ''
  editMonitorSearchResults.value = []
  showEditModal.value = true
}

// Закрытие модального окна редактирования
const closeEditModal = () => {
  showEditModal.value = false
  editField.value = ''
  editSelectedMonitors.value = []
  editMonitorSearch.value = ''
  editMonitorSearchResults.value = []
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

// Обновление поля компьютера
const updateComputerField = async () => {
  try {
    let updateData = {}
    
    switch (editField.value) {
      case 'asset_number':
        if (!editComputer.value.asset_number) {
          showWarning('Номер основного средства не может быть пустым')
          return
        }
        updateData = { asset_number: editComputer.value.asset_number }
        break
      case 'computer_type':
        updateData = { computer_type: editComputer.value.computer_type }
        break
      case 'system_unit':
        updateData = { system_unit: editComputer.value.system_unit }
        break
      case 'monitors':
        updateData = { monitors: editSelectedMonitors.value.map(m => m.id) }
        break
      case 'peripherals':
        updateData = {
          has_keyboard: editComputer.value.has_keyboard,
          has_mouse: editComputer.value.has_mouse
        }
        break
      case 'service_status':
        updateData = { service_status: editComputer.value.service_status }
        break
    }
    
    await axios.patch(`${API}/computers/${editComputer.value.id}/`, updateData)
    closeEditModal()
    await fetchAllData()
    showSuccess('Поле успешно обновлено!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления: ' + (error.response?.data?.detail || error.message))
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

// Удаление компьютера
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
      if (paginatedComputers.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
      showSuccess('Компьютер удален!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления компьютера')
    }
  }
}

// Открытие модальных окон
const openAddMonitorModal = () => {
  showMonitorModal.value = true
  newMonitorBrand.value = monitorSearch.value
}

onMounted(fetchAllData)
</script>

<style scoped>
/* Все предыдущие стили остаются, добавляем новые */

.clickable-asset {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  margin: -4px -8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.clickable-asset:hover {
  background: rgba(26, 188, 156, 0.15);
}

.edit-hint-small {
  opacity: 0;
  font-size: 0.7rem;
  color: #1abc9c;
  transition: opacity 0.2s;
}

.clickable-asset:hover .edit-hint-small {
  opacity: 1;
}

/* Остальные стили из предыдущей версии */
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

.cards-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

@media (max-width: 700px) {
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
  flex-wrap: wrap;
  gap: 8px;
}

.header-left {
  display: flex;
  align-items: center;
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

.card-body {
  padding: 12px 15px;
}

.info-row {
  margin-bottom: 10px;
  font-size: 0.85rem;
  line-height: 1.4;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  padding: 6px 8px;
  border-radius: 8px;
  transition: all 0.2s;
  cursor: pointer;
}

.info-row:hover {
  background: rgba(26, 188, 156, 0.1);
}

.label {
  font-weight: 600;
  color: #666;
  min-width: 110px;
  flex-shrink: 0;
}

.value {
  color: #333;
  flex: 1;
}

.edit-hint {
  opacity: 0;
  margin-left: 8px;
  font-size: 0.7rem;
  color: #1abc9c;
  transition: opacity 0.2s;
}

.info-row:hover .edit-hint {
  opacity: 1;
}

.service-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.status-operational {
  background: #d4edda;
  color: #155724;
}

.status-repair {
  background: #f8d7da;
  color: #721c24;
}

.status-upgrade {
  background: #fff3cd;
  color: #856404;
}

.no-data {
  color: #999;
  font-style: italic;
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
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.modal-subtitle {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
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
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .card-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .label {
    width: 100%;
    margin-bottom: 4px;
  }
}
</style>