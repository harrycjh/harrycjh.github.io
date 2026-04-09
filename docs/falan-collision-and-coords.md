# 法兰城坐标与碰撞说明（v4.46）

> 适用版本：`v4.46`

## 1. 坐标体系

当前法兰城至少有三层坐标：

1. 内部格坐标：`player.tx / player.ty`
2. 对玩家展示的显示坐标：右侧状态栏、调试传送输入框
3. 预览像素坐标：实际绘制到地图大画布上的 `x / y`

## 2. 内部格坐标与显示坐标

转换关系：

- `displayTx = internalTx`
- `displayTy = sceneMap.rows - 1 - internalTy`

对应代码：

- `internalToDisplay()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2132](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2132)
- `displayToInternal()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2139](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2139)

右侧 UI 统一显示的是这套“显示坐标”，不是运行时内部格坐标：

- [/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2440](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2440)

## 3. 内部格坐标到预览像素

等角投影公式：

```text
previewX = ((tx - ty) * halfW + baseX) * scale
previewY = ((tx + ty) * halfH + baseY) * scale
```

当前常量：

- `halfW = 32`
- `halfH = 23`
- `baseX = 7004`
- `baseY = -1578`
- `scale = 1`

对应代码：

- 公式：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2106](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2106)
- 地图参数：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1193](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1193)

## 4. 反算公式

浏览器里也保留了从预览像素反推出格子的函数：

- `previewToMap()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2121](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2121)

它主要用于：

- 计算当前可见格范围
- 物件视口裁剪

## 5. 当前碰撞来源

当前碰撞直接来自：

- [/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json)

它由离线脚本读取：

- [/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-city-1000-manifest.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-city-1000-manifest.json)
- [/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/collision-rules-by-object-id.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/collision-rules-by-object-id.json)

生成。新的基础底稿来自 `manifest.tileLayer`，不再把旧 `map-1000.json.ground/objects` 当坐标真相。

同时要注意：

- `manifest.objectItems` 是原始 object layer 的逐格条目
- 不是“大物件锚点列表”
- 所以当前碰撞修正只按每个 `object cell` 自身生效，不再按 `areaE/areaS` 向周围外扩

装载入口：

- `MAP_COLLISION_JSON`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2280](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2280)
- `loadCollisionFromDatMap()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2301](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2301)

这说明当前碰撞已经不是：

- 根据最终大图反推
- 运行时按 object 语义实时扣格

而是前端直接读离线好的最终 `flags`。

## 6. 一个非常重要的现状：碰撞当前开启

当前代码中：

```javascript
const ENABLE_MAP_COLLISION = true;
```

也就是：

- 碰撞数据会加载
- `collisionState.grid` 会准备好
- `isBlockedGridCell()` / `collides()` 会存在
- 并且真正移动时会参与拦截

代码位置：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1722](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1722)

如果后面有人问“为什么已经有格表但人物还是穿过去”，先看这个开关是否又被改回去了。

## 7. 碰撞格表的索引方向

当前格表索引不是简单的 `ty * width + tx`，而是：

```text
idx = tx * width + (width - 1 - ty)
```

对应代码：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2322](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2322)

这层如果文档不记，后面重新生成或人工核格时很容易读反。

## 8. 运行时碰撞探针

当前总开关已开启，`collides()` 仍使用多探针判定：

- 中心
- 左前脚
  - `[-0.28, 0.18]`
- 右前脚
  - `[0.28, 0.18]`
- 上方
  - `[0, -0.26]`

代码：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2334](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2334)

## 9. 调试传送为什么不走碰撞

调试传送按钮直接改 `player.tx / player.ty`，不会经过 `tryMoveWithCollision()`。  
所以即使未来重新打开碰撞，调试传送也仍然是“无拦截瞬移”。

代码：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2478](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2478)

## 10. 障碍格叠层只是视觉工具

当前障碍格叠层默认开启，但默认显示开关仍然由 UI 控制：

- `ENABLE_OBSTACLE_OVERLAY_LAYER = true`

并且它只是视觉 overlay，不等于实际阻挡逻辑。

代码：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1720](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1720)

## 11. 当前最容易踩坑的点

1. `itx / ity` 命名带历史包袱，实际已被当作内部格坐标使用。
2. 右侧坐标和调试输入框显示的是“显示坐标”，不是 `player.tx / ty`。
3. `map-1000-collision-final.json` 才是当前最终碰撞真相；旧 `map-1000.json` 现在只保留给历史兼容和对照，不再参与新底稿生成。
4. 现在移动卡顿、卡墙或仍能穿越，先确认 `ENABLE_MAP_COLLISION`、格表方向和探针参数。
