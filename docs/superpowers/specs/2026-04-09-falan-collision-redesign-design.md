# 法兰城碰撞重建设计稿

## 1. 目标

重做法兰城碰撞生成链，使碰撞结果符合以下原则：

- 地板层定义理论可行走范围
- 中间层物件按 `object id` 语义决定是否追加阻挡或放行
- 天空层永远不参与碰撞
- 前端继续只读取离线产物，不在运行时做语义碰撞推导

本次设计优先解决“障碍格不对”的根因，不顺带重构渲染架构。

## 2. 当前现状

当前前端直接读取：

- [/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000.json)

其中 `flags` 被当作最终碰撞格表使用。前端入口：

- [/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2280](/Users/chujianhe/.openclaw/workspace-taizi/index.html#L2280)

当前问题：

1. `flags` 的生成规则不在本仓库内，难以继续精修。
2. `flags` 把“原始地图阻挡”和“物件语义阻挡”混成了一份结果，后续难以解释。
3. 树、装饰、栏杆、门洞这类差异无法只靠现有成品 `flags` 稳定校正。

## 3. 设计原则

### 3.1 基础可走区

基础可走区采用：

- `ground layer`
- 与现有 `map-1000.json.flags` 取交集

也就是：

- 地板层决定“这里理论上能站人”
- 旧 `flags` 继续作为底稿，避免把原始地图里本来就不该走的区域整体放开

### 3.2 物件修正层

只有中间层物件参与碰撞修正：

- `mid layer` 可以改碰撞
- `sky layer` 永远不改碰撞

物件修正完全按 `object id` 生效，不引入“按地图坐标区域打补丁”的主方案。

### 3.3 前端职责

前端不再运行时推导物件语义碰撞，只负责：

1. 读取离线最终碰撞文件
2. 生成 `collisionState.grid`
3. 做 `collides()` 判定
4. 按同一份格表绘制障碍格 overlay

## 4. 产物结构

### 4.1 保留的输入

- 底稿碰撞：[/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000.json)
- 物件清单：[/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-city-1000-manifest.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/object-map/falan-city-1000-manifest.json)

### 4.2 新增文件

- 规则表：[/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/collision-rules-by-object-id.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/collision-rules-by-object-id.json)
- 生成脚本：[/Users/chujianhe/.openclaw/workspace-taizi/tools/build_falan_collision_from_rules.py](/Users/chujianhe/.openclaw/workspace-taizi/tools/build_falan_collision_from_rules.py)
- 最终碰撞文件：[/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final.json)
- 生成摘要：[/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final-summary.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000-collision-final-summary.json)

### 4.3 不覆盖旧文件

旧的：

- [/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000.json](/Users/chujianhe/.openclaw/workspace-taizi/assets/falan/map/map-1000.json)

先保留，不覆盖。原因：

- 方便对照
- 方便回退
- 方便逐步验证新规则是否比旧结果更好

## 5. 规则表格式

第一版规则表只支持三种语义：

```json
{
  "default": "inherit",
  "rules": {
    "10000": "force_pass",
    "10640": "force_block"
  }
}
```

语义定义：

- `inherit`
  - 不主动改动底稿碰撞
- `force_pass`
  - 把该 `object id` 覆盖到的格子强制设为可走
- `force_block`
  - 把该 `object id` 覆盖到的格子强制设为阻挡

第二阶段如果第一版不够，再给单个 `object id` 扩展局部 `cellMask`，但不作为第一版前提。

## 6. 生成算法

### 6.1 输入

离线脚本读取：

1. `map-1000.json`
2. `falan-city-1000-manifest.json`
3. `collision-rules-by-object-id.json`

### 6.2 基础格表

先生成 `baseWalkable`：

1. 从 `ground` 提取“有地板”的格子
2. 与旧 `flags` 取交集

结果含义：

- 有地板且旧 `flags` 允许的格子，才进入“基础可走区”

### 6.3 物件分层

根据 manifest 中的物件元数据，把对象分成：

- `mid`
- `sky`

只有 `mid` 参与碰撞修正。

### 6.4 物件占地

第一版使用：

- `areaE`
- `areaS`

来推导该 `object id` 的逻辑覆盖格范围。

约束：

- 只按 `object id` 修
- 不按具体地图坐标做特殊补丁

### 6.5 规则应用顺序

顺序固定为：

1. 先得到基础格表
2. 遍历全部中间层物件
3. 对命中规则的 `object id` 应用修正
4. 天空层全部跳过
5. 输出最终 `flags`

### 6.6 输出

输出文件结构与现有前端尽量兼容：

```json
{
  "width": 300,
  "height": 300,
  "flags": [0, 1, 1, 0]
}
```

如有必要，也可额外带：

- `source`
- `generatedAt`
- `ruleCounts`

但前端只依赖 `width / height / flags`。

## 7. 前端切换方案

前端只改碰撞文件入口：

- 从 `map-1000.json`
- 改为 `map-1000-collision-final.json`

其余逻辑尽量不动：

- `applyCollisionFromDatFlags()`
- `collisionGridIndex()`
- `isBlockedGridCell()`
- `collides()`
- `drawCollisionOverlay()`

这样可以把改动面压到最小，优先验证新碰撞结果本身。

## 8. 验证方案

### 8.1 离线验证

生成脚本至少输出：

- 阻挡格总数
- 被 `force_pass` 影响的物件数
- 被 `force_block` 影响的物件数
- 与旧 `flags` 相比变化了多少格

并生成一张碰撞预览图，便于肉眼核对。

### 8.2 前端验证

前端验证看三件事：

1. 打开“显示障碍格”后，overlay 与画面对位是否合理
2. 树、装饰、门洞、栏杆是否更接近预期
3. 桌面端和手机端是否共用同一套结果

### 8.3 回退

如果新结果不对，回退路径很简单：

1. 前端把碰撞入口切回旧 `map-1000.json`
2. 保留新脚本和规则表，继续迭代

## 9. 非目标

本轮不做：

- 按地图坐标打人工补丁
- 运行时动态语义碰撞
- 重新设计人物探针形状
- 重构地图渲染性能
- 覆盖所有地图，只先做法兰城 `1000`

## 10. 推荐实施顺序

1. 建规则表骨架，只放少量已知 `object id`
2. 写离线生成脚本
3. 产出 `map-1000-collision-final.json`
4. 前端切换到新文件
5. 用障碍格 overlay 和实跑体验迭代规则

## 11. 成功标准

满足以下几点即可认为第一版成功：

1. 前端不再依赖旧 `flags` 作为最终真相
2. 法兰城碰撞可由 `object id` 规则稳定迭代
3. 树与天空层覆盖物不再误挡
4. 建筑、墙体、栏杆类物件仍然可持续修正
5. 前端运行时负担不增加
