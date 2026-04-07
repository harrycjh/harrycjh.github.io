# 魔力宝贝 H5 还原版 - 设计策划案

## 1. 项目概述

### 1.1 项目背景
将经典端游《魔力宝贝》（CrossGate）移植为 HTML5 版本，采用垂直切片开发模式，优先实现战斗、地图探索、宠物三大核心系统，最大程度还原端游体验。

### 1.2 项目目标
- 完整还原端游核心玩法
- 支持浏览器直接运行
- 本地可玩，后续扩展 P2P 联机

### 1.3 技术选型
| 项目 | 选择 | 说明 |
|------|------|------|
| 游戏引擎 | Phaser 3.60+ | WebGL 渲染，内置场景/动画/物理 |
| 开发语言 | TypeScript 5.x | 类型安全，IDE 支持 |
| 架构模式 | 垂直切片 | 每系统逐步完善 |
| 渲染方式 | Canvas 2D + WebGL | 性能与兼容性平衡 |
| 存档方案 | LocalStorage | 本地持久化 |

---

## 2. 系统架构

### 2.1 整体架构图
```
┌─────────────────────────────────────────────────────────────────┐
│                        Game Client                              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Scenes    │  │    State    │  │   Config    │             │
│  │  Manager    │  │   Manager   │  │   Loader    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Battle    │  │    Map      │  │    Pet      │             │
│  │   System    │  │   Engine    │  │   System    │             │
│  │  (核心)     │  │             │  │             │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │    Asset    │  │    Audio    │  │    Save     │             │
│  │   Loader   │  │   Manager   │  │   System    │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心模块说明

#### 2.2.1 BattleSystem（战斗系统）
- **职责**：回合制战斗逻辑、伤害计算、技能调度
- **依赖**：Character、Skill、Pet 数据模块
- **接口**：startBattle()、executeAction()、endTurn()

#### 2.2.2 MapEngine（地图引擎）
- **职责**：地图渲染、人物移动、碰撞检测、NPC 触发
- **依赖**：TileSet、Character 位置数据
- **接口**：loadMap()、movePlayer()、interactNPC()

#### 2.2.3 PetSystem（宠物系统）
- **职责**：宠物捕获、养成、参战管理
- **依赖**：PetData、BattleSystem
- **接口**：capturePet()、enhancePet()、summonPet()

#### 2.2.4 StateManager（状态管理）
- **职责**：游戏状态维护、场景切换、数据同步
- **依赖**：所有系统
- **接口**：saveState()、loadState()、getState()

#### 2.2.5 AssetLoader（资源加载）
- **职责**：图片/音频资源加载、进度管理
- **依赖**：Phaser 资源系统
- **接口**：loadAll()、getAsset()、releaseAsset()

#### 2.2.6 SaveSystem（存档系统）
- **职责**：LocalStorage 读写、存档校验
- **依赖**：StateManager
- **接口**：save()、load()、exportSave()、importSave()

---

## 3. 战斗系统详细设计

### 3.1 回合制机制
采用经典 ATB（Active Time Battle）回合制：
- 每个人物/宠物有速度属性，影响行动顺序
- 行动条满后可执行行动
- 行动后重置行动条

### 3.2 元素克制关系
| 克制属性 | 被克制属性 |
|----------|-----------|
| 火 | 风 |
| 风 | 地 |
| 地 | 水 |
| 水 | 火 |
| 圣 | 暗 |
| 暗 | 圣 |

### 3.3 技能分类
| 类型 | 说明 | 示例 |
|------|------|------|
| 攻击技 | 造成伤害 | 魔法弹、剑气 |
| 治疗技 | 恢复生命 | 治疗、回复术 |
| 辅助技 | 增益/减益 | 加速、防御 |
| 召唤技 | 召唤宠物 | 召唤术 |

### 3.4 战斗流程
```
1. 战斗开始 → 加载敌我双方数据
2. 初始化 ATB 行动条
3. 循环：
   a. 更新行动条
   b. 行动条满者选择行动
   c. 执行行动（动画 + 伤害计算）
   d. 检查胜负条件
4. 战斗结束 → 结算经验/掉落
```

### 3.5 伤害计算公式
```
最终伤害 = 基础攻击 × 技能威力 / 防御 × 元素克制 × 暴击倍率
暴击倍率 = 1.5（暴击时）
```

---

## 4. 地图系统详细设计

### 4.1 地图类型
| 类型 | 说明 |
|------|------|
| 城镇 | 安全区，可与 NPC 对话、买卖物品 |
| 野外 | 遇敌地图，随机遭遇敌人 |
| 副本 | 特定任务/挑战区域 |

### 4.2 地图结构
- **TileMap**：基于 Tiled Map Editor 的 TMX 格式
- **碰撞层**：定义可行走区域和障碍物
- **事件层**：定义 NPC、触发器位置

### 4.3 人物移动
- 8 方向移动（上下左右 + 对角线）
- 碰撞检测基于 Tile 坐标
- 移动速度可配置

### 4.4 NPC 对话
- 点击 NPC 触发对话框
- 支持多分支对话树
- 对话触发战斗/任务/商店

---

## 5. 宠物系统详细设计

### 5.1 宠物分类
| 等级 | 说明 | 捕捉方式 |
|------|------|----------|
| 野生 | 野外遇敌 | 战斗中捕捉 |
| 贵族 | 较强 | 任务奖励 |
| 传说 | 最强 | BOSS 掉落 |

### 5.2 宠物属性
| 属性 | 说明 |
|------|------|
| 等级 | 1-100 |
| 生命 | HP 上限 |
| 魔力 | MP 上限 |
| 攻击 | 物理伤害 |
| 防御 | 减伤比例 |
| 敏捷 | 速度/闪避 |
| 元素 | 火/风/地/水/圣/暗 |

### 5.3 宠物技能
- 每只宠物拥有 1-4 个技能
- 技能通过升级解锁
- 技能可遗忘重新学习

### 5.4 捕捉机制
1. 战斗中使用"捕捉"指令
2. 计算捕捉概率 = (1 - 目标HP/目标MAXHP) × 基础概率
3. 成功则宠物加入队伍

---

## 6. 开发阶段规划

### Phase 1：地图探索（优先）
| 周次 | 内容 |
|------|------|
| 1 | 项目搭建、Phaser 3 集成、资源导入 |
| 2 | 地图渲染引擎、TileMap 加载 |
| 3 | 人物移动、碰撞检测、NPC 触发 |
| 4 | 城镇/野外地图切换、NPC 对话框架 |

### Phase 2：战斗系统（核心）
| 周次 | 内容 |
|------|------|
| 5 | 回合制框架、行动队列、ATB 机制 |
| 6 | 技能系统（攻击/治疗/辅助） |
| 7 | 元素克制、伤害计算、战斗结算 |
| 8 | 战斗动画、特效、音效 |

### Phase 3：宠物系统
| 周次 | 内容 |
|------|------|
| 9 | 宠物数据结构、宠物界面、宠物图鉴 |
| 10 | 宠物捕捉机制（原版概率公式） |
| 11 | 宠物养成（升级/技能/升阶） |
| 12 | 宠物参战、宠物状态同步 |

### Phase 4：扩展系统
| 内容 | 说明 |
|------|------|
| 物品系统 | 装备、道具、背包 |
| 任务系统 | 主线、支线、日常 |
| 生产系统 | 采集、合成 |
| 社交系统 | 后续 P2P 扩展预留 |

---

## 7. 数据结构

### 7.1 角色数据
```typescript
interface Character {
  id: string;
  name: string;
  job: JobType;
  level: number;
  exp: number;
  hp: number;
  maxHp: number;
  mp: number;
  maxMp: number;
  attack: number;
  defense: number;
  agility: number;
  element: ElementType;
  skills: Skill[];
  equipment: Equipment[];
}
```

### 7.2 宠物数据
```typescript
interface Pet {
  id: string;
  templateId: string;
  name: string;
  level: number;
  exp: number;
  hp: number;
  maxHp: number;
  attack: number;
  defense: number;
  agility: number;
  element: ElementType;
  skills: Skill[];
  isCaptured: boolean;
}
```

### 7.3 存档数据结构
```typescript
interface SaveData {
  version: string;
  timestamp: number;
  character: Character;
  pets: Pet[];
  inventory: Item[];
  quests: Quest[];
  maps: MapProgress[];
}
```

---

## 8. 美术资源方案

### 8.1 已有资源（来自原版客户端）
| 资源类型 | 来源目录 | 数量/说明 |
|----------|----------|-----------|
| 图形包 | crossgate_assets/extract_preview/graphics_export/ | 4个包，30,000+ 精灵 |
| 角色立绘 | crossgate_assets/extract_preview/character_gallery/ | 角色全身像 |
| 宠物精灵 | crossgate_assets/extract_preview/pet_scan/ | 宠物图鉴 |
| 动画数据 | crossgate_assets/extract_preview/animations_export/ | 角色动作动画 |
| 地图预览 | crossgate_assets/extract_preview/map_preview/ | 城市/野外地图 |
| 游戏音乐 | crossgate_assets/ | BGM (wav/ogg) |
| 地图数据 | crossgate602/map/0/ | 地图瓦片数据 |
| 资源包 | crossgate602/data/0/ | 1286 个资源文件 |

### 8.2 资源格式
- 图片：PNG（带透明通道）
- 动画：Spritesheet（Phaser 兼容）
- 音频：OGG/MP3（浏览器兼容）

### 8.3 资源管理
- 资源按需加载，避免首屏加载过慢
- 资源缓存复用
- 使用原版资源最大化还原度

---

## 9. 目录结构
```
magic-bubble-h5/
├── src/
│   ├── main.ts                 # 游戏入口
│   ├── config/                 # 配置文件
│   │   ├── game-config.ts
│   │   └── battle-config.ts
│   ├── data/                   # 静态数据
│   │   ├── jobs.ts
│   │   ├── skills.ts
│   │   ├── pets.ts
│   │   └── maps.ts
│   ├── entities/               # 游戏实体
│   │   ├── Character.ts
│   │   ├── Pet.ts
│   │   ├── Enemy.ts
│   │   └── NPC.ts
│   ├── systems/                # 核心系统
│   │   ├── BattleSystem.ts
│   │   ├── MapEngine.ts
│   │   ├── PetSystem.ts
│   │   └── SaveSystem.ts
│   ├── scenes/                 # Phaser 场景
│   │   ├── BootScene.ts
│   │   ├── LoadingScene.ts
│   │   ├── MenuScene.ts
│   │   ├── BattleScene.ts
│   │   ├── MapScene.ts
│   │   └── UIScene.ts
│   ├── ui/                     # UI 组件
│   │   ├── BattleUI.ts
│   │   ├── DialogUI.ts
│   │   └── PetUI.ts
│   └── utils/                  # 工具函数
│       ├── damage-calculator.ts
│       └── element-utils.ts
├── assets/                     # 资源文件
│   ├── images/
│   ├── audio/
│   └── tilemaps/
├── resources/                  # 原版资源（链接）
│   └── crossgate602/ -> ~/Downloads/crossgate602/
├── docs/                       # 文档
│   └── specs/                  # 设计文档
├── package.json
├── tsconfig.json
└── README.md
```

---

## 10. 成功标准

### 10.1 Phase 1 完成标准（地图探索）
- [ ] 可加载并显示地图
- [ ] 人物可在地图上移动
- [ ] NPC 对话框正常显示
- [ ] 城镇/野外可切换
- [ ] 原版地图资源正确解析

### 10.2 Phase 2 完成标准（战斗系统）
- [ ] 战斗可正常进行（我方 vs 敌方）
- [ ] 回合制正常运作
- [ ] 至少 5 种技能可用
- [ ] 元素克制生效（原版克制表）
- [ ] 伤害计算正确

### 10.3 Phase 3 完成标准（宠物系统）
- [ ] 可查看宠物列表
- [ ] 战斗中有捕捉选项
- [ ] 宠物可参战
- [ ] 宠物升级属性增长
- [ ] 原版宠物数据还原（等级/属性/技能）

---

## 11. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 原版资源无法获取 | 高 | 使用开源像素素材替代 |
| 项目规模过大 | 中 | 严格按阶段交付，及时调整范围 |
| Phaser 3 学习成本 | 低 | 官方文档完善，社区资源丰富 |
| 性能问题 | 中 | 善用对象池，按需加载资源 |

---

*文档版本：v1.0*
*创建日期：2026-04-07*
