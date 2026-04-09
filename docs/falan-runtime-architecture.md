# 法兰城运行架构（v4.44）

> 适用版本：`v4.44`

本文档描述当前 `html5 法兰城` 在浏览器里的主运行链路。

## 1. 当前主链概览

当前法兰城不是“整张大地图直接画到画布”，而是三层组合：

1. 地面层：`512x512` 的 ground / sky WebP 切片
2. 物件层：法兰城专用 `object-map manifest + atlas`
3. 角色层：旅人角色、传送水晶、天空层物件

核心入口：

- 场景配置：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1193](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1193)
- object-map 装载：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1614](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1614)
- 主绘制流程：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3218](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3218)

## 2. 地图基础参数

当前法兰城地图参数：

- 预览尺寸：`11128 x 8300`
- 逻辑格：`300 x 300`
- 等角投影参数：
  - `halfW = 32`
  - `halfH = 23`
  - `baseX = 7004`
  - `baseY = -1578`
  - `scale = 1`

来源：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1193](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1193)

## 3. 地面层

### 3.1 WebP 切片

地面层来自：

- `./assets/falan/map/tiles-512/falan-city-1000-ground-r{row}-c{col}.webp`
- `./assets/falan/map/tiles-512/falan-city-1000-sky-r{row}-c{col}.webp`

如果 ground 切片不存在，会回退去找旧的 combined 切片：

- `falan-city-1000-r{row}-c{col}.webp`

相关代码：

- ground URL：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2154](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2154)
- sky URL：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2158](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2158)
- legacy fallback：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2162](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2162)

### 3.2 视口切片缓存

前端不会一次性持有整图，而是：

- 根据相机算出当前可见 tile 范围
- 只确保附近切片加载
- 用 `tileState.cache` 控制缓存上限

相关代码：

- `visibleTileBounds()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2167](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2167)
- `ensureTile()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2190](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2190)
- `updateVisibleTiles()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2251](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2251)

## 4. 物件层

### 4.1 数据来源

法兰城物件不是运行时直接去读原始 `GraphicInfo*.bin`，而是先离线产出：

- manifest：[/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-city-1000-manifest.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-city-1000-manifest.json)
- atlas：
  - [/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/atlases/falan-atlas-00.png](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/atlases/falan-atlas-00.png)
  - [/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/atlases/falan-atlas-01.png](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/atlases/falan-atlas-01.png)

摘要统计：

- 非零地表 tile：`863`
- 非零 object id：`293`
- 物件摆放总数：`4873`
- atlas 资产数：`1156`

来源：[/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-city-1000-manifest-summary.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-city-1000-manifest-summary.json)

### 4.2 中间层 / 天空层

当前物件层会按 `GraphicInfo.flag` 划成：

- 中间层：与人物穿插排序
- 天空层：始终盖在人物之上

当前只有 `flag = 45` 被默认归入天空层。

相关代码：

- `OBJECT_SKY_FLAG_VALUES`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1215](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1215)
- `partitionObjectItemsMidSky()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1450](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1450)

### 4.3 视口分桶与排序缓存

当前中间层不再每帧全量排序所有物件，而是：

1. 先按锚点格建立索引
2. 只取当前视野附近的候选
3. 对候选做等角排序
4. 视野格边界不变时复用缓存

对应代码：

- 索引状态：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1219](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1219)
- `buildObjectCellIndex()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1463](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1463)
- `collectVisibleObjectRows()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1487](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1487)
- `getSortedVisibleObjectRows()`：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1501](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1501)

## 5. 角色与物件的层级关系

当前主链是：

1. 地面 ground layer
2. 中间层物件（与人物按等角键穿插）
3. 旅人角色
4. 传送水晶动画
5. 天空层物件
6. 黑幕过场

对应代码：

- 中间层 + 角色：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1530](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1530)
- 天空层：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1585](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1585)
- 场景绘制：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3218](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3218)

## 6. 动画来源

法兰城当前有两类动画：

- 旅人角色动作：`crossgate100253`
- 物件动画：由 `falan-object-animations.json` 指向 GIF 或帧图

水晶是特殊处理的第三类：通过 `103010` 的横向雪碧图切帧。

相关文件：

- 角色配置：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1127](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1127)
- 物件动画清单：[/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-object-animations.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-object-animations.json)

## 7. 碰撞当前不在主渲染链里

渲染和碰撞现在是分开的：

- 渲染：ground 切片 + object-map
- 碰撞：读取 `map-1000-collision-final.json`
- 生成链：`ground ∩ 原始 flags`，再由中间层 `object id` 规则修正
- 天空层 object 永远不参与碰撞

并且当前 `ENABLE_MAP_COLLISION = true`，所以运行时会按最终离线碰撞文件参与移动拦截。

对应代码：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1719](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1719)

## 8. 当前性能热点

当前性能面板中最值得看的项：

- `renderMap`：地面层重绘
- `blit`：地图层贴到主画布
- `player`：角色绘制
- `objectSprites`：中间层 + 天空层物件合计

性能面板 DOM：

- [/Users/chujianhe/.openclaw/workspace-taizi/index.html#L978](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L978)

采样逻辑：

- [/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1730](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L1730)
- [/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3390](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3390)

## 9. 当前入口与启动顺序

当前启动顺序：

1. `bootstrapFalan()`
2. 相机与 UI 初始同步
3. `registerServiceWorker()`
4. `loadObjectMapForDepth()`
5. `requestAnimationFrame(loop)`

入口：[/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3543](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L3543)
