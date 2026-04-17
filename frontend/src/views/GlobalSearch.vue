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
  
      <div v-else-if="totalResults === 0" class="no-results">
        <p>😕 Ничего не найдено по запросу "{{ searchQuery }}"</p>
        <p class="hint">Попробуйте изменить поисковый запрос</p>
      </div>
  
      <div v-else>
        <!-- Компьютеры -->
        <div v-if="searchResults.computers.length" class="results-section">
          <h2 class="section-title">
            <span class="section-icon">🖥️</span>
            Компьютеры ({{ searchResults.computers.length }})
          </h2>
          <div class="results-grid">
            <div v-for="comp in searchResults.computers" :key="comp.id" class="result-card computer-card">
              <div class="card-header">
                <strong>ОС №{{ comp.asset_number }}</strong>
                <span v-if="comp.needs_upgrade" class="badge-warning">⚠️ Модернизация</span>
              </div>
              <div class="card-body">
                <div><span class="label">💻 Системный блок:</span> {{ comp.system_unit || 'Не указан' }}</div>
                <div><span class="label">🖥️ Мониторы:</span> {{ getMonitorsList(comp) }}</div>
                <div><span class="label">⌨️ Периферия:</span> {{ getPeripherals(comp) }}</div>
                <div><span class="label">📍 Отдел:</span> {{ comp.department_name || 'Не указан' }}</div>
                <div><span class="label">👤 Сотрудник:</span> {{ comp.assigned_to_name || 'Не закреплен' }}</div>
              </div>
              <div class="card-footer">
                <button @click="goToComputer(comp.id)" class="view-btn">📋 Подробнее</button>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Сотрудники -->
        <div v-if="searchResults.employees.length" class="results-section">
          <h2 class="section-title">
            <span class="section-icon">👥</span>
            Сотрудники ({{ searchResults.employees.length }})
          </h2>
          <div class="results-grid">
            <div v-for="emp in searchResults.employees" :key="emp.id" class="result-card employee-card">
              <div class="card-header">
                <strong>{{ emp.last_name }} {{ emp.first_name }} {{ emp.patronymic || '' }}</strong>
              </div>
              <div class="card-body">
                <div><span class="label">📍 Отдел:</span> {{ emp.department_name || 'Не указан' }}</div>
                <div><span class="label">🔋 ИБП:</span> 
                  <span v-if="emp.ups_asset_number_detail">
                    ОС №{{ emp.ups_asset_number_detail.asset_number }} - {{ emp.ups_asset_number_detail.model }}
                    <span v-if="emp.ups_asset_number_detail.battery_replaced_at" class="battery-date">
                      (АКБ заменён: {{ formatDate(emp.ups_asset_number_detail.battery_replaced_at) }})
                    </span>
                  </span>
                  <span v-else class="no-data">Не закреплен</span>
                </div>
              </div>
              <div class="card-footer">
                <button @click="goToEmployee(emp.id)" class="view-btn">📋 Подробнее</button>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Рабочие места -->
        <div v-if="searchResults.workplaces.length" class="results-section">
          <h2 class="section-title">
            <span class="section-icon">📍</span>
            Рабочие места ({{ searchResults.workplaces.length }})
          </h2>
          <div class="results-grid">
            <div v-for="wp in searchResults.workplaces" :key="wp.id" class="result-card workplace-card">
              <div class="card-header">
                <strong>{{ wp.employee_name }}</strong>
                <span :class="['status-badge', getStatusClass(wp.status)]">
                  {{ getStatusText(wp.status) }}
                </span>
              </div>
              <div class="card-body">
                <div><span class="label">🏙️ Расположение:</span> {{ wp.city_name || 'Не указан' }}</div>
                <div><span class="label">🖨️ МФУ:</span> 
                  <span v-if="wp.mfp_detail">
                    ОС №{{ wp.mfp_detail.asset_number }} - {{ wp.mfp_detail.model }}
                    <span v-if="wp.mfp_detail.ip_address" class="ip-address">
                        <br>
                        (IP: {{ wp.mfp_detail.ip_address }})</span>
                  </span>
                  <span v-else class="no-data">Не указан</span>
                </div>
                <div><span class="label">🔋 ИБП:</span> 
                  <span v-if="wp.ups_detail">
                    ОС №{{ wp.ups_detail.asset_number }} - {{ wp.ups_detail.model }}
                    <span v-if="wp.ups_detail.battery_replaced_at" class="battery-date">
                        <br> 
                    (АКБ заменён:{{ formatDate(wp.ups_detail.battery_replaced_at) }})
                    
                      
                    </span>
                  </span>
                  <span v-else class="no-data">Не указан</span>
                </div>
                <div><span class="label">📅 Создано:</span> {{ formatDate(wp.created_at) }}</div>
              </div>
              <div class="card-footer">
                <button @click="goToWorkplace" class="view-btn">📋 Подробнее</button>
              </div>
            </div>
          </div>
        </div>
  
        <!-- МФУ -->
        <div v-if="searchResults.mfps.length" class="results-section">
          <h2 class="section-title">
            <span class="section-icon">🖨️</span>
            МФУ ({{ searchResults.mfps.length }})
          </h2>
          <div class="results-grid">
            <div v-for="mfp in searchResults.mfps" :key="mfp.id" class="result-card mfp-card">
              <div class="card-header">
                <strong>ОС №{{ mfp.asset_number }}</strong>
              </div>
              <div class="card-body">
                <div><span class="label">📠 Модель:</span> {{ mfp.model }}</div>
                <div><span class="label">📍 Отдел:</span> {{ mfp.department_name || 'Не указан' }}</div>
                <div><span class="label">🌐 IP адрес:</span> 
                  <code class="ip-address">{{ mfp.ip_address || 'не указан' }}</code>
                </div>
              </div>
              <div class="card-footer">
                <button @click="goToMFP(mfp.id)" class="view-btn">📋 Подробнее</button>
              </div>
            </div>
          </div>
        </div>
  
        <!-- Телевизоры -->
        <div v-if="searchResults.tvs.length" class="results-section">
          <h2 class="section-title">
            <span class="section-icon">📺</span>
            Телевизоры ({{ searchResults.tvs.length }})
          </h2>
          <div class="results-grid">
            <div v-for="tv in searchResults.tvs" :key="tv.id" class="result-card tv-card">
              <div class="card-header">
                <strong>ОС №{{ tv.asset_number || 'не определен' }}</strong>
              </div>
              <div class="card-body">
                <div><span class="label">📺 Марка:</span> {{ tv.brand }}</div>
                <div><span class="label">📏 Диагональ:</span> {{ tv.size }}"</div>
                <div><span class="label">📍 Место:</span> {{ tv.location || 'не указано' }}</div>
              </div>
              <div class="card-footer">
                <button @click="goToTV(tv.id)" class="view-btn">📋 Подробнее</button>
              </div>
            </div>
          </div>
        </div>
  
        <!-- ИБП -->
        <div v-if="searchResults.ups.length" class="results-section">
          <h2 class="section-title">
            <span class="section-icon">🔋</span>
            ИБП ({{ searchResults.ups.length }})
          </h2>
          <div class="results-grid">
            <div v-for="ups in searchResults.ups" :key="ups.id" class="result-card ups-card">
              <div class="card-header">
                <strong>ОС №{{ ups.asset_number }}</strong>
              </div>
              <div class="card-body">
                <div><span class="label">🔋 Модель:</span> {{ ups.model }}</div>
                <div><span class="label">📍 Отдел:</span> {{ ups.department_name || 'Не указан' }}</div>
                <div><span class="label">🔧 Аккумулятор:</span> 
                  <span v-if="ups.battery_serial_number">{{ ups.battery_serial_number }}</span>
                  <span v-else class="no-data">не указан</span>
                </div>
                <div><span class="label">📅 Замена АКБ:</span> 
                  <span v-if="ups.battery_replaced_at" class="battery-date">{{ formatDate(ups.battery_replaced_at) }}</span>
                  <span v-else class="no-data">не заменялся</span>
                </div>
                <div v-if="ups.comment"><span class="label">💬 Комментарий:</span> {{ ups.comment }}</div>
              </div>
              <div class="card-footer">
                <button @click="goToUPS(ups.id)" class="view-btn">📋 Подробнее</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import axios from 'axios'
  
  const route = useRoute()
  const router = useRouter()
  const API = 'http://localhost:8000/api'
  
  const loading = ref(true)
  const searchQuery = ref('')
  const searchResults = ref({
    computers: [],
    employees: [],
    mfps: [],
    tvs: [],
    ups: [],
    workplaces: []
  })
  
  const totalResults = computed(() => {
    return searchResults.value.computers.length +
           searchResults.value.employees.length +
           searchResults.value.mfps.length +
           searchResults.value.tvs.length +
           searchResults.value.ups.length +
           searchResults.value.workplaces.length
  })
  
  // Форматирование даты
  const formatDate = (date) => {
    if (!date) return ''
    return new Date(date).toLocaleDateString('ru-RU')
  }
  
  // Получение списка мониторов
  const getMonitorsList = (computer) => {
    if (computer.monitors_detail && computer.monitors_detail.length) {
      return computer.monitors_detail.map(m => m.brand).join(', ')
    }
    return 'нет'
  }
  
  // Получение периферии
  const getPeripherals = (computer) => {
    const peripherals = []
    if (computer.has_keyboard) peripherals.push('⌨️ Клавиатура')
    if (computer.has_mouse) peripherals.push('🖱️ Мышь')
    return peripherals.length ? peripherals.join(', ') : 'нет'
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
  
  // Глобальный поиск
  const performSearch = async () => {
    loading.value = true
    const query = searchQuery.value.toLowerCase()
    
    try {
      const [computersRes, employeesRes, mfpsRes, tvsRes, upsRes, workplacesRes] = await Promise.all([
        axios.get(`${API}/computers/`),
        axios.get(`${API}/employees/`),
        axios.get(`${API}/mfps/`),
        axios.get(`${API}/tvs/`),
        axios.get(`${API}/ups/`),
        axios.get(`${API}/workplaces/`)
      ])
      
      // Фильтрация компьютеров
      searchResults.value.computers = computersRes.data.filter(comp => {
        return comp.asset_number?.toLowerCase().includes(query) ||
               comp.system_unit?.toLowerCase().includes(query) ||
               comp.department_name?.toLowerCase().includes(query) ||
               comp.assigned_to_name?.toLowerCase().includes(query) ||
               comp.monitors_detail?.some(m => m.brand.toLowerCase().includes(query))
      })
      
      // Фильтрация сотрудников
      searchResults.value.employees = employeesRes.data.filter(emp => {
        return emp.last_name?.toLowerCase().includes(query) ||
               emp.first_name?.toLowerCase().includes(query) ||
               emp.patronymic?.toLowerCase().includes(query) ||
               emp.department_name?.toLowerCase().includes(query)
      })
      
      // Фильтрация МФУ
      searchResults.value.mfps = mfpsRes.data.filter(mfp => {
        return mfp.asset_number?.toLowerCase().includes(query) ||
               mfp.model?.toLowerCase().includes(query) ||
               mfp.department_name?.toLowerCase().includes(query) ||
               mfp.ip_address?.toLowerCase().includes(query)
      })
      
      // Фильтрация телевизоров
      searchResults.value.tvs = tvsRes.data.filter(tv => {
        return tv.asset_number?.toLowerCase().includes(query) ||
               tv.brand?.toLowerCase().includes(query) ||
               tv.location?.toLowerCase().includes(query)
      })
      
      // Фильтрация ИБП
      searchResults.value.ups = upsRes.data.filter(ups => {
        return ups.asset_number?.toLowerCase().includes(query) ||
               ups.model?.toLowerCase().includes(query) ||
               ups.department_name?.toLowerCase().includes(query) ||
               ups.comment?.toLowerCase().includes(query) ||
               ups.battery_serial_number?.toLowerCase().includes(query)
      })
      
      // Фильтрация рабочих мест
      searchResults.value.workplaces = workplacesRes.data.filter(wp => {
        return wp.employee_name?.toLowerCase().includes(query) ||
               wp.location?.toLowerCase().includes(query) ||
               wp.city_name?.toLowerCase().includes(query) ||
               wp.mfp_detail?.model?.toLowerCase().includes(query) ||
               wp.ups_detail?.model?.toLowerCase().includes(query)
      })
      
    } catch (error) {
      console.error('Ошибка поиска:', error)
    } finally {
      loading.value = false
    }
  }
  
  // Навигация к деталям
  const goToComputer = (id) => {
    router.push({ path: '/computers', query: { highlight: id } })
  }
  
  const goToEmployee = (id) => {
    router.push({ path: '/employees', query: { highlight: id } })
  }
  
  const goToMFP = (id) => {
    router.push({ path: '/mfps', query: { highlight: id } })
  }
  
  const goToTV = (id) => {
    router.push({ path: '/tvs', query: { highlight: id } })
  }
  
  const goToUPS = (id) => {
    router.push({ path: '/ups', query: { highlight: id } })
  }
  
  const goToWorkplace = () => {
    router.push({ path: '/' })
  }
  
  const clearSearch = () => {
    searchQuery.value = ''
    router.push({ path: '/' })
  }
  
  onMounted(() => {
    searchQuery.value = route.query.q || ''
    if (searchQuery.value) {
      performSearch()
    } else {
      loading.value = false
    }
  })
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
  
  .results-section {
    margin-bottom: 2rem;
  }
  
  .section-title {
    font-size: 1.3rem;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #1abc9c;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .section-icon {
    font-size: 1.5rem;
  }
  
  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
    gap: 1rem;
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
  
  .card-body {
    padding: 12px 15px;
    font-size: 0.9rem;
    line-height: 1.6;
  }
  
  .card-body div {
    margin-bottom: 5px;
  }
  
  .label {
    font-weight: 500;
    color: #666;
    min-width: 85px;
    display: inline-block;
  }
  
  .card-footer {
    padding: 10px 15px;
    background: #f8f9fa;
    border-top: 1px solid #eee;
    text-align: right;
  }
  
  .view-btn {
    background: #3498db;
    color: white;
    border: none;
    padding: 6px 15px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: background 0.2s;
  }
  
  .view-btn:hover {
    background: #2980b9;
  }
  
  .badge-warning {
    background: #e67e22;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
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
  
  .battery-date {
    font-size: 0.75rem;
    color: #27ae60;
  }
  
  .ip-address {
    background: #f0f0f0;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 0.8rem;
  }
  
  .no-data {
    color: #999;
    font-style: italic;
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
    margin-bottom: 10px;
  }
  
  .no-results .hint {
    font-size: 0.9rem;
    color: #999;
  }
  
  @media (max-width: 768px) {
    .results-grid {
      grid-template-columns: 1fr;
    }
    
    .search-info {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .card-header {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .label {
      min-width: 70px;
    }
  }
  </style>