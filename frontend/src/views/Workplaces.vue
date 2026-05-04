<template>
  <div class="page">
    <h1>📌 Рабочие места</h1>
    <p class="note">У одного сотрудника может быть несколько рабочих мест</p>

    <!-- Форма создания рабочего места -->
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

      <!-- Компьютер -->
      <div class="form-group">
        <label>Компьютер (необязательно):</label>
        <div class="search-wrapper">
          <input 
            type="text" 
            v-model="computerSearch" 
            @input="searchComputer" 
            @focus="searchComputer"
            placeholder="Введите номер ОС или системный блок..."
            class="search-input"
          >
          <div v-if="computerSearchResults.length" class="search-results">
            <div 
              v-for="comp in computerSearchResults" 
              :key="comp.id" 
              @click="selectComputer(comp)"
              class="search-result-item"
            >
              ОС №{{ comp.asset_number }} - {{ comp.system_unit || 'системный блок не указан' }}
            </div>
          </div>
        </div>
        <div v-if="selectedComputer" class="selected-tag">
          ОС №{{ selectedComputer.asset_number }} - {{ selectedComputer.system_unit || 'системный блок не указан' }}
          <button @click="selectedComputer = null" class="remove-btn">×</button>
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
        <div v-for="wp in paginatedWorkplaces" :key="wp.id" class="card">
          <div class="card-header">
            <div class="employee-info">
              <div class="clickable-employee" @click="openEmployeeEditModal(wp.employee)">
                <strong>{{ wp.employee_name }}</strong>
                <span class="edit-hint-small">✏️</span>
              </div>
              <span v-if="wp.department_name" class="department-badge">
                📍 {{ wp.department_name }}
              </span>
            </div>
            <button @click="deleteWorkplace(wp.id)" class="delete-btn" title="Удалить">🗑️</button>
          </div>
          <div class="card-body">
            <!-- Город -->
            <div class="info-row clickable" @click="openEditModal(wp, 'city')">
              <span class="label">🏙️ Город:</span>
              <span class="value">{{ wp.city_name || 'Не указан' }}</span>
              <span class="edit-hint">✏️</span>
            </div>
            
            <!-- МФУ -->
            <div class="info-row">
              <span class="label">🖨️ МФУ:</span>
              <div class="flex-row">
                <div class="clickable-value" @click="openMFPEditModal(wp)">
                  <span class="value">{{ wp.mfp_detail?.model || 'Не указан' }}</span>
                  <span class="edit-hint">✏️</span>
                </div>
              </div>
            </div>
            
            <!-- ИБП -->
            <div class="info-row">
              <span class="label">🔋 ИБП:</span>
              <div class="flex-row">
                <div class="clickable-value" @click="openEditModal(wp, 'ups')">
                  <span class="value">
                    {{ wp.ups_detail?.model || 'Не указан' }}
                    <span v-if="wp.ups_detail?.battery_replaced_at" class="battery-date">
                      (АКБ заменён: {{ formatDate(wp.ups_detail.battery_replaced_at) }})
                    </span>
                  </span>
                  <span class="edit-hint">✏️</span>
                </div>
                <button 
                  v-if="wp.ups_detail" 
                  @click="openUPSServiceModal(wp.ups_detail)" 
                  class="service-btn" 
                  title="Обслуживание ИБП"
                >
                  🔧
                </button>
              </div>
            </div>
            
            <!-- Компьютер -->
            <div class="info-row">
              <span class="label">🖥️ Компьютер:</span>
              <div class="flex-row">
                <div class="clickable-value" @click="openEditModal(wp, 'computer')">
                  <span class="value">
                    <span v-if="wp.computer_detail">
                      ОС №{{ wp.computer_detail.asset_number }}
                      <span v-if="wp.computer_detail.computer_type">({{ getComputerTypeText(wp.computer_detail.computer_type) }})</span>
                    </span>
                    <span v-else class="no-data">Не указан</span>
                  </span>
                  <span class="edit-hint">✏️</span>
                </div>
                <button 
                  v-if="wp.computer_detail" 
                  @click.stop="openComputerDetailsModal(wp.computer_detail)" 
                  class="details-btn" 
                  title="Детализация компьютера"
                >
                  📋
                </button>
              </div>
            </div>
            
            <!-- Комментарий ИБП -->
            <div v-if="wp.ups_detail?.comment" class="info-row comment-row">
              <span class="label">💬 Комментарий ИБП:</span>
              <span class="value comment">{{ wp.ups_detail.comment }}</span>
            </div>
            
            <!-- Статус -->
            <div class="info-row clickable" @click="openEditModal(wp, 'status')">
              <span class="label">📊 Статус:</span>
              <span :class="['status-badge', getStatusClass(wp.status)]">
                {{ getStatusText(wp.status) }}
              </span>
              <span class="edit-hint">✏️</span>
            </div>
            
            <!-- Дата создания -->
            <div class="info-row">
              <span class="label">📅 Создано:</span>
              <span class="value">{{ formatDate(wp.created_at) }}</span>
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

    <!-- Модальное окно редактирования сотрудника -->
    <div v-if="showEmployeeEditModal" class="modal">
      <div class="modal-content modal-large">
        <h3>✏️ Редактировать сотрудника</h3>
        <p class="modal-subtitle">Редактирование данных сотрудника</p>
        
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
        
        <div class="form-group">
          <label>Отдел:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="editEmployeeDepartmentSearch" 
              @input="searchEditEmployeeDepartments" 
              @focus="searchEditEmployeeDepartments"
              placeholder="Поиск отдела..."
              class="search-input"
            >
            <div v-if="editEmployeeDepartmentSearchResults.length" class="search-results">
              <div 
                v-for="dep in editEmployeeDepartmentSearchResults" 
                :key="dep.id" 
                @click="selectEditEmployeeDepartment(dep)"
                class="search-result-item"
              >
                {{ dep.name }}
              </div>
            </div>
          </div>
          <div v-if="editEmployeeSelectedDepartment" class="selected-tag">
            {{ editEmployeeSelectedDepartment.name }}
            <button @click="editEmployeeSelectedDepartment = null" class="remove-btn">×</button>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateEmployee" class="save-btn">💾 Сохранить</button>
          <button @click="closeEmployeeEditModal" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования МФУ -->
    <div v-if="showMFPEditModal" class="modal">
      <div class="modal-content modal-large">
        <h3>✏️ Редактировать МФУ</h3>
        <p class="modal-subtitle">Текущее МФУ: <strong>{{ editMFPData?.model || 'Не указано' }}</strong></p>
        
        <div class="form-group">
          <label>Номер основного средства:</label>
          <input v-model="editMFPData.asset_number" class="main-field">
        </div>
        
        <div class="form-group">
          <label>Модель МФУ:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="editMFPModelSearch" 
              @input="searchEditMFPModels" 
              @focus="searchEditMFPModels"
              placeholder="Поиск модели МФУ..."
              class="search-input"
            >
            <div v-if="editMFPModelSearchResults.length" class="search-results">
              <div 
                v-for="m in editMFPModelSearchResults" 
                :key="m.id" 
                @click="selectEditMFPModel(m)"
                class="search-result-item"
              >
                {{ m.model }}
              </div>
            </div>
          </div>
          <div v-if="editMFPSelectedModel" class="selected-tag">
            {{ editMFPSelectedModel.model }}
            <button @click="editMFPSelectedModel = null" class="remove-btn">×</button>
          </div>
        </div>
        
        <div class="form-group">
          <label>IP адрес:</label>
          <input 
            v-model="editMFPData.ip_address" 
            placeholder="192.168.1.100"
            class="search-input ip-input"
          >
          <small class="field-hint">Формат: XXX.XXX.XXX.XXX (например: 10.10.29.25)</small>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateMFP" class="save-btn">💾 Сохранить</button>
          <button @click="showMFPEditModal = false" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно редактирования рабочего места -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content modal-large">
        <h3>✏️ Редактировать рабочее место</h3>
        <p class="modal-subtitle">Сотрудник: <strong>{{ editWorkplace.employee_name }}</strong></p>
        
        <div v-if="editField === 'city'">
          <div class="form-group">
            <label>Город:</label>
            <select v-model="editCityValue" class="search-input">
              <option :value="null">Выберите город</option>
              <option v-for="city in locations" :key="city.id" :value="city.id">
                {{ city.name }}
              </option>
            </select>
          </div>
        </div>
        
        <div v-if="editField === 'ups'">
          <div class="form-group">
            <label>ИБП:</label>
            <div class="search-wrapper">
              <input 
                type="text" 
                v-model="editUPSSearch" 
                @input="searchEditUPS" 
                @focus="searchEditUPS"
                placeholder="Поиск ИБП..."
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
            <div v-if="editSelectedUPS" class="selected-tag">
              ОС №{{ editSelectedUPS.asset_number }} - {{ editSelectedUPS.model }}
              <button @click="editSelectedUPS = null" class="remove-btn">×</button>
            </div>
          </div>
        </div>
        
        <div v-if="editField === 'computer'">
          <div class="form-group">
            <label>Компьютер:</label>
            <div class="search-wrapper">
              <input 
                type="text" 
                v-model="editComputerSearch" 
                @input="searchEditComputer" 
                @focus="searchEditComputer"
                placeholder="Поиск компьютера..."
                class="search-input"
              >
              <div v-if="editComputerSearchResults.length" class="search-results">
                <div 
                  v-for="comp in editComputerSearchResults" 
                  :key="comp.id" 
                  @click="selectEditComputer(comp)"
                  class="search-result-item"
                >
                  ОС №{{ comp.asset_number }} - {{ comp.system_unit || 'системный блок не указан' }}
                </div>
              </div>
            </div>
            <div v-if="editSelectedComputer" class="selected-tag">
              ОС №{{ editSelectedComputer.asset_number }} - {{ editSelectedComputer.system_unit || 'системный блок не указан' }}
              <button @click="editSelectedComputer = null" class="remove-btn">×</button>
            </div>
          </div>
        </div>
        
        <div v-if="editField === 'status'">
          <div class="form-group">
            <label>Статус:</label>
            <select v-model="editStatusValue" class="search-input">
              <option value="active">✅ Активно</option>
              <option value="inactive">❌ Неактивно</option>
              <option value="maintenance">🔧 На обслуживании</option>
              <option value="repair">⚠️ Требует ремонта</option>
            </select>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="updateWorkplaceField" class="save-btn">💾 Сохранить</button>
          <button @click="closeEditModal" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно детализации компьютера -->
    <div v-if="showComputerDetailsModal" class="modal">
      <div class="modal-content modal-large">
        <h3>🖥️ Детали компьютера</h3>
        <p class="modal-subtitle">ОС №{{ computerDetails?.asset_number }}</p>
        
        <div class="computer-details">
          <div class="detail-row">
            <span class="detail-label">🖥️ Тип:</span>
            <span class="detail-value">{{ getComputerTypeText(computerDetails?.computer_type) }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">💻 Системный блок:</span>
            <span class="detail-value">{{ computerDetails?.system_unit || 'Не указан' }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">🖥️ Мониторы:</span>
            <span class="detail-value">
              <span v-if="computerDetails?.monitors_detail && computerDetails.monitors_detail.length">
                {{ computerDetails.monitors_detail.map(m => m.brand).join(', ') }}
              </span>
              <span v-else class="no-data">нет</span>
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">⌨️ Периферия:</span>
            <span class="detail-value">
              <span v-if="computerDetails?.has_keyboard && computerDetails?.has_mouse">Клавиатура, Мышь</span>
              <span v-else-if="computerDetails?.has_keyboard">Клавиатура</span>
              <span v-else-if="computerDetails?.has_mouse">Мышь</span>
              <span v-else class="no-data">нет</span>
            </span>
          </div>
          <div class="detail-row">
            <span class="detail-label">🔧 Статус:</span>
            <span :class="['service-badge', getServiceStatusClass(computerDetails?.service_status)]">
              {{ getServiceStatusText(computerDetails?.service_status) }}
            </span>
          </div>
        </div>
        
        <div class="modal-buttons">
          <button @click="showComputerDetailsModal = false" class="cancel-btn">Закрыть</button>
        </div>
      </div>
    </div>

    <!-- Модальное окно обслуживания ИБП -->
    <div v-if="showUPSServiceModal" class="modal">
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
const locations = ref([])
const allMFPs = ref([])
const allUPS = ref([])
const allComputers = ref([])
const allDepartments = ref([])

// Пагинация
const currentPage = ref(1)
const itemsPerPage = 4

// Выбранные значения для создания
const selectedEmployee = ref(null)
const selectedMFP = ref(null)
const selectedUPS = ref(null)
const selectedComputer = ref(null)

// Поисковые запросы для создания
const employeeSearch = ref('')
const employeeSearchResults = ref([])
const mfpSearch = ref('')
const mfpSearchResults = ref([])
const upsSearch = ref('')
const upsSearchResults = ref([])
const computerSearch = ref('')
const computerSearchResults = ref([])

// Форма создания
const form = ref({
  city: null,
  status: 'active',
  mfp: null,
  ups: null,
  computer: null
})

// Модальные окна
const showEditModal = ref(false)
const showEmployeeEditModal = ref(false)
const showComputerDetailsModal = ref(false)
const showUPSServiceModal = ref(false)
const showMFPEditModal = ref(false)

// Данные для редактирования рабочего места
const editWorkplace = ref({
  id: null,
  employee_name: '',
  city: null,
  mfp: null,
  ups: null,
  computer: null,
  status: 'active'
})
const editField = ref('')
const editCityValue = ref(null)
const editSelectedUPS = ref(null)
const editSelectedComputer = ref(null)
const editStatusValue = ref('active')

// Данные для редактирования МФУ
const editMFPData = ref({
  id: null,
  asset_number: '',
  model: '',
  ip_address: ''
})
const editMFPModelSearch = ref('')
const editMFPModelSearchResults = ref([])
const editMFPSelectedModel = ref(null)

// Поиск для модальных окон
const editUPSSearch = ref('')
const editUPSSearchResults = ref([])
const editComputerSearch = ref('')
const editComputerSearchResults = ref([])

// Данные для редактирования сотрудника
const editEmployee = ref({
  id: null,
  last_name: '',
  first_name: '',
  patronymic: '',
  department: null
})
const editEmployeeDepartmentSearch = ref('')
const editEmployeeDepartmentSearchResults = ref([])
const editEmployeeSelectedDepartment = ref(null)

// Данные для обслуживания ИБП
const selectedUPSForService = ref(null)
const upsBatteryHistory = ref([])
const newBattery = ref({
  old_battery_serial: '',
  new_battery_serial: '',
  performed_by: '',
  comment: ''
})

// Детали компьютера
const computerDetails = ref(null)

const confirmModal = ref(null)

// Пагинированные рабочие места
const paginatedWorkplaces = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return workplaces.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(workplaces.value.length / itemsPerPage)
})

// Форматирование даты
const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ru-RU')
}

// Валидация IP
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

// Типы компьютеров
const getComputerTypeText = (type) => {
  const texts = {
    'desktop': 'Стационарный',
    'laptop': 'Ноутбук',
    'all-in-one': 'Моноблок'
  }
  return texts[type] || 'Не указан'
}

// Статусы обслуживания компьютера
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
const fetchData = async () => {
  try {
    const [empRes, wpRes, locRes, mfpRes, upsRes, compRes, depRes] = await Promise.all([
      axios.get(`${API}/employees/`),
      axios.get(`${API}/workplaces/`),
      axios.get(`${API}/locations/`),
      axios.get(`${API}/mfps/`),
      axios.get(`${API}/ups/`),
      axios.get(`${API}/computers/`),
      axios.get(`${API}/departments/`)
    ])
    employees.value = empRes.data
    workplaces.value = wpRes.data
    locations.value = locRes.data
    allMFPs.value = mfpRes.data
    allUPS.value = upsRes.data
    allComputers.value = compRes.data
    allDepartments.value = depRes.data
  } catch (error) {
    console.error('Ошибка загрузки:', error)
    showError('Ошибка загрузки данных: ' + (error.response?.data?.detail || error.message))
  }
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

// Открытие модального окна редактирования МФУ
const openMFPEditModal = (workplace) => {
  editWorkplace.value = {
    id: workplace.id,
    employee_name: workplace.employee_name
  }
  
  if (workplace.mfp_detail) {
    editMFPData.value = {
      id: workplace.mfp_detail.id,
      asset_number: workplace.mfp_detail.asset_number,
      model: workplace.mfp_detail.model,
      ip_address: workplace.mfp_detail.ip_address || ''
    }
    editMFPSelectedModel.value = { id: workplace.mfp_detail.id, model: workplace.mfp_detail.model }
  } else {
    editMFPData.value = {
      id: null,
      asset_number: '',
      model: '',
      ip_address: ''
    }
    editMFPSelectedModel.value = null
  }
  editMFPModelSearch.value = ''
  editMFPModelSearchResults.value = []
  showMFPEditModal.value = true
}

// Поиск моделей МФУ для редактирования
const searchEditMFPModels = () => {
  if (!editMFPModelSearch.value) {
    editMFPModelSearchResults.value = []
    return
  }
  const uniqueModels = []
  const modelMap = new Map()
  allMFPs.value.forEach(mfp => {
    if (!modelMap.has(mfp.model)) {
      modelMap.set(mfp.model, { id: mfp.id, model: mfp.model })
      uniqueModels.push({ id: mfp.id, model: mfp.model })
    }
  })
  editMFPModelSearchResults.value = uniqueModels.filter(m => 
    m.model.toLowerCase().includes(editMFPModelSearch.value.toLowerCase())
  ).slice(0, 10)
}

const selectEditMFPModel = (model) => {
  editMFPSelectedModel.value = model
  editMFPData.value.model = model.model
  editMFPModelSearch.value = ''
  editMFPModelSearchResults.value = []
}

// Обновление МФУ
const updateMFP = async () => {
  if (!editMFPData.value.model) {
    showWarning('Пожалуйста, укажите модель МФУ')
    return
  }
  
  if (editMFPData.value.ip_address && !isValidIP(editMFPData.value.ip_address)) {
    showWarning('Пожалуйста, введите корректный IP адрес (формат: 192.168.1.100)')
    return
  }
  
  try {
    let mfpId = editMFPData.value.id
    
    if (!mfpId) {
      const newMFPData = {
        asset_number: editMFPData.value.asset_number || 'не определен',
        model: editMFPData.value.model,
        ip_address: editMFPData.value.ip_address || null
      }
      const response = await axios.post(`${API}/mfps/`, newMFPData)
      mfpId = response.data.id
    } else {
      const updateData = {
        asset_number: editMFPData.value.asset_number,
        model: editMFPData.value.model,
        ip_address: editMFPData.value.ip_address || null
      }
      await axios.put(`${API}/mfps/${mfpId}/`, updateData)
    }
    
    await axios.patch(`${API}/workplaces/${editWorkplace.value.id}/`, {
      mfp: mfpId
    })
    
    showMFPEditModal.value = false
    await fetchData()
    showSuccess('МФУ успешно обновлено!')
  } catch (error) {
    console.error('Ошибка обновления МФУ:', error)
    showError('Ошибка обновления МФУ: ' + (error.response?.data?.detail || error.message))
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

// Закрытие модального окна обслуживания ИБП
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
    await fetchData()
    
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
      await fetchData()
      showSuccess('Запись удалена!')
    } catch (error) {
      console.error('Ошибка удаления:', error)
      showError('Ошибка удаления записи')
    }
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

// Поиск МФУ
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

// Поиск ИБП
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

// Поиск компьютера
const searchComputer = () => {
  if (!computerSearch.value) {
    computerSearchResults.value = []
    return
  }
  computerSearchResults.value = allComputers.value.filter(comp => 
    comp.asset_number.toLowerCase().includes(computerSearch.value.toLowerCase()) ||
    (comp.system_unit && comp.system_unit.toLowerCase().includes(computerSearch.value.toLowerCase()))
  ).slice(0, 10)
}

const selectComputer = (comp) => {
  selectedComputer.value = comp
  form.value.computer = comp.id
  computerSearch.value = ''
  computerSearchResults.value = []
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
      computer: form.value.computer || null,
      is_active: form.value.status === 'active'
    }
    
    await axios.post(`${API}/workplaces/`, workplaceData)
    
    form.value = { city: null, status: 'active', mfp: null, ups: null, computer: null }
    selectedEmployee.value = null
    selectedMFP.value = null
    selectedUPS.value = null
    selectedComputer.value = null
    employeeSearch.value = ''
    mfpSearch.value = ''
    upsSearch.value = ''
    computerSearch.value = ''
    
    await fetchData()
    currentPage.value = Math.ceil(workplaces.value.length / itemsPerPage)
    showSuccess('Рабочее место успешно создано!')
  } catch (error) {
    console.error('Ошибка создания:', error)
    showError('Ошибка создания рабочего места: ' + (error.response?.data?.detail || error.message))
  }
}

// Поиск для модальных окон
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
  editSelectedUPS.value = ups
  editUPSSearch.value = ''
  editUPSSearchResults.value = []
}

const searchEditComputer = () => {
  if (!editComputerSearch.value) {
    editComputerSearchResults.value = []
    return
  }
  editComputerSearchResults.value = allComputers.value.filter(comp => 
    comp.asset_number.toLowerCase().includes(editComputerSearch.value.toLowerCase()) ||
    (comp.system_unit && comp.system_unit.toLowerCase().includes(editComputerSearch.value.toLowerCase()))
  ).slice(0, 10)
}

const selectEditComputer = (comp) => {
  editSelectedComputer.value = comp
  editComputerSearch.value = ''
  editComputerSearchResults.value = []
}

// Поиск отделов для редактирования сотрудника
const searchEditEmployeeDepartments = () => {
  if (!editEmployeeDepartmentSearch.value) {
    editEmployeeDepartmentSearchResults.value = []
    return
  }
  editEmployeeDepartmentSearchResults.value = allDepartments.value.filter(d => 
    d.name.toLowerCase().includes(editEmployeeDepartmentSearch.value.toLowerCase())
  ).slice(0, 10)
}

const selectEditEmployeeDepartment = (department) => {
  editEmployeeSelectedDepartment.value = department
  editEmployee.value.department = department.id
  editEmployeeDepartmentSearch.value = ''
  editEmployeeDepartmentSearchResults.value = []
}

// Открытие модального окна редактирования рабочего места
const openEditModal = (workplace, field) => {
  editWorkplace.value = {
    id: workplace.id,
    employee_name: workplace.employee_name,
    city: workplace.city,
    mfp: workplace.mfp,
    ups: workplace.ups,
    computer: workplace.computer,
    status: workplace.status
  }
  editField.value = field
  editCityValue.value = workplace.city
  editSelectedUPS.value = workplace.ups_detail
  editSelectedComputer.value = workplace.computer_detail
  editStatusValue.value = workplace.status
  editUPSSearch.value = ''
  editUPSSearchResults.value = []
  editComputerSearch.value = ''
  editComputerSearchResults.value = []
  showEditModal.value = true
}

// Закрытие модального окна редактирования
const closeEditModal = () => {
  showEditModal.value = false
  editField.value = ''
  editSelectedUPS.value = null
  editSelectedComputer.value = null
}

// Открытие модального окна редактирования сотрудника
const openEmployeeEditModal = (employeeId) => {
  const employee = employees.value.find(e => e.id === employeeId)
  if (employee) {
    editEmployee.value = {
      id: employee.id,
      last_name: employee.last_name,
      first_name: employee.first_name,
      patronymic: employee.patronymic || '',
      department: employee.department
    }
    editEmployeeSelectedDepartment.value = allDepartments.value.find(d => d.id === employee.department) || null
    editEmployeeDepartmentSearch.value = ''
    editEmployeeDepartmentSearchResults.value = []
    showEmployeeEditModal.value = true
  }
}

// Закрытие модального окна редактирования сотрудника
const closeEmployeeEditModal = () => {
  showEmployeeEditModal.value = false
  editEmployee.value = {
    id: null,
    last_name: '',
    first_name: '',
    patronymic: '',
    department: null
  }
  editEmployeeSelectedDepartment.value = null
}

// Обновление поля рабочего места
const updateWorkplaceField = async () => {
  try {
    let updateData = {}
    
    switch (editField.value) {
      case 'city':
        updateData = { city: editCityValue.value }
        break
      case 'ups':
        updateData = { ups: editSelectedUPS.value?.id || null }
        break
      case 'computer':
        updateData = { computer: editSelectedComputer.value?.id || null }
        break
      case 'status':
        updateData = { 
          status: editStatusValue.value,
          is_active: editStatusValue.value === 'active'
        }
        break
    }
    
    await axios.patch(`${API}/workplaces/${editWorkplace.value.id}/`, updateData)
    closeEditModal()
    await fetchData()
    showSuccess('Поле успешно обновлено!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления: ' + (error.response?.data?.detail || error.message))
  }
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
    closeEmployeeEditModal()
    await fetchData()
    showSuccess('Сотрудник успешно обновлен!')
  } catch (error) {
    console.error('Ошибка обновления:', error)
    showError('Ошибка обновления сотрудника: ' + (error.response?.data?.detail || error.message))
  }
}

// Открытие модального окна с деталями компьютера
const openComputerDetailsModal = (computer) => {
  computerDetails.value = computer
  showComputerDetailsModal.value = true
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
      if (paginatedWorkplaces.value.length === 1 && currentPage.value > 1) {
        currentPage.value--
      }
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
/* Все стили остаются как в предыдущей версии */
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
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
  flex-wrap: wrap;
  gap: 8px;
}

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

.delete-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #e74c3c;
  padding: 5px;
  border-radius: 6px;
  transition: all 0.2s;
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
  padding: 4px 0;
}

.info-row.clickable {
  cursor: pointer;
}

.info-row.clickable:hover {
  background: rgba(26, 188, 156, 0.05);
  border-radius: 8px;
}

.label {
  font-weight: 600;
  color: #666;
  min-width: 100px;
  flex-shrink: 0;
}

.value {
  color: #333;
  flex: 1;
}

.flex-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.clickable-value {
  flex: 1;
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 4px 8px;
  margin: -4px -8px;
  border-radius: 6px;
  transition: background 0.2s;
}

.clickable-value:hover {
  background: rgba(26, 188, 156, 0.1);
}

.clickable-value .edit-hint {
  opacity: 0;
  margin-left: 8px;
  font-size: 0.7rem;
  color: #1abc9c;
  transition: opacity 0.2s;
}

.clickable-value:hover .edit-hint {
  opacity: 1;
}

.edit-hint {
  opacity: 0;
  margin-left: 8px;
  font-size: 0.7rem;
  color: #1abc9c;
  transition: opacity 0.2s;
}

.info-row.clickable:hover .edit-hint {
  opacity: 1;
}

.service-btn, .details-btn {
  background: none;
  border: none;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 4px 8px;
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

.details-btn {
  color: #3498db;
}

.details-btn:hover {
  background: #3498db;
  color: white;
}

.comment-row {
  background: #fef5e7;
  border-left: 3px solid #f39c12;
  padding: 6px 10px;
  border-radius: 8px;
}

.value.comment {
  font-style: italic;
  color: #e67e22;
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

/* Стили для обслуживания ИБП */
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

/* Детали компьютера */
.computer-details {
  margin-top: 1rem;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  padding: 8px;
  border-bottom: 1px solid #eee;
}

.detail-label {
  font-weight: 600;
  color: #555;
  min-width: 120px;
  flex-shrink: 0;
}

.detail-value {
  color: #333;
  flex: 1;
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

.ip-input {
  font-family: 'Courier New', monospace;
  font-size: 1rem;
  letter-spacing: 0.5px;
}

.field-hint {
  display: block;
  margin-top: 5px;
  font-size: 0.75rem;
  color: #999;
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

@media (max-width: 768px) {
  .cards-grid {
    grid-template-columns: 1fr;
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
  
  .form-row {
    flex-direction: column;
  }
  
  .form-row .form-group {
    margin-bottom: 1rem;
  }
  
  .flex-row {
    flex-wrap: wrap;
  }
}
</style>