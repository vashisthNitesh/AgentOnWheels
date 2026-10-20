import axios from 'axios'
import { reactive } from 'vue'

export const auth = reactive({ user: null, ready: false })
const api = axios.create({ baseURL: '/api/', timeout: 60000 })

api.interceptors.request.use(cfg => {
  const t = localStorage.getItem('aow_access')
  if (t) cfg.headers.Authorization = `Bearer ${t}`
  return cfg
})

let refreshing = null
api.interceptors.response.use(r => r, async err => {
  const orig = err.config
  if (err.response?.status === 401 && !orig._retry && localStorage.getItem('aow_refresh') && !orig.url.includes('auth/')) {
    orig._retry = true
    refreshing = refreshing || axios.post('/api/auth/refresh/', { refresh: localStorage.getItem('aow_refresh') })
      .then(r => { localStorage.setItem('aow_access', r.data.access); if (r.data.refresh) localStorage.setItem('aow_refresh', r.data.refresh) })
      .finally(() => { refreshing = null })
    try { await refreshing; return api(orig) } catch { logout() }
  } else if (err.response?.status === 401) { logout() }
  return Promise.reject(err)
})

export async function login(username, password) {
  const { data } = await axios.post('/api/auth/login/', { username, password })
  localStorage.setItem('aow_access', data.access)
  localStorage.setItem('aow_refresh', data.refresh)
  await loadMe()       // only report success once the profile is loaded (ATS stayed on /login)
}
export async function loadMe() {
  try { auth.user = (await api.get('auth/me/')).data } catch { auth.user = null }
  auth.ready = true
  return auth.user
}
export function logout() {
  localStorage.removeItem('aow_access'); localStorage.removeItem('aow_refresh'); auth.user = null
  if (!location.pathname.startsWith('/login')) location.href = '/login?next=' + encodeURIComponent(location.pathname)
}
export function errText(e) {
  const d = e?.response?.data
  if (!d) return e?.code === 'ECONNABORTED' ? 'The server took too long to respond. Please retry.' : 'Network error — check your connection and retry.'
  if (typeof d === 'string') return 'Server error'
  return d.detail || Object.entries(d).map(([k, v]) => `${k === 'non_field_errors' ? '' : k + ': '}${[].concat(v).join(' ')}`).join(' · ')
}
export default api
