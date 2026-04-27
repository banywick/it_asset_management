import { createRouter, createWebHistory } from 'vue-router'
import Workplaces from '../views/Workplaces.vue'
import Computers from '../views/Computers.vue'
import MFPs from '../views/MFPs.vue'
import Cartridges from '../views/Cartridges.vue'
import TVs from '../views/TVs.vue'
import UPS from '../views/UPS.vue'
import Employees from '../views/Employees.vue'
import GlobalSearch from '../views/GlobalSearch.vue'
import Login from '../views/Login.vue'

// Проверка аутентификации
const isAuthenticated = () => {
  return localStorage.getItem('user') !== null
}

const routes = [
  { path: '/login', component: Login, name: 'Login' },
  { 
    path: '/', 
    component: Workplaces,
    meta: { requiresAuth: true }
  },
  { 
    path: '/computers', 
    component: Computers,
    meta: { requiresAuth: true }
  },
  { 
    path: '/mfps', 
    component: MFPs,
    meta: { requiresAuth: true }
  },
  { 
    path: '/cartridges', 
    component: Cartridges,
    meta: { requiresAuth: true }
  },
  { 
    path: '/tvs', 
    component: TVs,
    meta: { requiresAuth: true }
  },
  { 
    path: '/ups', 
    component: UPS,
    meta: { requiresAuth: true }
  },
  { 
    path: '/employees', 
    component: Employees,
    meta: { requiresAuth: true }
  },
  { 
    path: '/search', 
    component: GlobalSearch, 
    name: 'GlobalSearch',
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Навигационный guard
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated()) {
    next('/login')
  } else if (to.path === '/login' && isAuthenticated()) {
    next('/')
  } else {
    next()
  }
})

export default router