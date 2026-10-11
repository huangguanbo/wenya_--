/**
 * 生成小程序占位图标脚本
 * 使用 Node.js canvas 库生成简单的纯色图标
 * 
 * 使用方法:
 * 1. npm install canvas
 * 2. node generate-icons.js
 */

const fs = require('fs')
const path = require('path')

// 检查是否安装了 canvas
let canvas
try {
  canvas = require('canvas')
} catch (error) {
  console.log('❌ 未安装 canvas 库')
  console.log('')
  console.log('请先安装:')
  console.log('  cd miniprogram')
  console.log('  npm install canvas')
  console.log('')
  console.log('或者手动创建图标文件，参考 images/README.md')
  process.exit(1)
}

const { createCanvas } = canvas

// 图标配置
const icons = [
  { name: 'home', color: '#9ca3af', activeColor: '#16a34a' },
  { name: 'edit', color: '#9ca3af', activeColor: '#16a34a' },
  { name: 'trophy', color: '#9ca3af', activeColor: '#16a34a' },
  { name: 'community', color: '#9ca3af', activeColor: '#16a34a' },
  { name: 'profile', color: '#9ca3af', activeColor: '#16a34a' }
]

// 图标尺寸
const size = 81
const outputPath = path.join(__dirname, 'images')

// 确保输出目录存在
if (!fs.existsSync(outputPath)) {
  fs.mkdirSync(outputPath, { recursive: true })
}

/**
 * 绘制简单的图标（用圆角矩形表示）
 */
function drawIcon(color, symbol) {
  const c = createCanvas(size, size)
  const ctx = c.getContext('2d')
  
  // 透明背景
  
  // 绘制圆角矩形背景
  const padding = 16
  const iconSize = size - padding * 2
  const radius = 12
  
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.roundRect(padding, padding, iconSize, iconSize, radius)
  ctx.fill()
  
  // 绘制简单符号
  ctx.fillStyle = '#ffffff'
  ctx.font = 'bold 40px Arial'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillText(symbol, size / 2, size / 2 + 2)
  
  return c.toBuffer('image/png')
}

/**
 * 绘制 TabBar 图标
 */
function drawTabBarIcon(name, color, symbol) {
  console.log(`生成图标：${name} (${color})`)
  
  const buffer = drawIcon(color, symbol)
  const filePath = path.join(outputPath, `${name}.png`)
  
  fs.writeFileSync(filePath, buffer)
  console.log(`  ✓ ${filePath}`)
}

// 生成图标
console.log('🎨 开始生成小程序图标...\n')

const iconSymbols = {
  home: '🏠',
  edit: '✏️',
  trophy: '🏆',
  community: '👥',
  profile: ''
}

icons.forEach(icon => {
  // 默认状态
  drawTabBarIcon(icon.name, icon.color, iconSymbols[icon.name])
  
  // 选中状态
  drawTabBarIcon(`${icon.name}-active`, icon.activeColor, iconSymbols[icon.name])
})

// 生成默认头像
console.log('\n生成默认头像...')
const avatarCanvas = createCanvas(100, 100)
const avatarCtx = avatarCanvas.getContext('2d')

// 灰色背景
avatarCtx.fillStyle = '#e5e7eb'
avatarCtx.fillRect(0, 0, 100, 100)

// 白色用户剪影
avatarCtx.fillStyle = '#ffffff'
avatarCtx.beginPath()
avatarCtx.arc(50, 40, 25, 0, Math.PI * 2) // 头部
avatarCtx.fill()

avatarCtx.beginPath()
avatarCtx.arc(50, 70, 35, Math.PI, 0) // 身体
avatarCtx.fill()

const avatarBuffer = avatarCanvas.toBuffer('image/png')
fs.writeFileSync(path.join(outputPath, 'default-avatar.png'), avatarBuffer)
console.log('  ✓ default-avatar.png')

console.log('\n✅ 图标生成完成！')
console.log(`\n共生成了 ${icons.length * 2 + 1} 个图标文件`)
console.log('\n提示：这些是简单的占位图标，建议后续替换为专业设计的图标')
