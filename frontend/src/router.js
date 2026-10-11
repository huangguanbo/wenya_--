import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 页面组件
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Home from '@/views/Home.vue'
import Writing from '@/views/Writing.vue'
import WritingList from '@/views/WritingList.vue'
import Ranking from '@/views/Ranking.vue'
import Community from '@/views/Community.vue'
import WorkDetail from '@/views/WorkDetail.vue'
import Profile from '@/views/Profile.vue'
import Settings from '@/views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { requiresGuest: true }
  },
  {
    path: '/writing',
    name: 'Writing',
    component: Writing,
    meta: { requiresAuth: true }
  },
  {
    path: '/writing/:id',
    name: 'WritingDetail',
    component: Writing,
    meta: { requiresAuth: true }
  },
  {
    path: '/writings',
    name: 'WritingList',
    component: WritingList,
    meta: { requiresAuth: true }
  },
  {
    path: '/ranking',
    name: 'Ranking',
    component: Ranking,
    meta: { requiresAuth: true }
  },
  {
    path: '/community',
    name: 'Community',
    component: Community,
    meta: { requiresAuth: true }
  },
  {
    path: '/community/:id',
    name: 'WorkDetail',
    component: WorkDetail,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  if (to.meta.requiresAuth && !userStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.meta.requiresGuest && userStore.isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
