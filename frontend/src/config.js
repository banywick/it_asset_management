// frontend/src/config.js
// Определяем API URL в зависимости от окружения
const isDev = import.meta.env.DEV;
const API_URL = isDev ? '/api' : '/api'; // Относительный путь работает везде

export { API_URL };