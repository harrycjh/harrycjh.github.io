# 法兰城传送系统设计文档(SPEC)

本文档为法兰城传送系统的单一真相来源(Single Source of Truth)，所有传送相关实现均需参考本文档；
如有冲突以本文档为准；本文档更新后需同步更新相关文档及代码实现。

---

## 1. 概述

法兰城传送系统允许玩家通过接触传送水晶在不同位置之间瞬移。系统采用三角链路模式，玩家从水晶A传送后会到达链路中的下一个水晶，形成循环。

### 系统组成

- **水晶**:法兰城7个传送水晶节点，显示为游戏中的水晶图标
- **链路**:6条三角关系链路，连接方式为 A->B->C->A 循环
- **触发**:玩家走到水晶附近（0.38格范围）时自动触发
- **冷却**:每次传送后280ms冷却，防止快速连点
- **过场**:传送时播放黑幕覆盖/揭开的过渡动画

### 术语定义

| 术语 | 说明 |
|------|------|
| 水晶 | 传送水晶节点，游戏中显示为发光的晶体图标 |
| 链路 | 水晶之间的连接关系，决定传送目标 |
| 显示坐标 | 屏幕渲染用的瓦片坐标 (itx, ity) |
| 内部坐标 | 游戏逻辑用的瓦片坐标 (x, y) |
| refOid | 水晶对应的物件模板ID |

### 坐标系说明

游戏使用 isometric 斜角视角渲染，坐标系转换关系：
- 显示坐标 `itx` = 内部坐标 `x`
- 显示坐标 `ity` = 299 - 内部坐标 `y`

反向转换：
- 内部坐标 `x` = 显示坐标 `itx`
- 内部坐标 `y` = 299 - 显示坐标 `ity`

---

## 2. 水晶配置

### 2.1 水晶位置数据

来源:`index.html` -> `TELEPORT_CRYSTAL_SLOTS`

| 名称 | 显示坐标 (itx, ity) | 内部坐标 (x, y) | refOid | 区域 |
|---|---:|---:|---:|---|
| `__tc_0` | (76, 66) | (76, 233) | 17239 | 城东入口 |
| `__tc_1` | (100, 55) | (100, 244) | 17237 | 城东北 |
| `__tc_2` | (77, 236) | (77, 63) | 17239 | 城西 |
| `__tc_3` | (123, 225) | (123, 74) | 17239 | 城南 |
| `__tc_4` | (130, 135) | (130, 164) | 17239 | 城东南 |
| `__tc_5` | (146, 158) | (146, 141) | 17239 | 城南东 |
| `__tc_6` | (146, 135) | (146, 164) | 17239 | 废弃 |

### 2.2 水晶精灵说明

水晶使用 OID 17236-17241 的精灵渲染：
- **17241**: 主水晶精灵，使用最频繁
- **17237**: 大型水晶精灵，用于主要水晶位置
- **17239**: 中型水晶精灵，用于辅助位置
- **其他**: 变体精灵，装饰用

每个水晶位置由多个精灵组合而成，形成完整的晶体效果。

---

## 3. 链路配置

### 3.1 链路分组

来源:`index.html` -> `TELEPORT_TRIANGLE_GROUPS`

两个独立的三角链路：
- **链路1**: `__tc_0 -> __tc_4 -> __tc_3 -> __tc_0`
  - 覆盖城东、城东南、城南区域
- **链路2**: `__tc_1 -> __tc_5 -> __tc_2 -> __tc_1`
  - 覆盖城东北、城南东、城西区域

### 3.2 链路数据结构

```javascript
// 配置格式
const TELEPORT_TRIANGLE_GROUPS = [[0, 4, 3], [1, 5, 2]];

// 链路索引映射
const TELEPORT_LINKS = new Map();
// 链路1: 0->4->3->0
TELEPORT_LINKS.set(0, 4);  // 从0传送到4
TELEPORT_LINKS.set(4, 3);  // 从4传送到3
TELEPORT_LINKS.set(3, 0);  // 从3传送到0
// 链路2: 1->5->2->1
TELEPORT_LINKS.set(1, 5);  // 从1传送到5
TELEPORT_LINKS.set(5, 2);  // 从5传送到2
TELEPORT_LINKS.set(2, 1);  // 从2传送到1
```

### 3.3 传送逻辑

传送时计算下一个目标的算法：
1. 获取玩家当前所在水晶的索引 `currentIdx`
2. 从 `TELEPORT_LINKS` 中查找 `currentIdx` 对应的目标索引 `nextIdx`
3. 获取 `TELEPORT_CRYSTAL_SLOTS[nextIdx]` 的内部坐标
4. 将玩家传送到目标坐标

---

## 4. 触发机制

### 4.1 触发条件

触发传送需要满足以下条件：
- 玩家当前位置在某个水晶的 **0.38格范围内**
- 当前不在冷却期内（`Date.now() > teleportState.cooldownUntil`）
- 当前没有传送动画在播放（`teleportTransition.active === false`）

### 4.2 触发检测算法

```javascript
function findTeleportSlotAt(tx, ty) {
    const RADIUS = 0.38;
    for (let i = 0; i < TELEPORT_CRYSTAL_SLOTS.length; i++) {
        const slot = TELEPORT_CRYSTAL_SLOTS[i];
        const dx = tx - slot.x;
        const dy = ty - slot.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance <= RADIUS) {
            return i;  // 返回触发的水晶索引
        }
    }
    return -1;  // 没有触发任何水晶
}
```

### 4.3 传送执行流程

```javascript
function tryTeleportByCrystalLink(slotIdx) {
    // 1. 检查冷却
    if (Date.now() < teleportState.cooldownUntil) {
        return false;
    }

    // 2. 检查是否已在传送中
    if (teleportTransition.active) {
        return false;
    }

    // 3. 获取目标水晶
    const nextIdx = TELEPORT_LINKS.get(slotIdx);
    if (nextIdx === undefined) {
        return false;
    }

    // 4. 启动传送动画
    startTeleportTransition(slotIdx, nextIdx);

    // 5. 设置冷却
    teleportState.activeSlot = nextIdx;
    teleportState.cooldownUntil = Date.now() + TELEPORT_COOLDOWN_MS;

    return true;
}
```

### 4.4 配置参数

| 参数 | 值 | 说明 |
|------|---|---|
| `TELEPORT_TRIGGER_RADIUS` | 0.38 | 触发半径（格） |
| `TELEPORT_COOLDOWN_MS` | 280 | 冷却时间（毫秒） |

---

## 5. 过场动画

### 5.1 动画阶段

传送动画分为4个阶段：

| 阶段 | 时长 | 视觉效果 |
|------|------|----------|
| `cover` | 180ms | 黑幕从屏幕顶部向下覆盖 |
| `hold` | 167ms | 黑幕完全覆盖，停留10帧 |
| `reveal` | 180ms | 黑幕从顶部向下揭开 |
| `idle` | - | 动画完成 |

### 5.2 状态机

```javascript
const teleportTransition = {
    active: false,
    phase: 'idle',  // 'idle' | 'cover' | 'hold' | 'reveal'
    phaseStartMs: 0,
    fromIdx: -1,
    toIdx: -1
};
```

### 5.3 动画时序

```
时间轴:
0ms ----180ms------347ms------527ms
| cover  |  hold  |  reveal |
|--------|--------|---------|
        玩家坐标切换点
        (在 hold 阶段完成)
```

1. **cover 阶段 (0-180ms)**
   - 绘制黑色遮罩从顶部向下扩展
   - 遮罩高度 = 覆盖比例 * 屏幕高度
   - 覆盖比例 = 已用时间 / 180ms

2. **hold 阶段 (180-347ms)**
   - 遮罩完全覆盖屏幕
   - 在此阶段完成玩家坐标切换
   - 玩家位置从 fromIdx 变为 toIdx

3. **reveal 阶段 (347-527ms)**
   - 遮罩从顶部向下缩小（揭开效果）
   - 显示目标水晶所在场景
   - 揭开比例 = 已用时间 / 180ms

### 5.4 渲染实现

```javascript
function renderTeleportOverlay(ctx) {
    if (!teleportTransition.active) return;

    const elapsed = Date.now() - teleportTransition.phaseStartMs;
    const screenH = canvas.height;

    let coverRatio = 0;

    switch (teleportTransition.phase) {
        case 'cover':
            coverRatio = Math.min(1, elapsed / TELEPORT_PAGE_COVER_MS);
            break;
        case 'hold':
            coverRatio = 1;
            // 在 hold 阶段的开始，切换玩家坐标
            if (elapsed === 0) {
                executeTeleport();
            }
            break;
        case 'reveal':
            coverRatio = 1 - Math.min(1, elapsed / TELEPORT_PAGE_REVEAL_MS);
            break;
    }

    // 绘制黑幕
    if (coverRatio > 0) {
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, screenH * coverRatio);
    }
}
```

### 5.5 配置参数

| 参数 | 值 | 说明 |
|------|---|---|
| `TELEPORT_PAGE_COVER_MS` | 180 | 覆盖阶段时长 |
| `TELEPORT_PAGE_HOLD_MS` | 167 | 停留阶段时长（约10帧@60fps） |
| `TELEPORT_PAGE_REVEAL_MS` | 180 | 揭开阶段时长 |

---

## 6. 玩家移动与传送整合

### 6.1 updatePlayer 函数

```javascript
function updatePlayer() {
    // 1. 检测水晶触发范围
    const slotIdx = findTeleportSlotAt(player.tx, player.ty);

    // 2. 若已在传送中，直接返回
    if (teleportTransition.active) {
        return;
    }

    // 3. 若检测到水晶触发，尝试传送
    if (slotIdx >= 0) {
        tryTeleportByCrystalLink(slotIdx);
    }

    // 4. 更新冷却状态
    if (teleportState.cooldownUntil > 0 &&
        Date.now() > teleportState.cooldownUntil) {
        teleportState.activeSlot = -1;
        teleportState.cooldownUntil = 0;
    }
}
```

### 6.2 传送完成后的处理

```javascript
function onTeleportComplete() {
    // 1. 标记传送完成
    teleportTransition.active = false;
    teleportTransition.phase = 'idle';

    // 2. 更新玩家位置（已在 hold 阶段更新）
    // 位置已通过 executeTeleport() 更新

    // 3. 同步场景信息
    syncInfo();

    // 4. 切换 BGM（如需要）
    syncBgm();
}
```

---

## 7. 排序与渲染

### 7.1 排序坐标计算

水晶和玩家在 isometric 视角下需要正确的深度排序：

```javascript
function calculateSortKey(tx, ty, refOid = 0) {
    // sortTx/sortTy 用于排序
    const sortTx = tx;
    const sortTy = ty;

    // 排序规则：
    // 1. 按 sortTx + sortTy 对角线排序（对角线内按 sortTx 排序）
    // 2. 同格子时按 refOid 排序（小的在上）
    return {
        sortKey: sortTx + sortTy * 1000,
        refOid: refOid
    };
}
```

### 7.2 水晶渲染

水晶精灵渲染在玩家和NPC的上层（sky layer），使用 `objectLayer` 数据。

---

## 8. 调试与问题排查

### 8.1 常见问题

**问题1: 传送不触发**
- 检查 `TELEPORT_TRIGGER_RADIUS` 是否太大/太小
- 检查冷却时间 `TELEPORT_COOLDOWN_MS` 是否未重置
- 确认水晶精灵已正确加载

**问题2: 传送后位置错误**
- 检查内部坐标 (x, y) 是否正确
- 确认坐标系转换公式正确

**问题3: 动画显示异常**
- 检查各阶段时长配置
- 确认 `drawScene()` 中正确调用了渲染函数

### 8.2 调试方法

1. **强制刷新缓存**
   - 访问 `?falan_nocache=1`
   - 或在 DevTools 中禁用 Service Worker

2. **检查状态**
   ```javascript
   console.log('teleportState:', teleportState);
   console.log('teleportTransition:', teleportTransition);
   ```

3. **可视化触发范围**
   - 在 `findTeleportSlotAt` 中添加日志
   - 绘制圆形显示触发半径

---

## 9. 版本管理

### 9.1 需要同步更新的文件

| 文件 | 更新内容 |
|------|----------|
| `VERSION` | 主版本号 |
| `index.html` | `FALAN_BUILD_VERSION` |
| `manifest.webmanifest` | `version` |
| `sw.js` | `falan-shell-v*` / `falan-runtime-v*` |

### 9.2 发布流程

1. 更新 `VERSION` 文件
2. 更新 `index.html` 中的 `FALAN_BUILD_VERSION`
3. 更新 `manifest.webmanifest` 中的 `version`
4. 更新 `sw.js` 中的版本字符串
5. 提交代码并推送
6. 部署后访问 `?falan_nocache=1` 强制刷新

---

## 10. 相关文件

| 文件路径 | 说明 |
|----------|------|
| `index.html` | 主入口，包含传送水晶和链路配置 |
| `sw.js` | Service Worker，处理缓存和更新 |
| `manifest.webmanifest` | PWA 清单文件 |
| `VERSION` | 当前版本号 |
| `docs/falan-teleport-spec.md` | 本文档 |

---

## 11. 更新历史

| 版本 | 更新内容 |
|------|----------|
| v4.39 | 隐藏地图文字牌物件（`HIDDEN_OBJECT_OIDS`：`201`，含「城下丁」等共 15 处），SW `v422` |
| v4.38 | 发布版本号与 SW 缓存键同步（`falan-shell-v421` / `sw.js?v=421`），无玩法改动 |
| v4.37 | 修复/优化，停留10帧不变 |
| v4.36 | 传送全黑阶段增加10帧停留 |
| v4.35 | 传送第二段改为中间向上下卷开 |
| v4.34 | 传送过场改为黑幕下拉覆盖后直接恢复原画 |
| v4.33 | 传送改为黑幕翻页过场（上到下覆盖/揭开） |
| v4.32 | 传送顺序改为 tc0->tc4->tc3 与 tc1->tc5->tc2 |
| v4.31 | 传送水晶改为两组三角链路 |
