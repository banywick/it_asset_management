<template>
    <div v-if="visible" class="modal-overlay" @click.self="close">
      <div class="modal-container">
        <div class="modal-header">
          <h2><i class="fas fa-chart-bar"></i> Формирование отчета</h2>
          <button class="close-btn" @click="close">✖</button>
        </div>
        
        <div class="modal-body">
          <!-- Выбор периода -->
          <div class="form-section">
            <h3>📅 Выбор периода</h3>
            <div class="date-range">
              <div class="date-field">
                <label>Дата от:</label>
                <input type="date" v-model="dateFrom" class="date-input">
              </div>
              <div class="date-field">
                <label>Дата до:</label>
                <input type="date" v-model="dateTo" class="date-input">
              </div>
            </div>
            <div class="quick-dates">
              <button @click="setDateRange('today')" class="quick-btn">Сегодня</button>
              <button @click="setDateRange('week')" class="quick-btn">Неделя</button>
              <button @click="setDateRange('month')" class="quick-btn">Месяц</button>
              <button @click="setDateRange('quarter')" class="quick-btn">Квартал</button>
              <button @click="setDateRange('year')" class="quick-btn">Год</button>
              <button @click="clearDates" class="quick-btn">За все время</button>
            </div>
          </div>
          
          <!-- Выбор сущностей -->
          <div class="form-section">
            <h3>📋 Выберите данные для отчета</h3>
            <div class="entities-grid">
              <label class="entity-checkbox">
                <input type="checkbox" v-model="selectAll" @change="toggleAll">
                <span class="checkbox-label">
                  <i class="fas fa-check-double"></i> Выбрать все
                </span>
              </label>
              <label class="entity-checkbox">
                <input type="checkbox" v-model="entities.employees">
                <span class="checkbox-label">
                  <i class="fas fa-users"></i> Сотрудники
                </span>
              </label>
              <label class="entity-checkbox">
                <input type="checkbox" v-model="entities.workplaces">
                <span class="checkbox-label">
                  <i class="fas fa-building"></i> Рабочие места
                </span>
              </label>
              <label class="entity-checkbox">
                <input type="checkbox" v-model="entities.computers">
                <span class="checkbox-label">
                  <i class="fas fa-desktop"></i> Компьютеры
                </span>
              </label>
              <label class="entity-checkbox">
                <input type="checkbox" v-model="entities.mfps">
                <span class="checkbox-label">
                  <i class="fas fa-print"></i> МФУ
                </span>
              </label>
              <label class="entity-checkbox">
                <input type="checkbox" v-model="entities.ups">
                <span class="checkbox-label">
                  <i class="fas fa-battery-full"></i> ИБП
                </span>
              </label>
              <label class="entity-checkbox">
                <input type="checkbox" v-model="entities.cartridges">
                <span class="checkbox-label">
                  <i class="fas fa-boxes"></i> Картриджи
                </span>
              </label>
              <label class="entity-checkbox">
                <input type="checkbox" v-model="entities.tvs">
                <span class="checkbox-label">
                  <i class="fas fa-tv"></i> Телевизоры
                </span>
              </label>
            </div>
          </div>
          
          <!-- Пример отчета -->
          <div class="form-section preview-section">
            <h3>📊 Пример отчета</h3>
            <div class="preview-info">
              <p>Будет сгенерирован Excel файл с листами:</p>
              <ul>
                <li v-if="entities.employees || selectAll">📄 Сотрудники - ФИО, отдел, рабочее место, компьютер, ИБП, МФУ</li>
                <li v-if="entities.workplaces || selectAll">📄 Рабочие места - сотрудник, расположение, статус, оборудование</li>
                <li v-if="entities.computers || selectAll">📄 Компьютеры - ОС, тип, системный блок, мониторы, владелец</li>
                <li v-if="entities.mfps || selectAll">📄 МФУ - модель, IP, кабинет, серийный номер, статус</li>
                <li v-if="entities.ups || selectAll">📄 ИБП - модель, статус, аккумулятор, дата замены</li>
                <li v-if="entities.cartridges || selectAll">📄 Картриджи - модель, остатки на складах</li>
                <li v-if="entities.tvs || selectAll">📄 Телевизоры - марка, диагональ, расположение</li>
              </ul>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="generateReport" class="generate-btn" :disabled="loading">
            <i class="fas fa-file-excel"></i>
            {{ loading ? 'Формирование...' : 'Сформировать отчет' }}
          </button>
          <button @click="close" class="cancel-btn">Отмена</button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, watch } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from 'axios'
  import { showSuccess, showError, showWarning } from '../utils/toast'
  
  const API = '/api'
  const router = useRouter()
  
  const props = defineProps({
    visible: {
      type: Boolean,
      default: false
    }
  })
  
  const emit = defineEmits(['update:visible', 'report-generated'])
  
  const dateFrom = ref('')
  const dateTo = ref('')
  const selectAll = ref(true)
  const loading = ref(false)
  
  const entities = ref({
    employees: true,
    workplaces: true,
    computers: true,
    mfps: true,
    ups: true,
    cartridges: true,
    tvs: true
  })
  
  // Следим за изменением selectAll
  watch(selectAll, (newVal) => {
    entities.value = {
      employees: newVal,
      workplaces: newVal,
      computers: newVal,
      mfps: newVal,
      ups: newVal,
      cartridges: newVal,
      tvs: newVal
    }
  })
  
  // Установка диапазона дат
  const setDateRange = (range) => {
    const today = new Date()
    const to = new Date(today)
    
    let from = new Date(today)
    
    switch (range) {
      case 'today':
        from = new Date(today)
        break
      case 'week':
        from.setDate(today.getDate() - 7)
        break
      case 'month':
        from.setMonth(today.getMonth() - 1)
        break
      case 'quarter':
        from.setMonth(today.getMonth() - 3)
        break
      case 'year':
        from.setFullYear(today.getFullYear() - 1)
        break
    }
    
    dateFrom.value = from.toISOString().split('T')[0]
    dateTo.value = to.toISOString().split('T')[0]
  }
  
  const clearDates = () => {
    dateFrom.value = ''
    dateTo.value = ''
  }
  
  const toggleAll = () => {
    selectAll.value = !selectAll.value
  }
  
  const close = () => {
    emit('update:visible', false)
  }
  
  const generateReport = async () => {
    // Проверка авторизации перед отправкой запроса
    const user = localStorage.getItem('user')
    if (!user) {
      showWarning('Для формирования отчета необходимо авторизоваться')
      close()
      router.push('/login')
      return
    }
    
    loading.value = true
    
    const selectedEntities = []
    if (entities.value.employees) selectedEntities.push('employees')
    if (entities.value.workplaces) selectedEntities.push('workplaces')
    if (entities.value.computers) selectedEntities.push('computers')
    if (entities.value.mfps) selectedEntities.push('mfps')
    if (entities.value.ups) selectedEntities.push('ups')
    if (entities.value.cartridges) selectedEntities.push('cartridges')
    if (entities.value.tvs) selectedEntities.push('tvs')
    
    try {
      const response = await axios.post(`${API}/report/generate_report/`, {
        entities: selectedEntities,
        date_from: dateFrom.value || null,
        date_to: dateTo.value || null
      }, {
        responseType: 'blob'
      })
      
      // Создаем ссылку для скачивания
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      const contentDisposition = response.headers['content-disposition']
      let filename = 'report.xlsx'
      if (contentDisposition) {
        const match = contentDisposition.match(/filename="(.+)"/)
        if (match) filename = match[1]
      }
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      showSuccess('Отчет успешно сформирован!')
      close()
      emit('report-generated')
    } catch (error) {
      console.error('Ошибка формирования отчета:', error)
      // Если ошибка 401 (неавторизован)
      if (error.response?.status === 401) {
        showWarning('Сессия истекла. Пожалуйста, войдите заново.')
        localStorage.removeItem('user')
        router.push('/login')
      } else {
        showError('Ошибка формирования отчета')
      }
    } finally {
      loading.value = false
    }
  }
  </script>
  
  <style scoped>
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2000;
  }
  
  .modal-container {
    background: white;
    border-radius: 20px;
    width: 90%;
    max-width: 700px;
    max-height: 85vh;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
    animation: slideIn 0.3s ease;
  }
  
  @keyframes slideIn {
    from {
      opacity: 0;
      transform: translateY(-30px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 25px;
    background: linear-gradient(135deg, #1abc9c, #16a085);
    color: white;
  }
  
  .modal-header h2 {
    margin: 0;
    font-size: 1.3rem;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .close-btn {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    color: white;
    transition: transform 0.2s;
  }
  
  .close-btn:hover {
    transform: scale(1.1);
  }
  
  .modal-body {
    padding: 25px;
    max-height: calc(85vh - 140px);
    overflow-y: auto;
  }
  
  .form-section {
    margin-bottom: 25px;
    padding-bottom: 20px;
    border-bottom: 1px solid #eee;
  }
  
  .form-section:last-child {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
  
  .form-section h3 {
    color: #2c3e50;
    margin-bottom: 15px;
    font-size: 1rem;
  }
  
  .date-range {
    display: flex;
    gap: 20px;
    margin-bottom: 15px;
  }
  
  .date-field {
    flex: 1;
  }
  
  .date-field label {
    display: block;
    margin-bottom: 5px;
    color: #666;
    font-size: 0.85rem;
  }
  
  .date-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 0.9rem;
  }
  
  .date-input:focus {
    outline: none;
    border-color: #1abc9c;
  }
  
  .quick-dates {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }
  
  .quick-btn {
    padding: 5px 12px;
    background: #f0f0f0;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.2s;
  }
  
  .quick-btn:hover {
    background: #1abc9c;
    color: white;
  }
  
  .entities-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: 12px;
  }
  
  .entity-checkbox {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 8px 12px;
    background: #f8f9fa;
    border-radius: 10px;
    transition: all 0.2s;
  }
  
  .entity-checkbox:hover {
    background: #e8f5e9;
  }
  
  .entity-checkbox input {
    margin-right: 10px;
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
  
  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.9rem;
    color: #2c3e50;
  }
  
  .checkbox-label i {
    width: 20px;
    color: #1abc9c;
  }
  
  .preview-section {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 12px;
    margin-top: 10px;
  }
  
  .preview-info p {
    margin-bottom: 10px;
    color: #666;
    font-size: 0.85rem;
  }
  
  .preview-info ul {
    list-style: none;
    padding-left: 0;
  }
  
  .preview-info li {
    padding: 5px 0;
    font-size: 0.8rem;
    color: #555;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .preview-info li:before {
    content: "📄";
  }
  
  .modal-footer {
    display: flex;
    justify-content: flex-end;
    gap: 15px;
    padding: 20px 25px;
    background: #f8f9fa;
    border-top: 1px solid #eee;
  }
  
  .generate-btn {
    background: linear-gradient(135deg, #1abc9c, #16a085);
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
    transition: all 0.2s;
  }
  
  .generate-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(26, 188, 156, 0.4);
  }
  
  .generate-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  .cancel-btn {
    background: #e74c3c;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }
  
  .cancel-btn:hover {
    background: #c0392b;
  }
  
  @media (max-width: 768px) {
    .date-range {
      flex-direction: column;
      gap: 10px;
    }
    
    .entities-grid {
      grid-template-columns: 1fr;
    }
    
    .modal-footer {
      flex-direction: column;
    }
    
    .generate-btn, .cancel-btn {
      justify-content: center;
    }
  }
  </style>