# Phase 4: 扩展系统 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development

**Goal:** 实现物品系统和任务系统，完善游戏核心循环

---

## Task 1: 物品数据结构

**Files:**
- Create: `src/data/item-data.ts`

### Step 1: 创建 src/data/item-data.ts

```typescript
export type ItemType = 'weapon' | 'armor' | 'accessory' | 'consumable' | 'material';

export interface ItemData {
  id: string;
  name: string;
  type: ItemType;
  description: string;
  price: number;
  effect?: {
    hpRestore?: number;
    mpRestore?: number;
    attackBoost?: number;
    defenseBoost?: number;
  };
}

export const ITEMS: Record<string, ItemData> = {
  potion: {
    id: 'potion',
    name: '治疗药水',
    type: 'consumable',
    description: '恢复 50 HP',
    price: 50,
    effect: { hpRestore: 50 },
  },
  hi_potion: {
    id: 'hi_potion',
    name: '高级治疗药水',
    type: 'consumable',
    description: '恢复 200 HP',
    price: 200,
    effect: { hpRestore: 200 },
  },
  ether: {
    id: 'ether',
    name: '魔力药水',
    type: 'consumable',
    description: '恢复 30 MP',
    price: 80,
    effect: { mpRestore: 30 },
  },
  iron_sword: {
    id: 'iron_sword',
    name: '铁剑',
    type: 'weapon',
    description: '攻击力 +5',
    price: 200,
    effect: { attackBoost: 5 },
  },
  leather_armor: {
    id: 'leather_armor',
    name: '皮甲',
    type: 'armor',
    description: '防御力 +3',
    price: 150,
    effect: { defenseBoost: 3 },
  },
};

export interface InventorySlot {
  itemId: string;
  quantity: number;
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加物品数据结构"
```

---

## Task 2: 背包系统

**Files:**
- Create: `src/systems/InventorySystem.ts`
- Create: `src/scenes/InventoryScene.ts`

### Step 1: 创建 src/systems/InventorySystem.ts

```typescript
import { InventorySlot, ItemData, ITEMS } from '../data/item-data';

export class InventorySystem {
  private inventory: InventorySlot[] = [];
  private maxSlots = 20;

  constructor() {
    this.load();
  }

  load(): void {
    const saved = localStorage.getItem('inventory');
    this.inventory = saved ? JSON.parse(saved) : [];
  }

  save(): void {
    localStorage.setItem('inventory', JSON.stringify(this.inventory));
  }

  addItem(itemId: string, quantity: number = 1): boolean {
    const existing = this.inventory.find(slot => slot.itemId === itemId);
    if (existing) {
      existing.quantity += quantity;
    } else if (this.inventory.length < this.maxSlots) {
      this.inventory.push({ itemId, quantity });
    } else {
      return false; // 背包已满
    }
    this.save();
    return true;
  }

  removeItem(itemId: string, quantity: number = 1): boolean {
    const slot = this.inventory.find(s => s.itemId === itemId);
    if (!slot || slot.quantity < quantity) return false;

    slot.quantity -= quantity;
    if (slot.quantity <= 0) {
      this.inventory = this.inventory.filter(s => s.itemId !== itemId);
    }
    this.save();
    return true;
  }

  getInventory(): InventorySlot[] {
    return [...this.inventory];
  }

  getItemData(itemId: string): ItemData | undefined {
    return ITEMS[itemId];
  }

  hasItem(itemId: string): boolean {
    return this.inventory.some(slot => slot.itemId === itemId);
  }

  getItemCount(itemId: string): number {
    const slot = this.inventory.find(s => s.itemId === itemId);
    return slot?.quantity || 0;
  }
}
```

### Step 2: 创建 src/scenes/InventoryScene.ts

```typescript
import Phaser from 'phaser';
import { InventorySystem } from '../systems/InventorySystem';

export class InventoryScene extends Phaser.Scene {
  private inventory!: InventorySystem;
  private slots: Phaser.GameObjects.Container[] = [];

  constructor() {
    super({ key: 'InventoryScene' });
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x1a1a2e);
    this.inventory = new InventorySystem();

    this.add.text(400, 30, '背包', {
      fontSize: '24px',
      color: '#ffcc00',
    }).setOrigin(0.5);

    const backBtn = this.add.text(20, 20, '[ 返回 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setInteractive();
    backBtn.on('pointerdown', () => this.scene.pop());

    this.renderInventory();
  }

  private renderInventory(): void {
    this.slots.forEach(slot => slot.destroy());
    this.slots = [];

    const items = this.inventory.getInventory();

    if (items.length === 0) {
      this.add.text(400, 300, '背包是空的', {
        fontSize: '18px',
        color: '#ffffff',
      }).setOrigin(0.5);
      return;
    }

    let x = 100;
    let y = 100;

    items.forEach((slot) => {
      const itemData = this.inventory.getItemData(slot.itemId);
      if (!itemData) return;

      const container = this.add.container(x, y);

      const bg = this.add.graphics();
      bg.fillStyle(0x333366);
      bg.fillRect(0, 0, 200, 50);
      bg.lineStyle(1, 0x6666ff);
      bg.strokeRect(0, 0, 200, 50);
      container.add(bg);

      const nameText = this.add.text(10, 8, itemData.name, {
        fontSize: '14px',
        color: '#00ffff',
      });
      container.add(nameText);

      const descText = this.add.text(10, 28, `${itemData.description} x${slot.quantity}`, {
        fontSize: '10px',
        color: '#aaaaaa',
      });
      container.add(descText);

      this.slots.push(container);
      x += 220;
      if (x > 600) {
        x = 100;
        y += 70;
      }
    });
  }
}
```

### Step 3: 提交

```bash
git add -A && git commit -m "feat: 添加背包系统"
```

---

## Task 3: 任务系统

**Files:**
- Create: `src/data/quest-data.ts`
- Create: `src/systems/QuestSystem.ts`
- Create: `src/scenes/QuestScene.ts`

### Step 1: 创建 src/data/quest-data.ts

```typescript
export type QuestType = 'talk' | 'kill' | 'collect' | 'reach_level';

export interface QuestObjective {
  type: QuestType;
  target?: string;
  count?: number;
  current: number;
}

export interface QuestData {
  id: string;
  title: string;
  description: string;
  type: QuestType;
  objectives: QuestObjective[];
  reward: {
    exp: number;
    gold?: number;
    items?: { itemId: string; quantity: number }[];
  };
  isComplete: boolean;
  isRewardClaimed: boolean;
}

export const QUESTS: QuestData[] = [
  {
    id: 'quest_first_battle',
    title: '初次战斗',
    description: '前往野外与怪物战斗',
    type: 'kill',
    objectives: [{ type: 'kill', target: 'enemy', count: 1, current: 0 }],
    reward: { exp: 100, gold: 50 },
    isComplete: false,
    isRewardClaimed: false,
  },
  {
    id: 'quest_catch_pet',
    title: '初次捕捉',
    description: '捕捉一只宠物',
    type: 'collect',
    objectives: [{ type: 'collect', target: 'pet', count: 1, current: 0 }],
    reward: { exp: 150 },
    isComplete: false,
    isRewardClaimed: false,
  },
];
```

### Step 2: 创建 src/systems/QuestSystem.ts

```typescript
import { QuestData, QUESTS } from '../data/quest-data';

export class QuestSystem {
  private quests: QuestData[] = [];

  constructor() {
    this.load();
  }

  load(): void {
    const saved = localStorage.getItem('quests');
    this.quests = saved ? JSON.parse(saved) : QUESTS.map(q => ({ ...q }));
  }

  save(): void {
    localStorage.setItem('quests', JSON.stringify(this.quests));
  }

  getQuests(): QuestData[] {
    return this.quests;
  }

  updateQuestProgress(type: string, target: string, amount: number = 1): void {
    for (const quest of this.quests) {
      if (quest.isComplete || quest.isRewardClaimed) continue;

      for (const obj of quest.objectives) {
        if (obj.type === type && obj.target === target) {
          obj.current = Math.min(obj.count || 1, obj.current + amount);
        }
      }

      this.checkQuestComplete(quest);
    }
    this.save();
  }

  private checkQuestComplete(quest: QuestData): void {
    quest.isComplete = quest.objectives.every(obj => obj.current >= (obj.count || 1));
  }

  claimReward(questId: string): boolean {
    const quest = this.quests.find(q => q.id === questId);
    if (!quest || !quest.isComplete || quest.isRewardClaimed) return false;

    quest.isRewardClaimed = true;
    this.save();
    return true;
  }
}
```

### Step 3: 创建 src/scenes/QuestScene.ts

```typescript
import Phaser from 'phaser';
import { QuestSystem } from '../systems/QuestSystem';

export class QuestScene extends Phaser.Scene {
  private questSystem!: QuestSystem;
  private questCards: Phaser.GameObjects.Container[] = [];

  constructor() {
    super({ key: 'QuestScene' });
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x1a1a2e);
    this.questSystem = new QuestSystem();

    this.add.text(400, 30, '任务列表', {
      fontSize: '24px',
      color: '#ffcc00',
    }).setOrigin(0.5);

    const backBtn = this.add.text(20, 20, '[ 返回 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setInteractive();
    backBtn.on('pointerdown', () => this.scene.pop());

    this.renderQuests();
  }

  private renderQuests(): void {
    this.questCards.forEach(card => card.destroy());
    this.questCards = [];

    const quests = this.questSystem.getQuests();
    let y = 80;

    quests.forEach((quest) => {
      const card = this.createQuestCard(quest, 100, y);
      this.questCards.push(card);
      y += 100;
    });
  }

  private createQuestCard(quest: any, x: number, y: number): Phaser.GameObjects.Container {
    const card = this.add.container(x, y);

    const bg = this.add.graphics();
    bg.fillStyle(quest.isComplete && !quest.isRewardClaimed ? 0x336633 : 0x333366);
    bg.fillRoundedRect(0, 0, 600, 80, 8);
    card.add(bg);

    const titleText = this.add.text(15, 10, quest.title, {
      fontSize: '16px',
      color: '#ffcc00',
    });
    card.add(titleText);

    const descText = this.add.text(15, 35, quest.description, {
      fontSize: '12px',
      color: '#aaaaaa',
    });
    card.add(descText);

    const progressText = this.add.text(15, 55, `进度: ${quest.objectives[0]?.current || 0}/${quest.objectives[0]?.count || 1}`, {
      fontSize: '12px',
      color: quest.isComplete ? '#00ff00' : '#ffffff',
    });
    card.add(progressText);

    return card;
  }
}
```

### Step 4: 提交

```bash
git add -A && git commit -m "feat: 添加任务系统"
```

---

## Phase 4 验收标准

- [ ] 物品数据结构完整
- [ ] 背包可添加/移除物品
- [ ] 物品界面可查看
- [ ] 任务系统可追踪进度
- [ ] 任务奖励可领取

---

## 执行方式

**Subagent-Driven** - 每个 Task 分派独立子代理
