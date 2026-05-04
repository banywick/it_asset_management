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

      <!-- Новые поля -->
      <div class="form-row">
        <div class="form-group">
          <label>Номер кабинета:</label>
          <input 
            v-model="newMFP.cabinet_number" 
            placeholder="Например: 305"
            class="search-input"
          >
        </div>
        
        <div class="form-group">
          <label>Серийный номер:</label>
          <input 
            v-model="newMFP.serial_number" 
            placeholder="Серийный номер"
            class="search-input"
          >
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>Логин:</label>
          <input 
            v-model="newMFP.login" 
            placeholder="Логин для доступа"
            class="search-input"
          >
        </div>
        
        <div class="form-group">
          <label>Пароль:</label>
          <input 
            v-model="newMFP.password" 
            placeholder="Пароль для доступа"
            type="text"
            class="search-input"
          >
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label>MAC адрес:</label>
          <input 
            v-model="newMFP.mac_address" 
            placeholder="XX:XX:XX:XX:XX:XX"
            class="search-input mac-input"
          >
          <small class="field-hint">Формат: XX:XX:XX:XX:XX:XX</small>
        </div>
        
        <div class="form-group">
          <label>Статус:</label>
          <select v-model="newMFP.status" class="search-input">
            <option value="operational">✅ В эксплуатации</option>
            <option value="write_off">📦 На списание</option>
          </select>
        </div>
      </div>

      <div class="form-group">
        <label>Примечания:</label>
        <textarea 
          v-model="newMFP.notes" 
          placeholder="Дополнительная информация о МФУ..."
          rows="3"
          class="textarea-field"
        ></textarea>
      </div>

      <button @click="addMFP" class="submit-btn">💾 Добавить МФУ</button>
    </div>

    <!-- Список МФУ -->
    <div class="list">
      <h3>📋 Список МФУ ({{ mfps.length }} шт.)</h3>
      <div class="cards-grid">
        <div v-for="mfp in paginatedMFPs" :key="mfp.id" class="card">
          <div class="card-header">
            <div class="mfp-title">
              <strong>{{ mfp.model }}</strong>
              <span class="asset-badge">ОС №{{ mfp.asset_number }}</span>
            </div>
            <div class="card-actions">
              <span :class="['status-badge-small', getMFPStatusClass(mfp.status)]">
                {{ getMFPStatusText(mfp.status) }}
              </span>
              <button @click="openEditModal(mfp)" class="edit-btn" title="Редактировать">✏️</button>
              <button @click="deleteMFP(mfp.id)" class="delete-btn" title="Удалить">🗑️</button>
            </div>
          </div>
          <div class="card-body">
            <div class="info-grid">
              <div class="info-item">
                <span class="label">🌐 IP:</span>
                <span class="value">{{ mfp.ip_address || 'не указан' }}</span>
              </div>
              <div class="info-item">
                <span class="label">🏢 Кабинет:</span>
                <span class="value">{{ mfp.cabinet_number || 'не указан' }}</span>
              </div>
              <div class="info-item">
                <span class="label">🔢 Серийный номер:</span>
                <span class="value">{{ mfp.serial_number || 'не указан' }}</span>
              </div>
              <div class="info-item">
                <span class="label">🔗 MAC адрес:</span>
                <span class="value mac-value">{{ mfp.mac_address || 'не указан' }}</span>
              </div>
              <div v-if="mfp.login || mfp.password" class="info-item">
                <span class="label">🔐 Доступ:</span>
                <span class="value">
                  <span v-if="mfp.login">Логин: {{ mfp.login }}</span>
                  <span v-if="mfp.password"> / Пароль: {{ mfp.password }}</span>
                </span>
              </div>
              <div v-if="mfp.notes" class="info-item full-width">
                <span class="label">💬 Примечания:</span>
                <span class="value notes">{{ mfp.notes }}</span>
              </div>
            </div>
            <div class="compatible-cartridges" v-if="mfp.compatible_cartridges?.length">
              <div class="label">🖨️ Совместимые картриджи:</div>
              <div class="cartridges-list">
                <span v-for="cart in mfp.compatible_cartridges" :key="cart.id" class="cartridge-tag">
                  {{ cart.model }} (Минск: {{ cart.quantity_minsk }})
                </span>
              </div>
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
        
        <div class="form-group">
          <label>Модель МФУ:</label>
          <input v-model="editMFP.model" class="search-input">
        </div>
        
        <div class="form-group">
          <label>IP адрес:</label>
          <input v-model="editMFP.ip_address" class="search-input ip-input" placeholder="192.168.1.100">
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Номер кабинета:</label>
            <input v-model="editMFP.cabinet_number" class="search-input">
          </div>
          <div class="form-group">
            <label>Серийный номер:</label>
            <input v-model="editMFP.serial_number" class="search-input">
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Логин:</label>
            <input v-model="editMFP.login" class="search-input">
          </div>
          <div class="form-group">
            <label>Пароль:</label>
            <input v-model="editMFP.password" type="text" class="search-input">
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>MAC адрес:</label>
            <input v-model="editMFP.mac_address" class="search-input mac-input" placeholder="XX:XX:XX:XX:XX:XX">
          </div>
          <div class="form-group">
            <label>Статус:</label>
            <select v-model="editMFP.status" class="search-input">
              <option value="operational">✅ В эксплуатации</option>
              <option value="write_off">📦 На списание</option>
            </select>
          </div>
        </div>
        
        <div class="form-group">
          <label>Примечания:</label>
          <textarea v-model="editMFP.notes" rows="3" class="textarea-field"></textarea>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateMFP" class="save-btn">💾 Сохранить</button>
          <button @click="showEditModal = false" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <ConfirmModal ref="confirmModal" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { showSuccess, showError, showWarning } from '../utils/toast'
import ConfirmModal from '../components/ConfirmModal.vue'

const API = '/api'

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
  ip_address: '',
  cabinet_number: '',
  login: '',
  password: '',
  status: 'operational',
  notes: '',
  serial_number: '',
  mac_address: ''
})

// Данные для редактирования
const editMFP = ref({
  id: null,
  asset_number: '',
  model: '',
  ip_address: '',
  cabinet_number: '',
  login: '',
  password: '',
  status: 'operational',
  notes: '',
  serial_number: '',
  mac_address: ''
})

const confirmModal = ref(null)

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

// Валидация MAC адреса
const isValidMAC = (mac) => {
  if (!mac) return true
  const macRegex = /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/
  return macRegex.test(mac)
}

// Статусы МФУ
const getMFPStatusText = (status) => {
  const statusMap = {
    'operational': 'В эксплуатации',
    'write_off': 'На списание'
  }
  return statusMap[status] || status
}

const getMFPStatusClass = (status) => {
  const classMap = {
    'operational': 'status-operational',
    'write_off': 'status-write-off'
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
    const mfpRes = await axios.get(`${API}/mfps/`)
    mfps.value = mfpRes.data
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    showError('Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message))
  }
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
  
  if (newMFP.value.mac_address && !isValidMAC(newMFP.value.mac_address)) {
    showWarning('Пожалуйста, введите корректный MAC адрес (формат: XX:XX:XX:XX:XX:XX)')
    return
  }
  
  try {
    const mfpData = {
      asset_number: newMFP.value.asset_number || 'не определен',
      model: newMFP.value.model,
      ip_address: newMFP.value.ip_address || null,
      cabinet_number: newMFP.value.cabinet_number || null,
      login: newMFP.value.login || null,
      password: newMFP.value.password || null,
      status: newMFP.value.status,
      notes: newMFP.value.notes || null,
      serial_number: newMFP.value.serial_number || null,
      mac_address: newMFP.value.mac_address || null
    }
    
    await axios.post(`${API}/mfps/`, mfpData)
    
    newMFP.value = {
      asset_number: 'не определен',
      model: '',
      ip_address: '',
      cabinet_number: '',
      login: '',
      password: '',
      status: 'operational',
      notes: '',
      serial_number: '',
      mac_address: ''
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
    ip_address: mfp.ip_address || '',
    cabinet_number: mfp.cabinet_number || '',
    login: mfp.login || '',
    password: mfp.password || '',
    status: mfp.status || 'operational',
    notes: mfp.notes || '',
    serial_number: mfp.serial_number || '',
    mac_address: mfp.mac_address || ''
  }
  showEditModal.value = true
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
  
  if (editMFP.value.mac_address && !isValidMAC(editMFP.value.mac_address)) {
    showWarning('Пожалуйста, введите корректный MAC адрес (формат: XX:XX:XX:XX:XX:XX)')
    return
  }
  
  try {
    const mfpData = {
      asset_number: editMFP.value.asset_number,
      model: editMFP.value.model,
      ip_address: editMFP.value.ip_address || null,
      cabinet_number: editMFP.value.cabinet_number || null,
      login: editMFP.value.login || null,
      password: editMFP.value.password || null,
      status: editMFP.value.status,
      notes: editMFP.value.notes || null,
      serial_number: editMFP.value.serial_number || null,
      mac_address: editMFP.value.mac_address || null
    }
    
    await axios.put(`${API}/mfps/${editMFP.value.id}/`, mfpData)
    showEditModal.value = false
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
  padding: 1rem;
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

.textarea-field {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  line-height: 1.5;
}

.textarea-field:focus {
  outline: none;
  border-color: #1abc9c;
  box-shadow: 0 0 0 3px rgba(26, 188, 156, 0.1);
}

.ip-input, .mac-input {
  font-family: 'Courier New', monospace;
  letter-spacing: 0.5px;
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
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 1rem;
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

.mfp-title {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.mfp-title strong {
  font-size: 1rem;
  color: #2c3e50;
}

.asset-badge {
  background: #3498db;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 500;
}

.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.status-badge-small {
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

.status-write-off {
  background: #f8d7da;
  color: #721c24;
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 12px;
}

.info-item {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  gap: 4px;
  font-size: 0.8rem;
}

.info-item.full-width {
  grid-column: span 2;
}

.info-item .label {
  font-weight: 600;
  color: #666;
  min-width: 70px;
}

.info-item .value {
  color: #333;
  word-break: break-all;
}

.mac-value {
  font-family: 'Courier New', monospace;
  font-size: 0.75rem;
}

.value.notes {
  font-style: italic;
  color: #e67e22;
}

.compatible-cartridges {
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid #eee;
}

.compatible-cartridges .label {
  font-weight: 600;
  color: #666;
  font-size: 0.75rem;
  margin-bottom: 6px;
}

.cartridges-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.cartridge-tag {
  background: #e0e0e0;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  color: #555;
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
  max-width: 600px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
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
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .info-item.full-width {
    grid-column: span 1;
  }
  
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
  
  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .card-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>