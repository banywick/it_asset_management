<template>
    <div v-if="show" class="modal-overlay" @click.self="close">
      <div class="modal-container">
        <div class="modal-header">
          <div class="modal-icon" :class="type">
            <span v-if="type === 'danger'">⚠️</span>
            <span v-else-if="type === 'warning'">⚠️</span>
            <span v-else>❓</span>
          </div>
          <h3>{{ title }}</h3>
        </div>
        
        <div class="modal-body">
          <p>{{ message }}</p>
        </div>
        
        <div class="modal-footer">
          <button class="btn-cancel" @click="close">
            Отмена
          </button>
          <button class="btn-confirm" :class="type" @click="confirm">
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue'
  
  const show = ref(false)
  let resolvePromise = null
  
  const props = defineProps({
    title: {
      type: String,
      default: 'Подтверждение'
    },
    message: {
      type: String,
      default: 'Вы уверены?'
    },
    confirmText: {
      type: String,
      default: 'Да, удалить'
    },
    type: {
      type: String,
      default: 'danger' // danger, warning, info
    }
  })
  
  const open = () => {
    show.value = true
    return new Promise((resolve) => {
      resolvePromise = resolve
    })
  }
  
  const close = () => {
    show.value = false
    if (resolvePromise) resolvePromise(false)
  }
  
  const confirm = () => {
    show.value = false
    if (resolvePromise) resolvePromise(true)
  }
  
  defineExpose({ open })
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
    animation: fadeIn 0.2s ease;
  }
  
  .modal-container {
    background: white;
    border-radius: 16px;
    width: 90%;
    max-width: 400px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: slideIn 0.3s ease;
  }
  
  .modal-header {
    padding: 20px 20px 10px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    border-bottom: 1px solid #eee;
  }
  
  .modal-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
  }
  
  .modal-icon.danger {
    background: #fee;
  }
  
  .modal-icon.warning {
    background: #fff3e0;
  }
  
  .modal-icon.info {
    background: #e3f2fd;
  }
  
  .modal-header h3 {
    margin: 0;
    font-size: 1.2rem;
    color: #2c3e50;
  }
  
  .modal-body {
    padding: 20px;
  }
  
  .modal-body p {
    margin: 0;
    color: #555;
    line-height: 1.5;
  }
  
  .modal-footer {
    padding: 15px 20px 20px 20px;
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    border-top: 1px solid #eee;
  }
  
  .btn-cancel, .btn-confirm {
    padding: 8px 20px;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: all 0.2s;
  }
  
  .btn-cancel {
    background: #e0e0e0;
    color: #555;
  }
  
  .btn-cancel:hover {
    background: #d0d0d0;
  }
  
  .btn-confirm {
    background: #1abc9c;
    color: white;
  }
  
  .btn-confirm:hover {
    background: #16a085;
  }
  
  .btn-confirm.danger {
    background: #e74c3c;
  }
  
  .btn-confirm.danger:hover {
    background: #c0392b;
  }
  
  .btn-confirm.warning {
    background: #f39c12;
  }
  
  .btn-confirm.warning:hover {
    background: #e67e22;
  }
  
  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }
  
  @keyframes slideIn {
    from {
      transform: translateY(-50px);
      opacity: 0;
    }
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
  </style>