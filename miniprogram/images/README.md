# 文芽小程序图标说明

## 图标文件

由于无法直接生成图片文件，请按照以下说明准备图标：

### TabBar 图标（需要 2 套：默认状态和选中状态）

所有图标尺寸为 81px × 81px，PNG 格式，透明背景。

#### 1. 首页图标
- **home.png** (默认): 灰色房子轮廓图标 (#9ca3af)
- **home-active.png** (选中): 绿色实心房子图标 (#16a34a)

#### 2. 写作图标
- **edit.png** (默认): 灰色铅笔/编辑图标 (#9ca3af)
- **edit-active.png** (选中): 绿色铅笔/编辑图标 (#16a34a)

#### 3. 排行榜图标
- **trophy.png** (默认): 灰色奖杯图标 (#9ca3af)
- **trophy-active.png** (选中): 绿色奖杯图标 (#16a34a)

#### 4. 社区图标
- **community.png** (默认): 灰色人群/社区图标 (#9ca3af)
- **community-active.png** (选中): 绿色人群/社区图标 (#16a34a)

#### 5. 我的图标
- **profile.png** (默认): 灰色用户头像图标 (#9ca3af)
- **profile-active.png** (选中): 绿色用户头像图标 (#16a34a)

### 默认头像
- **default-avatar.png**: 100px × 100px，可以是默认的用户头像图片

## 图标获取方式

### 方式 1：使用图标库
推荐访问以下网站下载免费图标：
- [iconfont](https://www.iconfont.cn/) - 阿里巴巴矢量图标库
- [IconPark](https://iconpark.oceanengine.com/) - 字节跳动图标库
- [Remix Icon](https://remixicon.com/) - 开源中性风格图标

### 方式 2：使用 AI 生成
可以使用 AI 工具描述生成图标：
```
请生成一个简约风格的房子图标，线条简洁，用于小程序 TabBar，尺寸 81x81px
```

### 方式 3：临时占位
开发期间可以创建纯色占位图标：
```bash
# 使用在线工具或 PS 创建纯色方块作为临时占位
```

## 图标放置位置

将所有图标文件放置于：
```
miniprogram/images/
├── home.png
├── home-active.png
├── edit.png
├── edit-active.png
├── trophy.png
├── trophy-active.png
├── community.png
├── community-active.png
├── profile.png
├── profile-active.png
└── default-avatar.png
```

## 颜色规范

- **主色（选中态）**: #16a34a (绿色)
- **次色（默认态）**: #9ca3af (灰色)
- **背景**: 透明

## 注意事项

1. 图标必须为 PNG 格式，支持透明通道
2. 图标尺寸必须为 81px × 81px
3. 图标内容应简洁清晰，避免过于复杂
4. 选中态和默认态图标风格应保持一致
5. 图标文件不要过大，建议每个不超过 20KB
