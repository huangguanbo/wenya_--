# 图标文件说明

## 已生成的图标

✅ 以下图标已自动生成（占位图标）：

### TabBar 图标（81x81px）
| 文件 | 颜色 | 用途 |
|------|------|------|
| home.png | 灰色 #9ca3af | 首页 - 默认 |
| home-active.png | 绿色 #16a34a | 首页 - 选中 |
| edit.png | 灰色 #9ca3af | 写作 - 默认 |
| edit-active.png | 绿色 #16a34a | 写作 - 选中 |
| trophy.png | 灰色 #9ca3af | 排行榜 - 默认 |
| trophy-active.png | 绿色 #16a34a | 排行榜 - 选中 |
| community.png | 灰色 #9ca3af | 社区 - 默认 |
| community-active.png | 绿色 #16a34a | 社区 - 选中 |
| profile.png | 灰色 #9ca3af | 我的 - 默认 |
| profile-active.png | 绿色 #16a34a | 我的 - 选中 |

### 默认头像（100x100px）
- default-avatar.png - 用户默认头像

## 重新生成图标

如需重新生成图标，运行：

```bash
cd miniprogram
python3 generate-icons.py
```

依赖：
```bash
pip3 install Pillow
```

## 替换为专业图标

当前图标为简单的占位图标，建议后续替换为专业设计的图标：

### 图标要求
- 尺寸：81px × 81px
- 格式：PNG（支持透明通道）
- 风格：简洁清晰
- 颜色：
  - 默认状态：#9ca3af（灰色）
  - 选中状态：#16a34a（绿色）

### 推荐图标库
- [iconfont](https://www.iconfont.cn/) - 阿里巴巴矢量图标库
- [IconPark](https://iconpark.oceanengine.com/) - 字节跳动图标库
- [Remix Icon](https://remixicon.com/) - 开源中性风格图标
- [Feather Icons](https://feathericons.com/) - 简洁开源图标

### 设计建议
1. 保持图标风格一致
2. 使用简洁的几何图形
3. 避免过多细节（图标尺寸小）
4. 确保默认态和选中态有明显区分
5. 符合微信小程序设计规范

## 文件位置

```
miniprogram/images/
├── home.png
├── home-active.png
├── edit.png
├── edit-active.png
├── trophy.png
├── trophy-active.png
├── community.png
── community-active.png
├── profile.png
├── profile-active.png
└── default-avatar.png
```

## 验证图标

在微信开发者工具中：
1. 编译项目
2. 查看底部控制台是否有图标错误
3. 检查模拟器底部 TabBar 是否正常显示

---

**生成时间**: 2026 年 10 月 4 日
**图标数量**: 11 个
