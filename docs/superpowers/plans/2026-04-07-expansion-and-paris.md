# 地图扩展与法兰城 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 扩展更多地图和怪物，完成法兰城（主城）的完整实现

**Architecture:**
- 新地图系统支持多楼层建筑和区域
- 法兰城作为中心主城，连接各野外地图
- 怪物分级系统（普通/精英/BOSS）
- 地图传送门网络

**Tech Stack:** Phaser 3, TypeScript, LocalStorage

---

## Task 1: 扩展地图数据

**Files:**
- Modify: `src/data/map-data.ts`

- [ ] **Step 1: 添加新地图数据结构**

修改 `src/data/map-data.ts` 添加 5 张新地图：

```typescript
export interface MapData {
  id: string;
  name: string;
  width: number;
  height: number;
  tileSize: number;
  layers: TileLayer[];
  groundColor?: number; // 地面颜色
  buildings?: Building[]; // 建筑物
  portals?: Portal[]; // 传送门
  NPCs?: string[]; // NPC ID 列表
}

export interface Building {
  id: string;
  name: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: number;
  targetMap?: string; // 进入的目标地图
  targetX?: number;
  targetY?: number;
}

export interface Portal {
  id: string;
  x: number;
  y: number;
  targetMap: string;
  targetX: number;
  targetY: number;
  radius: number;
}

// 5 张新地图数据
export const FIELD_MAPS: Record<string, MapData> = {
  forest: {
    id: 'forest',
    name: '伊尔森林',
    width: 25,
    height: 19,
    tileSize: 32,
    groundColor: 0x2d5a27,
    layers: [{ name: 'collision', width: 25, height: 19, data: [] }],
    portals: [
      { id: 'to_paris', x: 12, y: 18, targetMap: 'paris', targetX: 12, targetY: 2, radius: 30 },
    ],
    NPCs: ['npc_forest_healer'],
  },
  desert: {
    id: 'desert',
    name: '沙漠地区',
    width: 25,
    height: 19,
    tileSize: 32,
    groundColor: 0xc2b280,
    layers: [{ name: 'collision', width: 25, height: 19, data: [] }],
    portals: [
      { id: 'to_paris', x: 12, y: 18, targetMap: 'paris', targetX: 12, targetY: 34, radius: 30 },
    ],
    NPCs: ['npc_desert_trader'],
  },
  snow: {
    id: 'snow',
    name: '雪拉伊雪原',
    width: 25,
    height: 19,
    tileSize: 32,
    groundColor: 0xe8f4f8,
    layers: [{ name: 'collision', width: 25, height: 19, data: [] }],
    portals: [
      { id: 'to_paris', x: 12, y: 18, targetMap: 'paris', targetX: 34, targetY: 12, radius: 30 },
    ],
  },
  volcano: {
    id: 'volcano',
    name: '火山地区',
    width: 25,
    height: 19,
    tileSize: 32,
    groundColor: 0x8b2500,
    layers: [{ name: 'collision', width: 25, height: 19, data: [] }],
    portals: [
      { id: 'to_paris', x: 12, y: 18, targetMap: 'paris', targetX: 2, targetY: 12, radius: 30 },
    ],
  },
  dungeon: {
    id: 'dungeon',
    name: '地下城',
    width: 25,
    height: 19,
    tileSize: 32,
    groundColor: 0x1a1a2e,
    layers: [{ name: 'collision', width: 25, height: 19, data: [] }],
    portals: [
      { id: 'to_volcano', x: 12, y: 18, targetMap: 'volcano', targetX: 12, targetY: 2, radius: 30 },
    ],
  },
};
```

- [ ] **Step 2: 提交**

```bash
git add -A && git commit -m "feat: 添加5张野外地图数据"
```

---

## Task 2: 法兰城地图

**Files:**
- Modify: `src/data/map-data.ts`
- Create: `src/data/paris-buildings.ts`

### Step 1: 创建法兰城建筑数据

创建 `src/data/paris-buildings.ts`：

```typescript
import { Building } from './map-data';

export const PARIS_BUILDINGS: Building[] = [
  // 医院
  {
    id: 'hospital',
    name: '医院',
    x: 8,
    y: 6,
    width: 4,
    height: 3,
    color: 0xff6666,
    targetMap: 'hospital_interior',
    targetX: 3,
    targetY: 3,
  },
  // 银行
  {
    id: 'bank',
    name: '银行',
    x: 14,
    y: 6,
    width: 4,
    height: 3,
    color: 0xdddd66,
  },
  // 武器店
  {
    id: 'weapon_shop',
    name: '武器店',
    x: 4,
    y: 14,
    width: 3,
    height: 3,
    color: 0x6666ff,
    targetMap: 'weapon_shop_interior',
    targetX: 3,
    targetY: 3,
  },
  // 魔法店
  {
    id: 'magic_shop',
    name: '魔法店',
    x: 8,
    y: 14,
    width: 3,
    height: 3,
    color: 0x9966ff,
  },
  // 旅馆
  {
    id: 'inn',
    name: '旅馆',
    x: 18,
    y: 14,
    width: 3,
    height: 3,
    color: 0x66ff66,
  },
  // 职业工会
  {
    id: 'guild',
    name: '职业工会',
    x: 20,
    y: 8,
    width: 4,
    height: 4,
    color: 0xff66ff,
  },
  // 宠物店
  {
    id: 'pet_shop',
    name: '宠物店',
    x: 12,
    y: 20,
    width: 3,
    height: 3,
    color: 0x66ffff,
  },
];

export const PARIS_PORTALS = [
  // 城门 - 通往城东森林
  { id: 'paris_to_east', x: 12, y: 1, targetMap: 'forest', targetX: 12, targetY: 17, radius: 25 },
  // 通往沙漠
  { id: 'paris_to_desert', x: 12, y: 35, targetMap: 'desert', targetX: 12, targetY: 1, radius: 25 },
  // 通往雪原
  { id: 'paris_to_snow', x: 35, y: 12, targetMap: 'snow', targetX: 1, targetY: 12, radius: 25 },
  // 通往火山
  { id: 'paris_to_volcano', x: 1, y: 12, targetMap: 'volcano', targetX: 17, targetY: 12, radius: 25 },
];
```

### Step 2: 添加法兰城主城数据

修改 `src/data/map-data.ts` 添加法兰城：

```typescript
// 法兰城主城 - 36x36 大地图
export const PARIS_MAP: MapData = {
  id: 'paris',
  name: '法兰城',
  width: 36,
  height: 36,
  tileSize: 32,
  groundColor: 0x8b7355, // 泥土色
  layers: [{ name: 'collision', width: 36, height: 36, data: [] }],
  portals: PARIS_PORTALS,
  NPCs: ['npc_paris_guard', 'npc_paris_guide', 'npc_paris_merchant'],
};
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 添加法兰城地图数据"
```

---

## Task 3: 扩展怪物数据

**Files:**
- Modify: `src/data/battle-data.ts`

### Step 1: 添加新怪物

修改 `src/data/battle-data.ts`：

```typescript
// 怪物稀有度
export type MonsterGrade = 'normal' | 'elite' | 'boss';

// 扩展 BattleEntityData 添加稀有度
export interface MonsterData extends BattleEntityData {
  grade: MonsterGrade;
  exp: number;
  gold: number;
  skills: string[];
}

// 所有怪物
export const MONSTERS: Record<string, MonsterData> = {
  // === 森林怪物 ===
  slime_green: {
    id: 'slime_green',
    name: '绿色史莱姆',
    level: 1,
    element: 'water',
    grade: 'normal',
    exp: 10,
    gold: 5,
    stats: { maxHp: 25, maxMp: 0, attack: 8, defense: 4, agility: 6 },
    skills: ['skill_attack'],
  },
  goblin: {
    id: 'goblin',
    name: '哥布林',
    level: 2,
    element: 'earth',
    grade: 'normal',
    exp: 20,
    gold: 10,
    stats: { maxHp: 45, maxMp: 5, attack: 14, defense: 7, agility: 10 },
    skills: ['skill_attack'],
  },
  bat: {
    id: 'bat',
    name: '蝙蝠',
    level: 3,
    element: 'wind',
    grade: 'normal',
    exp: 25,
    gold: 8,
    stats: { maxHp: 35, maxMp: 10, attack: 16, defense: 5, agility: 18 },
    skills: ['skill_attack'],
  },
  wolf: {
    id: 'wolf',
    name: '野狼',
    level: 4,
    element: 'neutral',
    grade: 'normal',
    exp: 35,
    gold: 15,
    stats: { maxHp: 60, maxMp: 0, attack: 22, defense: 10, agility: 14 },
    skills: ['skill_attack', 'skill_bite'],
  },

  // === 沙漠怪物 ===
  scorpion: {
    id: 'scorpion',
    name: '毒蝎',
    level: 5,
    element: 'earth',
    grade: 'normal',
    exp: 40,
    gold: 18,
    stats: { maxHp: 70, maxMp: 0, attack: 28, defense: 12, agility: 12 },
    skills: ['skill_attack', 'skill_poison'],
  },
  sand_worm: {
    id: 'sand_worm',
    name: '沙虫',
    level: 6,
    element: 'earth',
    grade: 'normal',
    exp: 50,
    gold: 25,
    stats: { maxHp: 90, maxMp: 20, attack: 30, defense: 15, agility: 8 },
    skills: ['skill_attack', 'skill_sandstorm'],
  },
  mantis: {
    id: 'mantis',
    name: '螳螂',
    level: 7,
    element: 'wind',
    grade: 'normal',
    exp: 55,
    gold: 22,
    stats: { maxHp: 65, maxMp: 15, attack: 35, defense: 8, agility: 20 },
    skills: ['skill_attack', 'skill_double_shot'],
  },

  // === 雪原怪物 ===
  ice_blob: {
    id: 'ice_blob',
    name: '冰精灵',
    level: 8,
    element: 'water',
    grade: 'normal',
    exp: 60,
    gold: 30,
    stats: { maxHp: 80, maxMp: 40, attack: 25, defense: 18, agility: 14 },
    skills: ['skill_attack', 'skill_ice_arrow'],
  },
  snowman: {
    id: 'snowman',
    name: '雪人',
    level: 9,
    element: 'water',
    grade: 'normal',
    exp: 70,
    gold: 35,
    stats: { maxHp: 120, maxMp: 30, attack: 32, defense: 25, agility: 10 },
    skills: ['skill_attack', 'skill_freeze'],
  },

  // === 火山怪物 ===
  fire_spirit: {
    id: 'fire_spirit',
    name: '火精灵',
    level: 10,
    element: 'fire',
    grade: 'normal',
    exp: 80,
    gold: 40,
    stats: { maxHp: 75, maxMp: 50, attack: 38, defense: 12, agility: 18 },
    skills: ['skill_attack', 'skill_fireball'],
  },
  lava_golem: {
    id: 'lava_golem',
    name: '岩浆巨人',
    level: 12,
    element: 'fire',
    grade: 'normal',
    exp: 100,
    gold: 50,
    stats: { maxHp: 180, maxMp: 20, attack: 42, defense: 35, agility: 5 },
    skills: ['skill_attack', 'skill_heavy_strike'],
  },

  // === 精英怪物 ===
  goblin_chief: {
    id: 'goblin_chief',
    name: '哥布林首领',
    level: 5,
    element: 'earth',
    grade: 'elite',
    exp: 150,
    gold: 100,
    stats: { maxHp: 200, maxMp: 30, attack: 40, defense: 25, agility: 15 },
    skills: ['skill_attack', 'skill_power_up', 'skill_charge'],
  },
  ancient_dragon: {
    id: 'ancient_dragon',
    name: '古代巨龙',
    level: 20,
    element: 'fire',
    grade: 'boss',
    exp: 500,
    gold: 300,
    stats: { maxHp: 500, maxMp: 100, attack: 80, defense: 50, agility: 25 },
    skills: ['skill_attack', 'skill_fireball', 'skill_power_up', 'skill_heavy_strike'],
  },
};

// 地图怪物配置
export const MAP_MONSTERS: Record<string, string[]> = {
  forest: ['slime_green', 'goblin', 'bat', 'wolf'],
  desert: ['scorpion', 'sand_worm', 'mantis'],
  snow: ['ice_blob', 'snowman', 'bat'],
  volcano: ['fire_spirit', 'lava_golem', 'wolf'],
  dungeon: ['goblin_chief', 'lava_golem', 'ancient_dragon'],
};
```

### Step 2: 添加新技能

修改 `src/data/skills.ts` 添加新技能：

```typescript
{
  id: 'skill_bite',
  name: '撕咬',
  type: 'attack',
  mpCost: 0,
  power: 120,
  target: 'single',
  description: '野兽撕咬攻击',
},
{
  id: 'skill_poison',
  name: '中毒',
  type: 'attack',
  mpCost: 10,
  power: 80,
  target: 'single',
  element: 'earth',
  description: '造成中毒伤害',
},
{
  id: 'skill_sandstorm',
  name: '沙尘暴',
  type: 'attack',
  mpCost: 15,
  power: 100,
  target: 'all',
  element: 'earth',
  description: '全体土属性攻击',
},
{
  id: 'skill_freeze',
  name: '冰冻',
  type: 'attack',
  mpCost: 20,
  power: 130,
  target: 'single',
  element: 'water',
  description: '水属性攻击并减速',
},
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 添加14种新怪物和新技能"
```

---

## Task 4: MapScene 升级

**Files:**
- Modify: `src/scenes/MapScene.ts`

### Step 1: 升级 MapScene 支持多地图

重写 `src/scenes/MapScene.ts`：

```typescript
import Phaser from 'phaser';
import { GAME_CONFIG } from '../config/game-config';
import { Player } from '../entities/Player';
import { NPC, NPCData } from '../entities/NPC';
import { CollisionSystem } from '../systems/CollisionSystem';
import { MapTransitionSystem, MapTransition } from '../systems/MapTransition';
import { BattleScene } from './BattleScene';
import { ShopScene } from './ShopScene';
import { PetUIScene } from './PetUIScene';
import { QuestScene } from './QuestScene';
import { InventoryScene } from './InventoryScene';
import { FieldMap } from '../systems/FieldMap';
import { PARIS_MAP, PARIS_BUILDINGS, PARIS_PORTALS, MapData } from '../data/map-data';

export class MapScene extends Phaser.Scene {
  private player!: Player;
  private npcs: NPC[] = [];
  private collisionSystem!: CollisionSystem;
  private mapTransition!: MapTransitionSystem;
  private currentMapId: string = 'paris';
  private fieldMap!: FieldMap;

  constructor() {
    super({ key: 'MapScene' });
  }

  init(data: { mapId?: string; spawnX?: number; spawnY?: number }): void {
    if (data.mapId) {
      this.currentMapId = data.mapId;
    }
  }

  create(): void {
    this.collisionSystem = new CollisionSystem();
    this.mapTransition = new MapTransitionSystem();
    this.mapTransition.setCurrentMap(this.currentMapId);

    const mapData = this.getMapData(this.currentMapId);
    this.fieldMap = new FieldMap(this, mapData);
    this.fieldMap.render();

    const spawnX = GAME_CONFIG.width / 2;
    const spawnY = GAME_CONFIG.height / 2;
    this.player = new Player(this, spawnX, spawnY, 'player');
    this.player.setCollisionSystem(this.collisionSystem);

    this.loadNPCs(mapData);

    this.scene.launch('UIScene');

    this.setupEventListeners();
  }

  private getMapData(mapId: string): MapData {
    // 根据 mapId 返回对应地图数据
    switch (mapId) {
      case 'paris':
        return PARIS_MAP;
      default:
        return PARIS_MAP;
    }
  }

  private loadNPCs(mapData: MapData): void {
    if (mapData.NPCs) {
      mapData.NPCs.forEach(npcId => {
        const npcData = this.getNPCData(npcId);
        if (npcData) {
          const npc = new NPC(this, npcData);
          this.npcs.push(npc);
        }
      });
    }
  }

  private getNPCData(npcId: string): NPCData | null {
    const npcs: Record<string, NPCData> = {
      npc_paris_guard: {
        id: 'npc_paris_guard',
        name: '城门卫兵',
        x: 200,
        y: 100,
        sprite: 'npc',
        defaultDialog: 'guard',
        dialogs: {
          guard: {
            text: '欢迎来到法兰城！',
            choices: [
              { text: '谢谢', next: 'bye' },
            ],
          },
          bye: { text: '祝您旅途愉快！' },
        },
      },
      npc_paris_guide: {
        id: 'npc_paris_guide',
        name: '导览员',
        x: 400,
        y: 200,
        sprite: 'npc',
        defaultDialog: 'guide',
        dialogs: {
          guide: {
            text: '法兰城是冒险者的起点！城里有很多设施：医院、银行、商店等。',
            choices: [
              { text: '知道了', next: 'bye' },
            ],
          },
          bye: { text: '再见！' },
        },
      },
    };
    return npcs[npcId] || null;
  }

  private setupEventListeners(): void {
    this.game.events.on('dialog-action', (action: string) => {
      if (action.startsWith('shop:')) {
        const shopId = action.substring(5);
        this.scene.start('ShopScene', { shopId });
      }
    });

    // 菜单按钮
    const menuBtn = this.add.text(700, 560, '[ 菜单 ]', {
      fontSize: '16px',
      color: '#ffffff',
    }).setInteractive();
    menuBtn.on('pointerdown', () => this.scene.start('MenuScene'));
  }

  update(): void {
    this.player.update();

    // 检查传送门
    const pos = this.player.getPosition();
    const portal = this.fieldMap.checkPortal(pos.x, pos.y);
    if (portal) {
      this.scene.start('MapScene', {
        mapId: portal.targetMap,
        spawnX: portal.targetX * GAME_CONFIG.tileSize,
        spawnY: portal.targetY * GAME_CONFIG.tileSize,
      });
    }

    // 检查建筑物入口
    const building = this.fieldMap.checkBuilding(pos.x, pos.y);
    if (building && building.targetMap) {
      this.scene.start(building.targetMap);
    }
  }
}
```

### Step 2: 创建 FieldMap 系统

创建 `src/systems/FieldMap.ts`：

```typescript
import Phaser from 'phaser';
import { GAME_CONFIG } from '../config/game-config';
import { MapData, Building, Portal, PARIS_BUILDINGS, PARIS_PORTALS } from '../data/map-data';

export class FieldMap {
  private scene: Phaser.Scene;
  private mapData: MapData;
  private graphics!: Phaser.GameObjects.Graphics;
  private buildingGraphics: Phaser.GameObjects.Graphics[] = [];
  private portalGraphics: Phaser.GameObjects.Graphics[] = [];
  private portals: Portal[] = [];
  private buildings: Building[] = [];

  constructor(scene: Phaser.Scene, mapData: MapData) {
    this.scene = scene;
    this.mapData = mapData;
  }

  render(): void {
    // 绘制地面
    this.graphics = this.scene.add.graphics();
    this.graphics.fillStyle(this.mapData.groundColor || 0x4a7c4e);
    this.graphics.fillRect(0, 0, GAME_CONFIG.width, GAME_CONFIG.height);

    // 绘制网格
    this.graphics.lineStyle(1, 0x000000, 0.2);
    for (let x = 0; x <= GAME_CONFIG.width; x += GAME_CONFIG.tileSize) {
      this.graphics.moveTo(x, 0);
      this.graphics.lineTo(x, GAME_CONFIG.height);
    }
    for (let y = 0; y <= GAME_CONFIG.height; y += GAME_CONFIG.tileSize) {
      this.graphics.moveTo(0, y);
      this.graphics.lineTo(GAME_CONFIG.width, y);
    }
    this.graphics.strokePath();

    // 绘制装饰
    this.renderDecorations();

    // 加载传送门
    this.portals = this.getPortals();
    this.portals.forEach(p => this.renderPortal(p));

    // 加载建筑物
    this.buildings = this.getBuildings();
    this.buildings.forEach(b => this.renderBuilding(b));
  }

  private renderDecorations(): void {
    const seed = this.hashCode(this.mapData.id);
    const rand = this.seededRandom(seed);

    // 根据地图类型绘制不同装饰
    for (let i = 0; i < 20; i++) {
      const x = Math.floor(rand() * GAME_CONFIG.width);
      const y = Math.floor(rand() * GAME_CONFIG.height);
      const size = 4 + Math.floor(rand() * 8);

      let color = 0x228b22; // 默认绿色
      if (this.mapData.id === 'desert') color = 0xd4a574;
      if (this.mapData.id === 'snow') color = 0xffffff;
      if (this.mapData.id === 'volcano') color = 0xff4500;

      this.graphics.fillStyle(color, 0.5);
      this.graphics.fillCircle(x, y, size);
    }
  }

  private renderPortal(portal: Portal): void {
    const g = this.scene.add.graphics();
    const x = portal.x * GAME_CONFIG.tileSize;
    const y = portal.y * GAME_CONFIG.tileSize;

    g.fillStyle(0x8844ff, 0.8);
    g.fillCircle(x, y, portal.radius || 20);
    g.lineStyle(2, 0xffffff, 0.8);
    g.strokeCircle(x, y, portal.radius || 20);

    // 传送门动画
    this.scene.tweens.add({
      targets: g,
      alpha: 0.5,
      duration: 500,
      yoyo: true,
      repeat: -1,
    });

    this.portalGraphics.push(g);
  }

  private renderBuilding(building: Building): void {
    const g = this.scene.add.graphics();
    const x = building.x * GAME_CONFIG.tileSize;
    const y = building.y * GAME_CONFIG.tileSize;
    const w = building.width * GAME_CONFIG.tileSize;
    const h = building.height * GAME_CONFIG.tileSize;

    // 建筑主体
    g.fillStyle(building.color, 0.9);
    g.fillRect(x, y, w, h);

    // 边框
    g.lineStyle(2, 0xffffff, 0.5);
    g.strokeRect(x, y, w, h);

    // 屋顶
    g.fillStyle(0x8b4513, 0.8);
    g.fillTriangle(x, y, x + w / 2, y - 15, x + w, y);

    // 门
    g.fillStyle(0x4a3728);
    g.fillRect(x + w / 2 - 8, y + h - 20, 16, 20);

    // 标签
    this.scene.add.text(x + w / 2, y + h / 2, building.name, {
      fontSize: '10px',
      color: '#ffffff',
    }).setOrigin(0.5);

    this.buildingGraphics.push(g);
  }

  private getPortals(): Portal[] {
    switch (this.mapData.id) {
      case 'paris':
        return PARIS_PORTALS;
      default:
        return [];
    }
  }

  private getBuildings(): Building[] {
    switch (this.mapData.id) {
      case 'paris':
        return PARIS_BUILDINGS;
      default:
        return [];
    }
  }

  checkPortal(x: number, y: number): Portal | null {
    for (const portal of this.portals) {
      const px = portal.x * GAME_CONFIG.tileSize;
      const py = portal.y * GAME_CONFIG.tileSize;
      const dist = Math.sqrt((x - px) ** 2 + (y - py) ** 2);
      if (dist < (portal.radius || 20)) {
        return portal;
      }
    }
    return null;
  }

  checkBuilding(x: number, y: number): Building | null {
    for (const building of this.buildings) {
      const bx = building.x * GAME_CONFIG.tileSize;
      const by = building.y * GAME_CONFIG.tileSize;
      const bw = building.width * GAME_CONFIG.tileSize;
      const bh = building.height * GAME_CONFIG.tileSize;

      if (x >= bx && x <= bx + bw && y >= by && y <= by + bh) {
        return building;
      }
    }
    return null;
  }

  private hashCode(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash);
  }

  private seededRandom(seed: number): () => number {
    let s = seed;
    return () => {
      s = Math.sin(s) * 10000;
      return s - Math.floor(s);
    };
  }
}
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 升级MapScene支持多地图和法兰城"
```

---

## Task 5: 室内场景

**Files:**
- Create: `src/scenes/HospitalScene.ts`
- Create: `src/scenes/WeaponShopScene.ts`

### Step 1: 创建医院场景

创建 `src/scenes/HospitalScene.ts`：

```typescript
import Phaser from 'phaser';
import { InventorySystem } from '../systems/InventorySystem';

export class HospitalScene extends Phaser.Scene {
  private inventory!: InventorySystem;

  constructor() {
    super({ key: 'HospitalScene' });
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x2a2a3a);
    this.inventory = new InventorySystem();

    this.add.text(400, 40, '法兰城医院', {
      fontSize: '28px',
      color: '#ff6666',
    }).setOrigin(0.5);

    this.add.text(400, 80, '在这里可以恢复 HP 和 MP', {
      fontSize: '14px',
      color: '#aaaaaa',
    }).setOrigin(0.5);

    const healBtn = this.add.text(400, 200, '[ 恢复全部 ]', {
      fontSize: '24px',
      color: '#00ff00',
    }).setOrigin(0.5).setInteractive();

    healBtn.on('pointerdown', () => {
      // 恢复逻辑
      this.showMessage('HP 和 MP 已完全恢复！');
    });

    const backBtn = this.add.text(20, 20, '[ 返回 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setInteractive();
    backBtn.on('pointerdown', () => this.scene.start('MapScene', { mapId: 'paris' }));
  }

  private showMessage(text: string): void {
    const msg = this.add.text(400, 400, text, {
      fontSize: '18px',
      color: '#ffffff',
    }).setOrigin(0.5);
    this.time.delayedCall(1500, () => msg.destroy());
  }
}
```

### Step 2: 创建武器店场景

创建 `src/scenes/WeaponShopScene.ts`：

```typescript
import Phaser from 'phaser';
import { ShopSystem } from '../systems/ShopSystem';
import { InventorySystem } from '../systems/InventorySystem';

export class WeaponShopScene extends Phaser.Scene {
  private shopSystem!: ShopSystem;
  private inventory!: InventorySystem;

  constructor() {
    super({ key: 'WeaponShopScene' });
  }

  init(): void {
    this.inventory = new InventorySystem();
    this.shopSystem = new ShopSystem(this.inventory);
    this.shopSystem.openShop('weapon_shop');
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x1a1a2e);

    this.add.text(400, 30, '武器店', {
      fontSize: '24px',
      color: '#6666ff',
    }).setOrigin(0.5);

    const backBtn = this.add.text(20, 20, '[ 返回 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setInteractive();
    backBtn.on('pointerdown', () => this.scene.start('MapScene', { mapId: 'paris' }));

    this.add.text(400, 80, '武器店装修中...', {
      fontSize: '16px',
      color: '#ffffff',
    }).setOrigin(0.5);
  }
}
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 添加医院和武器店室内场景"
```

---

## Task 6: 随机遇敌系统

**Files:**
- Modify: `src/scenes/MapScene.ts`
- Create: `src/systems/EncounterSystem.ts`

### Step 1: 创建遭遇系统

创建 `src/systems/EncounterSystem.ts`：

```typescript
import { MONSTERS, MAP_MONSTERS, MonsterData } from '../data/battle-data';

export class EncounterSystem {
  private encounterRate: number = 0.02; // 每次移动遇敌概率
  private lastEncounterTime: number = 0;
  private minEncounterInterval: number = 3000; // 最小遇敌间隔(ms)

  checkEncounter(mapId: string, isMoving: boolean): MonsterData[] | null {
    if (!isMoving) return null;

    const now = Date.now();
    if (now - this.lastEncounterTime < this.minEncounterInterval) {
      return null;
    }

    const monsters = MAP_MONSTERS[mapId];
    if (!monsters || monsters.length === 0) return null;

    // 随机遇敌
    if (Math.random() < this.encounterRate) {
      this.lastEncounterTime = now;
      return this.rollEncounter(mapId);
    }

    return null;
  }

  private rollEncounter(mapId: string): MonsterData[] {
    const monsterIds = MAP_MONSTERS[mapId];
    const count = Math.random() < 0.3 ? 2 : 1; // 30% 几率遇2只
    const encounter: MonsterData[] = [];

    for (let i = 0; i < count; i++) {
      const monsterId = monsterIds[Math.floor(Math.random() * monsterIds.length)];
      const monster = MONSTERS[monsterId];
      if (monster) {
        encounter.push({ ...monster });
      }
    }

    return encounter;
  }

  setEncounterRate(rate: number): void {
    this.encounterRate = rate;
  }
}
```

### Step 2: 修改 MapScene 集成遭遇系统

在 MapScene 中：

```typescript
// 在 MapScene 中添加
private encounterSystem!: EncounterSystem;

// 在 create() 中
this.encounterSystem = new EncounterSystem();

// 在 update() 中
const isMoving = this.player.isMoving();
const encounter = this.encounterSystem.checkEncounter(this.currentMapId, isMoving);
if (encounter && encounter.length > 0) {
  this.scene.start('BattleScene', { enemies: encounter });
}
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 添加随机遇敌系统"
```

---

## Task 7: 菜单集成

**Files:**
- Modify: `src/scenes/MenuScene.ts`

### Step 1: 更新菜单场景

修改 `src/scenes/MenuScene.ts`：

```typescript
// 添加更多菜单按钮
const mapBtn = this.add.text(400, 280, '[ 世界地图 ]', {
  fontSize: '20px',
  color: '#ffaa00',
}).setOrigin(0.5).setInteractive();

mapBtn.on('pointerdown', () => {
  this.scene.start('MapScene', { mapId: 'paris' });
});
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 更新主菜单"
```

---

## 验收标准

- [ ] 5 张野外地图可切换（森林、沙漠、雪原、火山、地城）
- [ ] 法兰城主城完整（建筑、传送门、NPC）
- [ ] 14 种新怪物可遭遇
- [ ] 随机遇敌系统工作
- [ ] 医院可恢复 HP/MP
- [ ] 建筑入口可进入室内
- [ ] 传送门网络连接各区域

---

## 执行方式

**Subagent-Driven** - 每个 Task 分派独立子代理
