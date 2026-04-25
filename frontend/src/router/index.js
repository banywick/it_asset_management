import { createRouter, createWebHistory } from 'vue-router'
import Workplaces from '../views/Workplaces.vue'
import Computers from '../views/Computers.vue'
import MFPs from '../views/MFPs.vue'
import Cartridges from '../views/Cartridges.vue'
import TVs from '../views/TVs.vue'
import UPS from '../views/UPS.vue'
import Employees from '../views/Employees.vue'
import GlobalSearch from '../views/GlobalSearch.vue'

const routes = [
  { path: '/', component: Workplaces },
  { path: '/computers', component: Computers },
  { path: '/mfps', component: MFPs },
  { path: '/cartridges', component: Cartridges },
  { path: '/tvs', component: TVs },
  { path: '/ups', component: UPS },
  { path: '/employees', component: Employees },
  { path: '/search', component: GlobalSearch, name: 'GlobalSearch' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router