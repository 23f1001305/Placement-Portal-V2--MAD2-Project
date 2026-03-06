import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import StudentRegister from '../views/StudentRegister.vue'
import CompanyRegister from '../views/CompanyRegister.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register/student',
    name: 'StudentRegister',
    component: StudentRegister
  },
  {
    path: '/register/company',
    name: 'CompanyRegister',
    component: CompanyRegister
  },
  {
    path: '/admin/dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'Admin' }
  },
  {
    path: '/company/dashboard',
    name: 'CompanyDashboard',
    component: CompanyDashboard,
    meta: { requiresAuth: true, role: 'Company' }
  },
  {
    path: '/student/dashboard',
    name: 'StudentDashboard',
    component: StudentDashboard,
    meta: { requiresAuth: true, role: 'Student' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  var token = localStorage.getItem('token')
  var role = localStorage.getItem('role')

  if (to.meta.requiresAuth) {
    if (!token) {
      next('/login')
    } else if (to.meta.role && to.meta.role !== role) {
      if (role === 'Admin') {
        next('/admin/dashboard')
      } else if (role === 'Company') {
        next('/company/dashboard')
      } else if (role === 'Student') {
        next('/student/dashboard')
      } else {
        next('/login')
      }
    } else {
      next()
    }
  } else {
    if (token && (to.path === '/login' || to.path === '/')) {
      if (role === 'Admin') {
        next('/admin/dashboard')
      } else if (role === 'Company') {
        next('/company/dashboard')
      } else if (role === 'Student') {
        next('/student/dashboard')
      } else {
        next()
      }
    } else {
      next()
    }
  }
})

export default router
