#!/usr/bin/env node
/**
 * 生成小程序占位图标脚本
 * 无需额外依赖，使用预定义的 PNG 数据
 * 
 * 使用方法: node generate-icons-simple.js
 */

const fs = require('fs')
const path = require('path')

// 简单的 PNG 文件生成（1x1 像素纯色，然后缩放）
// 这里使用一个简化方案：创建 SVG 然后说明手动转换

const icons = [
  { name: 'home', color: '9ca3af', activeColor: '16a34a' },
  { name: 'edit', color: '9ca3af', activeColor: '16a34a' },
  { name: 'trophy', color: '9ca3af', activeColor: '16a34a' },
  { name: 'community', color: '9ca3af', activeColor: '16a34a' },
  { name: 'profile', color: '9ca3af', activeColor: '16a34a' }
]

const outputPath = path.join(__dirname, 'images')

// 确保输出目录存在
if (!fs.existsSync(outputPath)) {
  fs.mkdirSync(outputPath, { recursive: true })
}

console.log('🎨 开始生成小程序占位图标...\n')

// 创建一个简单的 PNG 文件生成函数（1x1 像素）
function createSimplePNG(color) {
  // 这是一个最简单的 1x1 PNG 文件
  // 实际使用中建议使用图片编辑工具创建 81x81 的图标
  const hex = color.replace('#', '')
  const r = parseInt(hex.substr(0, 2), 16) || parseInt(hex.substr(0, 1), 16) * 17
  const g = parseInt(hex.substr(2, 2), 16) || parseInt(hex.substr(1, 1), 16) * 17
  const b = parseInt(hex.substr(4, 2), 16) || parseInt(hex.substr(2, 1), 16) * 17
  
  // PNG 文件头 + IHDR + IDAT + IEND
  // 这里简化处理，返回一个占位说明
  return null
}

// 生成说明文件
const readmeContent = `# 临时占位图标说明

由于无法直接生成 PNG 图标，请按照以下步骤创建临时图标：

## 方案 1：使用在线工具（推荐）

1. 访问 https://placeholder.com/ 或 https://via.placeholder.com/
2. 创建 81x81 的纯色图片
3. 下载并重命名为对应的图标名称

## 方案 2：使用 macOS 预览

1. 打开"预览"应用
2. 文件 → 新建空白文件
3. 设置尺寸为 81x81 像素
4. 填充颜色（灰色 #9ca3af 或绿色 #16a34a）
5. 导出为 PNG

## 方案 3：使用 Python

\`\`\`bash
# 安装 PIL
pip install Pillow

# 运行生成脚本
python generate-icons.py
\`\`\`

## 需要的图标文件

将以下文件放置在 images/ 目录：

### 首页
- home.png (灰色 #9ca3af)
- home-active.png (绿色 #16a34a)

### 写作
- edit.png (灰色 #9ca3af)
- edit-active.png (绿色 #16a34a)

### 排行榜
- trophy.png (灰色 #9ca3af)
- trophy-active.png (绿色 #16a34a)

### 社区
- community.png (灰色 #9ca3af)
- community-active.png (绿色 #16a34a)

### 我的
- profile.png (灰色 #9ca3af)
- profile-active.png (绿色 #16a34a)

### 默认头像
- default-avatar.png (100x100)

## 临时解决方案

如果只是想快速测试，可以临时移除 app.json 中的 tabBar 配置，
先运行小程序，然后再添加图标。
`

fs.writeFileSync(path.join(outputPath, 'CREATE_ICONS.md'), readmeContent)

console.log('❌ 无法直接生成 PNG 图标文件')
console.log('')
console.log('📄 已创建 images/CREATE_ICONS.md 说明文件')
console.log('')
console.log('📋 请选择以下方案之一：')
console.log('')
console.log('方案 1: 使用 Python 脚本生成（推荐）')
console.log('  cd miniprogram')
console.log('  python generate-icons.py')
console.log('')
console.log('方案 2: 手动创建图标')
console.log('  参考 images/CREATE_ICONS.md')
console.log('')
console.log('方案 3: 临时移除 tabBar 配置')
console.log('  编辑 app.json，注释掉 tabBar 部分')
console.log('')
