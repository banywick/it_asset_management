<template>
    <div class="page">
      <h1>🖨️ Управление картриджами</h1>
  
      <!-- Форма добавления нового картриджа -->
      <div class="form-card">
        <h3>➕ Добавить картридж</h3>
        
        <div class="form-group">
          <label>Модель картриджа:</label>
          <div class="search-wrapper">
            <input 
              type="text" 
              v-model="newCartridgeModelSearch" 
              @input="searchNewCartridgeModels" 
              placeholder="Введите модель картриджа..."
              class="search-input"
            >
            <div v-if="newCartridgeModelSearchResults.length" class="search-results">
              <div 
                v-for="cart in newCartridgeModelSearchResults" 
                :key="cart.id" 
                @click="selectExistingCartridgeForNew(cart)"
                class="search-result-item"
              >
                {{ cart.model }}
                <span class="quantity-hint">(Минск: {{ cart.quantity_minsk }})</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="selectedExistingCartridge" class="selected-info">
          <div class="info-card">
            <strong>Выбран картридж:</strong> {{ selectedExistingCartridge.model }}
            <div class="current-stock">Текущий остаток в Минске: {{ selectedExistingCartridge.quantity_minsk }} шт.</div>
          </div>
          
          <div class="form-group">
            <label>Количество для добавления:</label>
            <input v-model="addQuantity" type="number" min="1" class="search-input">
          </div>
          
          <div class="form-group">
            <label>Совместимые МФУ:</label>
            <div class="search-wrapper">
              <input 
                type="text" 
                v-model="addMfpSearch" 
                @input="searchAddMFPs" 
                placeholder="Поиск МФУ для добавления..."
                class="search-input"
              >
              <div v-if="addMfpSearchResults.length" class="search-results">
                <div 
                  v-for="mfp in addMfpSearchResults" 
                  :key="mfp.id" 
                  @click="addCompatibleMFPToCartridge(mfp)"
                  class="search-result-item"
                >
                  ОС №{{ mfp.asset_number }} - {{ mfp.model }}
                </div>
              </div>
            </div>
            <div class="selected-items">
              <div v-for="mfp in selectedExistingCartridge.compatible_mfps_detail" :key="mfp.id" class="selected-tag">
                {{ mfp.model }}
                <button @click="removeCompatibleMFPFromCartridge(mfp.id)" class="remove-btn">×</button>
              </div>
            </div>
          </div>
          
          <button @click="addToExistingCartridge" class="submit-btn">📥 Добавить на склад</button>
        </div>
        
        <div v-if="showNewCartridgeForm && !selectedExistingCartridge" class="new-cartridge-form">
          <div class="form-group">
            <label>Модель картриджа:</label>
            <input v-model="newCartridge.model" placeholder="Например: 045H" class="search-input">
          </div>
          
          <div class="form-group">
            <label>Количество (Минск):</label>
            <input v-model="newCartridge.quantity" type="number" min="1" class="search-input">
          </div>
          
          <div class="form-group">
            <label>Совместимые МФУ:</label>
            <div class="search-wrapper">
              <input 
                type="text" 
                v-model="newCartridgeMfpSearch" 
                @input="searchNewCartridgeMFPs" 
                placeholder="Поиск МФУ..."
                class="search-input"
              >
              <div v-if="newCartridgeMfpSearchResults.length" class="search-results">
                <div 
                  v-for="mfp in newCartridgeMfpSearchResults" 
                  :key="mfp.id" 
                  @click="addNewCartridgeMFP(mfp)"
                  class="search-result-item"
                >
                  ОС №{{ mfp.asset_number }} - {{ mfp.model }}
                </div>
              </div>
            </div>
            <div class="selected-items">
              <div v-for="mfp in newCartridgeSelectedMFPs" :key="mfp.id" class="selected-tag">
                {{ mfp.model }}
                <button @click="removeNewCartridgeMFP(mfp.id)" class="remove-btn">×</button>
              </div>
            </div>
          </div>
          
          <button @click="createNewCartridge" class="submit-btn">💾 Создать картридж</button>
        </div>
        
        <button v-if="!selectedExistingCartridge && !showNewCartridgeForm" @click="showNewCartridgeForm = true" class="small-btn">➕ Добавить новый картридж</button>
      </div>
  
      <!-- Список картриджей -->
      <div class="list">
        <h3>📋 Список картриджей ({{ cartridges.length }} шт.)</h3>
        <div class="cards-grid">
          <div v-for="cart in paginatedCartridges" :key="cart.id" class="card">
            <div class="card-header">
              <strong>{{ cart.model }}</strong>
              <div class="card-actions">
                <button @click="openTransferModal(cart)" class="transfer-btn" title="Переместить в Мачулищи">🚚</button>
                <button @click="openEditModal(cart)" class="edit-btn" title="Редактировать">✏️</button>
                <button @click="deleteCartridge(cart.id)" class="delete-btn" title="Удалить">🗑️</button>
              </div>
            </div>
            <div class="card-body">
              <div class="quantity-badge-container">
                <span class="quantity-badge minsk">🏙️ Минск: {{ cart.quantity_minsk }}</span>
                <span class="quantity-badge total">📊 Всего: {{ cart.quantity_minsk + cart.quantity_machulishchi }}</span>
              </div>
              <div v-if="cart.quantity_machulishchi > 0" class="machulishchi-info">
                📍 Мачулищи: {{ cart.quantity_machulishchi }} шт.
              </div>
              <div class="compatible-mfps">
                <div class="label">🖨️ Совместимые МФУ:</div>
                <div class="mfps-list">
                  <span v-for="mfp in cart.compatible_mfps_detail" :key="mfp.id" class="mfp-tag">
                    {{ mfp.model }}
                  </span>
                  <span v-if="!cart.compatible_mfps_detail?.length" class="no-data">нет</span>
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
  
      <!-- Модальное окно перемещения в Мачулищи -->
      <div v-if="showTransferModal" class="modal">
        <div class="modal-content">
          <h3>🚚 Перемещение картриджей в Мачулищи</h3>
          <p class="modal-subtitle">Картридж: <strong>{{ transferCartridge?.model }}</strong></p>
          
          <div class="form-group">
            <label>Доступно в Минске:</label>
            <div class="available-stock">{{ transferCartridge?.quantity_minsk }} шт.</div>
          </div>
          
          <div class="form-group">
            <label>Количество для перемещения:</label>
            <input v-model="transferQuantity" type="number" min="1" :max="transferCartridge?.quantity_minsk" class="search-input">
          </div>
          
          <div class="form-group">
            <label>Комментарий:</label>
            <textarea v-model="transferComment" placeholder="Причина перемещения..." rows="2" class="textarea-field"></textarea>
          </div>
          
          <div class="modal-buttons">
            <button @click="processTransfer" class="save-btn">✅ Переместить</button>
            <button @click="showTransferModal = false" class="cancel-btn">Отмена</button>
          </div>
        </div>
      </div>
  
      <!-- Модальное окно редактирования -->
      <div v-if="showEditModal" class="modal">
        <div class="modal-content modal-large">
          <h3>✏️ Редактировать картридж</h3>
          
          <div class="form-group">
            <label>Модель:</label>
            <input v-model="editCartridge.model" class="search-input">
          </div>
          
          <div class="form-group">
            <label>Количество в Минске:</label>
            <input v-model="editCartridge.quantity_minsk" type="number" min="0" class="search-input">
          </div>
          
          <div class="form-group">
            <label>Количество в Мачулищах:</label>
            <input v-model="editCartridge.quantity_machulishchi" type="number" min="0" class="search-input">
          </div>
          
          <div class="form-group">
            <label>Совместимые МФУ:</label>
            <div class="search-wrapper">
              <input 
                type="text" 
                v-model="editMfpSearch" 
                @input="searchEditMFPs" 
                placeholder="Поиск МФУ..."
                class="search-input"
              >
              <div v-if="editMfpSearchResults.length" class="search-results">
                <div 
                  v-for="mfp in editMfpSearchResults" 
                  :key="mfp.id" 
                  @click="addEditCompatibleMFP(mfp)"
                  class="search-result-item"
                >
                  ОС №{{ mfp.asset_number }} - {{ mfp.model }}
                </div>
              </div>
            </div>
            <div class="selected-items">
              <div v-for="mfp in editSelectedMFPs" :key="mfp.id" class="selected-tag">
                {{ mfp.model }}
                <button @click="removeEditCompatibleMFP(mfp.id)" class="remove-btn">×</button>
              </div>
            </div>
          </div>
          
          <div class="modal-buttons">
            <button @click="updateCartridge" class="save-btn">💾 Сохранить</button>
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
  
  const API = 'http://localhost:8000/api'
  
  const cartridges = ref([])
  const allMFPs = ref([])
  
  // Пагинация
  const currentPage = ref(1)
  const itemsPerPage = 6
  
  // Модальные окна
  const showEditModal = ref(false)
  const showTransferModal = ref(false)
  const showNewCartridgeForm = ref(false)
  
  // Данные для нового картриджа
  const newCartridgeModelSearch = ref('')
  const newCartridgeModelSearchResults = ref([])
  const selectedExistingCartridge = ref(null)
  const addQuantity = ref(1)
  const addMfpSearch = ref('')
  const addMfpSearchResults = ref([])
  
  // Данные для создания нового картриджа
  const newCartridge = ref({
    model: '',
    quantity: 1
  })
  const newCartridgeMfpSearch = ref('')
  const newCartridgeMfpSearchResults = ref([])
  const newCartridgeSelectedMFPs = ref([])
  
  // Данные для перемещения
  const transferCartridge = ref(null)
  const transferQuantity = ref(1)
  const transferComment = ref('')
  
  // Данные для редактирования
  const editCartridge = ref({
    id: null,
    model: '',
    quantity_minsk: 0,
    quantity_machulishchi: 0
  })
  const editSelectedMFPs = ref([])
  const editMfpSearch = ref('')
  const editMfpSearchResults = ref([])
  
  const confirmModal = ref(null)
  
  // Пагинированные картриджи
  const paginatedCartridges = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage
    const end = start + itemsPerPage
    return cartridges.value.slice(start, end)
  })
  
  const totalPages = computed(() => {
    return Math.ceil(cartridges.value.length / itemsPerPage)
  })
  
  const prevPage = () => {
    if (currentPage.value > 1) currentPage.value--
  }
  const nextPage = () => {
    if (currentPage.value < totalPages.value) currentPage.value++
  }
  
  // Загрузка данных
  const fetchData = async () => {
    try {
      const [cartRes, mfpRes] = await Promise.all([
        axios.get(`${API}/cartridges/`),
        axios.get(`${API}/mfps/`)
      ])
      cartridges.value = cartRes.data
      allMFPs.value = mfpRes.data
    } catch (error) {
      console.error('Ошибка загрузки:', error)
      showError('Ошибка загрузки данных')
    }
  }
  
  // Поиск существующих картриджей для добавления
  const searchNewCartridgeModels = () => {
    if (!newCartridgeModelSearch.value) {
      newCartridgeModelSearchResults.value = []
      return
    }
    newCartridgeModelSearchResults.value = cartridges.value.filter(cart =>
      cart.model.toLowerCase().includes(newCartridgeModelSearch.value.toLowerCase())
    ).slice(0, 10)
  }
  
  const selectExistingCartridgeForNew = (cart) => {
    selectedExistingCartridge.value = { ...cart, compatible_mfps_detail: [...(cart.compatible_mfps_detail || [])] }
    newCartridgeModelSearch.value = ''
    newCartridgeModelSearchResults.value = []
    addQuantity.value = 1
    addMfpSearch.value = ''
    addMfpSearchResults.value = []
    showNewCartridgeForm.value = false
  }
  
  // Поиск МФУ для добавления совместимости
  const searchAddMFPs = () => {
    if (!addMfpSearch.value) {
      addMfpSearchResults.value = []
      return
    }
    addMfpSearchResults.value = allMFPs.value.filter(mfp =>
      (mfp.model.toLowerCase().includes(addMfpSearch.value.toLowerCase()) ||
       mfp.asset_number.toLowerCase().includes(addMfpSearch.value.toLowerCase())) &&
      !selectedExistingCartridge.value.compatible_mfps_detail?.find(m => m.id === mfp.id)
    ).slice(0, 10)
  }
  
  const addCompatibleMFPToCartridge = (mfp) => {
    if (!selectedExistingCartridge.value.compatible_mfps_detail.find(m => m.id === mfp.id)) {
      selectedExistingCartridge.value.compatible_mfps_detail.push(mfp)
    }
    addMfpSearch.value = ''
    addMfpSearchResults.value = []
  }
  
  const removeCompatibleMFPFromCartridge = (mfpId) => {
    selectedExistingCartridge.value.compatible_mfps_detail = selectedExistingCartridge.value.compatible_mfps_detail.filter(m => m.id !== mfpId)
  }
  
  // Добавление к существующему картриджу
  const addToExistingCartridge = async () => {
    if (!selectedExistingCartridge.value) return
    
    if (addQuantity.value <= 0) {
      showWarning('Укажите корректное количество')
      return
    }
    
    try {
      const updateData = {
        model: selectedExistingCartridge.value.model,
        quantity_minsk: selectedExistingCartridge.value.quantity_minsk + addQuantity.value,
        quantity_machulishchi: selectedExistingCartridge.value.quantity_machulishchi,
        compatible_mfps: selectedExistingCartridge.value.compatible_mfps_detail.map(m => m.id)
      }
      
      await axios.put(`${API}/cartridges/${selectedExistingCartridge.value.id}/`, updateData)
      
      await axios.post(`${API}/cartridge-movements/`, {
        cartridge: selectedExistingCartridge.value.id,
        movement_type: 'in',
        to_location: 'minsk',
        quantity: addQuantity.value,
        comment: 'Поступление на склад в Минск'
      })
      
      selectedExistingCartridge.value = null
      addQuantity.value = 1
      newCartridgeModelSearch.value = ''
      
      await fetchData()
      showSuccess('Картриджи добавлены на склад!')
    } catch (error) {
      console.error('Ошибка добавления:', error)
      showError('Ошибка добавления на склад')
    }
  }
  
  // Поиск МФУ для нового картриджа
  const searchNewCartridgeMFPs = () => {
    if (!newCartridgeMfpSearch.value) {
      newCartridgeMfpSearchResults.value = []
      return
    }
    newCartridgeMfpSearchResults.value = allMFPs.value.filter(mfp =>
      mfp.model.toLowerCase().includes(newCartridgeMfpSearch.value.toLowerCase()) ||
      mfp.asset_number.toLowerCase().includes(newCartridgeMfpSearch.value.toLowerCase())
    ).slice(0, 10)
  }
  
  const addNewCartridgeMFP = (mfp) => {
    if (!newCartridgeSelectedMFPs.value.find(m => m.id === mfp.id)) {
      newCartridgeSelectedMFPs.value.push(mfp)
    }
    newCartridgeMfpSearch.value = ''
    newCartridgeMfpSearchResults.value = []
  }
  
  const removeNewCartridgeMFP = (mfpId) => {
    newCartridgeSelectedMFPs.value = newCartridgeSelectedMFPs.value.filter(m => m.id !== mfpId)
  }
  
  // Создание нового картриджа
  const createNewCartridge = async () => {
    if (!newCartridge.value.model) {
      showWarning('Введите модель картриджа')
      return
    }
    
    if (newCartridge.value.quantity <= 0) {
      showWarning('Укажите корректное количество')
      return
    }
    
    try {
      const cartridgeData = {
        model: newCartridge.value.model,
        quantity_minsk: newCartridge.value.quantity,
        quantity_machulishchi: 0,
        compatible_mfps: newCartridgeSelectedMFPs.value.map(m => m.id)
      }
      
      const response = await axios.post(`${API}/cartridges/`, cartridgeData)
      
      await axios.post(`${API}/cartridge-movements/`, {
        cartridge: response.data.id,
        movement_type: 'in',
        to_location: 'minsk',
        quantity: newCartridge.value.quantity,
        comment: 'Новый картридж, поступление на склад'
      })
      
      newCartridge.value = { model: '', quantity: 1 }
      newCartridgeSelectedMFPs.value = []
      showNewCartridgeForm.value = false
      
      await fetchData()
      showSuccess('Картридж создан!')
    } catch (error) {
      console.error('Ошибка создания:', error)
      showError('Ошибка создания картриджа')
    }
  }
  
  // Открытие модального окна перемещения
  const openTransferModal = (cart) => {
    transferCartridge.value = cart
    transferQuantity.value = 1
    transferComment.value = ''
    showTransferModal.value = true
  }
  
  // Перемещение в Мачулищи
  const processTransfer = async () => {
    if (!transferCartridge.value) return
    
    if (transferQuantity.value <= 0) {
      showWarning('Укажите корректное количество')
      return
    }
    
    if (transferQuantity.value > transferCartridge.value.quantity_minsk) {
      showWarning(`Недостаточно картриджей в Минске. Доступно: ${transferCartridge.value.quantity_minsk}`)
      return
    }
    
    try {
      const updateData = {
        model: transferCartridge.value.model,
        quantity_minsk: transferCartridge.value.quantity_minsk - transferQuantity.value,
        quantity_machulishchi: transferCartridge.value.quantity_machulishchi + transferQuantity.value,
        compatible_mfps: transferCartridge.value.compatible_mfps_detail?.map(m => m.id) || []
      }
      
      await axios.put(`${API}/cartridges/${transferCartridge.value.id}/`, updateData)
      
      await axios.post(`${API}/cartridge-movements/`, {
        cartridge: transferCartridge.value.id,
        movement_type: 'transfer',
        from_location: 'minsk',
        to_location: 'machulishchi',
        quantity: transferQuantity.value,
        comment: transferComment.value || 'Перемещение в Мачулищи'
      })
      
      showTransferModal.value = false
      await fetchData()
      showSuccess('Картриджи перемещены в Мачулищи!')
    } catch (error) {
      console.error('Ошибка перемещения:', error)
      showError('Ошибка перемещения картриджей')
    }
  }
  
  // Редактирование
  const openEditModal = (cart) => {
    editCartridge.value = { ...cart }
    editSelectedMFPs.value = [...(cart.compatible_mfps_detail || [])]
    editMfpSearch.value = ''
    editMfpSearchResults.value = []
    showEditModal.value = true
  }
  
  const searchEditMFPs = () => {
    if (!editMfpSearch.value) {
      editMfpSearchResults.value = []
      return
    }
    editMfpSearchResults.value = allMFPs.value.filter(mfp =>
      mfp.model.toLowerCase().includes(editMfpSearch.value.toLowerCase()) &&
      !editSelectedMFPs.value.find(m => m.id === mfp.id)
    ).slice(0, 10)
  }
  
  const addEditCompatibleMFP = (mfp) => {
    if (!editSelectedMFPs.value.find(m => m.id === mfp.id)) {
      editSelectedMFPs.value.push(mfp)
    }
    editMfpSearch.value = ''
    editMfpSearchResults.value = []
  }
  
  const removeEditCompatibleMFP = (mfpId) => {
    editSelectedMFPs.value = editSelectedMFPs.value.filter(m => m.id !== mfpId)
  }
  
  const updateCartridge = async () => {
    try {
      const updateData = {
        model: editCartridge.value.model,
        quantity_minsk: editCartridge.value.quantity_minsk,
        quantity_machulishchi: editCartridge.value.quantity_machulishchi,
        compatible_mfps: editSelectedMFPs.value.map(m => m.id)
      }
      await axios.put(`${API}/cartridges/${editCartridge.value.id}/`, updateData)
      showEditModal.value = false
      await fetchData()
      showSuccess('Картридж обновлен!')
    } catch (error) {
      console.error('Ошибка обновления:', error)
      showError('Ошибка обновления картриджа')
    }
  }
  
  // Удаление картриджа
  const deleteCartridge = async (id) => {
    const confirmed = await confirmModal.value.open({
      title: 'Удаление картриджа',
      message: 'Вы уверены, что хотите удалить этот картридж?',
      confirmText: 'Да, удалить',
      type: 'danger'
    })
    
    if (confirmed) {
      try {
        await axios.delete(`${API}/cartridges/${id}/`)
        await fetchData()
        if (paginatedCartridges.value.length === 1 && currentPage.value > 1) {
          currentPage.value--
        }
        showSuccess('Картридж удален!')
      } catch (error) {
        console.error('Ошибка удаления:', error)
        showError('Ошибка удаления картриджа')
      }
    }
  }
  
  onMounted(fetchData)
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
  
  .selected-info {
    margin: 1rem 0;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 12px;
  }
  
  .info-card {
    background: #e8f5e9;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 1rem;
  }
  
  .current-stock {
    margin-top: 8px;
    font-size: 0.85rem;
    color: #666;
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
  
  .small-btn {
    background: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.95rem;
    margin-top: 10px;
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
    grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
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
  
  .card-header strong {
    font-size: 1rem;
    color: #2c3e50;
  }
  
  .card-actions {
    display: flex;
    gap: 8px;
  }
  
  .transfer-btn, .edit-btn, .delete-btn {
    background: none;
    border: none;
    font-size: 1.1rem;
    cursor: pointer;
    padding: 5px;
    border-radius: 6px;
    transition: all 0.2s;
  }
  
  .transfer-btn {
    color: #f39c12;
  }
  
  .transfer-btn:hover {
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
  
  .quantity-badge-container {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-bottom: 5px;
  }
  
  .quantity-badge {
    display: inline-block;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .quantity-badge.minsk {
    background: #d4edda;
    color: #155724;
  }
  
  .quantity-badge.total {
    background: #cce5ff;
    color: #004085;
  }
  
  .machulishchi-info {
    font-size: 0.7rem;
    color: #856404;
    background: #fff3cd;
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    margin-bottom: 8px;
  }
  
  .compatible-mfps {
    margin-top: 8px;
  }
  
  .compatible-mfps .label {
    font-weight: 600;
    color: #666;
    font-size: 0.75rem;
    margin-bottom: 6px;
  }
  
  .mfps-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  
  .mfp-tag {
    background: #e0e0e0;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
    color: #555;
  }
  
  .no-data {
    color: #999;
    font-style: italic;
    font-size: 0.7rem;
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
  
  .available-stock {
    padding: 10px;
    background: #e8f5e9;
    border-radius: 8px;
    font-weight: 500;
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
  
  .quantity-hint {
    font-size: 0.7rem;
    color: #999;
    margin-left: 8px;
  }
  
  .new-cartridge-form {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #eee;
  }
  
  @media (max-width: 768px) {
    .cards-grid {
      grid-template-columns: 1fr;
    }
    
    .modal-content {
      padding: 1.5rem;
      margin: 1rem;
    }
    
    .selected-tag {
      font-size: 0.8rem;
    }
  }
  </style>