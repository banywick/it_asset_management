<template>
  <div class="page">
    <h1>🔋 ИБП (бесперебойники)</h1>

    <!-- Форма добавления ИБП -->
    <div class="form-card">
      <h3>➕ Добавить ИБП</h3>
      
      <div class="form-row">
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
          <input 
            v-model="newUPS.model" 
            placeholder="Модель ИБП"
            class="search-input"
          >
        </div>
      </div>

      <div class="form-group">
        <label>Статус:</label>
        <select v-model="newUPS.status" class="search-input">
          <option value="active">✅ Активен</option>
          <option value="repair">🔧 В ремонте</option>
          <option value="replaced">🔄 Заменен временно</option>
        </select>
      </div>

      <div class="form-group">
        <label>Комментарий:</label>
        <textarea 
          v-model="newUPS.comment" 
          placeholder="Дополнительная информация о ИБП..."
          rows="3"
          class="textarea-field"
        ></textarea>
      </div>

      <button @click="addUPS" class="submit-btn">💾 Добавить ИБП</button>
    </div>

    <!-- Список ИБП -->
    <div class="list">
      <h3>📋 Список ИБП ({{ upsList.length }} шт.)</h3>
      <div class="cards-grid">
        <div v-for="ups in paginatedUPS" :key="ups.id" class="card">
          <div class="card-header">
            <div class="ups-title">
              <strong>ОС №{{ ups.asset_number }}</strong>
              <span :class="['status-badge', getStatusClass(ups.status)]">
                {{ getStatusText(ups.status) }}
              </span>
            </div>
            <div class="card-actions">
              <button @click="openServiceModal(ups)" class="service-btn" title="Обслуживание">🔧</button>
              <button @click="openEditModal(ups)" class="edit-btn" title="Редактировать">✏️</button>
              <button @click="deleteUPS(ups.id)" class="delete-btn" title="Удалить">🗑️</button>
            </div>
          </div>
          <div class="card-body">
            <div class="info-row">
              <span class="label">🔋 Модель:</span>
              <span class="value">{{ ups.model }}</span>
            </div>
            <div v-if="ups.comment" class="info-row">
              <span class="label">💬 Комментарий:</span>
              <span class="value comment">{{ ups.comment }}</span>
            </div>
            <div v-if="ups.replacement_ups_detail" class="info-row replacement-info">
              <span class="label">🔄 Временная замена:</span>
              <span class="value">ОС №{{ ups.replacement_ups_detail.asset_number }} - {{ ups.replacement_ups_detail.model }}</span>
            </div>
            <div class="info-row">
              <span class="label">📅 Последняя замена АКБ:</span>
              <span class="value">
                <span v-if="ups.battery_history && ups.battery_history.length">
                  {{ formatDate(ups.battery_history[0].replaced_at) }}
                  <span class="battery-serial">({{ ups.battery_history[0].new_battery_serial }})</span>
                </span>
                <span v-else class="no-data">не заменялся</span>
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

    <!-- Модальное окно редактирования с поиском для временной замены -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content modal-large">
        <h3>✏️ Редактировать ИБП</h3>
        
        <div class="form-group">
          <label>Номер основного средства:</label>
          <input v-model="editUPS.asset_number" class="main-field">
        </div>
        
        <div class="form-group">
          <label>Модель ИБП:</label>
          <input v-model="editUPS.model" class="search-input">
        </div>
        
        <div class="form-group">
          <label>Статус:</label>
          <select v-model="editUPS.status" class="search-input">
            <option value="active">✅ Активен</option>
            <option value="repair">🔧 В ремонте</option>
            <option value="replaced">🔄 Заменен временно</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Комментарий:</label>
          <textarea v-model="editUPS.comment" rows="3" class="textarea-field"></textarea>
        </div>
        
        <!-- Временная замена с поиском -->
        <div class="form-group">
          <label>Временная замена (ИБП):</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="replacementSearch" 
              @input="searchReplacementUPS" 
              @focus="searchReplacementUPS"
              placeholder="Введите номер ОС или модель ИБП..."
              class="search-input"
            >
            <div v-if="replacementSearchResults.length" class="search-results">
              <div 
                v-for="item in replacementSearchResults" 
                :key="item.id" 
                @click="selectReplacementUPS(item)"
                class="search-result-item"
              >
                ОС №{{ item.asset_number }} - {{ item.model }}
                <span :class="['status-badge-small', getStatusClass(item.status)]">
                  {{ getStatusText(item.status) }}
                </span>
              </div>
            </div>
          </div>
          <div v-if="selectedReplacementUPS" class="selected-tag">
            ОС №{{ selectedReplacementUPS.asset_number }} - {{ selectedReplacementUPS.model }}
            <span :class="['status-badge-small', getStatusClass(selectedReplacementUPS.status)]">
              {{ getStatusText(selectedReplacementUPS.status) }}
            </span>
            <button @click="clearReplacementUPS" class="remove-btn">×</button>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateUPS" class="save-btn">💾 Сохранить</button>
          <button @click="closeEditModal" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно обслуживания -->
    <div v-if="showServiceModal" class="modal">
      <div class="modal-content modal-large">
        <h3>🔧 Обслуживание ИБП</h3>
        <p class="modal-subtitle">ИБП: <strong>ОС №{{ selectedUPSForService?.asset_number }} - {{ selectedUPSForService?.model }}</strong></p>
        
        <!-- Форма добавления замены -->
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
          <button @click="addBatteryHistory" class="submit-btn small">💾 Добавить запись</button>
        </div>
        
        <!-- История замен -->
        <div class="history-section">
          <h4>📋 История замен аккумуляторов</h4>
          <div v-if="batteryHistory.length" class="history-list">
            <div v-for="record in batteryHistory" :key="record.id" class="history-item">
              <div class="history-header">
                <span class="history-date">{{ formatDate(record.replaced_at) }}</span>
                <button @click="deleteBatteryHistory(record.id)" class="delete-small" title="Удалить запись">🗑️</button>
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
          <button @click="closeServiceModal" class="cancel-btn">Закрыть</button>
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

const upsList = ref([])
const batteryHistory = ref([])

// Пагинация
const currentPage = ref(1)
const itemsPerPage = 4

// Модальные окна
const showEditModal = ref(false)
const showServiceModal = ref(false)

// Данные для нового ИБП
const newUPS = ref({
  asset_number: 'не определен',
  model: '',
  status: 'active',
  comment: ''
})

// Данные для редактирования
const editUPS = ref({
  id: null,
  asset_number: '',
  model: '',
  status: 'active',
  comment: '',
  replacement_ups: null
})

// Поиск для временной замены
const replacementSearch = ref('')
const replacementSearchResults = ref([])
const selectedReplacementUPS = ref(null)

// Данные для обслуживания
const selectedUPSForService = ref(null)
const newBattery = ref({
  old_battery_serial: '',
  new_battery_serial: '',
  performed_by: '',
  comment: ''
})

const confirmModal = ref(null)

// Пагинированные ИБП
const paginatedUPS = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return upsList.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(upsList.value.length / itemsPerPage)
})

// Форматирование даты
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU')
}

// Статусы
const getStatusText = (status) => {
  const statusMap = {
    'active': 'Активен',
    'repair': 'В ремонте',
    'replaced': 'Заменен временно'
  }
  return statusMap[status] || status
}

const getStatusClass = (status) => {
  const classMap = {
    'active': 'status-active',
    'repair': 'status-repair',
    'replaced': 'status-replaced'
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
    const upsRes = await axios.get(`${API}/ups/`)
    upsList.value = upsRes.data
    console.log('Загружено ИБП:', upsList.value.length)
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    showError('Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message))
  }
}

// Загрузка истории замен
const fetchBatteryHistory = async (upsId) => {
  try {
    const response = await axios.get(`${API}/battery-history/?ups=${upsId}`)
    batteryHistory.value = response.data
  } catch (error) {
    console.error('Ошибка загрузки истории:', error)
    showError('Ошибка загрузки истории замен')
  }
}

// Поиск ИБП для временной замены
const searchReplacementUPS = () => {
  if (!replacementSearch.value) {
    replacementSearchResults.value = []
    return
  }
  replacementSearchResults.value = upsList.value.filter(item => 
    item.id !== editUPS.value.id && (
      item.asset_number.toLowerCase().includes(replacementSearch.value.toLowerCase()) ||
      item.model.toLowerCase().includes(replacementSearch.value.toLowerCase())
    )
  ).slice(0, 10)
}

// Выбор ИБП для временной замены
const selectReplacementUPS = (item) => {
  selectedReplacementUPS.value = item
  editUPS.value.replacement_ups = item.id
  replacementSearch.value = ''
  replacementSearchResults.value = []
}

// Очистка выбранного ИБП для временной замены
const clearReplacementUPS = () => {
  selectedReplacementUPS.value = null
  editUPS.value.replacement_ups = null
  replacementSearch.value = ''
  replacementSearchResults.value = []
}

// Добавление ИБП
const addUPS = async () => {
  if (!newUPS.value.model) {
    showWarning('Пожалуйста, укажите модель ИБП')
    return
  }
  
  try {
    const upsData = {
      asset_number: newUPS.value.asset_number || 'не определен',
      model: newUPS.value.model,
      status: newUPS.value.status,
      comment: newUPS.value.comment || null
    }
    
    console.log('Отправляем данные:', upsData)
    const response = await axios.post(`${API}/ups/`, upsData)
    console.log('Ответ:', response.data)
    
    newUPS.value = {
      asset_number: 'не определен',
      model: '',
      status: 'active',
      comment: ''
    }
    
    await fetchAllData()
    currentPage.value = Math.ceil(upsList.value.length / itemsPerPage)
    showSuccess('ИБП успешно добавлен!')
  } catch (error) {
    console.error('Ошибка добавления:', error)
    showError('Ошибка добавления ИБП: ' + (error.response?.data?.detail || error.message))
  }
}

// Открытие модального окна редактирования
const openEditModal = (ups) => {
  console.log('Редактирование ИБП:', ups)
  editUPS.value = {
    id: ups.id,
    asset_number: ups.asset_number,
    model: ups.model,
    status: ups.status || 'active',
    comment: ups.comment || '',
    replacement_ups: ups.replacement_ups || null
  }
  
  // Устанавливаем выбранный ИБП для временной замены
  if (ups.replacement_ups_detail) {
    selectedReplacementUPS.value = ups.replacement_ups_detail
  } else {
    selectedReplacementUPS.value = null
  }
  
  replacementSearch.value = ''
  replacementSearchResults.value = []
  showEditModal.value = true
}

// Закрытие модального окна редактирования
const closeEditModal = () => {
  showEditModal.value = false
  editUPS.value = {
    id: null,
    asset_number: '',
    model: '',
    status: 'active',
    comment: '',
    replacement_ups: null
  }
  selectedReplacementUPS.value = null
  replacementSearch.value = ''
  replacementSearchResults.value = []
}

// Обновление ИБП
const updateUPS = async () => {
  try {
    const upsData = {
      asset_number: editUPS.value.asset_number,
      model: editUPS.value.model,
      status: editUPS.value.status,
      comment: editUPS.value.comment || null,
      replacement_ups: editUPS.value.replacement_ups || null
    }
    
    console.log('Обновляем ИБП:', upsData)
    await axios.put(`${API}/ups/${editUPS.value.id}/`, upsData)
    closeEditModal()
    await fetchAllData()
    showSuccess('ИБП успешно обновлен!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления ИБП: ' + (error.response?.data?.detail || error.message))
  }
}

// Открытие модального окна обслуживания
const openServiceModal = async (ups) => {
  console.log('Обслуживание ИБП:', ups)
  selectedUPSForService.value = ups
  await fetchBatteryHistory(ups.id)
  newBattery.value = {
    old_battery_serial: '',
    new_battery_serial: '',
    performed_by: '',
    comment: ''
  }
  showServiceModal.value = true
}

// Закрытие модального окна обслуживания
const closeServiceModal = () => {
  showServiceModal.value = false
  selectedUPSForService.value = null
  batteryHistory.value = []
}

// Добавление записи о замене АКБ
const addBatteryHistory = async () => {
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
    await fetchBatteryHistory(selectedUPSForService.value.id)
    await fetchAllData()
    
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
const deleteBatteryHistory = async (id) => {
  const confirmed = await confirmModal.value.open({
    title: 'Удаление записи',
    message: 'Вы уверены, что хотите удалить эту запись о замене аккумулятора?',
    confirmText: 'Да, удалить',
    type: 'danger'
  })
  
  if (confirmed) {
    try {
      await axios.delete(`${API}/battery-history/${id}/`)
      await fetchBatteryHistory(selectedUPSForService.value.id)
      await fetchAllData()
      showSuccess('Запись удалена!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления записи')
    }
  }
}

// Удаление ИБП
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
      if (paginatedUPS.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
      showSuccess('ИБП удален!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления ИБП')
    }
  }
}

onMounted(() => {
  fetchAllData()
})
</script>

<style scoped>
/* ... все предыдущие стили ... */

/* Добавляем стиль для маленького бейджа статуса в результатах поиска */
.status-badge-small {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 0.65rem;
  font-weight: 500;
  margin-left: 8px;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
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

.submit-btn.small {
  width: auto;
  padding: 8px 16px;
  margin-top: 0;
  font-size: 0.9rem;
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

@media (max-width: 900px) {
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

.ups-title {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.ups-title strong {
  font-size: 1rem;
  color: #2c3e50;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.service-btn, .edit-btn, .delete-btn {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 5px;
  border-radius: 6px;
  transition: all 0.2s;
}

.service-btn {
  color: #f39c12;
}

.service-btn:hover {
  background: #f39c12;
  color: white;
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
  align-items: flex-start;
  flex-wrap: wrap;
}

.label {
  font-weight: 600;
  color: #666;
  min-width: 130px;
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

.replacement-info {
  background: #fff3cd;
  padding: 6px 10px;
  border-radius: 8px;
}

.battery-serial {
  font-size: 0.7rem;
  color: #27ae60;
  margin-left: 5px;
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

.status-repair {
  background: #f8d7da;
  color: #721c24;
}

.status-replaced {
  background: #fff3cd;
  color: #856404;
}

.no-data {
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

/* Модальное окно обслуживания */
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
  
  .label {
    width: 100%;
    margin-bottom: 4px;
  }
  
  .search-result-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
}
</style>