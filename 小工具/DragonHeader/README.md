# DragonHeader - 龙头buff监控器

> 用于 WoW Turtle Server 1.18 (乌龟服)，自动检测龙头buff并关停对应游戏进程。
> 支持多开：同时监控多个WoW实例，有buff的自动关闭，没buff的继续挂着等。

---

## 快速开始

### 第一步：截取模板图片

在游戏里等龙头buff出现，然后运行：

```bash
python buff_monitor.py --capture
```

1. 选择你要监听的WoW窗口编号
2. 在弹出的游戏截图上，**用鼠标框选龙头buff图标**（尽量精确，只框图标本身）
3. 按空格/回车确认 → 保存为模板

> 模板图片会保存在脚本同目录下的 `dragon_head_buff.png`。
> 如果框错了按 Esc 可以重新框选。
> **只需要做一次**，以后检测都用同一个模板。

### 第二步：启动监控

```bash
python buff_monitor.py
```

- 每秒检测一次所有WoW窗口
- 检测到龙头buff → 自动 Close 对应的游戏
- 没检测到 → 继续挂机等待

---

## 命令行选项

| 选项 | 说明 |
|------|------|
| `--capture` | 交互式模板截图工具（首次使用） |
| `--interval 0.5` | 检测间隔秒数，默认 1.0 |
| `--confidence 0.7` | 匹配置信度 0-1，默认 0.8。越低越容易匹配（但也更容易误报） |
| `--template path` | 指定模板图片路径 |
| `--debug` | 调试模式，显示每次检测的详细信息 |
| `--help` | 显示帮助 |

示例：

```bash
# 每0.5秒检测一次，更灵敏
python buff_monitor.py --interval 0.5

# 降低匹配阈值（如果模板和实际图标有差异）
python buff_monitor.py --confidence 0.7

# 看详细日志
python buff_monitor.py --debug
```

---

## 原理说明

| 步骤 | 实现 |
|------|------|
| 找窗口 | `win32gui.EnumWindows` 枚举所有 WoW 进程 |
| 截图 | **PrintWindow (PW_RENDERFULLCONTENT)** 进程级抓取 → 失败时自动回退前台截图 |
| 检测 | `OpenCV` 模板匹配 (`TM_CCOEFF_NORMED`) |
| 关进程 | `psutil` terminate → kill 递进处理 |

### 截图方式：进程级 PrintWindow（核心优势）

脚本不走屏幕合成，而是通过 Windows `PrintWindow` API 配合 `PW_RENDERFULLCONTENT` 标志，让 DWM 直接渲染目标窗口的完整内容到位图中。这是**进程级截图**：

```
                    ┌─────────────┐
PrintWindow(hwnd) ─→│    DWM      │─→ 目标窗口的完整渲染内容
                    │ 合成表面     │    （无视遮挡、无闪烁）
                    └─────────────┘
```

**对比：**

| 方式 | 有遮挡时 | 闪烁 | 走屏幕 |
|------|----------|------|--------|
| 屏幕截图 (mss) | ❌ 只能看到最上面窗口 | ❌ | ✅ |
| 前台提拉 + 截屏 | ✅ 逐个提拉到最前 | ❌ 窗口会跳 | ✅ |
| **PrintWindow (本脚本)** | ✅ **无视遮挡** | ✅ **无闪烁** | ❌ **不走屏幕** |

> PrintWindow 对窗口模式下的 DirectX 游戏有效。如果无效（例如全屏独占模式），脚本自动回退到前台提拉方案。

### 搜索区域

默认搜索窗口 **右上角 35% 宽 × 20% 高** 的区域，因为 Vanilla WoW 的 buff 栏就在右上角，最新 buff 出现在最右侧。

如果游戏 UI 缩放有调整，可以修改脚本开头的 `BUFF_REGION_RIGHT` 和 `BUFF_REGION_TOP` 参数。

---

## 注意事项

1. **模板截图必须精确**：只框图标本身，不要包含太多背景，否则容易误判
2. **窗口不能最小化**：最小化的窗口 PrintWindow 也无法捕获内容，会被跳过
3. **多开无需任何操作**：PrintWindow 是进程级的，无视遮挡，所有窗口同时检测，无闪烁
4. **安全**：只读 + 杀进程，不修改任何游戏文件，不注入内存，不hook API

---

## 文件结构

```
DragonHeader/
├── buff_monitor.py      # 主程序
├── dragon_head_buff.png # 龙头buff模板图片 (--capture生成)
└── README.md            # 本文件
```
