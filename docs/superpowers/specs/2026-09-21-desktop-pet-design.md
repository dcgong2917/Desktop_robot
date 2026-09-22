# 桌宠机器人设计文档

**日期**：2026-09-21  
**平台**：Windows  
**技术栈**：Python + PyQt6  

---

## 1. 项目概述

一个常驻 Windows 桌面的宠物角色，点击角色弹出功能面板，提供剪贴板管理、热榜聚合对话、音乐推荐、换皮/角色生成四大功能。AI 功能统一通过智谱 AI API（GLM 系列）实现。

---

## 2. 架构

### 目录结构

```
robot/
├── main.py                # 入口，启动 Qt 应用
├── ui/
│   ├── pet_widget.py      # 桌宠角色窗口（透明、置顶、可拖拽）
│   └── panel_widget.py    # 点击弹出的功能面板（Tab 布局）
├── modules/
│   ├── clipboard.py       # 剪贴板管理模块
│   ├── news.py            # 热榜聚合模块
│   ├── music.py           # 音乐推荐模块
│   └── skin.py            # 换皮/角色生成模块
├── services/
│   └── zhipu_client.py   # Claude API 封装（流式回复、多轮对话）
├── assets/
│   └── default_pet.gif    # 默认角色动图
├── data/
│   ├── clips.json         # 剪贴板历史数据
│   └── config.json        # API Key、窗口位置、当前皮肤路径
└── requirements.txt
```

### 核心交互流

```
pet_widget（角色）
  └─ 鼠标点击
       └─ panel_widget 弹出（Tab 面板）
            ├─ 剪贴板 Tab → clipboard.py → 读写 clips.json
            ├─ 热榜 Tab   → news.py → 拉取热榜 → claude_client → 流式显示
            ├─ 音乐 Tab   → music.py → claude_client → 返回推荐列表
            └─ 换皮 Tab   → skin.py → 图像生成 API → 更新 pet_widget
```

所有网络/AI 调用通过 `QThread` 在后台执行，完成后通过 Qt 信号回调主线程更新 UI。

---

## 3. 功能模块设计

### 3.1 角色窗口（pet_widget）

- 透明无边框窗口，始终置顶（`Qt.WindowStaysOnTopHint`）
- 支持鼠标拖拽移动，位置持久化到 `config.json`
- 角色图用 `QMovie` 支持 GIF 动图
- 左键单击弹出/收起 `panel_widget`
- 右键弹出上下文菜单（退出、设置）

### 3.2 功能面板（panel_widget）

- 四个 Tab：剪贴板 / 热榜 / 音乐 / 换皮
- 面板跟随角色位置显示，不遮挡角色
- 关闭按钮或点击角色外区域收起

### 3.3 剪贴板管理

**数据格式**（`clips.json`）：
```json
[
  {"id": "uuid", "name": "SSH 登录服务器", "content": "ssh user@192.168.1.100", "created_at": "2026-09-21T10:00:00"}
]
```

**功能**：
- 列表展示已保存条目（名称 + 内容预览）
- 点击条目 → 自动复制到系统剪贴板 + 短暂高亮反馈
- 新增按钮 → 弹出输入对话框填写名称和内容
- 右键条目 → 编辑 / 删除
- 搜索框（MVP 后期添加）：实时过滤列表

### 3.4 热榜聚合 + AI 追问

**数据源**：
- 微博热搜（RSS 或爬取）
- 知乎热榜
- GitHub Trending

**流程**：
1. 用户进入热榜 Tab 或点击刷新 → 后台拉取各源条目
2. 整理成结构化文本交给 Claude，生成一段有趣的今日摘要
3. 摘要流式显示在对话框中
4. 用户在输入框提问 → 追加到 `conversation_history` → 调 Claude → 流式回复
5. 每次刷新重置对话历史

**多轮对话结构**：
```python
conversation_history = [
    {"role": "user", "content": "今日热榜内容: ..."},
    {"role": "assistant", "content": "今天有趣的事情..."},
    {"role": "user", "content": "用户追问..."},
]
```

### 3.5 音乐推荐

**流程**：
1. 用户输入心情/场景描述（可留空）
2. 调 Claude，返回 3-5 首推荐，格式：歌名 + 歌手 + 一句推荐理由
3. 每首旁边显示"去听"按钮，点击拼接网易云搜索 URL 用浏览器打开

**网易云搜索 URL 格式**：
```
https://music.163.com/#/search/m/?s={歌名+歌手}&type=1
```

### 3.6 换皮/角色生成

**流程**：
1. 用户上传参考图（PNG/JPG）或输入文字描述
2. 调用图像生成 API（Replicate / Stable Diffusion API）
3. 生成结果显示预览，用户确认后：
   - 保存到 `assets/` 目录
   - 更新 `config.json` 中的皮肤路径
   - `pet_widget` 实时切换角色图

**图像生成 API**：首选 Replicate（无需自建服务，按次计费），模型用 `stability-ai/sdxl` 或风格迁移模型。

---

## 4. 数据与配置

### config.json 结构
```json
{
  "zhipu_api_key": "",
  "replicate_api_key": "",
  "window_x": 100,
  "window_y": 100,
  "current_skin": "assets/default_pet.gif"
}
```

### 首次启动
检测到 `claude_api_key` 为空 → 弹出设置对话框 → 用户填入 API Key → 保存。

---

## 5. 错误处理

| 场景 | 处理方式 |
|------|----------|
| 网络请求失败 | UI 显示"请求失败，点击重试"，不崩溃 |
| 智谱 AI API 调用失败 | 显示错误提示，保留上次内容 |
| API Key 无效 | 弹出提示引导重新配置 |
| 图像生成失败 | 提示失败原因，保持当前皮肤不变 |
| 热榜源不可用 | 跳过该源，显示其他源内容 |

---

## 6. 依赖

```
PyQt6>=6.6.0
zhipuai>=2.1.0
httpx>=0.27.0
replicate>=0.25.0
pyperclip>=1.8.2
```

---

## 7. 打包

使用 PyInstaller 打包为单个 `.exe`：
```bash
pyinstaller --onefile --windowed --icon=assets/icon.ico main.py
```
