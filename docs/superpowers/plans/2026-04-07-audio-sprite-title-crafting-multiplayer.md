# 音效精灵称号制造联机 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development

**Goal:** 实现音效系统、精灵解析、称号系统、生产制造、多人联机

**Architecture:**
- 音效系统：使用 Phaser 音频管理，原版 WAV 文件
- 精灵解析：创建 sprite sheet 解析工具，生成 CSS sprite
- 称号系统：玩家称号基于等级/任务/成就
- 生产制造：采集原料 + 合成配方 = 装备物品
- 多人联机：WebSocket P2P 战斗同步

**Tech Stack:** Phaser 3, WebSocket (PeerJS), TypeScript

---

## Task A: 音效/BGM 系统

### A1: 创建音频系统

**Files:**
- Create: `src/systems/AudioSystem.ts`
- Create: `src/data/audio-data.ts`
- Modify: `src/scenes/BattleScene.ts`

- [ ] **Step 1: 创建音频数据**

创建 `src/data/audio-data.ts`：

```typescript
export interface BGMData {
  id: string;
  name: string;
  file: string;
  volume?: number;
}

export interface SEData {
  id: string;
  name: string;
  file: string;
  volume?: number;
}

export const BGM_LIST: BGMData[] = [
  { id: 'bgm_title', name: '标题画面', file: 'cgbgm_m0.wav' },
  { id: 'bgm_town', name: '城市场景', file: 'cgbgm_m1.wav' },
  { id: 'bgm_field', name: '野外场景', file: 'cgbgm_f0.wav' },
  { id: 'bgm_battle', name: '战斗场景', file: 'cgbgm_b0.wav' },
  { id: 'bgm_dungeon', name: '地下城', file: 'cgbgm_d0.wav' },
];

export const SE_LIST: SEData[] = [
  { id: 'se_attack', name: '攻击', file: 'cgbtl_attack.wav' },
  { id: 'se_hit', name: '命中', file: 'cgbtl_hit.wav' },
  { id: 'se_victory', name: '胜利', file: 'cgbtl_victory.wav' },
  { id: 'se_levelup', name: '升级', file: 'cgsys_levelup.wav' },
  { id: 'se_cursor', name: '光标移动', file: 'cgsys_cursor.wav' },
  { id: 'se_decision', name: '确认', file: 'cgsys_decision.wav' },
];
```

- [ ] **Step 2: 创建音频系统**

创建 `src/systems/AudioSystem.ts`：

```typescript
import Phaser from 'phaser';
import { BGM_LIST, BGMData, SE_LIST, SEData } from '../data/audio-data';

export class AudioSystem {
  private scene: Phaser.Scene;
  private bgm?: Phaser.Sound.BaseSound;
  private seCache: Map<string, Phaser.Sound.BaseSound> = new Map();
  private bgmVolume: number = 0.5;
  private seVolume: number = 0.7;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
  }

  playBGM(bgmId: string, loop: boolean = true): void {
    const bgmData = BGM_LIST.find(b => b.id === bgmId);
    if (!bgmData) return;

    this.stopBGM();

    this.bgm = this.scene.sound.add(bgmData.file, {
      volume: this.bgmVolume * (bgmData.volume || 1),
      loop,
    });
    this.bgm.play();
  }

  stopBGM(): void {
    if (this.bgm) {
      this.bgm.stop();
      this.bgm = undefined;
    }
  }

  playSE(seId: string): void {
    const seData = SE_LIST.find(s => s.id === seId);
    if (!seData) return;

    let se = this.seCache.get(seId);
    if (!se) {
      se = this.scene.sound.add(seData.file, {
        volume: this.seVolume * (seData.volume || 1),
      });
      this.seCache.set(seId, se);
    }
    se.play();
  }

  setBGMVolume(volume: number): void {
    this.bgmVolume = Math.max(0, Math.min(1, volume));
    if (this.bgm) {
      this.bgm.setVolume(this.bgmVolume);
    }
  }

  setSEVolume(volume: number): void {
    this.seVolume = Math.max(0, Math.min(1, volume));
  }

  pauseBGM(): void {
    if (this.bgm) {
      this.bgm.pause();
    }
  }

  resumeBGM(): void {
    if (this.bgm) {
      this.bgm.resume();
    }
  }
}
```

- [ ] **Step 3: 集成到 BattleScene**

修改 `BattleScene.ts` 添加音效：

```typescript
import { AudioSystem } from '../systems/AudioSystem';

// 在 BattleScene 中
private audioSystem!: AudioSystem;

// 在 create() 中
this.audioSystem = new AudioSystem(this);

// 播放攻击音效
this.audioSystem.playSE('se_attack');

// 战斗胜利
this.audioSystem.playSE('se_victory');
```

- [ ] **Step 4: 复制音频文件**

```bash
mkdir -p public/audio/bgm public/audio/se
cp ~/Downloads/crossgate602/bin/bgm/cgbgm_*.wav public/audio/bgm/ 2>/dev/null || echo "BGM copy skipped"
cp ~/Downloads/crossgate602/bin/se/cgbtl_*.wav public/audio/se/ 2>/dev/null || echo "SE copy skipped"
cp ~/Downloads/crossgate602/bin/se/cgsys_*.wav public/audio/se/ 2>/dev/null || echo "SE copy skipped"
```

- [ ] **Step 5: 提交**

```bash
git add -A && git commit -m "feat: 添加音效/BGM系统"
```

---

## Task B: 精灵解析工具

### B1: 创建精灵表解析工具

**Files:**
- Create: `tools/parse-sprite.js`
- Create: `tools/generate-sprite-css.js`

- [ ] **Step 1: 创建精灵解析工具**

创建 `tools/parse-sprite.js`：

```javascript
const fs = require('fs');
const path = require('path');

const GRAPHIC_INFO_PATH = path.join(__dirname, '../Downloads/crossgate602/bin/GraphicInfo_20.bin');

function parseSpriteIndex(buffer) {
  const sprites = [];
  let offset = 0;

  while (offset < buffer.length - 16) {
    const entry = {
      id: sprites.length,
      offset: buffer.readUInt32LE(offset),
      size: buffer.readUInt32LE(offset + 4),
      width: buffer.readUInt16LE(offset + 8),
      height: buffer.readUInt16LE(offset + 10),
      paletteId: buffer.readUInt8(offset + 12),
      flags: buffer.readUInt8(offset + 13),
    };

    if (entry.offset > 0 && entry.size > 0) {
      sprites.push(entry);
    }
    offset += 16;
  }

  return sprites;
}

function scanSprites() {
  const buffer = fs.readFileSync(GRAPHIC_INFO_PATH);
  const sprites = parseSpriteIndex(buffer);

  console.log(`Found ${sprites.length} sprite entries`);

  // 输出前20个作为参考
  console.log(JSON.stringify(sprites.slice(0, 20), null, 2));

  return sprites;
}

const args = process.argv.slice(2);
if (args[0] === '--scan') {
  scanSprites();
}

module.exports = { parseSpriteIndex };
```

- [ ] **Step 2: 生成 CSS Sprite 占位符**

由于 Graphic_20.bin 是私有二进制格式，创建 CSS sprite 占位符系统：

创建 `tools/generate-sprite-css.js`：

```javascript
const fs = require('fs');

// 生成 CSS 变量占位符
const spriteCount = 100;

let css = `/* Auto-generated sprite variables */\n`;
css += `:root {\n`;

for (let i = 0; i < spriteCount; i++) {
  const hue = (i * 3.6) % 360;
  css += `  --sprite-${i}: hsl(${hue}, 50%, 50%);\n`;
}

css += `}\n`;

fs.writeFileSync('src/styles/sprites.css', css);
console.log(`Generated sprite CSS with ${spriteCount} placeholder variables`);
```

- [ ] **Step 3: 创建精灵渲染器**

创建 `src/systems/SpriteRenderer.ts`：

```typescript
import Phaser from 'phaser';
import { PaletteSystem } from './PaletteSystem';

export class SpriteRenderer {
  private scene: Phaser.Scene;
  private paletteSystem: PaletteSystem;

  constructor(scene: Phaser.Scene) {
    this.scene = scene;
    this.paletteSystem = new PaletteSystem();
  }

  // 使用调色板颜色创建占位符精灵
  createPlaceholderSprite(x: number, y: number, colorIndex: number, width: number = 32, height: number = 32): Phaser.GameObjects.Graphics {
    const graphics = this.scene.add.graphics();
    const color = this.paletteSystem.getColor(colorIndex % 256);

    graphics.fillStyle(color, 1);
    graphics.fillRect(0, 0, width, height);
    graphics.setPosition(x, y);

    return graphics;
  }

  // 创建怪物占位符精灵
  createMonsterSprite(monsterId: string, x: number, y: number): Phaser.GameObjects.Container {
    const container = this.scene.add.container(x, y);

    // 使用基于 monsterId 的哈希选择颜色
    const colorIndex = this.hashString(monsterId);
    const color = this.paletteSystem.getColor(colorIndex % 256);

    const graphics = this.scene.add.graphics();
    graphics.fillStyle(color, 1);
    graphics.fillCircle(0, 0, 20);
    graphics.fillStyle(0x000000, 0.3);
    graphics.fillCircle(-5, -5, 5);
    graphics.fillCircle(5, -5, 5);

    container.add(graphics);

    return container;
  }

  private hashString(str: string): number {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = ((hash << 5) - hash) + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash);
  }
}
```

- [ ] **Step 4: 提交**

```bash
git add -A && git commit -m "feat: 添加精灵解析工具和渲染器"
```

---

## Task C: 称号系统

### C1: 创建称号数据

**Files:**
- Create: `src/data/title-data.ts`
- Create: `src/systems/TitleSystem.ts`
- Create: `src/scenes/TitleScene.ts`

- [ ] **Step 1: 创建称号数据**

创建 `src/data/title-data.ts`：

```typescript
export type TitleType = 'level' | 'quest' | 'battle' | 'special';

export interface TitleData {
  id: string;
  name: string;
  description: string;
  type: TitleType;
  requirement: {
    type: TitleType;
    value: number;
  };
  icon?: string;
}

export const TITLES: TitleData[] = [
  // 等级称号
  { id: 'title_level_10', name: '冒险者', description: '达到10级', type: 'level', requirement: { type: 'level', value: 10 } },
  { id: 'title_level_20', name: '冒险王', description: '达到20级', type: 'level', requirement: { type: 'level', value: 20 } },
  { id: 'title_level_30', name: '勇者', description: '达到30级', type: 'level', requirement: { type: 'level', value: 30 } },
  { id: 'title_level_50', name: '英雄', description: '达到50级', type: 'level', requirement: { type: 'level', value: 50 } },
  { id: 'title_level_100', name: '传说', description: '达到100级', type: 'level', requirement: { type: 'level', value: 100 } },

  // 战斗称号
  { id: 'title_battle_10', name: '初出茅庐', description: '战斗10次', type: 'battle', requirement: { type: 'battle', value: 10 } },
  { id: 'title_battle_100', name: '身经百战', description: '战斗100次', type: 'battle', requirement: { type: 'battle', value: 100 } },
  { id: 'title_battle_1000', name: '战无不胜', description: '战斗1000次', type: 'battle', requirement: { type: 'battle', value: 1000 } },

  // 任务称号
  { id: 'title_quest_1', name: '初试锋芒', description: '完成1个任务', type: 'quest', requirement: { type: 'quest', value: 1 } },
  { id: 'title_quest_10', name: '任务达人', description: '完成10个任务', type: 'quest', requirement: { type: 'quest', value: 10 } },
  { id: 'title_quest_50', name: '任务大师', description: '完成50个任务', type: 'quest', requirement: { type: 'quest', value: 50 } },

  // 特殊称号
  { id: 'title_pet_collector', name: '驯兽师', description: '捕捉5只宠物', type: 'special', requirement: { type: 'special', value: 5 } },
  { id: 'title_wealthy', name: '富翁', description: '拥有10000金币', type: 'special', requirement: { type: 'special', value: 10000 } },
];
```

- [ ] **Step 2: 创建称号系统**

创建 `src/systems/TitleSystem.ts`：

```typescript
import { TitleData, TITLES } from '../data/title-data';

export class TitleSystem {
  private unlockedTitles: Set<string> = new Set();
  private currentTitle?: string;

  constructor() {
    this.load();
  }

  load(): void {
    const saved = localStorage.getItem('unlockedTitles');
    this.unlockedTitles = saved ? new Set(JSON.parse(saved)) : new Set();
    this.currentTitle = localStorage.getItem('currentTitle') || undefined;
  }

  save(): void {
    localStorage.setItem('unlockedTitles', JSON.stringify([...this.unlockedTitles]));
    if (this.currentTitle) {
      localStorage.setItem('currentTitle', this.currentTitle);
    }
  }

  checkAndUnlock(type: string, value: number): string[] {
    const newlyUnlocked: string[] = [];

    for (const title of TITLES) {
      if (this.unlockedTitles.has(title.id)) continue;

      if (title.requirement.type === type && value >= title.requirement.value) {
        this.unlockedTitles.add(title.id);
        newlyUnlocked.push(title.id);
      }
    }

    if (newlyUnlocked.length > 0) {
      this.save();
    }

    return newlyUnlocked;
  }

  getUnlockedTitles(): TitleData[] {
    return TITLES.filter(t => this.unlockedTitles.has(t.id));
  }

  getAvailableTitles(): TitleData[] {
    return TITLES;
  }

  setCurrentTitle(titleId: string): boolean {
    if (this.unlockedTitles.has(titleId)) {
      this.currentTitle = titleId;
      this.save();
      return true;
    }
    return false;
  }

  getCurrentTitle(): TitleData | undefined {
    if (!this.currentTitle) return undefined;
    return TITLES.find(t => t.id === this.currentTitle);
  }

  getProgress(titleId: string, currentValue: number): number {
    const title = TITLES.find(t => t.id === titleId);
    if (!title) return 0;
    return Math.min(1, currentValue / title.requirement.value);
  }
}
```

- [ ] **Step 3: 创建称号界面**

创建 `src/scenes/TitleScene.ts`：

```typescript
import Phaser from 'phaser';
import { TitleSystem } from '../systems/TitleSystem';
import { TitleData } from '../data/title-data';

export class TitleScene extends Phaser.Scene {
  private titleSystem!: TitleSystem;
  private titleCards: Phaser.GameObjects.Container[] = [];

  constructor() {
    super({ key: 'TitleScene' });
  }

  create(): void {
    this.titleSystem = new TitleSystem();

    this.cameras.main.setBackgroundColor(0x1a1a2e);

    this.add.text(400, 30, '称号列表', {
      fontSize: '24px',
      color: '#ffcc00',
    }).setOrigin(0.5);

    const backBtn = this.add.text(20, 20, '[ 返回 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setInteractive();
    backBtn.on('pointerdown', () => this.scene.pop());

    this.renderTitles();
  }

  private renderTitles(): void {
    this.titleCards.forEach(card => card.destroy());
    this.titleCards = [];

    const titles = this.titleSystem.getAvailableTitles();
    let y = 80;

    titles.forEach((title) => {
      const isUnlocked = this.titleSystem.getUnlockedTitles().some(t => t.id === title.id);
      const card = this.createTitleCard(title, isUnlocked, 100, y);
      this.titleCards.push(card);
      y += 80;
    });
  }

  private createTitleCard(title: TitleData, isUnlocked: boolean, x: number, y: number): Phaser.GameObjects.Container {
    const card = this.add.container(x, y);

    const bg = this.add.graphics();
    bg.fillStyle(isUnlocked ? 0x336633 : 0x333366);
    bg.fillRoundedRect(0, 0, 600, 70, 8);
    card.add(bg);

    const nameText = this.add.text(15, 10, title.name, {
      fontSize: '18px',
      color: isUnlocked ? '#ffcc00' : '#666666',
    });
    card.add(nameText);

    const descText = this.add.text(15, 40, title.description, {
      fontSize: '12px',
      color: '#aaaaaa',
    });
    card.add(descText);

    const typeText = this.add.text(500, 25, title.type, {
      fontSize: '12px',
      color: isUnlocked ? '#00ff00' : '#666666',
    }).setOrigin(0.5);
    card.add(typeText);

    if (isUnlocked) {
      const selectBtn = this.add.text(420, 25, '[ 装备 ]', {
        fontSize: '12px',
        color: '#00ffff',
      }).setOrigin(0.5).setInteractive();
      selectBtn.on('pointerdown', () => {
        this.titleSystem.setCurrentTitle(title.id);
        this.showMessage(`已装备称号: ${title.name}`);
      });
      card.add(selectBtn);
    }

    return card;
  }

  private showMessage(text: string): void {
    const msg = this.add.text(400, 550, text, {
      fontSize: '16px',
      color: '#ffffff',
    }).setOrigin(0.5);
    this.time.delayedCall(1500, () => msg.destroy());
  }
}
```

- [ ] **Step 4: 提交**

```bash
git add -A && git commit -m "feat: 添加称号系统"
```

---

## Task D: 生产制造系统

### D1: 创建制造数据

**Files:**
- Create: `src/data/craft-data.ts`
- Create: `src/systems/CraftSystem.ts`
- Create: `src/scenes/CraftScene.ts`

- [ ] **Step 1: 创建制造数据**

创建 `src/data/craft-data.ts`：

```typescript
export interface CraftMaterial {
  id: string;
  name: string;
  type: 'herb' | 'ore' | 'wood' | 'monster_drop';
  location: string; // 采集地点
}

export interface CraftRecipe {
  id: string;
  name: string;
  resultItemId: string;
  resultQuantity: number;
  materials: { materialId: string; quantity: number }[];
  requiredLevel: number;
  description: string;
}

export const MATERIALS: CraftMaterial[] = [
  { id: 'herb_green', name: '绿草', type: 'herb', location: 'forest' },
  { id: 'herb_red', name: '红草', type: 'herb', location: 'forest' },
  { id: 'herb_blue', name: '蓝草', type: 'herb', location: 'snow' },
  { id: 'ore_iron', name: '铁矿', type: 'ore', location: 'volcano' },
  { id: 'ore_copper', name: '铜矿', type: 'ore', location: 'desert' },
  { id: 'ore_silver', name: '银矿', type: 'ore', location: 'snow' },
  { id: 'wood_normal', name: '普通木材', type: 'wood', location: 'forest' },
  { id: 'wood_hard', name: '硬木材', type: 'wood', location: 'volcano' },
  { id: 'drop_slime', name: '史莱姆凝胶', type: 'monster_drop', location: 'forest' },
  { id: 'drop_dragon', name: '龙鳞', type: 'monster_drop', location: 'dungeon' },
];

export const RECIPES: CraftRecipe[] = [
  {
    id: 'recipe_potion',
    name: '治疗药水',
    resultItemId: 'potion',
    resultQuantity: 1,
    materials: [
      { materialId: 'herb_green', quantity: 2 },
      { materialId: 'herb_red', quantity: 1 },
    ],
    requiredLevel: 1,
    description: '恢复50 HP',
  },
  {
    id: 'recipe_hi_potion',
    name: '高级治疗药水',
    resultItemId: 'hi_potion',
    resultQuantity: 1,
    materials: [
      { materialId: 'herb_blue', quantity: 3 },
      { materialId: 'herb_green', quantity: 2 },
    ],
    requiredLevel: 5,
    description: '恢复200 HP',
  },
  {
    id: 'recipe_ether',
    name: '魔力药水',
    resultItemId: 'ether',
    resultQuantity: 1,
    materials: [
      { materialId: 'herb_blue', quantity: 2 },
      { materialId: 'drop_slime', quantity: 1 },
    ],
    requiredLevel: 3,
    description: '恢复30 MP',
  },
  {
    id: 'recipe_iron_sword',
    name: '铁剑',
    resultItemId: 'iron_sword',
    resultQuantity: 1,
    materials: [
      { materialId: 'ore_iron', quantity: 3 },
      { materialId: 'wood_normal', quantity: 2 },
    ],
    requiredLevel: 3,
    description: '攻击力+5',
  },
  {
    id: 'recipe_leather_armor',
    name: '皮甲',
    resultItemId: 'leather_armor',
    resultQuantity: 1,
    materials: [
      { materialId: 'drop_slime', quantity: 4 },
      { materialId: 'wood_normal', quantity: 1 },
    ],
    requiredLevel: 2,
    description: '防御力+3',
  },
  {
    id: 'recipe_dragon_sword',
    name: '龙之剑',
    resultItemId: 'dragon_sword',
    resultQuantity: 1,
    materials: [
      { materialId: 'ore_silver', quantity: 5 },
      { materialId: 'drop_dragon', quantity: 3 },
      { materialId: 'wood_hard', quantity: 2 },
    ],
    requiredLevel: 10,
    description: '攻击力+15',
  },
];
```

- [ ] **Step 2: 创建制造系统**

创建 `src/systems/CraftSystem.ts`：

```typescript
import { CraftRecipe, CraftMaterial, MATERIALS, RECIPES } from '../data/craft-data';
import { InventorySystem } from './InventorySystem';

export class CraftSystem {
  private inventory: InventorySystem;

  constructor(inventory: InventorySystem) {
    this.inventory = inventory;
  }

  getAvailableRecipes(): CraftRecipe[] {
    return RECIPES;
  }

  canCraft(recipeId: string): { canCraft: boolean; missing: string[] } {
    const recipe = RECIPES.find(r => r.id === recipeId);
    if (!recipe) return { canCraft: false, missing: [] };

    const missing: string[] = [];

    for (const material of recipe.materials) {
      const have = this.inventory.getItemCount(material.materialId);
      if (have < material.quantity) {
        const mat = MATERIALS.find(m => m.id === material.materialId);
        missing.push(`${mat?.name || material.materialId} (需要${material.quantity}, 有${have})`);
      }
    }

    return { canCraft: missing.length === 0, missing };
  }

  craft(recipeId: string): boolean {
    const recipe = RECIPES.find(r => r.id === recipeId);
    if (!recipe) return false;

    const { canCraft } = this.canCraft(recipeId);
    if (!canCraft) return false;

    // 消耗材料
    for (const material of recipe.materials) {
      this.inventory.removeItem(material.materialId, material.quantity);
    }

    // 获得产物
    this.inventory.addItem(recipe.resultItemId, recipe.resultQuantity);

    return true;
  }

  getMaterialData(materialId: string): CraftMaterial | undefined {
    return MATERIALS.find(m => m.id === materialId);
  }

  getPlayerMaterials(): { materialId: string; quantity: number }[] {
    const materials: { materialId: string; quantity: number }[] = [];
    const inv = this.inventory.getInventory();

    for (const slot of inv) {
      const mat = MATERIALS.find(m => m.id === slot.itemId);
      if (mat) {
        materials.push({ materialId: slot.itemId, quantity: slot.quantity });
      }
    }

    return materials;
  }
}
```

- [ ] **Step 3: 创建制造界面**

创建 `src/scenes/CraftScene.ts`：

```typescript
import Phaser from 'phaser';
import { CraftSystem } from '../systems/CraftSystem';
import { InventorySystem } from '../systems/InventorySystem';
import { RECIPES, MATERIALS, CraftRecipe } from '../data/craft-data';

export class CraftScene extends Phaser.Scene {
  private craftSystem!: CraftSystem;
  private inventory!: InventorySystem;
  private recipeCards: Phaser.GameObjects.Container[] = [];

  constructor() {
    super({ key: 'CraftScene' });
  }

  create(): void {
    this.inventory = new InventorySystem();
    this.craftSystem = new CraftSystem(this.inventory);

    this.cameras.main.setBackgroundColor(0x1a1a2e);

    this.add.text(400, 30, '生产制造', {
      fontSize: '24px',
      color: '#ffcc00',
    }).setOrigin(0.5);

    const backBtn = this.add.text(20, 20, '[ 返回 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setInteractive();
    backBtn.on('pointerdown', () => this.scene.pop());

    this.add.text(400, 60, '收集材料并在工作台制作装备和药水', {
      fontSize: '12px',
      color: '#888888',
    }).setOrigin(0.5);

    this.renderRecipes();
  }

  private renderRecipes(): void {
    this.recipeCards.forEach(card => card.destroy());
    this.recipeCards = [];

    const recipes = this.craftSystem.getAvailableRecipes();
    let y = 100;

    recipes.forEach((recipe) => {
      const { canCraft, missing } = this.craftSystem.canCraft(recipe.id);
      const card = this.createRecipeCard(recipe, canCraft, missing, 100, y);
      this.recipeCards.push(card);
      y += 100;
    });
  }

  private createRecipeCard(recipe: CraftRecipe, canCraft: boolean, missing: string[], x: number, y: number): Phaser.GameObjects.Container {
    const card = this.add.container(x, y);

    const bg = this.add.graphics();
    bg.fillStyle(canCraft ? 0x336633 : 0x333366);
    bg.fillRoundedRect(0, 0, 600, 90, 8);
    card.add(bg);

    const nameText = this.add.text(15, 10, recipe.name, {
      fontSize: '18px',
      color: canCraft ? '#ffcc00' : '#666666',
    });
    card.add(nameText);

    const descText = this.add.text(15, 40, recipe.description, {
      fontSize: '12px',
      color: '#aaaaaa',
    });
    card.add(descText);

    // 材料需求
    let materialStr = '';
    recipe.materials.forEach(m => {
      const mat = MATERIALS.find(x => x.id === m.materialId);
      materialStr += `${mat?.name || m.materialId} x${m.quantity} `;
    });
    const matText = this.add.text(15, 60, materialStr, {
      fontSize: '10px',
      color: '#888888',
    });
    card.add(matText);

    const craftBtn = this.add.text(500, 35, '[ 制造 ]', {
      fontSize: '14px',
      color: canCraft ? '#00ff00' : '#666666',
    }).setOrigin(0.5).setInteractive();

    if (canCraft) {
      craftBtn.on('pointerdown', () => {
        if (this.craftSystem.craft(recipe.id)) {
          this.showMessage(`制造成功: ${recipe.name}!`);
          this.renderRecipes();
        } else {
          this.showMessage('制造失败!');
        }
      });
    }

    card.add(craftBtn);

    return card;
  }

  private showMessage(text: string): void {
    const msg = this.add.text(400, 550, text, {
      fontSize: '16px',
      color: '#ffffff',
    }).setOrigin(0.5);
    this.time.delayedCall(1500, () => msg.destroy());
  }
}
```

- [ ] **Step 4: 提交**

```bash
git add -A && git commit -m "feat: 添加生产制造系统"
```

---

## Task E: 多人联机系统

### E1: 创建 P2P 联机系统

**Files:**
- Create: `src/systems/MultiplayerSystem.ts`
- Create: `src/scenes/LobbyScene.ts`
- Modify: `src/scenes/BattleScene.ts`

- [ ] **Step 1: 创建多人联机系统**

创建 `src/systems/MultiplayerSystem.ts`：

```typescript
import Peer, { DataConnection } from 'peerjs';

export interface PlayerInfo {
  id: string;
  name: string;
  job?: string;
  level?: number;
}

export interface BattleSyncData {
  type: 'battle_start' | 'battle_action' | 'battle_end';
  playerId: string;
  data: any;
}

export class MultiplayerSystem {
  private peer?: Peer;
  private connections: Map<string, DataConnection> = new Map();
  private localPlayerId?: string;
  private onReceiveAction?: (data: BattleSyncData) => void;
  private onPlayerJoin?: (player: PlayerInfo) => void;
  private onPlayerLeave?: (playerId: string) => void;

  constructor() {
    this.load();
  }

  private load(): void {
    const saved = localStorage.getItem('playerInfo');
    if (saved) {
      const info = JSON.parse(saved);
      this.localPlayerId = info.id;
    }
  }

  private savePlayerInfo(info: PlayerInfo): void {
    this.localPlayerId = info.id;
    localStorage.setItem('playerInfo', JSON.stringify(info));
  }

  async host(playerInfo: PlayerInfo): Promise<string> {
    return new Promise((resolve, reject) => {
      const id = `player_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      this.savePlayerInfo({ ...playerInfo, id });

      this.peer = new Peer(id, {
        debug: 1,
      });

      this.peer.on('open', (peerId) => {
        console.log('Hosting with ID:', peerId);

        this.peer!.on('connection', (conn) => {
          this.handleConnection(conn);
        });

        resolve(peerId);
      });

      this.peer.on('error', (err) => {
        console.error('Peer error:', err);
        reject(err);
      });
    });
  }

  async join(hostId: string, playerInfo: PlayerInfo): Promise<void> {
    return new Promise((resolve, reject) => {
      const id = `player_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      this.savePlayerInfo({ ...playerInfo, id });

      this.peer = new Peer(id, {
        debug: 1,
      });

      this.peer.on('open', (peerId) => {
        const conn = this.peer!.connect(hostId, {
          reliable: true,
        });

        conn.on('open', () => {
          this.handleConnection(conn);
          resolve();
        });

        conn.on('error', (err) => {
          reject(err);
        });
      });

      this.peer.on('error', (err) => {
        console.error('Peer error:', err);
        reject(err);
      });
    });
  }

  private handleConnection(conn: DataConnection): void {
    console.log('Connection established:', conn.peer);

    conn.on('open', () => {
      this.connections.set(conn.peer, conn);
      this.sendPlayerInfo(conn);
    });

    conn.on('data', (data) => {
      this.handleData(conn.peer, data);
    });

    conn.on('close', () => {
      this.connections.delete(conn.peer);
      if (this.onPlayerLeave) {
        this.onPlayerLeave(conn.peer);
      }
    });
  }

  private sendPlayerInfo(conn: DataConnection): void {
    if (this.localPlayerId) {
      const info = JSON.parse(localStorage.getItem('playerInfo') || '{}');
      conn.send({
        type: 'player_info',
        data: info,
      });
    }
  }

  private handleData(fromId: string, data: any): void {
    if (data.type === 'player_info' && this.onPlayerJoin) {
      this.onPlayerJoin(data.data);
    } else if (data.type === 'battle_sync' && this.onReceiveAction) {
      this.onReceiveAction(data.data);
    }
  }

  sendBattleAction(action: BattleSyncData): void {
    const message = {
      type: 'battle_sync',
      data: action,
    };

    this.connections.forEach((conn) => {
      conn.send(message);
    });
  }

  setOnReceiveAction(callback: (data: BattleSyncData) => void): void {
    this.onReceiveAction = callback;
  }

  setOnPlayerJoin(callback: (player: PlayerInfo) => void): void {
    this.onPlayerJoin = callback;
  }

  setOnPlayerLeave(callback: (playerId: string) => void): void {
    this.onPlayerLeave = callback;
  }

  getConnectedPlayers(): string[] {
    return [...this.connections.keys()];
  }

  disconnect(): void {
    this.connections.forEach((conn) => conn.close());
    this.connections.clear();

    if (this.peer) {
      this.peer.destroy();
      this.peer = undefined;
    }
  }
}
```

- [ ] **Step 2: 创建联机大厅场景**

创建 `src/scenes/LobbyScene.ts`：

```typescript
import Phaser from 'phaser';
import { MultiplayerSystem, PlayerInfo } from '../systems/MultiplayerSystem';

export class LobbyScene extends Phaser.Scene {
  private multiplayer!: MultiplayerSystem;
  private isHost: boolean = false;
  private myId?: string;
  private players: PlayerInfo[] = [];
  private playerTexts: Phaser.GameObjects.Text[] = [];

  constructor() {
    super({ key: 'LobbyScene' });
  }

  create(): void {
    this.multiplayer = new MultiplayerSystem();

    this.cameras.main.setBackgroundColor(0x1a1a2e);

    this.add.text(400, 30, '多人联机', {
      fontSize: '24px',
      color: '#ffcc00',
    }).setOrigin(0.5);

    const backBtn = this.add.text(20, 20, '[ 返回 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setInteractive();
    backBtn.on('pointerdown', () => {
      this.multiplayer.disconnect();
      this.scene.start('MenuScene');
    });

    // Host 按钮
    const hostBtn = this.add.text(200, 100, '[ 创建房间 ]', {
      fontSize: '20px',
      color: '#00ff00',
    }).setOrigin(0.5).setInteractive();
    hostBtn.on('pointerdown', () => this.createRoom());

    // Join 输入
    this.add.text(200, 160, '房间ID:', {
      fontSize: '14px',
      color: '#ffffff',
    });

    const joinBtn = this.add.text(400, 200, '[ 加入房间 ]', {
      fontSize: '20px',
      color: '#00ffff',
    }).setOrigin(0.5).setInteractive();
    joinBtn.on('pointerdown', () => this.joinRoom());

    // 玩家列表
    this.add.text(500, 100, '玩家列表:', {
      fontSize: '16px',
      color: '#ffcc00',
    });

    this.multiplayer.setOnPlayerJoin((player) => {
      this.players.push(player);
      this.updatePlayerList();
    });

    this.multiplayer.setOnPlayerLeave((playerId) => {
      this.players = this.players.filter(p => p.id !== playerId);
      this.updatePlayerList();
    });
  }

  private async createRoom(): void {
    const saved = localStorage.getItem('playerInfo');
    const info = saved ? JSON.parse(saved) : { name: '玩家' };

    try {
      this.myId = await this.multiplayer.host({
        ...info,
        name: info.name || '主机',
      });
      this.isHost = true;
      this.showMessage(`房间已创建! ID: ${this.myId}`);
    } catch (e) {
      this.showMessage('创建房间失败');
    }
  }

  private async joinRoom(): void {
    // 简单起见，使用固定IDjoin
    this.showMessage('请输入房间ID...');
  }

  private updatePlayerList(): void {
    this.playerTexts.forEach(t => t.destroy());
    this.playerTexts = [];

    let y = 130;
    this.players.forEach((player) => {
      const text = this.add.text(500, y, `${player.name} ${player.id === this.myId ? '(你)' : ''}`, {
        fontSize: '14px',
        color: '#ffffff',
      });
      this.playerTexts.push(text);
      y += 25;
    });
  }

  private showMessage(text: string): void {
    const msg = this.add.text(400, 500, text, {
      fontSize: '16px',
      color: '#ffffff',
    }).setOrigin(0.5);
    this.time.delayedCall(3000, () => msg.destroy());
  }
}
```

- [ ] **Step 3: 提交**

```bash
git add -A && git commit -m "feat: 添加多人联机P2P系统"
```

---

## 验收标准

### A: 音效/BGM
- [ ] BGM 可播放/停止/调整音量
- [ ] 音效可播放
- [ ] 战斗场景音效集成

### B: 精灵解析
- [ ] 精灵索引解析工具可运行
- [ ] CSS sprite 占位符生成
- [ ] 怪物占位符精灵渲染

### C: 称号系统
- [ ] 称号数据完整（14个称号）
- [ ] 可解锁/装备称号
- [ ] 称号界面可查看

### D: 生产制造
- [ ] 制造配方完整
- [ ] 材料消耗/产物获得
- [ ] 制造界面可操作

### E: 多人联机
- [ ] PeerJS 集成
- [ ] 可创建/加入房间
- [ ] 玩家列表同步

---

## 执行方式

**Subagent-Driven** - 每个 Task 分派独立子代理

## 子任务分解

由于 A-E 每个包含多个子任务，使用以下结构：

| Feature | Subtasks |
|---------|----------|
| A: 音效/BGM | A1: 音频系统, A2: BattleScene集成 |
| B: 精灵解析 | B1: 解析工具, B2: 渲染器 |
| C: 称号系统 | C1: 称号数据, C2: 称号系统, C3: 称号界面 |
| D: 生产制造 | D1: 制造数据, D2: 制造系统, D3: 制造界面 |
| E: 多人联机 | E1: P2P系统, E2: 大厅场景 |
