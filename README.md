# Wox Multiscreen Blank Script Plugin

通过 Multiscreen Blank 的公开命令行接口控制显示器遮罩。

这是一个**单文件 Wox Script Plugin**：不需要构建、`dist/`、`.wox` 包或 Python SDK Host。Wox 每次查询或执行操作时直接运行脚本。

## 使用方式

插件仅使用 `msb` 触发词。

直接输入 `msb` 时提供以下基础操作：

| Wox 操作 | 实际命令 |
| --- | --- |
| 遮罩全部显示器 | `MultiscreenBlank2.exe /blank all` |
| 遮罩鼠标所在显示器 | `MultiscreenBlank2.exe /blank current` |
| 取消全部显示器遮罩 | `MultiscreenBlank2.exe /reveal all` |

### 按显示器名称切换遮罩

在 `msb` 后直接输入 Multiscreen Blank 中配置的显示器名称：

```text
msb Side Screen
```

选中结果后会切换该显示器的遮罩状态，并执行：

```text
MultiscreenBlank2.exe /toggle name "Side Screen"
```

显示器名称含空格时不需要额外输入引号。建议先在 Multiscreen Blank 主界面为每台显示器设置稳定的名称；名称不区分大小写。

## 安装

### 直接安装

将脚本复制到 Wox 的用户脚本目录，然后重启 Wox：

```text
C:\Users\<用户名>\.wox\wox-user\plugins\scripts\Wox.Plugin.Script.MultiscreenBlank.py
```


### Wox Store 发布

这是脚本插件，Store 的 `DownloadUrl` 应直接指向默认分支中的 [`Wox.Plugin.Script.MultiscreenBlank.py`](https://raw.githubusercontent.com/Flartiny/Wox.Plugin.BlankScreen/master/Wox.Plugin.Script.MultiscreenBlank.py)，而不是 `.wox` 压缩包。Store 条目使用 `Runtime: "script"` 和 `IconEmoji: "⬛"`。

### 可执行文件位置

默认自动识别：

```text
C:\Program Files\Nookkin\MultiscreenBlank2\MultiscreenBlank2.exe
```

若应用安装在别处，请在 Wox 的该脚本插件设置中配置 **Multiscreen Blank 可执行文件**（`executable_path`）为 `MultiscreenBlank2.exe` 的完整路径。

## 调试

脚本会把每次查询和执行的命令记录到同目录的：

```text
Wox.Plugin.Script.MultiscreenBlank.log
```

该日志是运行时产物，已被 Git 忽略。

## 参考

- [Multiscreen Blank 命令行参数](https://multiscreenblank.nookkin.com/advanced.ndoc)
- [Wox Script Plugin 开发指南](https://github.com/Wox-launcher/Wox/blob/master/www/docs/zh/development/plugins/script-plugin.md)

## 许可证

[MIT License](LICENSE)
