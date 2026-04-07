# 法兰城传送系统设计文档(SPEC)

本文档为法兰城传送系统的单一真相来源(Single Source of Truth)，所有传送相关实现均需参考本文档；
如有冲突以本文档为准；本文档更新后需同步更新相关文档及代码实现。

---

## 1. 概述

- 水晶:法兰城传送水晶位置(共 7 个)
- 链路:传送链路三角关系(共 6 条)
- 触发:玩家触发条件检测(基于 UI 事件)
- 坐标:玩家当前坐标(`player.tx` / `player.ty`)
- 链路类型:A->B->C->A 循环链路
- 冷却:触发间隔控制(防止快速连点)

术语:
- 水晶(水晶):传送水晶节点(可视化图标)
- 链路(链路):水晶之间的连接关系

---

## 2. 坐标系统

### 2.1 坐标系转换

- `itx = display_x`
- `ity = 299 - display_y`

反向转换:
- `display_x = itx`
- `display_y = 299 - ity`

### 2.2 排序坐标

- `sortTx/sortTy` 与 `itx/ity` 的关系(用于渲染排序)
- 排序时使用**对角线**;同对角线按x排序
- 同格子时,优先 `refOid`(参考物件编号),小的在上

---

## 3. 水晶配置

来源:`index.html` -> `TELEPORT_CRYSTAL_SLOTS`

| 名称 | 显示坐标 (itx, ity) | 内部坐标 (x, y) | refOid | 备注 |
|---|---:|---:|---:|---|
| `__tc_0` | (76, 66) | (76, 233) | 17239 |  |
| `__tc_1` | (100, 55) | (100, 244) | 17237 |  |
| `__tc_2` | (77, 236) | (77, 63) | 17239 |  |
| `__tc_3` | (123, 225) | (123, 74) | 17239 |  |
| `__tc_4` | (130, 135) | (130, 164) | 17239 |  |
| `__tc_5` | (146, 158) | (146, 141) | 17239 |  |
| `__tc_6` | (146, 135) | (146, 164) | 17239 | 废弃(未启用) |

备注:
- `__tc_6` 已废弃,原设计为额外水晶,实际未使用

---

## 4. 链路配置

来源:`index.html` -> `TELEPORT_TRIANGLE_GROUPS`

两个三角链路:
- 三角1:`__tc_0 -> __tc_4 -> __tc_3 -> __tc_0`
- 三角2:`__tc_1 -> __tc_5 -> __tc_2 -> __tc_1`

代码配置:
- 配置格式 `[[0,4,3],[1,5,2]]`
- 链路索引对应 `TELEPORT_LINKS: Map<fromIdx, toIdx>`

优先级:
1. 检测到水晶,按 `TELEPORT_TRIANGLE_GROUPS` 确定链路
2. 计算下一跳/上一跳,找到目标水晶索引

---

## 5. 触发机制

配置:
- `TELEPORT_TRIGGER_RADIUS = 0.38`
- `TELEPORT_COOLDOWN_MS = 280`

核心函数:
- `findTeleportSlotAt(tx, ty)`:检测玩家是否在水晶范围内
- `tryTeleportByCrystalLink()`:尝试执行传送逻辑

状态变量:
- `teleportState.activeSlot`
- `teleportState.cooldownUntil`

注意事项:
- 玩家需在水晶范围内才能触发(可近距离跨格子触发)
- 冷却时间防止快速连点

---

## 6. 过场动画(传送特效)

配置:
- `TELEPORT_PAGE_COVER_MS = 180`
- `TELEPORT_PAGE_HOLD_MS = round(10 * 1000 / 60)`(约 167ms)
- `TELEPORT_PAGE_REVEAL_MS = 180`

状态机:`teleportTransition`
- `active`
- `phase`: `idle | cover | hold | reveal`
- `phaseStartMs`
- `fromIdx` / `toIdx`

时序:
1. `cover`:黑幕从顶部覆盖下来
2. 计算传送后坐标(黑幕覆盖期间)
3. `hold`:黑幕完全覆盖时停留 10 帧
4. `reveal`:黑幕从顶部向下揭开/显示目标
5. 传送完成,玩家位置更新

渲染:
- 在 `drawScene()` 渲染遮罩层,不影响场景

优化:
- 提前计算目标位置,避免时序问题

---

## 7. 事件/状态更新

- `updatePlayer()`:
  1) 检测水晶触发范围
  2) 若 active,直接 return
  3) 尝试触发传送
  4) 更新传送状态

- `drawScene()`:
  - 渲染传送遮罩特效

- `syncInfo()` / `syncBgm()`:
  - 传送后同步更新场景 UI 及 BGM 状态

---

## 8. 测试计划

### 8.1 基础测试

1. 水晶显示正确
2. 范围内触发正常
3. 按 `TELEPORT_CRYSTAL_SLOTS` 验证水晶位置

### 8.2 链路测试

按 `TELEPORT_TRIANGLE_GROUPS`,测试每个三角链路

### 8.3 边界测试

参数:
- `TELEPORT_PAGE_COVER_MS`
- `TELEPORT_PAGE_HOLD_MS`
- `TELEPORT_PAGE_REVEAL_MS`

测试:
- 慢速/快速点击,验证时序正确
- 连续触发限制,验证冷却

---

## 9. 已知问题

### 9.1 已解决

- 水晶显示坐标问题(初始版本已修复)

### 9.2 待解决

- 传送后坐标抖动(链路切换)
- 传送后BGM切换(部分场景)
- `__tc_6` 未启用问题
- 冷却期间无法取消
- 快速连续点击处理

### 9.3 调试

1. 强制刷新资源:
   - 链接 `?falan_nocache=1`
   - 或在 DevTools 中禁用 SW 缓存

2. 检查水晶/链路:
   - 检查水晶坐标是否正确
   - 检查 `refOid` 对应物件是否存在

3. 检查冷却:
   - 调整 `TELEPORT_COOLDOWN_MS`
   - 检查 `activeSlot` 状态残留

---

## 10. 版本管理(部署流程)

需要同步更新:
- `VERSION`
- `index.html` 中 `FALAN_BUILD_VERSION`
- `manifest.webmanifest` 中 `version`
- `index.html` 中 sw.js 的 `?v=...`
- `sw.js` 中的 `falan-shell-v...` / `falan-runtime-v...`

强制刷新:
- 链接 `?falan_nocache=1`

---

## 11. Git 约定

- 提交:需执行 `commit + push`
- 拉取:需执行 `fetch/pull` 保持同步
- 注意: `.gitignore` 已配置,不要提交大文件

---

## 12. 相关文件

- 主文件:`index.html`
- SW 文件:`sw.js`
- PWA 文件:`manifest.webmanifest`
- 版本文件:`VERSION`
- 规格文档:`docs/falan-teleport-spec.md`

---

## 13. 更新历史

- v4.37:修复/优化,停留 10 帧
- v4.36:遮罩增加 10 帧
- v4.35:改为中间向上下卷开
- v4.34:改为黑幕下拉覆盖
- v4.33:改为黑幕翻页过场
- v4.32:修正链路 `tc0->tc4->tc3` 与 `tc1->tc5->tc2`
- v4.31:水晶链路改为两组三角
