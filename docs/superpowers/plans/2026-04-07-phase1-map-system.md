# Phase 1: 地图探索系统 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现地图渲染引擎，支持加载原版地图资源，人物可自由移动，NPC 对话系统可用

**Architecture:** 基于 Phaser 3 的 Tilemap 系统，原版资源通过解析后的 JSON 配置加载，地图切换通过 Scene 跳转实现

**Tech Stack:** Phaser 3.60+, TypeScript 5.x, 原版地图数据

---

## 文件结构

```
src/
├── main.ts                      # 游戏入口
├── config/
│   └── game-config.ts           # 游戏配置
├── data/
│   └── map-data.ts             # 地图配置数据
├── entities/
│   ├── Player.ts               # 玩家角色
│   └── NPC.ts                  # NPC 实体
├── systems/
│   ├── MapEngine.ts            # 地图引擎核心
│   ├── CollisionSystem.ts      # 碰撞检测
│   └── DialogSystem.ts         # 对话系统
└── scenes/
    ├── BootScene.ts            # 启动场景（加载资源）
    ├── LoadingScene.ts          # 加载过渡
    ├── MenuScene.ts             # 主菜单
    ├── MapScene.ts              # 地图主场景
    └── UIScene.ts               # UI 场景（对话框等）

resources/                       # 原版资源链接
└── crossgate602 -> ~/Downloads/crossgate602/
```

---

## Task 1: 项目初始化

**Files:**
- Create: `package.json`
- Create: `tsconfig.json`
- Create: `index.html`
- Create: `src/main.ts`
- Create: `src/config/game-config.ts`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "magic-bubble-h5",
  "version": "1.0.0",
  "description": "魔力宝贝 H5 还原版",
  "main": "dist/main.js",
  "scripts": {
    "dev": "parcel index.html",
    "build": "tsc && parcel build index.html",
    "start": "parcel index.html --open"
  },
  "devDependencies": {
    "parcel": "^2.11.0",
    "typescript": "^5.3.0"
  },
  "dependencies": {
    "phaser": "^3.70.0"
  }
}
```

- [ ] **Step 2: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true
  },
  "include": ["src/**/*"]
}
```

- [ ] **Step 3: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>魔力宝贝 H5</title>
  <style>
    body { margin: 0; padding: 0; background: #000; }
    #game-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; }
  </style>
</head>
<body>
  <div id="game-container"></div>
  <script type="module" src="./src/main.ts"></script>
</body>
</html>
```

- [ ] **Step 4: 创建 src/config/game-config.ts**

```typescript
export const GAME_CONFIG = {
  width: 816,
  height: 624,
  tileSize: 32,
  scale: 1,
  audioPath: 'resources/crossgate_assets/',
  mapPath: 'resources/crossgate602/map/',
};
```

- [ ] **Step 5: 创建 src/main.ts**

```typescript
import Phaser from 'phaser';
import { GAME_CONFIG } from './config/game-config';
import { BootScene } from './scenes/BootScene';
import { LoadingScene } from './scenes/LoadingScene';
import { MenuScene } from './scenes/MenuScene';
import { MapScene } from './scenes/MapScene';
import { UIScene } from './scenes/UIScene';

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: GAME_CONFIG.width,
  height: GAME_CONFIG.height,
  parent: 'game-container',
  pixelArt: true,
  scene: [BootScene, LoadingScene, MenuScene, MapScene, UIScene],
};

new Phaser.Game(config);
```

- [ ] **Step 6: 提交代码**

```bash
cd ~/magic-bubble-h5 && git init && git add -A && git commit -m "feat: 项目初始化，Phaser 3 + TypeScript"
```

---

## Task 2: 基础场景创建

**Files:**
- Create: `src/scenes/BootScene.ts`
- Create: `src/scenes/LoadingScene.ts`
- Create: `src/scenes/MenuScene.ts`
- Create: `src/scenes/MapScene.ts`
- Create: `src/scenes/UIScene.ts`

- [ ] **Step 1: 创建 BootScene.ts**

```typescript
import Phaser from 'phaser';

export class BootScene extends Phaser.Scene {
  constructor() {
    super({ key: 'BootScene' });
  }

  preload(): void {
    // 创建加载进度条
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    const progressBar = this.add.graphics();
    const progressBox = this.add.graphics();
    progressBox.fillStyle(0x222222, 0.8);
    progressBox.fillRect(width / 2 - 160, height / 2 - 25, 320, 50);

    const loadingText = this.add.text(width / 2, height / 2 - 50, '加载中...', {
      fontSize: '20px',
      color: '#ffffff',
    });
    loadingText.setOrigin(0.5, 0.5);

    this.load.on('progress', (value: number) => {
      progressBar.clear();
      progressBar.fillStyle(0xffffff, 1);
      progressBar.fillRect(width / 2 - 150, height / 2 - 15, 300 * value, 30);
    });
  }

  create(): void {
    this.scene.start('LoadingScene');
  }
}
```

- [ ] **Step 2: 创建 LoadingScene.ts**

```typescript
import Phaser from 'phaser';
import { GAME_CONFIG } from '../config/game-config';

export class LoadingScene extends Phaser.Scene {
  constructor() {
    super({ key: 'LoadingScene' });
  }

  preload(): void {
    // 加载原版资源
    // 这里先加载占位图，正式开发时替换为解析后的原版资源
    this.load.image('player', 'https://labs.phaser.io/assets/sprites/phaser-dude.png');
  }

  create(): void {
    this.scene.start('MenuScene');
  }
}
```

- [ ] **Step 3: 创建 MenuScene.ts**

```typescript
import Phaser from 'phaser';

export class MenuScene extends Phaser.Scene {
  constructor() {
    super({ key: 'MenuScene' });
  }

  create(): void {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // 标题
    this.add.text(width / 2, height / 3, '魔力宝贝 H5', {
      fontSize: '48px',
      color: '#ffcc00',
      fontStyle: 'bold',
    }).setOrigin(0.5);

    // 开始按钮
    const startBtn = this.add.text(width / 2, height / 2, '[ 开始游戏 ]', {
      fontSize: '24px',
      color: '#ffffff',
    }).setOrigin(0.5).setInteractive();

    startBtn.on('pointerover', () => startBtn.setColor('#ffff00'));
    startBtn.on('pointerout', () => startBtn.setColor('#ffffff'));
    startBtn.on('pointerdown', () => {
      this.scene.start('MapScene');
    });

    // 背景色
    this.cameras.main.setBackgroundColor(0x1a1a2e);
  }
}
```

- [ ] **Step 4: 创建 MapScene.ts**

```typescript
import Phaser from 'phaser';
import { GAME_CONFIG } from '../config/game-config';

export class MapScene extends Phaser.Scene {
  private player!: Phaser.GameObjects.Sprite;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private wasd!: { W: Phaser.Input.Keyboard.Key; A: Phaser.Input.Keyboard.Key; S: Phaser.Input.Keyboard.Key; D: Phaser.Input.Keyboard.Key };

  constructor() {
    super({ key: 'MapScene' });
  }

  create(): void {
    // 创建测试地图（16x12 格子）
    const graphics = this.add.graphics();

    // 绘制地面（草地）
    graphics.fillStyle(0x4a7c4e);
    graphics.fillRect(0, 0, GAME_CONFIG.width, GAME_CONFIG.height);

    // 绘制边界
    graphics.lineStyle(2, 0x000000);
    for (let x = 0; x <= GAME_CONFIG.width; x += GAME_CONFIG.tileSize) {
      graphics.moveTo(x, 0);
      graphics.lineTo(x, GAME_CONFIG.height);
    }
    for (let y = 0; y <= GAME_CONFIG.height; y += GAME_CONFIG.tileSize) {
      graphics.moveTo(0, y);
      graphics.lineTo(GAME_CONFIG.width, y);
    }
    graphics.strokePath();

    // 创建玩家
    this.player = this.add.sprite(
      GAME_CONFIG.width / 2,
      GAME_CONFIG.height / 2,
      'player'
    );
    this.player.setOrigin(0.5);

    // 设置键盘输入
    this.cursors = this.input.keyboard!.createCursorKeys();
    this.wasd = {
      W: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      A: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      S: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      D: this.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    };

    // 启动 UI 场景
    this.scene.launch('UIScene');
  }

  update(): void {
    const speed = 4;
    let dx = 0;
    let dy = 0;

    if (this.cursors.left.isDown || this.wasd.A.isDown) dx = -speed;
    else if (this.cursors.right.isDown || this.wasd.D.isDown) dx = speed;

    if (this.cursors.up.isDown || this.wasd.W.isDown) dy = -speed;
    else if (this.cursors.down.isDown || this.wasd.S.isDown) dy = speed;

    // 边界检测
    const newX = this.player.x + dx;
    const newY = this.player.y + dy;

    if (newX > 16 && newX < GAME_CONFIG.width - 16) {
      this.player.x = newX;
    }
    if (newY > 16 && newY < GAME_CONFIG.height - 16) {
      this.player.y = newY;
    }
  }
}
```

- [ ] **Step 5: 创建 UIScene.ts**

```typescript
import Phaser from 'phaser';

export class UIScene extends Phaser.Scene {
  constructor() {
    super({ key: 'UIScene' });
  }

  create(): void {
    // UI 场景叠加在 MapScene 上
    // 用于显示对话框、背包等 UI 元素
  }
}
```

- [ ] **Step 6: 提交代码**

```bash
cd ~/magic-bubble-h5 && git add -A && git commit -m "feat: 创建基础场景框架"
```

---

## Task 3: 玩家角色实体

**Files:**
- Create: `src/entities/Player.ts`
- Modify: `src/scenes/MapScene.ts`

- [ ] **Step 1: 创建 src/entities/Player.ts**

```typescript
import Phaser from 'phaser';
import { GAME_CONFIG } from '../config/game-config';

export interface PlayerData {
  name: string;
  level: number;
  hp: number;
  maxHp: number;
  mp: number;
  maxMp: number;
  x: number;
  y: number;
}

export class Player extends Phaser.GameObjects.Container {
  public sprite!: Phaser.GameObjects.Sprite;
  public data: PlayerData;

  private moveSpeed = 4;
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private wasd!: { W: Phaser.Input.Keyboard.Key; A: Phaser.Input.Keyboard.Key; S: Phaser.Input.Keyboard.Key; D: Phaser.Input.Keyboard.Key };

  constructor(scene: Phaser.Scene, x: number, y: number, texture: string) {
    super(scene, x, y);
    this.data = {
      name: '冒险者',
      level: 1,
      hp: 100,
      maxHp: 100,
      mp: 50,
      maxMp: 50,
      x,
      y,
    };

    this.sprite = scene.add.sprite(0, 0, texture);
    this.sprite.setOrigin(0.5);
    this.add(this.sprite);

    scene.add.existing(this);

    this.setupInput();
  }

  private setupInput(): void {
    this.cursors = this.scene.input.keyboard!.createCursorKeys();
    this.wasd = {
      W: this.scene.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.W),
      A: this.scene.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.A),
      S: this.scene.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.S),
      D: this.scene.input.keyboard!.addKey(Phaser.Input.Keyboard.KeyCodes.D),
    };
  }

  update(): void {
    let dx = 0;
    let dy = 0;

    if (this.cursors.left.isDown || this.wasd.A.isDown) dx = -this.moveSpeed;
    else if (this.cursors.right.isDown || this.wasd.D.isDown) dx = this.moveSpeed;

    if (this.cursors.up.isDown || this.wasd.W.isDown) dy = -this.moveSpeed;
    else if (this.cursors.down.isDown || this.wasd.S.isDown) dy = this.moveSpeed;

    // 边界检测
    const newX = this.x + dx;
    const newY = this.y + dy;

    if (newX > 16 && newX < GAME_CONFIG.width - 16) {
      this.x = newX;
    }
    if (newY > 16 && newY < GAME_CONFIG.height - 16) {
      this.y = newY;
    }
  }

  getPosition(): { x: number; y: number } {
    return { x: this.x, y: this.y };
  }
}
```

- [ ] **Step 2: 修改 MapScene.ts 使用 Player 实体**

```typescript
import Phaser from 'phaser';
import { Player } from '../entities/Player';

export class MapScene extends Phaser.Scene {
  private player!: Player;

  create(): void {
    // ... 地图绘制代码保持不变 ...

    // 使用 Player 实体替代普通 sprite
    this.player = new Player(
      this,
      GAME_CONFIG.width / 2,
      GAME_CONFIG.height / 2,
      'player'
    );
  }

  update(): void {
    this.player.update();
  }
}
```

- [ ] **Step 3: 提交代码**

```bash
cd ~/magic-bubble-h5 && git add -A && git commit -m "feat: 创建 Player 实体类，支持键盘移动"
```

---

## Task 4: 碰撞检测系统

**Files:**
- Create: `src/systems/CollisionSystem.ts`
- Create: `src/data/map-data.ts`
- Modify: `src/scenes/MapScene.ts`

- [ ] **Step 1: 创建 src/data/map-data.ts**

```typescript
export interface TileLayer {
  name: string;
  width: number;
  height: number;
  data: number[][]; // 0 = 可通行, 1 = 障碍
}

export interface MapData {
  id: string;
  name: string;
  width: number;
  height: number;
  tileSize: number;
  layers: TileLayer[];
}

// 测试地图数据
export const TEST_MAP: MapData = {
  id: 'test_map',
  name: '测试地图',
  width: 25,
  height: 19,
  tileSize: 32,
  layers: [
    {
      name: 'collision',
      width: 25,
      height: 19,
      data: [], // 空数组表示全可通行
    },
  ],
};
```

- [ ] **Step 2: 创建 src/systems/CollisionSystem.ts**

```typescript
import { MapData } from '../data/map-data';
import { GAME_CONFIG } from '../config/game-config';

export class CollisionSystem {
  private mapData: MapData | null = null;
  private collisionLayer: boolean[][] = [];

  setMap(mapData: MapData): void {
    this.mapData = mapData;

    // 初始化碰撞层
    this.collisionLayer = [];
    for (let y = 0; y < mapData.height; y++) {
      this.collisionLayer[y] = [];
      for (let x = 0; x < mapData.width; x++) {
        // 默认全可通行
        this.collisionLayer[y][x] = false;
      }
    }

    // 解析碰撞数据
    if (mapData.layers.length > 0) {
      const collisionData = mapData.layers[0].data;
      if (collisionData.length > 0) {
        for (let y = 0; y < mapData.height; y++) {
          for (let x = 0; x < mapData.width; x++) {
            this.collisionLayer[y][x] = collisionData[y]?.[x] === 1;
          }
        }
      }
    }
  }

  canMoveTo(x: number, y: number): boolean {
    if (!this.mapData) return true;

    const tileX = Math.floor(x / GAME_CONFIG.tileSize);
    const tileY = Math.floor(y / GAME_CONFIG.tileSize);

    // 边界检测
    if (tileX < 0 || tileX >= this.mapData.width) return false;
    if (tileY < 0 || tileY >= this.mapData.height) return false;

    return !this.collisionLayer[tileY][tileX];
  }

  getMapData(): MapData | null {
    return this.mapData;
  }
}
```

- [ ] **Step 3: 修改 MapScene.ts 集成碰撞系统**

```typescript
import Phaser from 'phaser';
import { Player } from '../entities/Player';
import { CollisionSystem } from '../systems/CollisionSystem';
import { TEST_MAP } from '../data/map-data';
import { GAME_CONFIG } from '../config/game-config';

export class MapScene extends Phaser.Scene {
  private player!: Player;
  private collisionSystem!: CollisionSystem;

  create(): void {
    // 初始化碰撞系统
    this.collisionSystem = new CollisionSystem();
    this.collisionSystem.setMap(TEST_MAP);

    // ... 地图绘制代码 ...

    this.player = new Player(this, GAME_CONFIG.width / 2, GAME_CONFIG.height / 2, 'player');

    // 传递碰撞系统给 Player
    (this.player as any).collisionSystem = this.collisionSystem;
  }

  update(): void {
    this.player.update();
  }
}
```

- [ ] **Step 4: 修改 Player.ts 支持碰撞检测**

```typescript
import Phaser from 'phaser';
import { GAME_CONFIG } from '../config/game-config';
import { CollisionSystem } from '../systems/CollisionSystem';

export class Player extends Phaser.GameObjects.Container {
  // ... 现有代码 ...

  private collisionSystem: CollisionSystem | null = null;

  setCollisionSystem(cs: CollisionSystem): void {
    this.collisionSystem = cs;
  }

  update(): void {
    let dx = 0;
    let dy = 0;

    if (this.cursors.left.isDown || this.wasd.A.isDown) dx = -this.moveSpeed;
    else if (this.cursors.right.isDown || this.wasd.D.isDown) dx = this.moveSpeed;

    if (this.cursors.up.isDown || this.wasd.W.isDown) dy = -this.moveSpeed;
    else if (this.cursors.down.isDown || this.wasd.S.isDown) dy = this.moveSpeed;

    const newX = this.x + dx;
    const newY = this.y + dy;

    // 使用碰撞系统检测
    if (this.collisionSystem?.canMoveTo(newX, this.y) && newX > 16 && newX < GAME_CONFIG.width - 16) {
      this.x = newX;
    }
    if (this.collisionSystem?.canMoveTo(this.x, newY) && newY > 16 && newY < GAME_CONFIG.height - 16) {
      this.y = newY;
    }
  }
}
```

- [ ] **Step 5: 提交代码**

```bash
cd ~/magic-bubble-h5 && git add -A && git commit -m "feat: 添加碰撞检测系统"
```

---

## Task 5: NPC 实体与对话系统

**Files:**
- Create: `src/entities/NPC.ts`
- Create: `src/systems/DialogSystem.ts`
- Modify: `src/scenes/MapScene.ts`
- Modify: `src/scenes/UIScene.ts`

- [ ] **Step 1: 创建 src/entities/NPC.ts**

```typescript
import Phaser from 'phaser';

export interface DialogNode {
  text: string;
  next?: string;           // 下一节点 ID
  choices?: {              // 分支选项
    text: string;
    next: string;
  }[];
  action?: string;          // 触发动作
}

export interface NPCData {
  id: string;
  name: string;
  x: number;
  y: number;
  sprite: string;
  dialogs: Record<string, DialogNode>;
  defaultDialog: string;
}

export class NPC extends Phaser.GameObjects.Container {
  public data: NPCData;
  private sprite!: Phaser.GameObjects.Sprite;
  private indicator!: Phaser.GameObjects.Text;
  public dialogSystem: any;

  constructor(scene: Phaser.Scene, data: NPCData) {
    super(scene, data.x, data.y);
    this.data = data;

    // NPC 精灵（使用玩家贴图做占位）
    this.sprite = scene.add.sprite(0, -16, 'player');
    this.sprite.setScale(0.8);
    this.sprite.setTint(0xcccccc); // NPC 色调区分
    this.add(this.sprite);

    // 交互指示器
    this.indicator = scene.add.text(0, -40, '!', {
      fontSize: '16px',
      color: '#ffff00',
    });
    this.indicator.setOrigin(0.5);
    this.add(this.indicator);

    scene.add.existing(this);

    this.setupInteraction();
    this.startIndicatorAnimation();
  }

  private setupInteraction(): void {
    this.sprite.setInteractive();
    this.sprite.on('pointerdown', () => {
      this.scene.events.emit('npc-talk', this.data);
    });
  }

  private startIndicatorAnimation(): void {
    this.scene.tweens.add({
      targets: this.indicator,
      y: -35,
      duration: 500,
      yoyo: true,
      repeat: -1,
    });
  }
}
```

- [ ] **Step 2: 创建 src/systems/DialogSystem.ts**

```typescript
import { DialogNode, NPCData } from '../entities/NPC';

export class DialogSystem {
  private currentNPC: NPCData | null = null;
  private currentNodeId: string | null = null;
  private onDialogStart?: (npc: NPCData) => void;
  private onDialogEnd?: () => void;
  private onMessage?: (text: string, choices?: { text: string; next: string }[]) => void;

  setCallbacks(callbacks: {
    onStart?: (npc: NPCData) => void;
    onEnd?: () => void;
    onMessage?: (text: string, choices?: { text: string; next: string }[]) => void;
  }): void {
    this.onDialogStart = callbacks.onStart;
    this.onDialogEnd = callbacks.onEnd;
    this.onMessage = callbacks.onMessage;
  }

  startDialog(npc: NPCData): void {
    this.currentNPC = npc;
    this.currentNodeId = npc.defaultDialog;
    this.onDialogStart?.(npc);
    this.showCurrentNode();
  }

  selectChoice(choiceIndex: number): void {
    if (!this.currentNPC || !this.currentNodeId) return;

    const node = this.currentNPC.dialogs[this.currentNodeId];
    if (node?.choices && node.choices[choiceIndex]) {
      this.currentNodeId = node.choices[choiceIndex].next;
      this.showCurrentNode();
    }
  }

  next(): void {
    if (!this.currentNPC || !this.currentNodeId) return;

    const node = this.currentNPC.dialogs[this.currentNodeId];
    if (node?.next) {
      this.currentNodeId = node.next;
      this.showCurrentNode();
    } else {
      this.endDialog();
    }
  }

  private showCurrentNode(): void {
    if (!this.currentNPC || !this.currentNodeId) return;

    const node = this.currentNPC.dialogs[this.currentNodeId];
    if (node) {
      if (node.choices && node.choices.length > 0) {
        this.onMessage?.(node.text, node.choices);
      } else {
        this.onMessage?.(node.text);
      }
    }
  }

  endDialog(): void {
    this.currentNPC = null;
    this.currentNodeId = null;
    this.onDialogEnd?.();
  }

  isActive(): boolean {
    return this.currentNPC !== null;
  }
}
```

- [ ] **Step 3: 修改 UIScene.ts 添加对话框**

```typescript
import Phaser from 'phaser';
import { DialogSystem } from '../systems/DialogSystem';
import { NPCData } from '../entities/NPC';

export class UIScene extends Phaser.Scene {
  private dialogSystem!: DialogSystem;
  private dialogBox!: Phaser.GameObjects.Container;
  private dialogText!: Phaser.GameObjects.Text;
  private choiceButtons: Phaser.GameObjects.Text[] = [];
  private isDialogActive = false;

  constructor() {
    super({ key: 'UIScene' });
  }

  create(): void {
    this.dialogSystem = new DialogSystem();
    this.dialogSystem.setCallbacks({
      onStart: (npc) => this.showDialog(npc),
      onEnd: () => this.hideDialog(),
      onMessage: (text, choices) => this.showMessage(text, choices),
    });

    // 监听 NPC 对话事件
    this.game.events.on('npc-talk', (npc: NPCData) => {
      this.dialogSystem.startDialog(npc);
    });

    // 创建对话框容器（初始隐藏）
    this.createDialogBox();

    // 点击继续
    this.input.keyboard?.on('keydown-SPACE', () => {
      if (this.isDialogActive) {
        if (this.choiceButtons.length === 0) {
          this.dialogSystem.next();
        }
      }
    });
  }

  private createDialogBox(): void {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    this.dialogBox = this.add.container(0, height - 150);
    this.dialogBox.setVisible(false);

    // 背景
    const bg = this.add.graphics();
    bg.fillStyle(0x000000, 0.85);
    bg.fillRoundedRect(20, 0, width - 40, 120, 8);
    bg.lineStyle(2, 0xffffff);
    bg.strokeRoundedRect(20, 0, width - 40, 120, 8);
    this.dialogBox.add(bg);

    // NPC 名称
    const nameText = this.add.text(35, 10, '', {
      fontSize: '14px',
      color: '#ffff00',
    });
    this.dialogBox.add(nameText);
    (this.dialogBox as any).nameText = nameText;

    // 对话文字
    this.dialogText = this.add.text(35, 35, '', {
      fontSize: '16px',
      color: '#ffffff',
      wordWrap: { width: width - 70 },
    });
    this.dialogBox.add(this.dialogText);

    // 继续提示
    const continueHint = this.add.text(width - 45, 105, '▼', {
      fontSize: '12px',
      color: '#aaaaaa',
    });
    this.dialogBox.add(continueHint);
  }

  private showDialog(npc: NPCData): void {
    this.isDialogActive = true;
    this.dialogBox.setVisible(true);
    (this.dialogBox as any).nameText.setText(npc.name);
  }

  private hideDialog(): void {
    this.isDialogActive = false;
    this.dialogBox.setVisible(false);
    this.clearChoices();
  }

  private showMessage(text: string, choices?: { text: string; next: string }[]): void {
    this.dialogText.setText(text);
    this.clearChoices();

    if (choices && choices.length > 0) {
      let yOffset = 70;
      choices.forEach((choice, index) => {
        const btn = this.add.text(50, yOffset, `[ ${choice.text} ]`, {
          fontSize: '14px',
          color: '#00ffff',
        });
        btn.setInteractive({ useHandCursor: true });
        btn.on('pointerover', () => btn.setColor('#ffffff'));
        btn.on('pointerout', () => btn.setColor('#00ffff'));
        btn.on('pointerdown', () => {
          this.dialogSystem.selectChoice(index);
        });
        this.dialogBox.add(btn);
        this.choiceButtons.push(btn);
        yOffset += 25;
      });
    }
  }

  private clearChoices(): void {
    this.choiceButtons.forEach(btn => btn.destroy());
    this.choiceButtons = [];
  }
}
```

- [ ] **Step 4: 修改 MapScene.ts 添加测试 NPC**

```typescript
import Phaser from 'phaser';
import { Player } from '../entities/Player';
import { NPC, NPCData } from '../entities/NPC';
import { TEST_MAP } from '../data/map-data';
import { GAME_CONFIG } from '../config/game-config';

// 测试 NPC 数据
const TEST_NPC: NPCData = {
  id: 'test_npc_1',
  name: '村民',
  x: 200,
  y: 200,
  sprite: 'npc',
  defaultDialog: 'hello',
  dialogs: {
    hello: {
      text: '欢迎来到魔力宝贝的世界！',
      next: 'info',
    },
    info: {
      text: '这里是一个充满冒险的地方，祝你旅途愉快！',
      choices: [
        { text: '谢谢', next: 'bye' },
        { text: '再问我一次', next: 'hello' },
      ],
    },
    bye: {
      text: '再见，冒险者！',
    },
  },
};

export class MapScene extends Phaser.Scene {
  private player!: Player;
  private npcs: NPC[] = [];

  create(): void {
    // ... 地图绘制和玩家创建代码 ...

    // 添加测试 NPC
    const npc = new NPC(this, TEST_NPC);
    this.npcs.push(npc);

    // 将 UIScene 的对话系统连接到 MapScene
    const uiScene = this.scene.get('UIScene') as any;
    this.game.events.on('npc-talk', (npcData: NPCData) => {
      // 暂停玩家移动
      this.player.setVisible(false);
    });
  }

  update(): void {
    this.player.update();
  }
}
```

- [ ] **Step 5: 提交代码**

```bash
cd ~/magic-bubble-h5 && git add -A && git commit -m "feat: 添加 NPC 实体和对话系统"
```

---

## Task 6: 原版地图资源解析准备

**Files:**
- Create: `src/systems/ResourceParser.ts`
- Create: `src/data/original-maps.ts`

- [ ] **Step 1: 创建 src/systems/ResourceParser.ts**

```typescript
// 原版资源解析器
// 用于解析 ~/Downloads/crossgate602 中的地图数据

export interface ParsedTileSet {
  firstgid: number;
  name: string;
  tileWidth: number;
  tileHeight: number;
  image?: string;
}

export interface ParsedMap {
  width: number;
  height: number;
  tilewidth: number;
  tileheight: number;
  tilesets: ParsedTileSet[];
  layers: any[];
}

export class ResourceParser {
  // 注意：原版地图数据是二进制格式，需要逆向分析
  // 这里提供框架，实际解析逻辑需要根据具体格式实现

  static async parseMapFile(filePath: string): Promise<ParsedMap | null> {
    // TODO: 实现原版地图文件解析
    // 目前阶段返回 null，使用测试地图
    console.warn('原版地图解析尚未实现，使用测试地图');
    return null;
  }

  static async loadAllMaps(): Promise<Map<string, ParsedMap>> {
    const maps = new Map<string, ParsedMap>();

    // 原版地图列表（需要手动维护或从资源目录扫描）
    const mapFiles = [
      '1000', // 法兰城
      '1001', // 城东
      '1002', // 城西
      // ... 更多地图
    ];

    for (const mapId of mapFiles) {
      const map = await this.parseMapFile(`map/${mapId}`);
      if (map) {
        maps.set(mapId, map);
      }
    }

    return maps;
  }

  static convertToPhaserTilemap(parsed: ParsedMap): any {
    // 将解析后的数据转换为 Phaser Tilemap 格式
    // TODO: 实现转换逻辑
    return null;
  }
}
```

- [ ] **Step 2: 创建 src/data/original-maps.ts**

```typescript
// 原版地图元数据
// 记录地图 ID、名称、类型等信息

export interface OriginalMapMeta {
  id: string;
  name: string;
  type: 'town' | 'field' | 'dungeon';
 BGM?: string;
  monsters?: string[];
}

export const ORIGINAL_MAPS: OriginalMapMeta[] = [
  { id: '1000', name: '法兰城', type: 'town', BGM: 'cgbgm_m0' },
  { id: '1001', name: '城东地区', type: 'field', BGM: 'cgbgm_f0', monsters: ['史莱姆', '哥布林'] },
  { id: '1002', name: '城西地区', type: 'field', BGM: 'cgbgm_f0', monsters: ['蝙蝠', '野狼'] },
  // ... 更多地图
];

export function getMapById(id: string): OriginalMapMeta | undefined {
  return ORIGINAL_MAPS.find(m => m.id === id);
}
```

- [ ] **Step 3: 提交代码**

```bash
cd ~/magic-bubble-h5 && git add -A && git commit -m "feat: 添加原版地图解析框架"
```

---

## Task 7: 地图切换系统

**Files:**
- Create: `src/systems/MapTransition.ts`
- Modify: `src/scenes/MapScene.ts`

- [ ] **Step 1: 创建 src/systems/MapTransition.ts**

```typescript
import Phaser from 'phaser';
import { MapData } from '../data/map-data';

export interface MapTransition {
  fromMap: string;
  toMap: string;
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
}

export class MapTransitionSystem {
  private scene: Phaser.Scene;
  private transitions: MapTransition[] = [];
  private currentMapId: string | null = null;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  addTransition(transition: MapTransition): void {
    this.transitions.push(transition);
  }

  setCurrentMap(mapId: string): void {
    this.currentMapId = mapId;
  }

  checkTransition(x: number, y: number): MapTransition | null {
    if (!this.currentMapId) return null;

    for (const t of this.transitions) {
      if (t.fromMap === this.currentMapId) {
        // 检查是否在传送点范围内
        const dx = Math.abs(x - t.fromX);
        const dy = Math.abs(y - t.fromY);
        if (dx < 20 && dy < 20) {
          return t;
        }
      }
    }
    return null;
  }

  getTransitionsForMap(mapId: string): MapTransition[] {
    return this.transitions.filter(t => t.fromMap === mapId);
  }
}
```

- [ ] **Step 2: 修改 MapScene.ts 支持地图切换**

```typescript
export class MapScene extends Phaser.Scene {
  // ... 现有代码 ...

  private mapTransition!: MapTransitionSystem;
  private currentMapData: MapData | null = null;

  create(): void {
    // ... 现有代码 ...

    this.mapTransition = new MapTransitionSystem(this);

    // 添加传送点
    this.mapTransition.addTransition({
      fromMap: 'test_map',
      toMap: 'test_map_2',
      fromX: GAME_CONFIG.width - 50,
      fromY: GAME_CONFIG.height / 2,
      toX: 50,
      toY: GAME_CONFIG.height / 2,
    });
  }

  update(): void {
    this.player.update();

    // 检查传送点
    const pos = this.player.getPosition();
    const transition = this.mapTransition.checkTransition(pos.x, pos.y);
    if (transition) {
      this.scene.start('MapScene', { mapId: transition.toMap, spawnX: transition.toX, spawnY: transition.toY });
    }
  }
}
```

- [ ] **Step 3: 提交代码**

```bash
cd ~/magic-bubble-h5 && git add -A && git commit -m "feat: 添加地图切换系统"
```

---

## Phase 1 验收标准

- [ ] 地图可加载并显示
- [ ] 人物可在地图上移动（WASD/方向键）
- [ ] NPC 对话框正常显示（按空格继续）
- [ ] 城镇/野外可切换
- [ ] 原版地图资源解析框架就绪

---

## 执行方式

**Plan complete and saved to `docs/superpowers/plans/2026-04-07-phase1-map-system.md`.**

Two execution options:

**1. Subagent-Driven (recommended)** - I dispatch a fresh subagent per task, review between tasks, fast iteration

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints

**Which approach?**
