# 法兰城传送系统设计文档（当前实现）

> 状态：对应 `html5 法兰城 v4.41`
>
> 这份文档描述的是当前网页实现，而不是早期推导过程。如果和运行代码冲突，先修正文档并同步核对代码。

## 1. 作用范围

本文档只覆盖法兰城地图内的传送水晶系统，包括：

- 水晶点位与链路
- 触发半径、冷却与黑幕过场
- 调试传送输入框的坐标语义
- 水晶在当前深度排序地图中的渲染方式

不覆盖：

- 房屋门口传送
- `coordinatev3_2.bin` 的历史研究推导
- 旧版大地图切片方案

## 2. 当前代码锚点

- 水晶配置：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1238](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1238)
- 传送逻辑：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2500](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2500)
- 传送过场：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2517](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2517)
- 调试传送：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2478](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2478)

## 3. 坐标语义

### 3.1 两套坐标

当前实现里有两套坐标：

- 运行时内部格坐标：`player.tx / player.ty`
- 给人看的显示坐标：右侧状态栏、调试传送输入框里那套

转换关系：

- `displayTx = internalTx`
- `displayTy = sceneMap.rows - 1 - internalTy`

对应代码：

- `internalToDisplay()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2132](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2132)
- `displayToInternal()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2139](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2139)

### 3.2 `itx / ity` 的历史命名漂移

`TELEPORT_CRYSTAL_SLOTS` 里字段名仍然叫 `itx / ity`，但当前代码里它们实际存放的是**运行时内部格坐标**。
这也是最容易让人误读的地方。

例如：

- `__tc_0 = { itx: 76, ity: 66 }`
- 显示到侧栏时会再经过 `internalToDisplay()` 变成 `(76, 233)`

也就是说：

- 代码内比较距离时，用 `itx / ity`
- 面向玩家显示时，再转成显示坐标

## 4. 水晶点位

来源：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1249](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1249)

| 键 | 运行时内部格 `(tx, ty)` | 显示坐标 `(x, y)` | refOid | 说明 |
|---|---:|---:|---:|---|
| `__tc_0` | `(76, 66)` | `(76, 233)` | `17239` | 参与链路 |
| `__tc_1` | `(100, 55)` | `(100, 244)` | `17237` | 参与链路 |
| `__tc_2` | `(77, 236)` | `(77, 63)` | `17239` | 参与链路 |
| `__tc_3` | `(123, 225)` | `(123, 74)` | `17239` | 参与链路 |
| `__tc_4` | `(130, 135)` | `(130, 164)` | `17239` | 参与链路 |
| `__tc_5` | `(146, 158)` | `(146, 141)` | `17239` | 参与链路 |
| `__tc_6` | `(146, 135)` | `(146, 164)` | `17239` | 仅显示，不参与自动传送 |

## 5. 链路配置

来源：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1259](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1259)

当前只有两组三角链路，合计 6 个参与点：

- 组 1：`__tc_0 -> __tc_4 -> __tc_3 -> __tc_0`
- 组 2：`__tc_1 -> __tc_5 -> __tc_2 -> __tc_1`

`__tc_6` 保留显示，但不加入 `TELEPORT_LINKS`。

## 6. 触发规则

### 6.1 触发条件

当前自动传送需同时满足：

- 当前不在过场中
- `performance.now() >= teleportState.cooldownUntil`
- 玩家落在某个参与链路水晶的半径 `0.38` 格内
- 命中的水晶不是本次传送刚落地的那个 `activeSlot`

对应代码：

- `findTeleportSlotAt()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2500](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2500)
- `tryTeleportByCrystalLink()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2587](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2587)

### 6.2 参数

来源：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1276](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1276)

| 常量 | 值 | 说明 |
|---|---:|---|
| `TELEPORT_TRIGGER_RADIUS` | `0.38` | 触发半径 |
| `TELEPORT_COOLDOWN_MS` | `280` | 传送后冷却 |
| `TELEPORT_PAGE_COVER_MS` | `180` | 黑幕盖上时长 |
| `TELEPORT_PAGE_HOLD_MS` | `167` 左右 | 全黑停留 10 帧 |
| `TELEPORT_PAGE_REVEAL_MS` | `180` | 黑幕揭开时长 |

## 7. 过场状态机

状态：

- `idle`
- `cover`
- `hold`
- `reveal`

结构来源：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1285](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1285)

### 7.1 当前真实时序

当前代码的真实行为是：

1. `startTeleportTransition()` 进入 `cover`
2. `cover` 时长结束后，**立刻切玩家坐标**
3. 然后进入 `hold`
4. `hold` 结束后进入 `reveal`
5. `reveal` 结束后设置 `activeSlot` 和冷却

注意，这和早期文档里“在 hold 阶段完成坐标切换”的描述不同。
当前实现切点在 `cover -> hold` 交界处。

对应代码：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2547](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2547)

### 7.2 黑幕形态

- `cover`：自上而下盖黑
- `hold`：整屏全黑
- `reveal`：从中间向上下打开

对应代码：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2517](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2517)

## 8. 水晶渲染

### 8.1 当前资产来源

当前水晶不是直接复用静态 OID，而是：

- 用 `refOid` 复制底座绘制偏移
- 再注入 `__tc_*` 虚拟资源键
- 叠加一张从 `103010/d0_a0.gif` 导出的横向雪碧图

资源来源：

- 雪碧图：[/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/animes/base/103010/d0_a0-sheet.png](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/animes/base/103010/d0_a0-sheet.png)
- 配置：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1238](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1238)

### 8.2 绘制层级

水晶画在“角色层”：

- 中间层物件与人物穿插完成后再画
- 仍然位于天空层之下

这样可以保证：

- 人物不会被水晶的排序打乱
- 水晶动画和人物在同一帧刷新

对应代码：

- `drawTeleportCrystalsPlayerLayer()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1521](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1521)
- `drawDepthSortedMiddleAndPlayer()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1530](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1530)

## 9. 调试传送

右侧“调试传送”输入框接收的是**显示坐标**，不是内部格坐标。

流程：

1. 读取输入框 `displayX / displayY`
2. 通过 `displayToInternal()` 转为运行时坐标
3. 直接写入 `player.tx / player.ty`
4. 不走碰撞拦截

对应代码：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2478](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2478)

## 10. 已知限制

1. `TELEPORT_CRYSTAL_SLOTS` 的 `itx / ity` 命名仍然带历史包袱，容易被误解。
2. 传送文案与坐标显示统一使用“显示坐标”，但运行时比较距离仍然用内部格。
3. 当前文档只覆盖法兰城水晶传送，不代表房屋入口传送已经接入。

## 11. 维护建议

后续如果改动以下任一项，必须同步更新本文档：

- 水晶点位
- 三角链路
- 触发半径 / 冷却
- 黑幕过场时序
- 调试传送坐标语义
- 水晶渲染资源或层级
