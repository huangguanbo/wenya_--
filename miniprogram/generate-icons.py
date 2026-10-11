#!/usr/bin/env python3
"""
生成微信小程序占位图标脚本
使用 PIL/Pillow 库生成简单的纯色图标

使用方法:
    python3 generate-icons.py
    
依赖:
    pip install Pillow
"""

import os
from PIL import Image, ImageDraw, ImageFont

# 图标配置
ICONS = [
    {'name': 'home', 'symbol': '🏠'},
    {'name': 'edit', 'symbol': '✏️'},
    {'name': 'trophy', 'symbol': '🏆'},
    {'name': 'community', 'symbol': ''},
    {'name': 'profile', 'symbol': '👤'},
]

COLORS = {
    'default': '#9ca3af',  # 灰色
    'active': '#16a34a',   # 绿色
}

# 输出目录
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'images')

# 确保输出目录存在
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)


def create_icon(symbol, color, size=81):
    """创建图标图片"""
    # 创建透明背景图片
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制圆角矩形背景
    padding = 16
    icon_size = size - padding * 2
    radius = 12
    
    # 转换颜色
    if color.startswith('#'):
        color = color[1:]
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    
    # 绘制圆角矩形
    draw.rounded_rectangle(
        [padding, padding, size - padding, size - padding],
        radius=radius,
        fill=(r, g, b, 255)
    )
    
    # 注意：PIL 默认不支持 emoji，这里用白色矩形代替
    # 实际使用时建议手动添加 emoji 或使用专业图标
    center = size // 2
    symbol_size = 30
    draw.rectangle(
        [center - symbol_size // 2, center - symbol_size // 2,
         center + symbol_size // 2, center + symbol_size // 2],
        fill=(255, 255, 255, 200)
    )
    
    return img


def create_avatar(size=100):
    """创建默认头像"""
    # 创建灰色背景
    img = Image.new('RGB', (size, size), '#e5e7eb')
    draw = ImageDraw.Draw(img)
    
    # 绘制简单的用户剪影
    center = size // 2
    
    # 头部（圆形）
    head_radius = 25
    draw.ellipse(
        [center - head_radius, 20 - head_radius,
         center + head_radius, 20 + head_radius],
        fill='#ffffff'
    )
    
    # 身体（半圆形）
    body_radius = 35
    draw.ellipse(
        [center - body_radius, 50,
         center + body_radius, 50 + body_radius * 2],
        fill='#ffffff'
    )
    
    return img


def main():
    print('🎨 开始生成小程序图标...\n')
    
    count = 0
    
    # 生成 TabBar 图标
    for icon in ICONS:
        # 默认状态（灰色）
        img = create_icon(icon['symbol'], COLORS['default'])
        filepath = os.path.join(OUTPUT_DIR, f"{icon['name']}.png")
        img.save(filepath, 'PNG')
        print(f'  ✓ {icon["name"]}.png')
        count += 1
        
        # 选中状态（绿色）
        img = create_icon(icon['symbol'], COLORS['active'])
        filepath = os.path.join(OUTPUT_DIR, f"{icon['name']}-active.png")
        img.save(filepath, 'PNG')
        print(f'  ✓ {icon["name"]}-active.png')
        count += 1
    
    # 生成默认头像
    avatar = create_avatar()
    filepath = os.path.join(OUTPUT_DIR, 'default-avatar.png')
    avatar.save(filepath, 'PNG')
    print(f'  ✓ default-avatar.png')
    count += 1
    
    print(f'\n✅ 图标生成完成！共生成了 {count} 个图标文件')
    print(f'\n📁 保存位置：{OUTPUT_DIR}')
    print('\n💡 提示：这些是简单的占位图标，建议后续替换为专业设计的图标')


if __name__ == '__main__':
    try:
        main()
    except ImportError:
        print('❌ 错误：未安装 Pillow 库')
        print('')
        print('请先安装:')
        print('  pip3 install Pillow')
        print('')
    except Exception as e:
        print(f'❌ 错误：{e}')
