<template>
    <div class="auth-page">
      <canvas ref="canvasRef" class="particle-canvas"></canvas>
      
      <div class="auth-container">
        <div class="auth-card" :class="{ 'flipped': isRegisterMode }">
          <!-- Login Side -->
          <div class="auth-side login-side">
            <div class="auth-header">
              <div class="logo">
                <i class="fas fa-chalkboard-user"></i>
                <span>IT Asset Tracker</span>
              </div>
              <h2>Добро пожаловать!</h2>
              <p>Войдите в систему для продолжения работы</p>
            </div>
            
            <form @submit.prevent="handleLogin" class="auth-form">
              <div class="input-group">
                <i class="fas fa-user"></i>
                <input 
                  type="text" 
                  v-model="loginForm.username" 
                  placeholder="Логин"
                  required
                >
              </div>
              <div class="input-group">
                <i class="fas fa-lock"></i>
                <input 
                  :type="showPassword ? 'text' : 'password'" 
                  v-model="loginForm.password" 
                  placeholder="Пароль"
                  required
                >
                <i 
                  class="fas" 
                  :class="showPassword ? 'fa-eye-slash' : 'fa-eye'"
                  @click="showPassword = !showPassword"
                ></i>
              </div>
              
              <button type="submit" class="auth-btn" :disabled="loading">
                <i class="fas fa-sign-in-alt"></i>
                {{ loading ? 'Вход...' : 'Войти' }}
              </button>
            </form>
            
            <div class="auth-footer">
              <p>Нет аккаунта? 
                <a href="#" @click.prevent="toggleMode">Зарегистрироваться</a>
              </p>
            </div>
          </div>
          
          <!-- Register Side -->
          <div class="auth-side register-side">
            <div class="auth-header">
              <div class="logo">
                <i class="fas fa-chalkboard-user"></i>
                <span>IT Asset Tracker</span>
              </div>
              <h2>Создать аккаунт</h2>
              <p>Зарегистрируйтесь для доступа к системе</p>
            </div>
            
            <form @submit.prevent="handleRegister" class="auth-form">
              <div class="input-group">
                <i class="fas fa-user"></i>
                <input 
                  type="text" 
                  v-model="registerForm.username" 
                  placeholder="Логин"
                  required
                >
              </div>
              <div class="input-group">
                <i class="fas fa-envelope"></i>
                <input 
                  type="email" 
                  v-model="registerForm.email" 
                  placeholder="Email"
                  required
                >
              </div>
              <div class="input-row">
                <div class="input-group half">
                  <i class="fas fa-user-tie"></i>
                  <input 
                    type="text" 
                    v-model="registerForm.first_name" 
                    placeholder="Имя"
                  >
                </div>
                <div class="input-group half">
                  <i class="fas fa-user-tag"></i>
                  <input 
                    type="text" 
                    v-model="registerForm.last_name" 
                    placeholder="Фамилия"
                  >
                </div>
              </div>
              <div class="input-group">
                <i class="fas fa-lock"></i>
                <input 
                  :type="showRegPassword ? 'text' : 'password'" 
                  v-model="registerForm.password" 
                  placeholder="Пароль"
                  required
                >
                <i 
                  class="fas" 
                  :class="showRegPassword ? 'fa-eye-slash' : 'fa-eye'"
                  @click="showRegPassword = !showRegPassword"
                ></i>
              </div>
              <div class="input-group">
                <i class="fas fa-lock"></i>
                <input 
                  :type="showRegPassword2 ? 'text' : 'password'" 
                  v-model="registerForm.password2" 
                  placeholder="Подтверждение пароля"
                  required
                >
                <i 
                  class="fas" 
                  :class="showRegPassword2 ? 'fa-eye-slash' : 'fa-eye'"
                  @click="showRegPassword2 = !showRegPassword2"
                ></i>
              </div>
              
              <button type="submit" class="auth-btn" :disabled="loading">
                <i class="fas fa-user-plus"></i>
                {{ loading ? 'Регистрация...' : 'Зарегистрироваться' }}
              </button>
            </form>
            
            <div class="auth-footer">
              <p>Уже есть аккаунт? 
                <a href="#" @click.prevent="toggleMode">Войти</a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue'
  import { useRouter } from 'vue-router'
  import axios from 'axios'
  import { showSuccess, showError, showWarning, showInfo } from '../utils/toast'
  
  const router = useRouter()
  const API = 'http://localhost:8000/api'
  
  const isRegisterMode = ref(false)
  const loading = ref(false)
  const showPassword = ref(false)
  const showRegPassword = ref(false)
  const showRegPassword2 = ref(false)
  
  const loginForm = ref({
    username: '',
    password: ''
  })
  
  const registerForm = ref({
    username: '',
    email: '',
    first_name: '',
    last_name: '',
    password: '',
    password2: ''
  })
  
  const canvasRef = ref(null)
  let mouseX = 0
  let mouseY = 0
  let particles = []
  let animationId = null
  let time = 0
  
  // Параметры частиц
  const PARTICLE_COUNT = 120
  const CONNECTION_DISTANCE = 150
  const MOUSE_RADIUS = 120
  
  class Particle {
    constructor(canvas) {
      this.canvas = canvas
      this.reset()
    }
    
    reset() {
      this.x = Math.random() * this.canvas.width
      this.y = Math.random() * this.canvas.height
      this.vx = (Math.random() - 0.5) * 0.8
      this.vy = (Math.random() - 0.5) * 0.8
      this.size = Math.random() * 2.5 + 1
      this.originalSize = this.size
      this.waveSpeed = 0.02 + Math.random() * 0.03
      this.wavePhase = Math.random() * Math.PI * 2
    }
    
    update(mouseX, mouseY) {
      this.x += this.vx
      this.y += this.vy
      
      if (this.x < 0) {
        this.x = 0
        this.vx = -this.vx
      }
      if (this.x > this.canvas.width) {
        this.x = this.canvas.width
        this.vx = -this.vx
      }
      if (this.y < 0) {
        this.y = 0
        this.vy = -this.vy
      }
      if (this.y > this.canvas.height) {
        this.y = this.canvas.height
        this.vy = -this.vy
      }
      
      this.size = this.originalSize + Math.sin(time * this.waveSpeed + this.wavePhase) * 0.3
      
      if (mouseX !== 0 || mouseY !== 0) {
        let dx = mouseX - this.x
        let dy = mouseY - this.y
        let distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < MOUSE_RADIUS) {
          let force = (MOUSE_RADIUS - distance) / MOUSE_RADIUS
          let angle = Math.atan2(dy, dx)
          let moveX = Math.cos(angle) * force * 3
          let moveY = Math.sin(angle) * force * 3
          this.x -= moveX
          this.y -= moveY
          this.vx -= moveX * 0.1
          this.vy -= moveY * 0.1
          this.size = this.originalSize + force * 1.5
        }
      }
      
      this.vx *= 0.99
      this.vy *= 0.99
      
      if (Math.abs(this.vx) < 0.1 && Math.random() < 0.01) {
        this.vx += (Math.random() - 0.5) * 0.5
      }
      if (Math.abs(this.vy) < 0.1 && Math.random() < 0.01) {
        this.vy += (Math.random() - 0.5) * 0.5
      }
    }
    
    draw(ctx) {
      ctx.beginPath()
      ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2)
      
      const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size)
      gradient.addColorStop(0, 'rgba(255, 255, 255, 0.9)')
      gradient.addColorStop(1, 'rgba(26, 188, 156, 0.6)')
      ctx.fillStyle = gradient
      ctx.fill()
    }
  }
  
  const initParticles = () => {
    if (!canvasRef.value) return
    particles = []
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push(new Particle(canvasRef.value))
    }
  }
  
  const drawConnections = (ctx) => {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        let dx = particles[i].x - particles[j].x
        let dy = particles[i].y - particles[j].y
        let distance = Math.sqrt(dx * dx + dy * dy)
        
        if (distance < CONNECTION_DISTANCE) {
          let opacity = (1 - distance / CONNECTION_DISTANCE) * 0.4
          ctx.beginPath()
          ctx.moveTo(particles[i].x, particles[i].y)
          ctx.lineTo(particles[j].x, particles[j].y)
          
          const gradient = ctx.createLinearGradient(particles[i].x, particles[i].y, particles[j].x, particles[j].y)
          gradient.addColorStop(0, `rgba(26, 188, 156, ${opacity})`)
          gradient.addColorStop(1, `rgba(52, 152, 219, ${opacity})`)
          ctx.strokeStyle = gradient
          ctx.lineWidth = 0.8
          ctx.stroke()
        }
      }
    }
  }
  
  const drawMouseConnection = (ctx) => {
    if (mouseX === 0 && mouseY === 0) return
    
    for (let i = 0; i < particles.length; i++) {
      let dx = mouseX - particles[i].x
      let dy = mouseY - particles[i].y
      let distance = Math.sqrt(dx * dx + dy * dy)
      
      if (distance < MOUSE_RADIUS) {
        let opacity = (1 - distance / MOUSE_RADIUS) * 0.6
        ctx.beginPath()
        ctx.moveTo(mouseX, mouseY)
        ctx.lineTo(particles[i].x, particles[i].y)
        ctx.strokeStyle = `rgba(26, 188, 156, ${opacity})`
        ctx.lineWidth = 1.2
        ctx.stroke()
      }
    }
  }
  
  const animate = () => {
  if (!canvasRef.value) return
  
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  
  // Полностью очищаем canvas вместо наложения полупрозрачного слоя
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  
  for (let particle of particles) {
    particle.update(mouseX, mouseY)
    particle.draw(ctx)
  }
  
  drawConnections(ctx)
  drawMouseConnection(ctx)
  
  time += 0.016
  animationId = requestAnimationFrame(animate)
}
  
  const resizeCanvas = () => {
    if (!canvasRef.value) return
    canvasRef.value.width = window.innerWidth
    canvasRef.value.height = window.innerHeight
    initParticles()
  }
  
  const handleMouseMove = (e) => {
    mouseX = e.clientX
    mouseY = e.clientY
  }
  
  const handleMouseLeave = () => {
    mouseX = 0
    mouseY = 0
  }
  
  const toggleMode = () => {
    isRegisterMode.value = !isRegisterMode.value
    loginForm.value = { username: '', password: '' }
    registerForm.value = {
      username: '',
      email: '',
      first_name: '',
      last_name: '',
      password: '',
      password2: ''
    }
  }
  
  const handleLogin = async () => {
  loading.value = true
  try {
    const response = await axios.post(`${API}/auth/login/`, loginForm.value)
    if (response.data.success) {
      showSuccess(response.data.message)
      // Сохраняем данные пользователя
      localStorage.setItem('user', JSON.stringify(response.data.user))
      // Принудительно обновляем страницу для синхронизации
      window.location.href = '/'
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || 'Ошибка входа'
    if (errorMsg.includes('подтверждения')) {
      showWarning(errorMsg)
    } else {
      showError(errorMsg)
    }
  } finally {
    loading.value = false
  }
}
  
  const handleRegister = async () => {
    if (registerForm.value.password !== registerForm.value.password2) {
      showWarning('Пароли не совпадают')
      return
    }
    
    loading.value = true
    try {
      const response = await axios.post(`${API}/auth/register/`, registerForm.value)
      if (response.data.success) {
        showSuccess(response.data.message)
        // Очищаем форму и переключаемся на вход
        registerForm.value = {
          username: '',
          email: '',
          first_name: '',
          last_name: '',
          password: '',
          password2: ''
        }
        isRegisterMode.value = false
      }
    } catch (error) {
      const errors = error.response?.data
      if (errors) {
        if (errors.username) showError(`Ошибка: ${errors.username.join(', ')}`)
        else if (errors.email) showError(`Ошибка: ${errors.email.join(', ')}`)
        else if (errors.password) showError(`Ошибка: ${errors.password.join(', ')}`)
        else showError('Ошибка регистрации')
      } else {
        showError('Ошибка регистрации')
      }
    } finally {
      loading.value = false
    }
  }
  
  onMounted(() => {
    resizeCanvas()
    window.addEventListener('resize', resizeCanvas)
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseleave', handleMouseLeave)
    animate()
  })
  
  onUnmounted(() => {
    window.removeEventListener('resize', resizeCanvas)
    window.removeEventListener('mousemove', handleMouseMove)
    window.removeEventListener('mouseleave', handleMouseLeave)
    if (animationId) {
      cancelAnimationFrame(animationId)
    }
  })
  </script>
  
  <style scoped>
  .auth-page {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: hidden;
  }
  
  .particle-canvas {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 1;
  }
  
  .auth-container {
    position: relative;
    z-index: 2;
    width: 100%;
    max-width: 450px;
    margin: 20px;
  }
  
  .auth-card {
    position: relative;
    width: 100%;
    min-height: 550px;
    transition: transform 0.6s;
    transform-style: preserve-3d;
  }
  
  .auth-card.flipped {
    transform: rotateY(180deg);
  }
  
  .auth-side {
    position: absolute;
    width: 100%;
    height: 120%;
    backface-visibility: hidden;
    background: rgba(255, 255, 255, 0.95);
    border-radius: 20px;
    padding: 40px 30px;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
  }
  
  .login-side {
    transform: rotateY(0deg);
  }
  
  .register-side {
    transform: rotateY(180deg);
  }
  
  .auth-header {
    text-align: center;
    margin-bottom: 30px;
  }
  
  .logo {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    font-size: 1.5rem;
    font-weight: bold;
    color: #1abc9c;
    margin-bottom: 20px;
  }
  
  .logo i {
    font-size: 2rem;
  }
  
  .auth-header h2 {
    color: #2c3e50;
    margin-bottom: 8px;
  }
  
  .auth-header p {
    color: #7f8c8d;
    font-size: 0.9rem;
  }
  
  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }
  
  .input-group {
    position: relative;
    display: flex;
    align-items: center;
  }
  
  .input-group i:first-child {
    position: absolute;
    left: 15px;
    color: #1abc9c;
    font-size: 1rem;
  }
  
  .input-group input {
    width: 100%;
    padding: 12px 15px 12px 45px;
    border: 1px solid #ddd;
    border-radius: 10px;
    font-size: 1rem;
    transition: all 0.3s;
  }
  
  .input-group input:focus {
    outline: none;
    border-color: #1abc9c;
    box-shadow: 0 0 0 3px rgba(26, 188, 156, 0.1);
  }
  
  .input-group i:last-child {
    position: absolute;
    right: 15px;
    cursor: pointer;
    color: #999;
  }
  
  .input-row {
    display: flex;
    gap: 15px;
  }
  
  .input-group.half {
    flex: 1;
  }
  
  .auth-btn {
    background: linear-gradient(135deg, #1abc9c, #16a085);
    color: white;
    border: none;
    padding: 14px;
    border-radius: 10px;
    font-size: 1rem;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
  }
  
  .auth-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(26, 188, 156, 0.4);
  }
  
  .auth-btn:disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  .auth-footer {
    text-align: center;
    margin-top: 25px;
    padding-top: 20px;
    border-top: 1px solid #eee;
  }
  
  .auth-footer a {
    color: #1abc9c;
    text-decoration: none;
    font-weight: 500;
  }
  
  .auth-footer a:hover {
    text-decoration: underline;
  }
  
  @media (max-width: 768px) {
    .auth-side {
      padding: 30px 20px;
    }
    
    .input-row {
      flex-direction: column;
      gap: 15px;
    }
  }
  </style>