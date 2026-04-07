# 法兰城传送系统策划与实现总览

本文档汇总当前网页版法兰城传送功能的策划约定、坐标配置、动画节奏、发布与协作规范。

## 1. 坐标体系

- 显示坐标 -> 内部格：
  - `itx = display_x`
  - `ity = 299 - display_y`
- 排序字段使用格坐标：`sortTx = itx`、`sortTy = ity`
- 水晶底座偏移继承 `refOid`（当前多数为 `17239`，`__tc_1` 为 `17237`）

## 2. 当前水晶点配置（7个）

源码位置：`index.html` 中 `TELEPORT_CRYSTAL_SLOTS`

| 槽位 | 内部格 (itx, ity) | 显示坐标 (x, y) | 备注 |
|---|---:|---:|---|
| `__tc_0` | (76, 66) | (76, 233) | 参与传送 |
| `__tc_1` | (100, 55) | (100, 244) | 参与传送 |
| `__tc_2` | (77, 236) | (77, 63) | 参与传送 |
| `__tc_3` | (123, 225) | (123, 74) | 参与传送 |
| `__tc_4` | (130, 135) | (130, 164) | 参与传送 |
| `__tc_5` | (146, 158) | (146, 141) | 参与传送 |
| `__tc_6` | (146, 135) | (146, 164) | 仅显示，不参与自动传送 |

## 3. 传送网络规则（两组三角）

源码位置：`index.html` 中 `TELEPORT_TRIANGLE_GROUPS`

- 组1：`__tc_0 -> __tc_4 -> __tc_3 -> __tc_0`
- 组2：`__tc_1 -> __tc_5 -> __tc_2 -> __tc_1`

说明：
- 当前按策划仅纳入 6 个点自动传送，`__tc_6` 仅作为显示点保留。
- 触发为踩到传送点附近自动传送（不是手动点击交互）。

## 4. 触发判定与防抖参数

源码位置：`index.html`

- `TELEPORT_TRIGGER_RADIUS = 0.38`
- `TELEPORT_COOLDOWN_MS = 280`

逻辑要点：
- 每帧在 `updatePlayer()` 内调用传送检测
- 通过 `findTeleportSlotAt()` 判定是否进入某传送点半径
- 冷却与 `activeSlot` 联合防止连续来回连跳

## 5. 传送过场动画（当前版本）

源码位置：`index.html` 的 `teleportTransition` 系列逻辑

当前流程：
1. 黑幕从上往下覆盖（`TELEPORT_PAGE_COVER_MS = 180`）
2. 全黑停留 10 帧（`TELEPORT_PAGE_HOLD_MS = round(10 * 1000 / 60)`，约 167ms）
3. 从中间向上/下同时卷开（`TELEPORT_PAGE_REVEAL_MS = 180`）

实现要点：
- 切坐标发生在覆盖完成、进入全黑阶段时
- 过场期间锁移动输入
- 通过 `drawScene()` 末尾叠加黑幕矩形实现，不侵入地图图层资源

## 6. 版本与缓存策略

每次功能改动需同步递增并对齐：

- `VERSION`
- `index.html` 中 `FALAN_BUILD_VERSION`
- `manifest.webmanifest` 的 `"version"`
- `index.html` 中 `sw.js?v=...`
- `sw.js` 中缓存键（`falan-shell-v...` / `falan-runtime-v...`）

强制清缓存方式：
- 地址栏追加：`?falan_nocache=1`

## 7. 预览资源提交策略

为避免超大文件与误提交，以下内容默认不入库（见 `.gitignore`）：

- `assets/falan/map/falan-city-*-preview.*`
- `assets/falan/map/map-*-flags-preview.png`
- `assets/falan/map-previews-map0-lt1000/`
- `assets/falan/map-previews-*/`
- `map-previews-map0-lt1000.html`

## 8. 协作约定（当前执行方式）

- 默认工作流：改动完成后直接 `commit + push`
- 多设备协作前建议先同步远端：`git fetch` / `git pull`
- 发布后如用户反馈“看不到改动”，优先排查 SW 缓存（`?falan_nocache=1`）

## 9. 快速定位代码

- 传送点坐标：`index.html` -> `TELEPORT_CRYSTAL_SLOTS`
- 三角链路：`index.html` -> `TELEPORT_TRIANGLE_GROUPS`
- 触发与跳转：`findTeleportSlotAt()`、`tryTeleportByCrystalLink()`
- 过场状态机：`teleportTransition`、`updateTeleportTransition()`、`teleportCurtainRect()`
- 黑幕绘制：`drawScene()` 末尾

