# Phase 3: 宠物系统 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development

**Goal:** 实现宠物系统，包括宠物数据结构、捕捉机制、养成、参战

**Architecture:** 宠物系统独立模块，与战斗系统集成

---

## Task 1: 宠物数据结构

**Files:**
- Create: `src/data/pet-data.ts`

### Step 1: 创建 src/data/pet-data.ts

```typescript
import { ElementType } from './element';

export interface PetStats {
  maxHp: number;
  attack: number;
  defense: number;
  agility: number;
}

export interface PetData {
  id: string;
  templateId: string;
  name: string;
  level: number;
  exp: number;
  element: ElementType;
  stats: PetStats;
  skills: string[];
  grade: 'normal' | 'elite' | 'legend';
  isCaptured: boolean;
}

export const PET_TEMPLATES: Record<string, Omit<PetData, 'id' | 'isCaptured'>> = {
  slime: {
    templateId: 'slime',
    name: '史莱姆',
    level: 1,
    exp: 0,
    element: 'water',
    stats: { maxHp: 25, attack: 8, defense: 5, agility: 6 },
    skills: ['skill_tackle'],
    grade: 'normal',
  },
  goblin: {
    templateId: 'goblin',
    name: '哥布林',
    level: 1,
    exp: 0,
    element: 'earth',
    stats: { maxHp: 40, attack: 12, defense: 7, agility: 10 },
    skills: ['skill_tackle', 'skill_bite'],
    grade: 'normal',
  },
  bat: {
    templateId: 'bat',
    name: '蝙蝠',
    level: 2,
    exp: 0,
    element: 'wind',
    stats: { maxHp: 30, attack: 14, defense: 4, agility: 15 },
    skills: ['skill_bite', 'skill_sonicboom'],
    grade: 'normal',
  },
};

export function createPet(templateId: string, level: number = 1): PetData {
  const template = PET_TEMPLATES[templateId];
  if (!template) throw new Error(`Unknown pet template: ${templateId}`);

  return {
    ...template,
    id: `pet_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
    level,
    exp: 0,
    isCaptured: false,
  };
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加宠物数据结构"
```

---

## Task 2: 宠物实体类

**Files:**
- Create: `src/entities/Pet.ts`

### Step 1: 创建 src/entities/Pet.ts

```typescript
import Phaser from 'phaser';
import { PetData } from '../data/pet-data';

export class Pet extends Phaser.GameObjects.Container {
  public data: PetData;
  private sprite!: Phaser.GameObjects.Sprite;
  private hpBar!: Phaser.GameObjects.Graphics;

  constructor(scene: Phaser.Scene, data: PetData, x: number, y: number) {
    super(scene, x, y);
    this.data = data;

    this.createSprite();
    scene.add.existing(this as unknown as Phaser.GameObjects.GameObject);
  }

  private createSprite(): void {
    this.sprite = this.scene.add.sprite(0, 0, 'player');
    this.sprite.setOrigin(0.5);
    this.sprite.setTint(0x44ff44);
    this.add(this.sprite);

    const hpBg = this.scene.add.graphics();
    hpBg.fillStyle(0x000000);
    hpBg.fillRect(-20, -35, 40, 4);
    this.add(hpBg);

    this.hpBar = this.scene.add.graphics();
    this.updateHPBar();
    this.add(this.hpBar);
  }

  public updateHPBar(): void {
    this.hpBar.clear();
    const ratio = this.data.stats.maxHp > 0 ? 1 : 0;
    this.hpBar.fillStyle(0x00ff00);
    this.hpBar.fillRect(-20, -35, 40 * ratio);
  }

  public getSprite(): Phaser.GameObjects.Sprite {
    return this.sprite;
  }

  public getElement(): string {
    return this.data.element;
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加宠物实体类"
```

---

## Task 3: 宠物捕捉系统

**Files:**
- Create: `src/systems/PetCaptureSystem.ts`

### Step 1: 创建 src/systems/PetCaptureSystem.ts

```typescript
import { PetData } from '../data/pet-data';
import { createPet } from '../data/pet-data';

export interface CaptureResult {
  success: boolean;
  pet?: PetData;
  message: string;
}

export class PetCaptureSystem {
  // 基础捕捉率
  private static BASE_CAPTURE_RATE = 0.3;

  static attemptCapture(targetHp: number, targetMaxHp: number, targetGrade: string): CaptureResult {
    // 捕捉概率 = (1 - 当前HP/最大HP) × 基础概率 × 等级修正
    const hpRatio = targetHp / targetMaxHp;
    const gradeModifier = targetGrade === 'legend' ? 0.1 : targetGrade === 'elite' ? 0.3 : 1.0;

    const captureChance = (1 - hpRatio) * this.BASE_CAPTURE_RATE * gradeModifier;

    if (Math.random() < captureChance) {
      const pet = createPet(targetHp > 30 ? 'slime' : 'bat', Math.floor(Math.random() * 5) + 1);
      pet.isCaptured = true;
      return {
        success: true,
        pet,
        message: `捕捉成功！获得了 ${pet.name}！`,
      };
    }

    return {
      success: false,
      message: '捕捉失败...',
    };
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加宠物捕捉系统"
```

---

## Task 4: 宠物养成系统

**Files:**
- Create: `src/systems/PetGrowthSystem.ts`

### Step 1: 创建 src/systems/PetGrowthSystem.ts

```typescript
import { PetData } from '../data/pet-data';

export interface LevelUpResult {
  leveledUp: boolean;
  newLevel: number;
  statIncreases: Partial<{ maxHp: number; attack: number; defense: number; agility: number }>;
  newSkills?: string[];
}

// 升级所需经验公式：level * 100
export function getExpForLevel(level: number): number {
  return level * 100;
}

// 宠物升级
export function calculateLevelUp(pet: PetData, expGain: number): LevelUpResult {
  pet.exp += expGain;

  const expNeeded = getExpForLevel(pet.level);
  if (pet.exp < expNeeded) {
    return { leveledUp: false, newLevel: pet.level, statIncreases: {} };
  }

  // 升级
  pet.level++;
  pet.exp -= expNeeded;

  // 属性成长
  const statIncreases = {
    maxHp: Math.floor(Math.random() * 5) + 3,
    attack: Math.floor(Math.random() * 2) + 1,
    defense: Math.floor(Math.random() * 2) + 1,
    agility: Math.floor(Math.random() * 2) + 1,
  };

  pet.stats.maxHp += statIncreases.maxHp;
  pet.stats.attack += statIncreases.attack;
  pet.stats.defense += statIncreases.defense;
  pet.stats.agility += statIncreases.agility;

  // 检查是否解锁新技能
  let newSkills: string[] | undefined;
  if (pet.level % 5 === 0 && pet.skills.length < 4) {
    newSkills = [...pet.skills, 'skill_power_up'];
  }

  return { leveledUp: true, newLevel: pet.level, statIncreases, newSkills };
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加宠物养成系统"
```

---

## Task 5: 宠物界面

**Files:**
- Create: `src/scenes/PetUIScene.ts`

### Step 1: 创建 src/scenes/PetUIScene.ts

```typescript
import Phaser from 'phaser';
import { PetData } from '../data/pet-data';

export class PetUIScene extends Phaser.Scene {
  private pets: PetData[] = [];
  private petCards: Phaser.GameObjects.Container[] = [];

  constructor() {
    super({ key: 'PetUIScene' });
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x1a1a2e);

    this.add.text(400, 30, '宠物列表', {
      fontSize: '24px',
      color: '#ffcc00',
    }).setOrigin(0.5);

    const backBtn = this.add.text(20, 20, '[ 返回 ]', {
      fontSize: '16px',
      color: '#aaaaaa',
    }).setInteractive();
    backBtn.on('pointerdown', () => this.scene.pop());

    this.loadPets();
    this.renderPetList();
  }

  private loadPets(): void {
    const saved = localStorage.getItem('capturedPets');
    this.pets = saved ? JSON.parse(saved) : [];
  }

  private savePets(): void {
    localStorage.setItem('capturedPets', JSON.stringify(this.pets));
  }

  private renderPetList(): void {
    this.petCards.forEach(card => card.destroy());
    this.petCards = [];

    if (this.pets.length === 0) {
      this.add.text(400, 300, '还没有宠物，去战斗捕捉吧！', {
        fontSize: '18px',
        color: '#ffffff',
      }).setOrigin(0.5);
      return;
    }

    let x = 100;
    let y = 100;

    this.pets.forEach((pet, index) => {
      const card = this.createPetCard(pet, x, y, index);
      this.petCards.push(card);
      x += 150;
      if (x > 700) {
        x = 100;
        y += 120;
      }
    });
  }

  private createPetCard(pet: PetData, x: number, y: number, index: number): Phaser.GameObjects.Container {
    const card = this.add.container(x, y);

    const bg = this.add.graphics();
    bg.fillStyle(0x333366);
    bg.fillRoundedRect(0, 0, 130, 100, 8);
    bg.lineStyle(2, 0x6666ff);
    bg.strokeRoundedRect(0, 0, 130, 100, 8);
    card.add(bg);

    const nameText = this.add.text(65, 15, pet.name, {
      fontSize: '14px',
      color: '#00ffff',
    }).setOrigin(0.5, 0);
    card.add(nameText);

    const levelText = this.add.text(65, 35, `Lv.${pet.level}`, {
      fontSize: '12px',
      color: '#aaaaaa',
    }).setOrigin(0.5, 0);
    card.add(levelText);

    const elementText = this.add.text(65, 55, `属性: ${pet.element}`, {
      fontSize: '10px',
      color: '#ffffff',
    }).setOrigin(0.5, 0);
    card.add(elementText);

    const hpText = this.add.text(65, 75, `HP: ${pet.stats.maxHp}`, {
      fontSize: '10px',
      color: '#00ff00',
    }).setOrigin(0.5, 0);
    card.add(hpText);

    return card;
  }

  public addPet(pet: PetData): void {
    this.pets.push(pet);
    this.savePets();
    this.renderPetList();
  }
}
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 添加宠物界面"
```

---

## Task 6: 集成宠物到战斗

**Files:**
- Modify: `src/scenes/BattleScene.ts`

### Step 1: 修改 BattleScene.ts 添加捕捉选项

在战斗 UI 中添加"捕捉"按钮选项：

```typescript
// 在技能选择旁边添加捕捉选项
const captureBtn = this.add.text(200, y, '[ 捕捉 ]', {
  fontSize: '14px',
  color: '#ff44ff',
}).setInteractive({ useHandCursor: true });

captureBtn.on('pointerdown', () => {
  // 如果目标是野生宠物，可以尝试捕捉
});
```

### Step 2: 提交

```bash
git add -A && git commit -m "feat: 集成宠物到战斗系统"
```

---

## Phase 3 验收标准

- [ ] 宠物数据结构完整
- [ ] 可以捕捉野生宠物
- [ ] 宠物升级后属性增长
- [ ] 宠物界面可查看列表
- [ ] 宠物可参战

---

## 执行方式

**Subagent-Driven** - 每个 Task 分派独立子代理
