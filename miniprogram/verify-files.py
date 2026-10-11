#!/usr/bin/env python3
"""
文芽小程序文件验证脚本
检查所有必需文件是否存在且内容正确

使用方法:
    python3 verify-files.py
"""

import os
import sys

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 必需文件清单
REQUIRED_FILES = {
    '核心配置': [
        'app.js',
        'app.json',
        'app.wxss',
        'project.config.json',
        'sitemap.json',
    ],
    '工具模块': [
        'utils/api.js',
        'utils/auth.js',
        'utils/config.js',
        'utils/util.js',
        'utils/logger.js',
    ],
    '页面文件': [
        'pages/index/index.wxml',
        'pages/index/index.js',
        'pages/index/index.wxss',
        'pages/index/index.json',
        
        'pages/writing/writing.wxml',
        'pages/writing/writing.js',
        'pages/writing/writing.wxss',
        'pages/writing/writing.json',
        
        'pages/ranking/ranking.wxml',
        'pages/ranking/ranking.js',
        'pages/ranking/ranking.wxss',
        'pages/ranking/ranking.json',
        
        'pages/community/community.wxml',
        'pages/community/community.js',
        'pages/community/community.wxss',
        'pages/community/community.json',
        
        'pages/profile/profile.wxml',
        'pages/profile/profile.js',
        'pages/profile/profile.wxss',
        'pages/profile/profile.json',
        
        'pages/login/login.wxml',
        'pages/login/login.js',
        'pages/login/login.wxss',
        'pages/login/login.json',
        
        'pages/register/register.wxml',
        'pages/register/register.js',
        'pages/register/register.wxss',
        'pages/register/register.json',
        
        'pages/writing-detail/writing-detail.wxml',
        'pages/writing-detail/writing-detail.js',
        'pages/writing-detail/writing-detail.wxss',
        'pages/writing-detail/writing-detail.json',
        
        'pages/settings/settings.wxml',
        'pages/settings/settings.js',
        'pages/settings/settings.wxss',
        'pages/settings/settings.json',
        
        'pages/logs/logs.wxml',
        'pages/logs/logs.js',
        'pages/logs/logs.wxss',
        'pages/logs/logs.json',
    ],
    '图片资源': [
        'images/home.png',
        'images/home-active.png',
        'images/edit.png',
        'images/edit-active.png',
        'images/trophy.png',
        'images/trophy-active.png',
        'images/community.png',
        'images/community-active.png',
        'images/profile.png',
        'images/profile-active.png',
        'images/default-avatar.png',
    ],
}


def check_file(filepath):
    """检查文件是否存在且不为空"""
    full_path = os.path.join(BASE_DIR, filepath)
    
    if not os.path.exists(full_path):
        return False, '文件不存在'
    
    if os.path.getsize(full_path) == 0:
        return False, '文件为空'
    
    return True, 'OK'


def main():
    print('=' * 60)
    print('文芽小程序文件验证')
    print('=' * 60)
    print()
    
    total_count = 0
    ok_count = 0
    failed_files = []
    
    for category, files in REQUIRED_FILES.items():
        print(f'📁 {category}')
        print('-' * 40)
        
        category_ok = 0
        category_total = len(files)
        
        for filepath in files:
            total_count += 1
            exists, message = check_file(filepath)
            
            if exists:
                ok_count += 1
                category_ok += 1
                status = '✅'
            else:
                status = '❌'
                failed_files.append((filepath, message))
            
            print(f'  {status} {filepath}')
        
        # 计算类别完成率
        rate = category_ok / category_total * 100 if category_total > 0 else 0
        print(f'\n  完成率：{category_ok}/{category_total} ({rate:.1f}%)\n')
    
    # 总体统计
    print('=' * 60)
    print(f'总计：{ok_count}/{total_count} 文件正常')
    
    overall_rate = ok_count / total_count * 100 if total_count > 0 else 0
    print(f'完成率：{overall_rate:.1f}%')
    print('=' * 60)
    
    # 显示失败的文件
    if failed_files:
        print('\n❌ 失败的文件:')
        for filepath, message in failed_files:
            print(f'  - {filepath}: {message}')
        
        return 1
    else:
        print('\n✅ 所有文件检查通过！')
        print('\n下一步：在微信开发者工具中打开 miniprogram 目录并编译')
        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f'❌ 错误：{e}')
        sys.exit(1)
