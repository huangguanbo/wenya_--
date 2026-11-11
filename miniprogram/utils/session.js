/**
 * 会话 Cookie 管理
 * 后端使用 Flask-Login 会话认证，登录态由 Set-Cookie 下发，后续请求需带上 Cookie
 */
const COOKIE_KEY = 'wenya_session_cookie'

// 目前后端只会下发这两个 Cookie，过滤掉无关项避免请求头膨胀
const COOKIE_NAMES = ['session', 'remember_token']

function getCookieMap() {
  const raw = wx.getStorageSync(COOKIE_KEY) || ''
  const map = {}

  String(raw).split(';').forEach((item) => {
    const pair = item.trim()
    const index = pair.indexOf('=')
    if (index <= 0) return
    map[pair.slice(0, index)] = pair.slice(index + 1)
  })

  return map
}

function saveCookieMap(map) {
  const value = Object.keys(map)
    .filter((name) => map[name])
    .map((name) => `${name}=${map[name]}`)
    .join('; ')

  if (value) {
    wx.setStorageSync(COOKIE_KEY, value)
  } else {
    wx.removeStorageSync(COOKIE_KEY)
  }
}

function saveFromHeader(header) {
  const raw = header && (header['Set-Cookie'] || header['set-cookie'])
  if (!raw) return

  const map = getCookieMap()
  const values = Array.isArray(raw) ? raw : [raw]

  values.forEach((value) => {
    // Expires 属性里也含逗号，只在逗号后紧跟 cookie 名时才拆分
    String(value).split(/,(?=\s*[A-Za-z0-9_-]+=)/).forEach((item) => {
      const pair = item.split(';')[0].trim()
      const index = pair.indexOf('=')
      if (index <= 0) return

      const name = pair.slice(0, index).trim()
      if (COOKIE_NAMES.indexOf(name) === -1) return

      const val = pair.slice(index + 1).trim()
      if (val) {
        map[name] = val
      } else {
        delete map[name]
      }
    })
  })

  saveCookieMap(map)
}

function getCookie() {
  return wx.getStorageSync(COOKIE_KEY) || ''
}

function hasSession() {
  return !!getCookieMap().session
}

function buildHeader(contentType) {
  const header = {}
  if (contentType) {
    header['Content-Type'] = contentType
  }

  const cookie = getCookie()
  if (cookie) {
    header['Cookie'] = cookie
  }

  return header
}

function clear() {
  wx.removeStorageSync(COOKIE_KEY)
}

module.exports = {
  getCookie,
  hasSession,
  saveFromHeader,
  buildHeader,
  clear
}
