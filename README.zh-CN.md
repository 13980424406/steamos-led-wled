# SteamOS LED → WLED

通过 UDP DRGB、USB 串口或两者同时使用，将 Steam Deck 的 LED 灯条同步到 [WLED](https://github.com/Aircoookie/WLED) 控制器。USB 串口模式会将兼容 WLED 的 Adalight 数据帧直接发送到已连接 ESP32-S3 上运行的 WLED。17 颗源 LED 会通过加权平均映射到配置的灯带长度（1–256 颗）；输出按单条线性灯带处理，不支持矩阵布局。

无需自定义 MCU 固件。ESP32-S3 运行 WLED，通过 USB 串口接收 LED 数据帧并驱动已配置的灯带。

**[English](README.md) | [Português (PT-BR)](README.pt-br.md)**

## 工作原理

1. 从内核模块读取 `/dev/valve-leds-shim` 中的 100 字节 LED 快照
2. 将 17 颗源 LED 映射到目标灯带长度
3. 在服务端渲染 Steam Deck 灯效（彩虹、呼吸、巡逻、工厂、演示）
4. 应用可选叠加效果（温度、通知、音频 VU）
5. 通过 **UDP DRGB** 和/或 USB 串口 **Adalight** 向 WLED 发送像素数据
6. 播放启动、关机、挂起和恢复动画

## 环境要求

- **Steam Deck**（SteamOS），或运行 Steam 游戏模式（Game Mode）的 Linux PC
- 使用 WLED 输出时，需要同一网络中的 **WLED 设备**
- 使用 USB 串口输出时，需要 **兼容 WLED 的控制器**；支持通过兼容固件暴露 USB 串口的 Waveshare ESP32-S3-Matrix
- **Python 3**（受支持的发行版缺少 Python 3 时，安装器会安装；本桥接服务仅使用标准库）

### 配置 WLED

使用 UDP 输出时，请先在网络中配置 WLED 控制器。仅使用 USB 串口输出时，不需要 Wi-Fi 或 WLED IP 地址。网络输出的快速配置步骤：

1. **向 ESP8266 或 ESP32 烧录 WLED**：
   - 从 [WLED releases](https://github.com/Aircoookie/WLED/releases) 下载最新版本
   - 推荐使用 [WLED 网页安装器](https://install.wled.me/)（Chrome/Edge）
2. **连接 Wi-Fi**：烧录后连接 `WLED-AP` 热点并配置 Wi-Fi 凭据
3. **配置灯带**：在 WLED 设置 → LED Preferences 中设置正确的 LED 数量和类型（WS2812B、SK6812 等）
4. **记下 IP 地址**：WLED 主页面会显示 IP；安装器也可以自动发现设备
5. **启用 UDP 同步**：在 WLED 设置 → Sync Interfaces 中确认 UDP 端口为 **21324**（默认值）

详细说明请参阅 [WLED 文档](https://kno.wled.ge/)。

## 安装

```bash
git clone https://github.com/rpf16rj/steamos-led-wled.git
cd steamos-led-wled
sudo ./install.sh
```

安装器会：

1. 询问使用 WLED、USB 还是两者同时输出
2. 选择 WLED 输出时，通过 mDNS/子网扫描自动发现设备
3. 选择 USB 输出时，询问 USB 串口设备
4. 询问逻辑 LED 数量和叠加效果选项
5. 安装所需系统软件包；缺少 Python 3 时也会安装
6. 编译并安装 `leds-valve-shim` 内核模块
7. 安装 bridge 服务并生成 `/etc/steamos-led-wled.conf`
8. 启用并启动 systemd 服务

### 在 ESP32-S3-Matrix 上运行 WLED

请烧录支持 ESP32-S3 并暴露 USB 串口接口的 WLED 固件。在 WLED 的 LED Preferences 中，设置板载 LED 数据引脚（Waveshare ESP32-S3-Matrix 为 GPIO 14）、LED 类型和数量，使其与 `num_leds` 一致。WLED 串口接口支持 Adalight；请在 Sync 设置中将串口波特率设为与 `usb_serial_baud` 一致（默认 `115200`）。仅使用 USB 输出时，不需要 Wi-Fi 或 WLED IP 地址。

主机上的设备通常为 `/dev/ttyACM0`。请确保服务用户有权限访问该设备（通常通过 `dialout` 或 `uucp` 组）。参阅 [WLED 串口文档](https://kno.wled.ge/interfaces/serial/)和 [Waveshare 板卡说明](https://www.waveshare.com/wiki/ESP32-S3-Matrix)。

## Decky Loader 插件

使用 **Toolkit SteamOS Control** Decky 插件，可在 Steam 游戏模式（Game Mode）中直接控制叠加效果：

- 仓库：[toolkit-steamos-control-decky](https://github.com/rpf16rj/toolkit-steamos-control-decky)
- 无需离开 Game Mode，即可切换温度、音频 VU 和通知叠加效果

## 配置

编辑 `/etc/steamos-led-wled.conf`：

```ini
[steamos-led-wled]
# wled（UDP）、usb（USB 串口）或 both（两者）
output_mode = wled

# WLED 设备 IP 地址
wled_host = 192.168.1.100

# WLED UDP 实时控制端口（默认：21324）
wled_port = 21324

# 输出的逻辑 LED 数量（1–256）
num_leds = 8

# WLED USB 串口设备及波特率
usb_serial_device = /dev/ttyACM0
usb_serial_baud = 115200

# 串口协议：adalight（默认）或 json（WLED JSON over Serial）
usb_serial_protocol = adalight

# valve-leds-shim 设备路径
device = /dev/valve-leds-shim

# 叠加效果（true/false）
temp_overlay = true
notify_overlay = true
audio_overlay = true
```

源数据包含 17 颗 LED。`num_leds` 可设为 1–256：输出数量少于 17 时，通过加权平均合并源 LED；多于 17 时，将源 LED 按比例分布到灯带，并在源 LED 边界进行加权平均。请将 WLED 中配置的灯带数量设为与 `num_leds` 一致。仅使用 USB 输出时无需设置 `wled_host`，并将 `output_mode` 设为 `usb`。将 `output_mode` 设为 `both` 可通过 UDP 和 USB 串口同时发送映射后的帧。

安装时可选择串口协议，也可手动设置 `usb_serial_protocol`：`adalight`（默认，发送 Adalight 二进制帧）或 `json`（通过 WLED JSON API over Serial 发送换行分隔的 JSON 命令）。该设置仅在 `output_mode` 为 `usb` 或 `both` 时生效。

修改配置后重启服务：

```bash
sudo systemctl restart steamos-led-wled
```

## 功能

### LED 灯效（服务端渲染）

所有 Steam Deck LED 灯效均由桥接服务渲染，并发送到配置的输出设备：

| 灯效 | 说明 |
| ---- | ---- |
| **手动** | 使用 Steam 游戏模式设置的静态颜色 |
| **彩虹** | 所有 LED 循环变换色相 |
| **呼吸** | 亮度脉动 |
| **巡逻** | 往返移动的光点 |
| **工厂** | 交替显示互补色 |
| **演示** | 循环播放所有灯效 |

### 叠加效果

| 叠加效果 | 说明 |
| -------- | ---- |
| **温度** | 根据 CPU/GPU 温度（> 65°C）将灯条显示为黄到红的渐变 |
| **通知** | 成就通知闪金色，消息通知闪蓝色 |
| **音频 VU** | 由系统音频（PipeWire/PulseAudio）驱动的 VU 表 |

优先级：通知 > 音频+温度 > Steam 游戏模式

### 动画

| 事件 | 动画 |
| ---- | ---- |
| **启动** | 从中心向两侧扫亮 Steam 蓝色，然后脉动 |
| **关机** | 从两端向中心渐暗 |
| **挂起** | 缓慢熄灭 |
| **恢复** | 快速从中心向两侧扫亮 |

## 常用命令

```bash
# 查看服务状态
sudo systemctl status steamos-led-wled

# 实时查看日志
sudo journalctl -u steamos-led-wled -f

# 重启服务
sudo systemctl restart steamos-led-wled

# 停止服务
sudo systemctl stop steamos-led-wled
```

## 卸载

```bash
sudo ./uninstall.sh
```

## UDP 协议

使用 WLED 的 **DRGB** 实时协议，端口为 21324：

| 字节 | 值 | 说明 |
| ---- | -- | ---- |
| 0 | `0x02` | 协议：DRGB |
| 1 | `0x02` | 超时：2 秒 |
| 2+n×3 | R | 第 n 颗 LED 的红色值 |
| 3+n×3 | G | 第 n 颗 LED 的绿色值 |
| 4+n×3 | B | 第 n 颗 LED 的蓝色值 |

HyperHDR、Hyperion 和其他 Ambilight 方案也使用相同协议。

## USB 串口协议

USB 输出使用 WLED 的 Adalight 串口协议发送完整 RGB 帧：

| 字段 | 大小 | 说明 |
| ---- | ---- | ---- |
| 帧头 | 3 字节 | ASCII `Ada` |
| 像素数量 | 2 字节 | 大端序，实际数量减一 |
| 校验和 | 1 字节 | 数量高字节 XOR 数量低字节 XOR `0x55` |
| 数据 | 3 × 数量 | 按物理灯带顺序排列的 RGB 字节（主机最多发送 256 颗） |

这是 WLED 用于实时 LED 数据的串口协议。项目不再发送旧版 `SLW1` 自定义 MCU 协议；请在 ESP32-S3 上烧录 WLED，而不是构建单独的 MCU 固件。

### Windows USB CDC 测试工具

`tools/wled_usb_cdc_adalight_test.py` 可在 Windows 上通过 COM 口测试 WLED 的 Adalight 接收。该脚本在打开串口前关闭 DTR/RTS，以避免触发开发板复位；并按 128 字节分块、每块间隔 1 ms 发送，避免一次性写入大帧导致接收不完整。测试期间每秒重发白点图案，结束时发送全黑帧。

1. 在 WLED 的 **Config → Sync Interfaces → Serial** 中，将波特率设为 `921600`。
2. 安装 Python 依赖：

   ```powershell
   py -3 -m pip install pyserial
   ```

3. 在设备管理器中找到 WLED 使用的 COM 口，并运行以下命令。将 `COM4` 改为实际端口，并让 `--led-count` 与 WLED 中配置的 LED 数量一致：

   ```powershell
   py -3 tools\wled_usb_cdc_adalight_test.py COM4 --led-count 320
   ```

默认会点亮每隔 10 颗的一颗白灯，持续 10 秒，然后发送全黑帧。可使用 `--spacing`、`--duration`、`--baud` 调整图案、时长和波特率；WLED 与脚本波特率必须一致。优先选择承载 WLED 串口数据的原生 USB CDC COM 口；如果开发板需要双 USB 口供电，请按板卡要求同时连接。参考 [WLED USB CDC Adalight 排查记录](https://github.com/CJYLZS/midi-visualize/blob/master/docs/troubleshooting/2026-08-01-wled-usb-cdc-adalight.md)。

## 许可证

MIT
