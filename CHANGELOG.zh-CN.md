# 更新日志

本文件记录项目的重要变更。

**[English](CHANGELOG.md) | [Português (PT-BR)](CHANGELOG.pt-br.md)**

## [1.1.0] - 2026-11-27

### 新增

- 新增基于 WLED Adalight 协议的 USB 串口输出。将 `output_mode` 设为 `usb` 或 `both`，并配置 `usb_serial_device`/`usb_serial_baud`；仅 USB 模式无需 Wi-Fi 或 WLED IP 地址。
- 支持输出 1–256 颗 LED：将 17 颗源 LED 按比例映射到目标灯带，并通过加权平均实现缩减或扩展。

## [1.0.5] - 2026-08-28

### 修复

- vermagic 不匹配时自动重新构建内核模块；启动后保持 LED 点亮。

## [1.0.4] - 2026-08-13

### 新增

- 可配置温度阈值、VU 表模式/方向/颜色，以及更平滑的动画。

## [1.0.3] - 2026-08-12

### 变更

- 优化主循环，减少 CPU 负载下的卡顿。

## [1.0.2] - 2026-08-11

### 修复

- 修复 WLED 启动预设配置和非阻塞式开机流程。

## [1.0.1] - 2026-08-11

### 新增

- 启动和关机时通过 HTTP 控制 WLED 电源。
- 安装时自动配置 WLED 启动彩虹预设。

### 修复

- 安装时一并安装 `steam_effects.py`。

## [1.0.0] - 2026-08-09

### 新增

- 首次发布。
- 使用 DRGB 协议（端口 21324）的 WLED UDP 实时桥接。
- 从 `/dev/valve-leds-shim`（`valve-leds-shim` 内核模块）读取 LED 快照。
- 将 17 颗源 LED 映射到可配置的灯带长度（1–17）。
- 在服务端渲染 Steam Deck 灯效：
  - 手动（静态颜色）
  - 彩虹（色相循环）
  - 呼吸（亮度脉动）
  - 巡逻（往返移动的光点）
  - 工厂（交替显示互补色）
  - 演示（循环播放所有灯效）
- 叠加效果：
  - 温度：根据 CPU/GPU 温度显示黄到红的渐变条
  - 通知：Steam 成就/消息到达时闪烁
  - 音频响应：由 PipeWire/PulseAudio 驱动的 VU 表
- 动画：
  - 启动：从中心向两侧扫亮 Steam 蓝色
  - 关机：从两端向中心渐暗
  - 挂起：缓慢熄灭
  - 恢复：快速从中心向两侧扫亮
- 自动发现 WLED 设备（mDNS 和子网扫描）。
- 通过 `/etc/steamos-led-wled.conf` 配置。
- 交互式安装器，支持 SteamOS、Arch、Debian 和 Fedora 依赖管理。
- 提供支持自动重启的 systemd 服务。
- 提供卸载脚本。
- 集成 Decky Loader 插件（Toolkit SteamOS Control）。
